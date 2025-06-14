import concurrent.futures
from functools import cache
import re
from bs4 import BeautifulSoup
from markdown import markdown
from typing import Dict, List, Union

# from langchain_chroma import Chroma
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)

# from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.text_splitter import (
    SemanticChunker,
    BreakpointThresholdType,
)
from langchain.schema.document import Document

from source.load_env import SETTINGS
from source.models.config.logging import logger
from source.chains import get_embeddings  # Updated import

# from source.models.concepts import ConceptDataTable
# from source.models.source import SourceContents
# from source.models.topics import TopicDataTable


@cache
def get_text_splitter(chunk_size, chunk_overlap):
    if chunk_size < chunk_overlap:
        chunk_overlap = chunk_size / 2

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )


def markdown_to_text(markdown_string):
    """Converts a markdown string to plaintext"""

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r"<pre>(.*?)</pre>", "\1", html)
    html = re.sub(r"<code>(.*?)</code>", "\1", html)
    html = html.replace("```markdown", "")
    html = html.replace("```", "")

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = "".join(soup.findAll(string=True))

    return text


def split_text(text, split=SETTINGS.default_llms.instruct.char_limit, overlap=100):
    text_len = len(text)
    split = text_len // (text_len / split)
    if (text_len - split) > overlap:
        splitter = get_text_splitter(chunk_size=split, chunk_overlap=overlap)
        return splitter.split_text(text)
    else:
        return [text]


def join_documents(texts, split=SETTINGS.default_llms.instruct.char_limit):
    joins = []
    text_join = ""

    total_len = 0
    for text in texts:
        _text = ""
        if isinstance(text, str):
            _text = text
        else:
            _text = text.page_content

        total_len += len(_text)

    chunks = total_len // split + 1
    chunk_length = total_len // chunks

    for text in texts:
        _text = ""
        if isinstance(text, str):
            _text = text
        else:
            _text = text.page_content

        if (
            len(_text) > 100
            and (len(text_join) + len(_text)) > chunk_length
            and len(text_join) > 100
        ):
            joins.append(text_join)
            text_join = _text
        else:
            text_join += _text + "\n\n"

    joins.append(text_join)

    return joins


def semantic_splitter(
    text,
    split=SETTINGS.default_llms.instruct.char_limit,
    progress_cb=None,
    threshold_type: BreakpointThresholdType = "percentile",
):
    if len(text) > 1000:
        less_text = split_text(text, SETTINGS.default_embeddings.default.char_limit, 0)
    else:
        less_text = [text]

    semantic_splitter = SemanticChunker(
        get_embeddings("base"), breakpoint_threshold_type="percentile"
    )

    texts = []
    for i, txt in enumerate(less_text):
        texts = texts + (
            semantic_splitter.split_text(txt)
            if len(txt.strip()) > 100
            else [txt.strip()]
        )
        if progress_cb is not None and callable(progress_cb):
            progress_cb(len(less_text), i)

    return join_documents(texts, split)


def __split_text(semantic_splitter: SemanticChunker, txt: str):
    try:
        resp = (
            semantic_splitter.split_text(txt)
            if len(txt.strip()) > 100
            else [txt.strip()]
        )
    except Exception as e:
        logger.error(e)
        resp = [txt.strip()]
    return resp


# Breakpoint defaults:
# "percentile": 95,
# "standard_deviation": 3,
# "interquartile": 1.5,
# "gradient": 95,


async def a_semantic_splitter(
    texts: Union[str, List[str]],
    split=SETTINGS.default_llms.instruct.char_limit,
    progress_cb=None,
    threshold_type: BreakpointThresholdType = "percentile",
    breakpoint_threshold=None,
):
    if isinstance(texts, str):
        texts = [texts]

    less_text = []
    for text in texts:
        if len(text) > 1000:
            less_text += split_text(
                text, SETTINGS.default_embeddings.default.char_limit, 0
            )
        else:
            less_text.append(text)

    semantic_splitter = SemanticChunker(
        get_embeddings("base"),
        breakpoint_threshold_type=threshold_type,
        breakpoint_threshold_amount=breakpoint_threshold,
    )

    texts = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_text = {
            executor.submit(__split_text, semantic_splitter, txt): txt
            for txt in less_text
        }
        for future in concurrent.futures.as_completed(future_to_text):
            texts.extend(future.result())
            if progress_cb is not None and callable(progress_cb):
                progress_cb(len(less_text), len(texts))

    return join_documents(texts, split)


def split_markdown(text, split=SETTINGS.default_llms.instruct.char_limit):
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
        ("#####", "Header 5"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )

    md_texts = markdown_splitter.split_text(text)
    texts = [
        text for md_text in md_texts for text in split_text(md_text.page_content, split)
    ]
    # avg_len = sum(len(text) for text in texts) / len(texts)
    # min_len = min(len(text) for text in texts)
    # max_len = max(len(text) for text in texts)

    # logger.debug(f"Average length of each string in texts: {avg_len}, Min length: {min_len}, Max length: {max_len}, Total amount of strings: {len(texts)}")

    return join_documents(texts, split)


def create_document_lists(
    list_of_strings: List[str],
    source="local",
    list_of_metadata: List[Dict[str, any]] = None,
):
    doc_list = []

    for index, item in enumerate(list_of_strings):
        metadata = list_of_metadata[index] if list_of_metadata else None
        if metadata is None:
            metadata = {"source": source, "index": index}

        if len(item) > 3000:
            split_texts = split_text(item, split=3000, overlap=100)
            for split_item in split_texts:
                doc = Document(
                    page_content=split_item,
                    metadata=metadata,
                )
                doc_list.append(doc)
        else:
            doc = Document(
                page_content=item,
                metadata=metadata,
            )
            doc_list.append(doc)

    return doc_list


# def get_source_rag_chunks(
#     texts: List[str],
#     source: str,
#     categories: List[str],
#     content: SourceContents,
#     filetype: str = "txt",
# ) -> tuple[List[str], List[Dict[str, Dict]], List[Dict]]:
#     if texts is not None and filetype != "md":
#         rag_split = split_text(
#             "\n".join(texts),
#             SETTINGS.default_embeddings.default.char_limit,
#             SETTINGS.default_embeddings.default.overlap,
#         )
#     elif filetype == "md":
#         rag_split = split_text(
#             markdown_to_text("\n".join(texts)),
#             SETTINGS.default_embeddings.default.char_limit,
#             SETTINGS.default_embeddings.default.overlap,
#         )

#     rag_ids = [source + "_" + str(i) for i in range(len(rag_split))]
#     rag_metadatas = [
#         {
#             "source": source,
#             "categories": ", ".join(categories),
#             "filetype": filetype,
#             "split": i,
#         }
#         for i in range(len(rag_split))
#     ]

#     if content.formatted_content is not None and content.formatted_content:
#         if (
#             len(content.formatted_content)
#             > SETTINGS.default_embeddings.default.char_limit
#         ):
#             formatted_split = split_text(
#                 content.formatted_content,
#                 SETTINGS.default_embeddings.default.char_limit,
#                 SETTINGS.default_embeddings.default.overlap,
#             )
#         else:
#             formatted_split = [content.formatted_content]

#         page_contents = []
#         if content.pages is not None and len(content.pages) > 1:
#             page_contents = [page.content for page in content.pages]

#         rag_split = rag_split + formatted_split + page_contents
#         rag_ids = rag_ids + [
#             source + "_formatted_" + str(i) for i in range(len(formatted_split))
#         ] + [
#             source + "_formatted_page_" + str(i)
#             for i in range(len(page_contents))
#         ]
#         rag_metadatas = rag_metadatas + [
#             flatten_dict({
#                 "source": "formatted_" + source,
#                 "categories": ", ".join(categories),
#                 "filetype": filetype,
#                 "split": i,
#             })
#             for i in range(len(formatted_split))
#         ] + [
#             flatten_dict({
#                 "source": "formatted_page_" + source,
#                 "categories": ", ".join(categories),
#                 "filetype": filetype,
#                 "split": i,
#             })
#             for i in range(len(page_contents))
#         ]
#         rag_metadatas = [{k: v for k, v in metadata.items() if v is not None} for metadata in rag_metadatas]

#     return rag_split, rag_ids, rag_metadatas


# def get_concept_rag_chunks(
#     category_id: str,
#     concepts: List[ConceptDataTable],
# ) -> List[tuple[ConceptDataTable, List[str], List[Dict[str, Dict]], List[Dict]]]:
#     response = []
#     for i, concept in enumerate(concepts):
#         # concept_split = []
#         # concept_ids = []
#         # concept_metadatas = []
#         concept_split = split_text(
#             concept.content,
#             SETTINGS.default_embeddings.default.char_limit,
#             SETTINGS.default_embeddings.default.overlap,
#         )
#         # concept_split += concept_split
#         concept_ids = [
#             f"{category_id if category_id not in concept.id else ''}{concept.id}_{i}_{j}".replace(" ", "_")
#             for j in range(len(concept_split))
#         ]

#         concept_metadatas = [
#             flatten_dict({
#                 "concept_id": concept.id,
#                 "concept_taxonomy": ", ".join([tag for tag in concept.taxonomy]),
#                 "split": str(i) + "_" + str(j),
#                 "references": "\n".join(
#                     [
#                         str(reference)
#                         for reference in concept.references
#                     ]
#                 ),
#             })
#             for j in range(len(concept_split))
#         ]
#         concept_metadatas = [{k: v for k, v in metadata.items() if v is not None} for metadata in concept_metadatas]
#         response.append((concept, concept_split, concept_ids, concept_metadatas))
#     return response

# def get_topic_rag_chunks(
#     topics: List[TopicDataTable],
#     source: str,
#     categories: List[str],
# ) -> List[tuple[TopicDataTable, List[str], List[Dict[str, Dict]], List[Dict]]]:
#     response = []
#     category_id = "-".join(categories).lower().strip().replace(" ", "_")
#     for i, topic in enumerate(topics):
#         # topic_split = []
#         # topic_ids = []
#         # topic_metadatas = []
#         topic_split = split_text(
#             topic.page_content,
#             SETTINGS.default_embeddings.default.char_limit,
#             SETTINGS.default_embeddings.default.overlap,
#         )
#         # topic_split += topic_split
#         id = f"{topic.topic.lower().strip().replace(' ', '_')}"
#         topic_ids = [
#             (
#                 (
#                     (category_id + "-" + id)
#                     if category_id not in id
#                     else id
#                 )
#                 + "_"
#                 + str(i)
#                 + "_"
#                 + str(j)
#             ).replace(" ", "_")
#             for j in range(len(topic_split))
#         ]

#         topic_metadatas = [
#             flatten_dict({
#                 "source": source,
#                 "topic": topic.topic,
#                 "topic_id": id,
#                 "categories": ", ".join(categories),
#                 "split": str(i) + "_" + str(j),
#                 **topic.doc_metadata,
#             })
#             for j in range(len(topic_split))
#         ]
#         # Remove None type keys from topic_metadata
#         topic_metadatas = [{k: v for k, v in metadata.items() if v is not None} for metadata in topic_metadatas]

#         topic.chroma_collections = list(set(["rag_" + cat + "_topic" for cat in categories]))
#         topic.chroma_ids = list(set(topic_ids))
#         response.append((topic, topic_split, topic_ids, topic_metadatas))
#     return response
