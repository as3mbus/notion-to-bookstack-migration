class NotionPage:
    def __init__(self, text: str):
        pos = text.find("\n")
        page_title = text[2:pos]
        page_content = text[pos+1:]
        pos = page_content.find("\n\n")
        page_meta = page_content[1:pos]
        page_content = page_content[pos+1:]

        self.title = page_title
        self.metadata = page_meta
        self.content = page_content
