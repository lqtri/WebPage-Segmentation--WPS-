from lxml import html, etree
from xmldiff import main, formatting
import command 

file1 = "stackoverflow.com_source1.html"
file2 = "stackoverflow.com_source2.html"

with open(file1, 'r', encoding='utf-8') as inp:
    htmldoc = html.fromstring(inp.read())

with open("output1.xml", 'wb') as out:
    out.write(etree.tostring(htmldoc))

with open(file2, 'r', encoding='utf-8') as inp:
    htmldoc = html.fromstring(inp.read())

with open("output2.xml", 'wb') as out:
    out.write(etree.tostring(htmldoc))

# diff = main.diff_files('output1.xml', 'output2.xml', formatter=formatting.XMLFormatter())

# with open("diff.xml", 'w') as out:
#     out.write(diff)

command.run(['xmldiff output1.xml output2.xml > diff.xml'])
