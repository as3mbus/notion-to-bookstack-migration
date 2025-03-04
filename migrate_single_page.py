import os
import json
import codecs
from bookstack_api import BookstackAPI, BookData, PageData
from notion_formatting import NotionPage
from regex_utilities import ReplaceSymbolsWithinBrackets, ReplaceSymbols
from bookstack_control import *
import pandas
import textwrap
import re

def debug(string):
    if (not enable_debug):
        return
    print(string)

# region credential setup


f = open('credential.json')
cred = json.load(f)
bookstack_api = BookstackAPI()
bookstack_api.LoadCredential(cred)

# endregion

# region Configurations
enable_debug = True
book_id= 85
relative_path = "input"
file_name = "[S-Unreal] Unreal Style Guidelines 80893b3a9d024025a0a78d4259fcd4f3.md"

# endregion
input_dir_path = os.path.join(os.getcwd(), relative_path)
bookstack_page_data = InitiatePage(bookstack_api,book_id,file_name)
file_path = os.path.join(input_dir_path, file_name)
page_id = bookstack_page_data.id
f = codecs.open(file_path, 'r', encoding='utf-8')
page_content = f.read()
notion_page = NotionPage(page_content)
# print(notion_page.content)
notion_page.content = ReplaceSymbolsWithinBrackets(notion_page.content)
notion_page.content = LoadPageAttachments(
    bookstack_api, page_id, file_path, notion_page.content, True)
update_page_response = bookstack_api.update_page(
    page_id=page_id, book_id=None,
    title=notion_page.title, content=notion_page.content, tags=[])
# debug(json.dumps(update_page_response, indent=2))

# print(notion_page.content)