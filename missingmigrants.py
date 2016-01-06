import re
import requests
import lxml.html
import xypath

from StringIO import StringIO

def get_table_from_header(header):
    header_text = header.text_content()
    if 'Deaths by month' not in header_text:
        return None
    year = int(re.search(r"(\d{4})", header_text).group(1))

    table, = header.xpath(".//following::table[1]") # lxml element
    table_as_file = StringIO(lxml.html.tostring(table))
    return xypath.Table.from_file_object(table_as_file, table_index=0)
    # the table index is 0 as the <table> element only refers to one table.
    # this is a simple case so we could just iterate over the <tr> and <td>
    # elements instead.

def clean_table(table):
    return # TODO
    for row in table:
        for cell in row:
            for char in " ,*":
                cell.value = cell.value.replace(char, "")



BASEURL = "http://missingmigrants.iom.int/en/latest-global-figures"
html = requests.get(BASEURL).content
root = lxml.html.fromstring(html)

headers = root.xpath("//h1")

for header in headers:
    table = get_table_from_header(header)
    if table is None:
        continue
    clean_table(table)

    for row in table:
        for cell in row:
            print cell





    print "!!"




#x = xypath.Table.from_file_object(html_fileobject, table_index=0)
