import re
class NotionPage:
    def __init__(self, text: str):
        pos = re.search(r"[\n\r]", text)
        page_title = text[2:pos.start()]
        page_content = text[pos.start()+1:]
        pos = re.search(r"[\n\r][\n\r]", text)
        page_meta = page_content[1:pos.start()]
        page_content = page_content[pos.start()+1:]

        self.title = page_title
        self.metadata = page_meta
        self.content = page_content
