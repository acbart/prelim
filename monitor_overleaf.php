file_get_contents

'''
from bs4 import BeautifulSoup
import requests
import re

URL = 'https://www.overleaf.com/read/zckrydxqzkzg'

content = requests.get(URL).content

soup = BeautifulSoup(content)

main_content = soup.find(id='doc_content').string
main_content = main_content.split('\\maketitle')[1]

section_count = main_content.count('\\section')
subsection_count = main_content.count('\\subsection')
word_count = len(main_content.split())
character_count = len(main_content)

print section_count, subsection_count, word_count, character_count

print "Outline"
for line in main_content.split("\n"):
    sections = re.search('\\\\section\{(.*)\}', line)
    subsections = re.search('\\\\subsection\{(.*)\}', line)
    subsubsections = re.search('\\\\subsubsection\{(.*)\}', line)
    if sections is not None:
        print sections.group(1)
    elif subsections:
        print "\t", subsections.group(1)
    elif subsubsections:
        print "\t\t", subsubsections.group(1)

'''