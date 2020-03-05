from nntplib import NNTP
from datetime import date, timedelta

today = date.today()
yesterday = today - timedelta(days=1)

servername = "news.gmane.io"
group = "gmane.comp.python.committers"
server = NNTP(servername)

# see https://docs.python.org/3/library/nntplib.html
# This command is frequently disabled by NNTP server administrators.
ids = server.newnews(group, yesterday)[1]

subject = None
for i in ids:
    head = server.head(i)[3]
    for line in head:
        if line.lower().startswith("subject:"):
            subject = line[9:]
            break

    body = server.body(i)[3]

    print(subject)
    print("-" * len(subject))
    print("\n".join(body))
