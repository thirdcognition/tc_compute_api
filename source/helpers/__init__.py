import re


def convert_to_path(title: str) -> str:
    # Remove illegal characters for file names
    sanitized_title = re.sub(r'[<>:"/\\|?*]', "", title)
    # Replace spaces with underscores
    path_safe_title = sanitized_title.replace(" ", "_").lower()
    return path_safe_title
