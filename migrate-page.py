import os
import json
import codecs
from bookstack_api import BookstackAPI, BookData, PageData
from notion_formatting import NotionPage
from regex_utilities import ReplaceSpaceWithinBrackets, ReplaceSpace
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

# endregion

# create book
def InitiateBook(bookstack_api, book_name, book_description):
    create_book_response = bookstack_api.create_book(
        book_name, book_description)
    debug(json.dumps(create_book_response, indent=2))
    return BookData(create_book_response)

# create empty page
def InitiatePage(bookstack_api, book_id, page_title):
    create_page_response = bookstack_api.create_page(
        book_id, page_title, "Upload In Progress")
    debug(json.dumps(create_page_response, indent=2))
    output = PageData(create_page_response)
    return output

# add page index data to page indexing table
def AddPageIndex(bookstack_api: BookstackAPI, book_data: BookData, file_path: str, input_data_index, execute_api):
    file_name = file_path[file_path.rfind('/')+1:]

    if (os.path.isdir(file_path)) or (file_name[0] == '.'):
        return

    f = codecs.open(file_path, 'r', encoding='utf-8')
    page_content = f.read()

    notion_page = NotionPage(page_content)
    relatedData = input_data_index['Name'] == notion_page.title
    if (input_data_index.loc[relatedData, 'Name'].empty):
        print("[WARNING] No Related Data in Indexes, Adding New Index Data")
        relatedData = len(input_data_index.index)
        input_data_index.loc[relatedData, 'Name'] = notion_page.title

    input_data_index.loc[relatedData, 'FileName'] = file_name
    input_data_index.loc[relatedData, 'FilePath'] = file_path

    if (execute_api):
        page_data = InitiatePage(
            bookstack_api, book_data.id, notion_page.title)
        page_url = f"{bookstack_api.cred['url']}books/{book_data.slug}/page/{page_data.slug}"
        input_data_index.loc[relatedData, 'slug'] = page_data.slug
        input_data_index.loc[relatedData, 'PageID'] = page_data.id
        input_data_index.loc[relatedData, 'PageUrl'] = page_url

        print(
            f"Page Url : {input_data_index.loc[relatedData, 'PageUrl'].values[0]}")


# index page data 
def InitiatePageIndexes(bookstack_api: BookstackAPI, book_data: BookData, input_dir_path: str, input_data_index: pandas.DataFrame, execute_api: bool = True):
    input_files = os.listdir(input_dir_path)
    for file_name in input_files:
        file_path = os.path.join(input_dir_path, file_name)
        AddPageIndex(
            bookstack_api, book_data, file_path, input_data_index, execute_api)

    return input_data_index


# upload all page attachment (image, and files)
def LoadPageAttachments(bookstack_api: BookstackAPI, page_id: int, file_path: str, content_data: str, execute_api: bool = False):
    attachment_dir_path = file_path[0:file_path.rfind(".")]
    attachment_dir_name = file_path[file_path.rfind(
        "\\")+1:file_path.rfind(".")]
    # print(file_path)

    if (not os.path.exists(attachment_dir_path)):
        return content_data

    attachment_files = os.listdir(attachment_dir_path)

    i = 0
    for attachment_name in attachment_files:
        attachment_path = os.path.join(
            attachment_dir_path, attachment_name)

        attachment_url = f"{i}attachments/{i}"

        if execute_api:
            create_attachments_response = bookstack_api.create_attachment(
                page_id, attachment_name, attachment_path)
            debug(textwrap.indent(json.dumps(
                create_attachments_response, indent=2), '  '))
            attachment_id = create_attachments_response['id']
            print(f"  attachment id : {attachment_id}")
            attachment_url = f"{bookstack_api.cred['url']}attachments/{attachment_id}"

        attachment_link_path = os.path.join(
            attachment_dir_name, attachment_name)
        attachment_link_path = attachment_link_path.replace('\\', '/')
        content_data = content_data.replace(
            attachment_link_path, attachment_url)

        i += 1

    # print (content_data)
    return content_data


# format page to adapt with page url and attachment url 
def CalibratePageLinks(content_data: str, index_page_data: pandas.DataFrame):

    for match in re.finditer('((?<!!)\[.*\])\(((?!http).*)\)', content_data):
        print
        relatedData = index_page_data.loc[index_page_data['FileName'] == match.group(
            2)]
        if (relatedData['FilePath'].empty):
            continue
        try:
            page_url = relatedData["PageUrl"].values[0]
        except:
            page_url = 'pageUrl'
        content_data = content_data.replace(
            match.group(2),  page_url)
    return content_data


# parse tag 
def LoadTagData(page_index: pandas.Series):

    tagString = page_index['Parents (Topic)']
    if (pandas.isnull(tagString)):
        return None
    tagString = ReplaceSpace(tagString)
    tagList = tagString.split(',')
    tagArray = []
    for tag in tagList:
        tag = tag[tag.rfind('/')+1:tag.rfind(' ')]
        tag = tag.lower().replace(' ', '-')
        tagArray.append(tag)

    return tagArray


# parse complete page information 
def LoadPageData(bookstack_api: BookstackAPI, index_data: pandas.Series, index_page_data: pandas.DataFrame, execute_api: bool = False):
    file_path = index_data['FilePath']
    page_id = 0
    if (execute_api):
        page_id = int(index_data['PageID'])

    f = codecs.open(file_path, 'r', encoding='utf-8')
    page_content = f.read()


    notion_page = NotionPage(page_content)
    notion_page.content = ReplaceSpaceWithinBrackets(notion_page.content)
    notion_page.content = LoadPageAttachments(
        bookstack_api, page_id, file_path, notion_page.content, execute_api)
    notion_page.content = CalibratePageLinks(
        notion_page.content, index_page_data)

    tagString = LoadTagData(index_data)
    tagObj = []
    if (tagString != None):
        tagObj = list(map((lambda string: {'name': string}), tagString))
        print(tagObj)

    if (execute_api):
        update_page_response = bookstack_api.update_page(
            page_id=page_id, book_id=None,
            title=notion_page.title, content=notion_page.content, tags=tagObj)
        debug(json.dumps(update_page_response, indent=2))

    print(notion_page.content)

# region Main


# book_data = InitiateBook(bookstack_api, book_name, book_description)
# book_data = None

# dataFrame = pandas.read_csv(os.path.join(os.getcwd(), datamap_file))
# input_directory_path = os.path.join(os.getcwd(), relative_path)

# file_name = "Unreal Engine 5 Installation 3a14402970134e8689bdfce4fa8b4de5.md"
# file_path = os.path.join(input_directory_path, file_name)
# dataFrame = AddPageIndex(bookstack_api, book_data,file_path, dataFrame, True)

# dataFrame = InitiatePageIndexes(
    # bookstack_api, book_data, input_directory_path, dataFrame, True)
# dataFrame = dataFrame.sort_values('Name', ascending=False)
# dataFrame.to_csv(dataset_output_file, index=False)

dataFrame = pandas.read_csv(os.path.join(os.getcwd(), dataset_output_file))




# row = dataFrame.loc[dataFrame['Name'] == 'Unreal Engine 5 Installation'].iloc[0]
# LoadPageData(bookstack_api,row,dataFrame, True)

for index, row in dataFrame.iterrows():
    LoadPageData(bookstack_api, row, dataFrame, True)

# endregion
