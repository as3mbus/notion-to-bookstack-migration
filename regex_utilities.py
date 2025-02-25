import re


def ReplaceSymbolsWithinBrackets(string: str):

    pattern = r'\(([^)]*)\)'

    new_string = re.sub(


        pattern,


        lambda x: f"({ReplaceSymbols(x.group(1))})",
        string)

    return new_string


def ReplaceSymbols(string: str):

    new_string = re.sub(r'%20', ' ', string)
    new_string = re.sub(r'%5B', '[', new_string)
    new_string = re.sub(r'%5D', ']', new_string)
    return new_string
