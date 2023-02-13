import os
import json
import codecs
from bookstack_api import BookstackAPI
from notion_formatting import NotionPage
from regex_utilities import replaceSpace
import textwrap


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
book_id = 27
relative_path = "input"

# endregion

input_directory_path = os.path.join(os.getcwd(), relative_path)
input_files = os.listdir(input_directory_path)

for file_name in input_files:
    file_path = os.path.join(input_directory_path, file_name)

    print("==== Files ===")
    print(file_path)

    if (os.path.isdir(file_path)) or (file_name[0] == '.'):
        continue

    print("==== Page ===")
    f = codecs.open(file_path, 'r', encoding='utf-8')
    page_content = f.read()

    notion_page = NotionPage(page_content)
    print(f"Title : {notion_page.title}")
    print(f"Meta :\n{notion_page.metadata}")
    notion_page.content = replaceSpace(notion_page.content)

    attachment_dir_path = file_path[0:file_path.rfind(".")]
    attachment_dir_name = file_name[0:file_name.rfind(".")]
    print(f"Have Attachment ? : {os.path.exists(attachment_dir_path)}")

    create_page_response = bookstack_api.create_page(
        book_id, notion_page.title, "Upload In Progress")
    debug(json.dumps(create_page_response, indent=2))
    page_id = create_page_response['id']
    print(f"Page ID : {page_id}")

    if (os.path.exists(attachment_dir_path)):
        print(f"Attachment directory : {attachment_dir_name}")
        attachment_files = os.listdir(attachment_dir_path)

        for attachment_name in attachment_files:

            print("  ==== Attachment ===")
            print(f"  attachment name : {attachment_name}")
            attachment_path = os.path.join(
                attachment_dir_path, attachment_name)

            create_attachments_response = bookstack_api.create_attachment(
                page_id, attachment_name, attachment_path)
            debug(textwrap.indent(json.dumps(
                create_attachments_response, indent=2), '  '))
            attachment_id = create_attachments_response['id']
            print(f"  attachment id : {attachment_id}")

            attachment_link_path = os.path.join(
                attachment_dir_name, attachment_name)
            attachment_link_path = attachment_link_path.replace('\\', '/')
            notion_page.content = notion_page.content.replace(
                attachment_link_path, f"{bookstack_api.cred['url']}attachments/{attachment_id}")

    debug(notion_page.content)
    update_page_response = bookstack_api.update_page(
        page_id=page_id, book_id=None,
        title=notion_page.title, content=notion_page.content)
    debug(json.dumps(update_page_response, indent=2))
