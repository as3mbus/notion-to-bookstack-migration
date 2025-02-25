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

enable_debug = False
book_name = "Tech Operation Wiki"
book_description = ""
relative_path = "input"
datamap_file = "dataMap.csv"
dataset_output_file = 'output.csv'
tag_key = "Tags"

# endregion

# region Main


# Create Book

book_data = InitiateBook(bookstack_api, book_name, book_description)

# book_data = BookData(
#     {"id": 84,
#      "name": "Tech Operation Wiki",
#      "slug": "tech-operation-wiki", })

# Read Page Database Table

dataFrame = pandas.read_csv(os.path.join(os.getcwd(), datamap_file))
input_directory_path = os.path.join(os.getcwd(), relative_path)

# Create Empty Page for Indexing

dataFrame = InitiatePageIndexes(
    bookstack_api, book_data, input_directory_path, dataFrame, True)
dataFrame = dataFrame.sort_values('Name', ascending=False)
dataFrame.to_csv(dataset_output_file, index=False)

# write Pages Index containing Page Name, Page ID, Page Url, and filepath

dataFrame = pandas.read_csv(os.path.join(os.getcwd(), dataset_output_file))

# Upload Content , attachment, and resolve Links URL

for index, row in dataFrame.iterrows():
    LoadPageData(bookstack_api, row, dataFrame, tag_key, True)

# endregion
