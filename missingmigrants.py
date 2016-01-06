import re
import csv

import requests
import lxml.html
import xypath

from StringIO import StringIO

import xlwt

def write_excel(sheets, sheet_names):
    wb = xlwt.Workbook()
    for sheet, sheet_name in zip(sheets, sheet_names):
        ws = wb.add_sheet(sheet_name)
        for row_num, row in enumerate(sheet):
            for col_num, cell in enumerate(row):
                ws.write(row_num, col_num, cell)
    wb.save('example.xls')

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

def get_table_simple(header):
    # this won't work if there's colspans/rowspans etc.
    # but it's OK for this simple case.
    table, = header.xpath(".//following::table[1]") # lxml element
    trs = table.xpath(".//tr")
    for tr in trs:
        tds = tr.xpath(".//td|th")
        values = [td.text_content() for td in tds]
        yield values

def clean_table(table):
    for row in table:
        row_builder = []
        for cell in row:
            for original, replacement in {u'\xa0': ' ',
                                          '*': '',
                                          ',': ''}.items():
                cell = cell.replace(original, replacement)
            cell = cell.strip()
            row_builder.append(cell)
        yield row_builder

BASEURL = "http://missingmigrants.iom.int/en/latest-global-figures"
html = requests.get(BASEURL).content
root = lxml.html.fromstring(html)

headers = root.xpath("//h1")
headers = [header for header in headers if 'Deaths by month' in header.text_content()]

tables = []
table_names = []

for header in headers:
    year = int(re.search(r"(\d{4})", header.text_content()).group(1))
    table = get_table_simple(header)
    table = clean_table(table)
    tables.append(table)
    table_names.append(str(year))

write_excel(tables, table_names)



#x = xypath.Table.from_file_object(html_fileobject, table_index=0)
