import os
import json
import codecs
from bookstack_api import BookstackAPI, BookData, PageData
from notion_formatting import NotionPage
from regex_utilities import ReplaceSymbolsWithinBrackets, ReplaceSymbols
import pandas
import textwrap
import re

enable_debug = True


def debug(string):

    if (not enable_debug):
        return
    print(string)


def InitiateBook(bookstack_api, book_name, book_description):

    create_book_response = bookstack_api.create_book(
        book_name, book_description)

    debug(json.dumps(create_book_response, indent=2))

    return BookData(create_book_response)

# create empty page


def InitiatePage(bookstack_api, book_id, page_title):
    create_page_response = bookstack_api.create_page(
        book_id, page_title, "Upload In Progress")
    # debug(json.dumps(create_page_response, indent=2))
    return PageData(create_page_response)

# add page index data to page indexing table


def AddPageIndex(bookstack_api: BookstackAPI, book_data: BookData, file_path: str, input_data_index: pandas.DataFrame, execute_api: bool = True):
    # TODO: handle various directory separator for other os
    file_name = file_path[file_path.rfind('\\')+1:]

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
        input_data_index.loc[relatedData, 'PageID'] = int(
            page_data.id)  # TODO: data is registered as float

        input_data_index.loc[relatedData, 'PageUrl'] = page_url

        # print(f"Page Url : {input_data_index.loc[relatedData, 'PageUrl']}")


# index page data
def InitiatePageIndexes(bookstack_api: BookstackAPI, book_data: BookData, input_dir_path: str, input_data_index: pandas.DataFrame, execute_api: bool = True):
    input_files = os.listdir(input_dir_path)
    for file_name in input_files:
        if (file_name == ".gitkeep" or not file_name.endswith(".md")):
            continue

        file_path = os.path.join(input_dir_path, file_name)

        AddPageIndex(
            bookstack_api, book_data, file_path, input_data_index, execute_api)

    return input_data_index


# upload all page attachment (image, and files)
def LoadPageAttachments(bookstack_api: BookstackAPI, page_id: int, file_path: str, content_data: str, execute_api: bool = False):

    # TODO: Replace with Images
    attachment_dir_path = file_path[0:file_path.rfind(".")]
    attachment_dir_name = file_path[file_path.rfind(
        "\\")+1:file_path.rfind(".")]

    if (not os.path.exists(attachment_dir_path)):
        return content_data

    attachment_files = os.listdir(attachment_dir_path)
    i = 0

    for attachment_name in attachment_files:
        attachment_path = os.path.join(
            attachment_dir_path, attachment_name)

        attachment_url = f"{i}attachments/{i}"

        if execute_api:
            # TODO: replace with Image API for image files
            create_attachments_response = bookstack_api.create_attachment(
                page_id, attachment_name, attachment_path)

            debug(textwrap.indent(json.dumps(
                create_attachments_response, indent=2), '  '))

            attachment_id = create_attachments_response['id']
            attachment_url = f"{bookstack_api.cred['url']}attachments/{attachment_id}"

        attachment_link_path = os.path.join(
            attachment_dir_name, attachment_name)

        attachment_link_path = attachment_link_path.replace('\\', '/')
        content_data = content_data.replace(
            attachment_link_path, attachment_url)

        i += 1

    return content_data


# format page to adapt with page url and attachment url


def CalibratePageLinks(content_data: str, index_page_data: pandas.DataFrame):

    for match in re.finditer('((?<!!)\[.*\])\(((?!http).*)\)', content_data):
        relatedData = index_page_data.loc[index_page_data['FileName'] == match.group(
            2)]

        if (relatedData['FilePath'].empty):
            continue

        try:
            page_url = relatedData["PageUrl"].values[0]
        except:
            page_url = 'pageUrl'

        content_data = content_data.replace(match.group(2),  page_url)
    return content_data


# parse tag


def LoadTagData(page_index: pandas.Series, tag_key: str):

    if tag_key not in page_index:
        return None

    tagString = page_index[tag_key]

    if (pandas.isnull(tagString)):
        return None

    tagString = ReplaceSymbols(tagString)
    tagList = tagString.split(',')
    tagArray = []

    for tag in tagList:
        tag = tag.strip()
        tag = tag.lower().replace(' ', '-')
        tagArray.append(tag)

    return tagArray


# load page data and update content of bookstack page information


def LoadPageData(bookstack_api: BookstackAPI, index_data: pandas.Series, index_page_data: pandas.DataFrame, Tag_Key: str = "Tags", execute_api: bool = False):

    file_path = index_data['FilePath']
    page_id = 0

    if (execute_api):
        page_id = int(index_data['PageID'])

    f = codecs.open(file_path, 'r', encoding='utf-8')
    page_content = f.read()

    notion_page = NotionPage(page_content)

    notion_page.content = ReplaceSymbolsWithinBrackets(notion_page.content)
    notion_page.content = LoadPageAttachments(
        bookstack_api, page_id, file_path, notion_page.content, execute_api)

    notion_page.content = CalibratePageLinks(
        notion_page.content, index_page_data)

    tagString = LoadTagData(index_data, tag_key=Tag_Key)
    tagObj = None

    if (tagString != None):
        tagObj = []
        tagObj = list(map((lambda string: {'name': string}), tagString))
    
    if (execute_api):
        update_page_response = bookstack_api.update_page(
            page_id=page_id, book_id=None,
            title=notion_page.title, content=notion_page.content, tags=tagObj)

        debug(json.dumps(update_page_response, indent=2))
