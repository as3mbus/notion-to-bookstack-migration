from email.mime import application, multipart
import requests
import json


class BookData:
    def __init__(self):
        self.name
        self.id
        self.slug

    def __init__(self, create_book_response):
        self.name = create_book_response['name']
        self.id = create_book_response['id']
        self.slug = create_book_response['slug']


class PageData:
    def __init__(self):
        self.name
        self.id
        self.slug

    def __init__(self, create_page_response):
        self.name = create_page_response['name']
        self.id = create_page_response['id']
        self.slug = create_page_response['slug']


class BookstackAPI:
    def __init__(self) -> None:
        pass

    def LoadCredential(self, cred):
        self.header = BookstackAPI.AuthenticationHeader(
            cred['token'], cred['secret'])
        self.cred = cred

    def AuthenticationHeader(token, secret):
        # Set up the API request headers and payload
        return {
            "Authorization": f'Token {token}:{secret}'
        }

    def create_page(self, book_id, title, content):
        # Send the API request
        payload = {
            "book_id": book_id,
            "name": title,
            "markdown": content
        }
        header = self.header
        header["Content-Type"]: 'application/json'

        response = requests.post(
            self.cred['url']+'api/pages', headers=header, json=payload)

        # Check if the request was successful (201 status code)
        if response.status_code == 200:
            # Print the API response data
            print(f"Create Page {title} Success")
            return response.json()
        else:
            # Print the error message if the request failed
            print(f"API request failed: {response.text}")
            return None

    def update_page(self, page_id, book_id, title, content, tags=None):
        # Send the API request
        payload = {
            "name": title,
            "markdown": content,
        }
        if tags is not None:
            payload["tags"] = tags
        if (book_id):
            payload["book_id"] = book_id
        header = self.header
        header["Content-Type"]: 'application/json'

        response = requests.put(
            f"{self.cred['url']}api/pages/{page_id}", headers=header, json=payload)

        # Check if the request was successful (201 status code)
        if response.status_code == 200:
            # Print the API response data
            print("Update Page Request Success")
            return response.json()
        else:
            # Print the error message if the request failed
            print(f"API request failed: {response.text}")
            return None

    def list_page(self):
        header = self.header
        header["Content-Type"]: 'application/json'

        response = requests.get(
            f"{self.cred['url']}api/pages/?count=500", headers=header)

        # Check if the request was successful (201 status code)
        if response.status_code == 200:
            # Print the API response data
            print("request suceed")
            return response.json()
        else:
            # Print the error message if the request failed
            print(f"API request failed: {response.text}")
            return None

    def read_page(self, page_id):
        header = self.header
        header["Content-Type"]: 'application/json'

        response = requests.get(
            f"{self.cred['url']}api/pages/{page_id}", headers=header)

        # Check if the request was successful (201 status code)
        if response.status_code == 200:
            # Print the API response data
            # print("request suceed")
            return response.json()
        else:
            # Print the error message if the request failed
            print(f"API request failed: {response.text}")
            return None

    def delete_page(self, page_id):
        header = self.header
        header["Content-Type"]: 'application/json'

        response = requests.delete(
            f"{self.cred['url']}api/pages/{page_id}", headers=header)

        # Check if the request was successful (201 status code)
        if response.status_code == 204:
            # Print the API response data
            print("Delete Page Request Success")
            return response
        else:
            # Print the error message if the request failed
            print(f"API request failed: {response.text}")
            print(response)
            return None


# TODO: waiting for local bookstack update for image API


    def create_image(self, page_id, title, file_path):
        header = self.header
        header["Content-Type"]: 'multipart/form-data'

        payload = {
            "type": "gallery",
            "uploaded_to": page_id,
            "name": title,
        }
        file_data = {"file": ("{title}", open(file_path, "rb"), "image")}

        response = requests.post(
            self.cred['url']+'api/image-gallery', headers=header, data=payload, files=file_data)

        # Check if the request was successful (200 status code)
        if response.status_code == 200:
            # Print the API response data
            print("Create Image Request Success")
            return response.json()
        else:
            # Print the error message if the request failed
            print(f"API request failed: {response.text}")
            return None

    def create_attachment(self, page_id, title, file_path):
        header = self.header
        header["Content-Type"]: 'multipart/form-data'

        payload = {
            "uploaded_to": page_id,
            "name": title,
        }
        file_data = {"file": ("{title}", open(file_path, "rb"), "image")}

        response = requests.post(
            self.cred['url']+'api/attachments', headers=header, data=payload, files=file_data)

        # Check if the request was successful (200 status code)
        if response.status_code == 200:
            # Print the API response data
            print("Create Attachment Request Success")
            return response.json()
        else:
            # Print the error message if the request failed
            print(f"API request failed: {response.text}")
            return None

    def create_book(self, title, description):
        header = self.header
        header["Content-Type"]: 'multipart/form-data'

        payload = {
            "name": title,
            "description": "" + description
        }

        response = requests.post(
            self.cred['url']+'api/books', headers=header, json=payload)

        # Check if the request was successful (201 status code)
        if response.status_code == 200:
            # Print the API response data
            print("Create Book request success")
            return response.json()
        else:
            # Print the error message if the request failed
            print(f"API request failed: {response.text}")
            return None
