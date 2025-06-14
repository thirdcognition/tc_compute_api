import json
import os
import pprint as pp
import re
from typing import Any, Dict, List, Union
from pydantic import BaseModel
import yaml
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

from source.models.config.default_env import DEBUGMODE
from source.models.config.logging import logger


current_dir = os.path.dirname(os.path.abspath(__file__))


def print_params(msg="", params="", method=logger.debug):
    if DEBUGMODE:
        if msg:
            method(f"\n\n\n{msg}")
        if params:
            method(f"'\n\n{pp.pformat(params).replace('\\n', '\n')}\n\n")


def pretty_print(obj, msg=None, force=DEBUGMODE, method=logger.debug):
    if force:
        if msg:
            method(f"\n\n\n{msg}\n")
        else:
            method(f"\n\n\n{type(obj)}\n")
        if obj is None:
            method("obj = None")
        elif isinstance(obj, BaseModel):
            try:
                method(obj.model_dump_json(indent=2))
            except Exception as e:
                method(f"Failed to serialize BaseModel: {e}")
                method(repr(obj))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                method(f"\n{i}:\n")
                if isinstance(item, BaseModel):
                    method(item.model_dump_json(indent=2))
                    method("\n\n")
                else:
                    pp.pprint(item)
        elif isinstance(obj, type):
            method(f"Non-serializable type: {obj}")
        else:
            try:
                pp.pprint(obj)
            except Exception as e:
                method(f"Failed to pretty print object: {e}")
                method(repr(obj))
        method("\n\n")


def validate_category(category: str) -> bool:
    # Check length
    if not 3 <= len(category) <= 63:
        return False
    # Check start and end with alphanumeric character
    if not category[0].isalnum() or not category[-1].isalnum():
        return False
    # Check for valid characters
    if not re.match(r"^[A-Za-z0-9_\-]*$", category) or " " in category:
        return False
    # Check for consecutive periods
    if ".." in category:
        return False
    # Check for IPv4 address
    if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", category):
        return False
    return True


def is_valid_email(email):
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


# def get_chain_with_history(chain_id: str, chain: RunnableSequence):
#     if "history_chains" not in st.session_state:
#         st.session_state["history_chains"] = {}
#     if chain_id in st.session_state["history_chains"]:
#         return st.session_state["history_chains"][chain_id]

#     history_chain = RunnableWithMessageHistory(
#         runnable=chain,
#         get_session_history=get_session_history,
#         input_messages_key="question",
#         output_messages_key="answer",
#         history_messages_key="chat_history",
#     )

#     st.session_state["history_chains"][chain_id] = history_chain
#     return history_chain


def read_and_load_yaml(file_path):
    with open(file_path, "r") as file:
        content = file.read().replace("\t", "    ")
        data = yaml.safe_load(content)
    return data


def get_text_from_completion(completion):
    completion_content = repr(completion)
    if isinstance(completion, List) and isinstance(completion[0], Document):
        completion_content = "\n\n".join(
            [doc.page_content.strip() for doc in completion]
        )
    elif isinstance(completion, tuple):
        if isinstance(completion[0], bool):
            completion_content = completion[1].strip()
        elif len(completion) == 2:
            completion_content = (
                f"<think> {completion[1].strip()} </think>"
                if len(completion[1].strip()) > 0
                else ""
            ) + f"{completion[0].strip()}"
        else:
            completion_content = completion[0].strip()
    elif isinstance(completion, BaseMessage):
        completion_content = completion.content.strip()
    elif isinstance(completion, Document):
        completion_content = completion.page_content
    elif isinstance(completion, BaseModel):
        completion_content = completion.model_dump_json()
    elif isinstance(completion, dict) and "content" in completion.keys():
        if isinstance(completion["content"], str):
            completion_content = str(completion["content"]).strip()
        else:
            completion_content = json.dumps(completion["content"], indent=2)
        completion_content = str(completion["content"]).strip()
    elif isinstance(completion, str):
        completion_content = completion.strip()

    return completion_content


def get_number(page_number):
    if isinstance(page_number, (int, float)):
        return int(page_number)
    elif isinstance(page_number, str) and page_number.isdigit():
        return int(page_number)
    elif ", " in page_number:
        page_number = page_number.split(", ")[0]
        if page_number.isdigit():
            return int(page_number)
    return 0


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_dict({str(i): item}, new_key).items())
        else:
            try:
                if not isinstance(v, (int, float, str, bool)):
                    v = json.dumps(v)
                items.append((new_key, v))
            except Exception as e:
                logger.error(f"Error flattening key '{new_key}': {e}")
                continue
    return dict(items)


def combine_metadata(docs: List[Document]) -> Dict[str, Any]:
    combined_metadata = {k: v for k, v in docs[0].metadata.items()}
    for doc in docs[1:]:
        for k, v in doc.metadata.items():
            if k in combined_metadata and combined_metadata[k] is not None:
                if isinstance(combined_metadata[k], dict):
                    combined_metadata[k].update(v)
                elif isinstance(combined_metadata[k], list):
                    if isinstance(v, list):
                        combined_metadata[k].extend(v)
                    else:
                        combined_metadata[k].append(v)
                elif isinstance(combined_metadata[k], str):
                    combined_metadata[k] += f", {repr(v)}"
                else:
                    combined_metadata[k] = f"{repr(combined_metadata[k])}, {repr(v)}"
            else:
                combined_metadata[k] = v

    return combined_metadata


def get_specific_tag(items, tag="category_tag") -> List[dict]:
    found_items = []
    for item in items:
        if item["tag"] == tag:
            found_items.append(item)
        if 0 < len(item["children"]):
            found_items.extend(get_specific_tag(item["children"], tag))
    return found_items


def convert_tags_to_dict(input_dict, tags, output_tag="item"):
    output_dict = {output_tag: {}}

    for child in input_dict["children"]:
        if child["tag"] in tags:
            if child["tag"] in output_dict[output_tag]:
                if isinstance(output_dict[output_tag][child["tag"]], list):
                    output_dict[output_tag][child["tag"]].append(child["body"].strip())
                else:
                    output_dict[output_tag][child["tag"]] = [
                        output_dict[output_tag][child["tag"]],
                        child["body"].strip(),
                    ]
            else:
                output_dict[output_tag][child["tag"]] = child["body"].strip()

    return output_dict


def get_id_str(item):
    if isinstance(item, list):
        item = "-".join(item)
    if isinstance(item, dict):
        item = "-".join(item.values())

    item = re.sub(
        r"[\'\(\)\"]", "", item
    )  # remove single quotes, parentheses, and double quotes
    item = re.sub(
        r"[\n\t]+", " ", item
    )  # replace newline and tab characters with a space
    item = re.sub(r"\s+", " ", item)  # replace multiple whitespaces with a single space
    item = item.replace(" ", "-")  # replace spaces with hyphens
    item = re.sub(r"-+", "-", item)  # replace multiple hyphens with a single hyphen
    item = item.lower()  # convert to lowercase
    item = item.strip("-")  # remove leading and trailing hyphens
    item = item.strip()  # remove leading and trailing hyphens
    return item


def get_unique_id(id_str: str, existing_ids: List[str] = []):
    if existing_ids is None:
        existing_ids = []
    id = get_id_str(id_str)
    if id not in existing_ids:
        return id
    id_index = 0
    max = len(existing_ids) + 10
    while True and id_index < max:
        id_index += 1
        new_id = f"{id}_{id_index}"
        if new_id not in existing_ids:
            return new_id
    return f"{id}_{id_index}"


def get_item_str(
    items: Union[Any, List],
    as_json: bool = False,
    as_tags: bool = False,
    as_array: bool = False,
    key_names: List[str] = [
        "id",
    ],
    key_mapping: Dict[str, str] = {},
    select_keys: List[str] = None,
    item_str="item",
    one_liner=False,
    show_empty_keys=False,
) -> Union[str, List[str]]:
    if not isinstance(items, list):
        items = [items]

    ret_str = []
    for item in items:
        item_dict = {}
        if isinstance(item, str):
            ret_str.append(item)
            continue
        if isinstance(item, BaseModel):
            item = item.model_dump()
        # Replace with Database object
        # if isinstance(item, Base):
        #     item = item.__dict__

        for key in key_names:
            if (select_keys is None or key in select_keys) and key in item.keys():
                value = item[key]
                if value is None and not show_empty_keys:
                    continue
                elif value is None and not as_json:
                    value = "None"
                # logger.debug(key, value)
                if isinstance(value, Document):
                    value = value.page_content

                if not isinstance(value, (str, int, float, bool, type(None))):
                    if not as_json:
                        value = yaml.dump(value)
                    else:
                        if isinstance(value, BaseModel):
                            value = value.model_dump(mode="json")
                        # elif isinstance(value, Base):
                        #     value = value.__dict__
                        elif isinstance(value, (dict, list, tuple, set)):
                            if isinstance(value, dict):
                                value = {k: v for k, v in value.items()}
                            else:
                                value = list(value)
                            for i, v in enumerate(value):
                                if isinstance(v, (str, int, float, bool, type(None))):
                                    value[i] = v
                                elif isinstance(v, BaseModel):
                                    value[i] = v.model_dump(mode="json")
                                # elif isinstance(v, Base):
                                #     value[i] = v.__dict__
                                else:
                                    try:
                                        value[i] = json.dumps(v)
                                    except BaseException:
                                        value[i] = repr(v)

                if isinstance(value, str):
                    if one_liner:
                        value = value.replace("\n", " ")
                        value = re.sub(r"\s+", " ", value)
                    value = value.strip()

                item_dict[
                    key if key not in key_mapping.keys() else key_mapping[key]
                ] = value
        if as_json:
            item_str = json.dumps(item_dict, indent=2 if not one_liner else None)
        elif as_tags:
            item_str = ""
            for key in item_dict.keys():
                if isinstance(item_dict[key], str) and "\n" in item_dict[key]:
                    item_str += f"<{key}>\n{item_dict[key]}\n</{key}>\n"
                else:
                    item_str += f"<{key}>{item_dict[key]}</{key}> "
                    if not one_liner:
                        item_str += "\n"
        else:
            item_str = ""
            for key in item_dict.keys():
                if isinstance(item_dict[key], str) and "\n" in item_dict[key]:
                    item_str += str(key).capitalize() + ":\n" + item_dict[key] + "\n"
                else:
                    item_str += f"{str(key).capitalize()}: {item_dict[key]} "
                    if not one_liner:
                        item_str += "\n"

            item_str = item_str.strip()
        if as_tags:
            ret_str.append(
                (
                    ("<" + item_str + ">{}</" + item_str + ">")
                    if one_liner
                    else ("<" + item_str + ">\n{}\n</" + item_str + ">\n\n")
                ).format(item_str)
            )
        else:
            ret_str.append(item_str)

    if as_array:
        return ret_str
    if as_json:
        if len(items) == 1:
            return ret_str[0]
        else:
            return ("[{}]" if one_liner else "[\n{}\n]\n\n").format(", ".join(ret_str))
    if as_tags:
        if len(items) == 1:
            return ret_str[0]
        else:
            return (
                ("<" + item_str + "s>{}</" + item_str + "s>")
                if one_liner
                else ("<" + item_str + "s>\n{}\n</" + item_str + "s>\n\n")
            )

    if len(items) == 1:
        return ret_str[0]
    else:
        return (" " if one_liner else "\n\n").join(ret_str)
