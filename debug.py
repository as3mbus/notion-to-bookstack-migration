from bookstack_api import BookstackAPI
import json

f = open('credential.json')
cred = json.load(f)
book_id = 27

bookstack_api = BookstackAPI()
bookstack_api.LoadCredential(cred)

# response = bookstack_api.create_page(27,"test title","abcdefg")
# response = bookstack_api.update_page(page_id=83,book_id=None,title= 'update_test', content='markdown')

page_list_response = bookstack_api.list_page()
print(len(page_list_response["data"]))


for data in page_list_response["data"]:
    if(data["book_id"] != book_id): continue
    # print(data)
    read_page_response = bookstack_api.read_page(data["id"])
    if(read_page_response["markdown"] != "Upload In Progress"): continue
    print(read_page_response["name"])
    delete_page_response = bookstack_api.delete_page(data["id"])