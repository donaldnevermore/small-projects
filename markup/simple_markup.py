import sys
import re
from util import blocks

output_file = open("test_output.html", "w")
output_file.write("<html><head><title>markup</title><body>")

title = True
input_file = open("test_input.txt", "r")

for block in blocks(input_file):
    block = re.sub(r"\*(.+?)\*", r"<em>\1</em>", block)
    if title:
        output_file.write("<h1>")
        output_file.write(block)
        output_file.write("</h1>")
        title = False
    else:
        output_file.write("<p>")
        output_file.write(block)
        output_file.write("</p>")

output_file.write("</body></html>")
output_file.close()
input_file.close()
