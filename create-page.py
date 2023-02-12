import os
import json
import codecs
from bookstack_api import BookstackAPI

# Set up the API endpoint URL and request parameters

f = open('credential.json')
cred = json.load(f)

bookstack_api = BookstackAPI()
bookstack_api.LoadCredential(cred)


current_dir = os.getcwd()
# relative path to target directory
relative_path = "input"
dir_path = os.path.join(current_dir, relative_path)

# get a list of all files in the directory
files = os.listdir(dir_path)

for file_name in files:
    file_path = os.path.join(dir_path, file_name)
    print(file_path)
    print(os.path.isdir(file_path))
    if (os.path.isdir(file_path)):
        continue

    f = codecs.open(file_path, 'r', encoding='utf-8')
    page_content = f.read()

    # pos = page_content.find("\n")
    # page_title = page_content[2:pos]
    # page_content = page_content[pos+1:]
    # pos = page_content.find("\n\n")
    # page_meta = page_content[1:pos]
    # page_content = page_content[pos+1:]
    
    # create_page_response = bookstack_api.create_page(27,page_title,"")
    # create_page_response['id']

    pos = file_path.rfind(".")
    attachment_dir_path = file_path[0:pos]
    print(attachment_dir_path)
    print(f"attachment exist : {os.path.exists(attachment_dir_path)}")
    attachment_file_list = os.listdir(attachment_dir_path)
    for attachment_name in attachment_file_list:
        attachment_path = os.path.join(attachment_dir_path, attachment_name)
        print(attachment_path)
        bookstack_api.create_attachment(81,attachment_name,attachment_path)




print(page_title)
print(page_meta)


