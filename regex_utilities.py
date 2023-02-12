import re


def replaceSpace(string: str):
    pattern = r'\(([^)]*)\)'
    new_string = re.sub(
        pattern,
        lambda x: f"({re.sub(r'%20', ' ', x.group(1))})",
        string)
    return new_string
