import re


def ReplaceSpaceWithinBrackets(string: str):
    pattern = r'\(([^)]*)\)'
    new_string = re.sub(
        pattern,
        lambda x: f"({ReplaceSpace(x.group(1))})",
        string)
    return new_string


def ReplaceSpace(string:str):
    new_string = re.sub(r'%20',' ' ,string)
    return new_string