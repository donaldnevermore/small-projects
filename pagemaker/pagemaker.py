from xml.sax.handler import ContentHandler
from xml.sax import parse
from io import TextIOWrapper


class PageMaker(ContentHandler):
    passthrough: bool = False
    out: TextIOWrapper

    def startElement(self, name: str, attrs) -> None:
        if name == "page":
            self.passthrough = True
            self.out = open(attrs["name"] + ".html", "w")
            self.out.write("<html><head>\n")
            self.out.write(f"<title>{attrs['title']}</title>\n")
            self.out.write("</head><body>\n")
        elif self.passthrough:
            self.out.write(f"<{name}")
            for key, val in attrs.items():
                self.out.write(f' {key}="{val}"')
            self.out.write(">")

    def endElement(self, name: str) -> None:
        if name == "page":
            self.passthrough = False
            self.out.write("\n</body></html>\n")
            self.out.close()
        elif self.passthrough:
            self.out.write(f"</{name}>")

    def characters(self, content: str) -> None:
        if self.passthrough:
            self.out.write(content)


if __name__ == "__main__":
    parse("website.xml", PageMaker())
