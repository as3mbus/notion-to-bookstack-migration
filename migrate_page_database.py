import os
import json
import codecs
from bookstack_api import BookstackAPI, BookData, PageData
from notion_formatting import NotionPage
from regex_utilities import ReplaceSpaceWithinBrackets, ReplaceSpace
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
book_name = "BookName"
book_description = "test Book for use case"
relative_path = "input"
datamap_file = "dataMap.csv"
dataset_output_file = 'output.csv'
tag_key = "PageTag"

# endregion

# region Main


##### Create Book

book_data = InitiateBook(bookstack_api, book_name, book_description)
# book_data = BookData({"id": 75,
#     "name": "BookName",
#     "slug": "bookname-yK5",})


#### Read Page Database Table
dataFrame = pandas.read_csv(os.path.join(os.getcwd(), datamap_file))
input_directory_path = os.path.join(os.getcwd(), relative_path)

# file_name = "Unreal Engine 5 Installation 3a14402970134e8689bdfce4fa8b4de5.md"
# file_path = os.path.join(input_directory_path, file_name)
# dataFrame = AddPageIndex(bookstack_api, book_data,file_path, dataFrame, True)

##### Create Empty Page for Indexing
dataFrame = InitiatePageIndexes(bookstack_api, book_data, input_directory_path, dataFrame, True)
dataFrame = dataFrame.sort_values('Name', ascending=False)
dataFrame.to_csv(dataset_output_file, index=False)

#### write Pages Index containing Page Name, Page ID, Page Url, and filepath
dataFrame = pandas.read_csv(os.path.join(os.getcwd(), dataset_output_file))

# row = dataFrame.loc[dataFrame['Name'] == 'Unreal Engine 5 Installation'].iloc[0]
# LoadPageData(bookstack_api,row,dataFrame, True)

###### Upload Content , attachment, and resolve Links URL
for index, row in dataFrame.iterrows():
    LoadPageData(bookstack_api, row, dataFrame, tag_key, True)

# endregion
