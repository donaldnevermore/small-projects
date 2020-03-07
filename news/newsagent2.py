from nntplib import NNTP, decode_header
from urllib.request import urlopen
import textwrap
import re


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

    def __init__(self, servername, group, howmany):
        self.servername = servername
        self.group = group
        self.howmany = howmany

    def get_items(self):
        server = NNTP(self.servername)
        resp, count, first, last, name = server.group(self.group)
        start = last - self.howmany + 1
        resp, overviews = server.over((start, last))
        for id, over in overviews:
            title = decode_header(over["subject"])
            resp, info = server.body(id)
            body = "\n".join(line.decode("latin")
                             for line in info.lines) + "\n\n"
            yield NewsItem(title, body)
        server.quit()


class SimpleWebSource:
    """
    使用正则表达式从网页中提取新闻项目的新闻来源
    """

    def __init__(self, url, title_pattern, body_pattern, encoding="utf8"):
        self.url = url
        self.title_pattern = re.compile(title_pattern)
        self.body_pattern = re.compile(body_pattern)
        self.encoding = encoding

    def get_items(self):
        text = urlopen(self.url).read().decode(self.encoding)
        titles = self.title_pattern.findall(text)
        bodies = self.body_pattern.findall(text)
        for title, body in zip(titles, bodies):
            yield NewsItem(title, textwrap.fill(body) + "\n")


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
        print("""
        <html>
          <head>
            <title>Today"s News</title>
          </head>
          <body>
          <h1>Today"s News</h1>
        """, file=out)

        print("<ul>", file=out)
        id = 0
        for item in items:
            id += 1
            print(f"""  <li><a href="#{id}">{item.title}</a></li>""", file=out)
        print("</ul>", file=out)

        id = 0
        for item in items:
            id += 1
            print(f"""<h2><a name="{id}">{item.title}</a></h2>""", file=out)
            print(f"<pre>{item.body}</pre>", file=out)

        print("""
          </body>
        </html>
        """, file=out)


def run_default_setup():
    """
    来源和目标的默认设置，可以自己修改
    """
    agent = NewsAgent()

    # 从BBS新闻站获取新闻的SimpleWebSource
    reuters_url = "http://www.reuters.com/news/world"
    reuters_title = r"""<h2><a href="[^"]*"\s*>(.*?)</a>"""
    reuters_body = r"</h2><p>(.*?)</p>"
    reuters = SimpleWebSource(reuters_url, reuters_title, reuters_body)

    agent.add_source(reuters)

    # 获取新闻的NNTPSource
    clpa_server = "news.ntnu.no"
    clpa_group = "comp.lang.python.announce"
    clpa_howmany = 10
    clpa = NNTPSource(clpa_server, clpa_group, clpa_howmany)

    agent.add_source(clpa)

    agent.add_destination(PlainDestination())
    agent.add_destination(HTMLDestination("news.html"))

    agent.distribute()


if __name__ == "__main__":
    run_default_setup()
