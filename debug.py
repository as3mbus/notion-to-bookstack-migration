from bookstack_api import BookstackAPI
import json

f = open('credential.json')
cred = json.load(f)
book_id = 27

bookstack_api = BookstackAPI()
bookstack_api.LoadCredential(cred)
print( bookstack_api.header)

# response = bookstack_api.create_page(27,"test title","abcdefg")
response = bookstack_api.update_page(page_id=83,book_id=None,title= 'update_test', content='markdown')

