from bs4 import BeautifulSoup
import requests
import re
import json
import time
from pprint import pprint
import os, sys
from collections import OrderedDict

PROJECTS = {
    'tetc-blockpy': 'hymnfbvhxkqn',
    'lact-toce': 'hmgpntgdxpcw',
    'compsac-blockpy': 'frqkrzkmqdyv',
    'sigcse-corgis': 'jygsxtkvfkrb'
}

try:
    PROJECT_NAME = sys.argv[1]
    PROJECT_URL = PROJECTS[PROJECT_NAME]
except IndexError:
    raise Exception("Invalid project name. Must be one of: "+", ".join(PROJECTS.keys()))

URL = 'https://www.overleaf.com/read/'+PROJECT_URL
LOG_FILENAME = PROJECT_NAME+'.log'

content = requests.get(URL).content

soup = BeautifulSoup(content)

main_content = soup.find(id='doc_content').string
main_content = main_content.split('\\maketitle')[1]

section_count = main_content.count('\\section')
subsection_count = main_content.count('\\subsection')
word_count = len(main_content.split())
character_count = len(main_content)

current_section = []
current_subsection = []
current_subsubsection = []
held_section = None
held_subsection = None
held_subsubsection = None
data = OrderedDict()
cursor = None
for line in main_content.split("\n"):
    sections = re.search('\\\\section\{(.*)\}', line)
    subsections = re.search('\\\\subsection\{(.*)\}', line)
    subsubsections = re.search('\\\\subsubsection\{(.*)\}', line)
    ready_symbol = re.search('%READY%', line)
    if sections is not None:
        #if held_section is not None:
        #    print held_section, "(words: {})".format(sum(current_section))
        held_section = sections.group(1)
        #print held_section#, "(words: {})".format(sum(current_section))
        current_section = []
        data[held_section] = {'ready': False, 'children': OrderedDict()}
        cursor = 'section'
    elif subsections:
        #if held_subsection is not None:
            #print "\t", held_subsection, "(words: {})".format(sum(current_subsection))
        held_subsection = subsections.group(1)
        #print "\t", held_subsection#, "(words: {})".format(sum(current_subsection))
        current_subsection = []
        data[held_section]['children'][held_subsection] = {'ready': False, 'children': OrderedDict()}
        cursor = 'subsection'
    elif subsubsections:
        #if held_subsubsection is not None:
            #print "\t\t", held_subsubsection, "(words: {})".format(sum(current_subsubsection))
        held_subsubsection = subsubsections.group(1)
        #print "\t\t", held_subsubsection#, "(words: {})".format(sum(current_subsubsection))
        current_subsubsection = []
        data[held_section]['children'][held_subsection]['children'][held_subsubsection] = False
        cursor = 'subsubsection'
    else:
        current_section.append(len(line.split()))
        current_subsection.append(len(line.split()))
        current_subsubsection.append(len(line.split()))
    if ready_symbol:
        if cursor == 'section':
            data[held_section]['ready'] = True
        elif cursor == 'subsection':
            data[held_section]['children'][held_subsection]['ready'] = True
        elif cursor == 'subsubsection':
            data[held_section]['children'][held_subsection]['children'][held_subsubsection] = True
for section, subsections in data.items():
    print section, '' if subsections['ready'] else '(!!!)'
    for subsection, subsubsections in subsections['children'].items():
        print '\t', subsection, '' if subsubsections['ready'] else '(!!!)'
        for subsubsection, readiness in subsubsections['children'].items():
            print '\t'*2, subsubsection, '' if readiness else '(!!!)'
        
        
print "--"*10

print "Sections", section_count
print "Subsections", subsection_count
print "Word Count", word_count
print "Character Count", character_count
print "Estimated pages", (word_count) / 450

if os.path.exists(LOG_FILENAME):
    with open(LOG_FILENAME, 'r') as input:
        record = json.load(input)
else:
    with open(LOG_FILENAME, 'w') as output:
        record = []
        json.dump(record, output)
today = time.strftime("%d/%m/%Y")
if record:
    first_record_ever_words = record[0]['words']
    different_days_worked = len(set(r['day'] for r in record))
    if [r for r in record if r['day'] == today]:
        first_record_today = sorted([r for r in record if r['day'] == today], 
                                    key=lambda r: r['epoch'])[0]
        print "Today's Growth", word_count - first_record_today['words']
    print "Total Growth", word_count - first_record_ever_words
    print "Average Growth", int((word_count - first_record_ever_words)/float(different_days_worked))
else:
    print "Making initial record"
record.append({
    'epoch': time.time(),
    'words': word_count,
    'characters': character_count,
    'day': today,
    'time': time.strftime("%I:%M:%S")
})
    
with open(LOG_FILENAME, 'w') as output:
    json.dump(record, output)