from typing import List
from xml.sax.handler import ContentHandler
from xml.sax import parse


class HeadlineHandler(ContentHandler):
    in_headline: bool = False
    headlines: List[str]
    data: List[str]

    def __init__(self, headlines) -> None:
        super().__init__()
        self.headlines = headlines
        self.data = []

    def startElement(self, name: str, attrs) -> None:
        if name == "h1":
            self.in_headline = True

    def endElement(self, name: str) -> None:
        if name == "h1":
            text = "".join(self.data)
            self.data = []
            self.headlines.append(text)
            self.in_headline = False

    def characters(self, content: str) -> None:
        if self.in_headline:
            self.data.append(content)


if __name__ == "__main__":
    headlines = []
    parse("website.xml", HeadlineHandler(headlines))
    print("The following <h1> elements were found:")
    for h in headlines:
        print(h)
