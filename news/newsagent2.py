from nntplib import NNTP
from datetime import date, timedelta
from email import message_from_string
from urllib.request import urlopen
import textwrap
import re


def wrap(string, max=70):
    """
    将字符串调整为最大行宽
    """
    return "\n".join(textwrap.wrap(string)) + "\n"


class NewsAgent:
    """
    可以从新闻来源获取新闻项目并且发布到新闻目标的对象
    """

    def __init__(self):
        self.sources = []
        self.destinations = []

    def add_source(self, source):
        self.sources.append(source)

    def add_destination(self, dest):
        self.destinations.append(dest)

    def distribute(self):
        """
        从所有来源获取所有新闻项目并且发布到最新新闻目标的对象
        """
        items = []
        for source in self.sources:
            items.extend(source.get_items())
        for dest in self.destinations:
            dest.receive_items(items)


class NewsItem:
    """
    包括标题和主体文本的简单新闻项目
    """

    def __init__(self, title, body):
        self.title = title
        self.body = body


class NNTPSource:
    """
    从NNTP组获取新闻项目的新闻来源
    """

    def __init__(self, servername, group, window):
        self.servername = servername
        self.group = group
        self.window = window

    def get_items(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        server = NNTP(self.servername)

        # see https://docs.python.org/3/library/nntplib.html
        # This command is frequently disabled by NNTP server administrators.
        ids = server.newnews(self.group, yesterday)[1]

        for id in ids:
            lines = server.article(id)[3]
            message = message_from_string("\n".join(lines))

            title = message["subject"]
            body = message.get_payload()
            if message.is_multipart():
                body = body[0]

            yield NewsItem(title, body)

        server.quit()


class SimpleWebSource:
    """
    使用正则表达式从网页中提取新闻项目的新闻来源
    """

    def __init__(self, url, title_pattern, body_pattern):
        self.url = url
        self.title_pattern = re.compile(title_pattern)
        self.body_pattern = re.compile(body_pattern)

    def get_items(self):
        text = urlopen(self.url).read()
        titles = self.title_pattern.findall(text)
        bodies = self.body_pattern.findall(text)
        for title, body in zip(titles, bodies):
            yield NewsItem(title, wrap(body))


class PlainDestination:
    """
    将所有新闻项目格式化为存文本的新闻目标类
    """

    @staticmethod
    def receive_items(items):
        for item in items:
            print(item.title)
            print("-" * len(item.title))
            print(item.body)


class HTMLDestination:
    """
    将所有新闻项目格式化为HTML的目标类
    """

    def __init__(self, filename):
        self.filename = filename

    def receive_items(self, items):
        out = open(self.filename, "w")
        print(out, """
        <html>
            <head>
                <title>Today's News</title>
            </head>
            <body>
            <h1>Today's News</h1>
        """)
        print(out, "<ul>")
        id = 0
        for item in items:
            id += 1
            print(out, f"""<li><a href="#{id}">{item.title}</a></li>""")
        print(out, "</ul>")


def run_default_setup():
    """
    来源和目标的默认设置，可以自己修改
    """

    agent = NewsAgent()

    # 从BBS新闻站获取新闻的SimpleWebSource
    bbc_url = "http://news.bbc.co.uk/text_only.stm"
    bbc_title = r"""(?s)a href="[^"]*">\s*<b>\s*(.*?)\s*</b>"""
    bbc_body = r"(?s)</a>\s*<br />\s*(.*?)\s*<"
    bbc = SimpleWebSource(bbc_url, bbc_title, bbc_body)

    agent.add_source(bbc)

    # 获取新闻的NNTPSource
    servername = "news.gmane.io"
    group = "gmane.comp.python.committers"
    window = 1
    server = NNTPSource(servername, group, window)

    agent.add_source(server)
    agent.add_destination(PlainDestination())
    agent.add_destination(HTMLDestination("news.html"))
    agent.distribute()


if __name__ == "__main__":
    run_default_setup()
