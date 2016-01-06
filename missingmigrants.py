import re
import csv

import requests
import lxml.html

from StringIO import StringIO
from collections import OrderedDict

import xlwt

def write_excel(sheets, sheet_names):
    """Given a list of sheets [which are lists of rows, which are lists of cell values]
       and a list of sheet names, make an Excel workbook"""
    wb = xlwt.Workbook()
    for sheet, sheet_name in zip(sheets, sheet_names):
        ws = wb.add_sheet(sheet_name)
        for row_num, row in enumerate(sheet):
            for col_num, cell in enumerate(row):
                try:
                    as_float = float(cell)
                    ws.write(row_num, col_num, as_float) # write number to excel
                except Exception, e:
                    ws.write(row_num, col_num, cell) # write without changing to number
    wb.save('migrants.xls')

def get_table_simple(header):
    """Assuming a very simple table with no colspans, rowspans etc, extract the table data"""
    # this won't work if there's colspans/rowspans etc.
    # but it's OK for this simple case.
    table, = header.xpath(".//following::table[1]") # lxml element
    trs = table.xpath(".//tr")
    for tr in trs:
        tds = tr.xpath(".//td|th")
        values = [td.text_content() for td in tds]
        yield values

def clean_table(table):
    """Remove redundant characters from the values"""
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

def find_caveats(header):
    """Return the caveats for a table given its header
    note: this is likely to be easily broken: there is no trivial way of getting the comment text out!"""
    ptags = header.xpath("./following::table[1]/following-sibling::p")[:3]
    texts = [ptag.text_content() for ptag in ptags if ptag.text_content().strip()]
    return '\n'.join(texts)

def create_metadata(**info):
    """Create a template for the metadata and insert the contents of parameters into it"""
    metadata = OrderedDict([
            ["source", "http://missingmigrants.iom.int/"],
            ["methodology", "Unknown"],
            ["date", ""],
            ["location", BASEURL],
            ["caveats", ""],
            ["comments", "Creative Commons Attribution 4.0 International License."]
            ])
    metadata.update(info)
    return metadata

def append_metadata(table, metadata):
    """Add the metadata to the end of the table"""
    table = list(table)
    table.append([])
    for key, value in metadata.items():
        table.append([key, value])
    return table

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
    metadata = create_metadata(date=year, caveats=find_caveats(header))
    table = append_metadata(table, metadata)
    tables.append(table)
    table_names.append(str(year))
write_excel(tables, table_names)
