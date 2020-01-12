from nntplib import NNTP
import time
from datetime import date, datetime

# # yesterday=localtime(time() - day)
new_date = datetime(2000, 1, 1)
# # date=strftime('%y%m%d',yesterday)
# # hour=strftime('%H%M%S',yesterday)

servername = "news.newsfan.net"
group = "comp.lang.python"
server = NNTP(servername)
# (resp, count, first, last, name)=server.group('comp.lang.python')
# (resp, subs) = s.xhdr('subject', (str(first)+'-'+str(last)))
ids = server.newnews(group, new_date)[1]

# for i in ids:
#     head=server.head(i)[3]
#     for line in head:
#         if line.lower().startswith('subject:'):
#             subject=line[9:]
#             break

#     body=server.body(i)[3]

#     print(subject)
#     print('-'*len(subject))
#     print('\n'.join(body))

# from nntplib import *
# s = NNTP('web.aioe.org')
# (resp, count, first, last, name) = s.group('comp.lang.python')
# (resp, subs) = s.xhdr('subject', (str(first)+'-'+str(last)))
# for subject in subs[-10:]:
#   print(subject)
# number = input('Which article do you want to read? ')
# (reply, num, id, list) = s.body(str(number))
# for line in list:
#   print(line)
