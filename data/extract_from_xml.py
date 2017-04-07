# -*- coding: utf-8 -*-#
import re

INPUT_XML = 'news_tensite_xml.dat'
OUTPUT_FILE = 'data_content.txt'

with open(INPUT_XML, 'r') as xml_file, open(OUTPUT_FILE, 'w') as output_file:
    for line in xml_file:
        content = re.search(r'(?<=<content>).*(?=</content>)', line)
        if content is None:
            continue
        content = content.group()
        output_file.write(content + '\n')
