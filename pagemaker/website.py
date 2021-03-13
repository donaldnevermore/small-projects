from typing import Tuple
from xml.sax.handler import ContentHandler
from xml.sax import parse
import os
from io import TextIOWrapper


class Dispatcher:
    def dispatch(self, prefix, name, attrs=None):
        mname = prefix + "_" + name
        dname = "default_" + prefix
        method = getattr(self, mname, None)

        args: Tuple
        if callable(method):
            args = ()
        else:
            method = getattr(self, dname, None)
            args = (name,)
        if prefix == "start":
            args += (attrs,)
        if callable(method):
            method(*args)

    def startElement(self, name, attrs):
        self.dispatch("start", name, attrs)

    def endElement(self, name):
        self.dispatch("end", name)


class WebsiteConstructor(Dispatcher, ContentHandler):
    passthrough: bool = False
    out: TextIOWrapper

    def __init__(self, directory):
        self.directory = [directory]
        self.ensure_directory()

    def ensure_directory(self):
        path = os.path.join(*self.directory)
        os.makedirs(path, exist_ok=True)

    def characters(self, content):
        if self.passthrough:
            self.out.write(content)

    def default_start(self, name, attrs):
        if self.passthrough:
            self.out.write("<" + name)
            for key, val in attrs.items():
                self.out.write(f' {key}="{val}"')
            self.out.write(">")

    def default_end(self, name):
        if self.passthrough:
            self.out.write(f"</{name}>")

    def start_directory(self, attrs):
        self.directory.append(attrs["name"])
        self.ensure_directory()

    def end_directory(self):
        self.directory.pop()

    def start_page(self, attrs):
        filename = os.path.join(*self.directory + [attrs["name"] + ".html"])
        self.out = open(filename, "w")
        self.write_header(attrs["title"])
        self.passthrough = True

    def end_page(self):
        self.passthrough = False
        self.write_footer()
        self.out.close()

    def write_header(self, title):
        self.out.write("<html>\n<head>\n <title>")
        self.out.write(title)
        self.out.write("</title>\n </head>\n <body>\n")

    def write_footer(self):
        self.out.write("\n </body>\n</html>\n")


if __name__ == "__main__":
    parse(
        "website.xml",
        WebsiteConstructor("public_html"),
    )
