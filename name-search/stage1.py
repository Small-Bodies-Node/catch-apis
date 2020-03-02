"""
STAGE 1 of Pipeline

"""

import re
import os
import time
import json
from time import sleep
from typing import List
from bs4 import BeautifulSoup, element
from requests import Response, request
from models.name_search import NameSearch, EBodyType

from stage0 import asteroid_json_file, comet_html_file, dataDirPath, name_search_items_csv_file
from services.query import parse_target_name

###############################################
# Define our array for all comets and asteroids
###############################################

name_search_items: List[NameSearch] = []

############################
# Load and format comet_html
############################

comet_html: str
print("Retrieving html from previously saved file...")
with open(comet_html_file, 'r') as f:
    comet_html = f.read()

# Parse raw html; by inspection, target content is in a single <pre> element
soup: BeautifulSoup = BeautifulSoup(comet_html, 'html.parser')
preTag: element.Tag = soup.find('pre')
target_content: str = preTag.text
target_content_lines: List[str] = target_content.split('\n')

# Parse lines of text; convert to csv-style lines
print(">>> Parsing comet html...")
for i, line in enumerate(target_content_lines):

    #################################################################################
    # Extract units from lines in html; example Line (spaces made dashes):
    # '--(12059)-du-Chatelet--------------du-Châtelet-'
    # '---(785)-Zwetana-----------------------Zwetana'
    # Notice the pesky multi-space gap between non-accented name and accented name
    #################################################################################

    try:
        # Split the pesky multi-space gap
        # E.g. temp1 <=== ['--(12059)-du-Chatelet', 'du-Châtelet']
        temp1 = re.split(r'\s{6,}', line)

        # Find first occurence of chars in parentheses
        # E.g. number <=== ['12059'][0]
        number: str = re.findall(r'\(([^)]+)\)', temp1[0])[0]

        # Find unaccented name:
        # E.g. unaccentedName  <=== 'du-Chatelet'
        unaccentedName = re.sub(r'\s*\(([^)]+)\)\s', '', temp1[0])

        # Find accented name:
        # E.g. unaccentedName <=== 'du-Chatelet'
        accentedName = temp1[1]

        line_sans_parentheses: str = re.sub(r"\(|\)", '', line)

        # Save items to list of SmallBody entries
        name_search_items.append(
            NameSearch(
                target=parse_target_name(line_sans_parentheses)[1],
                comparison_text=number + " " + unaccentedName,
                display_text=number + " " + unaccentedName,
                body_type=parse_target_name(line_sans_parentheses)[0]
            )
        )
    except:
        # Print lines that don't work or conform to above pattern
        print('Failed Line: >>>'+line+'<<<')


###############################
# Load and format asteroid_json
###############################

#
# Keys of json object:
#
# [
#     'Orbit_type',
#     'Provisional_packed_desig',
#     'Year_of_perihelion',
#     'Month_of_perihelion',
#     'Day_of_perihelion',
#     'Perihelion_dist',
#     'e',
#     'Peri',
#     'Node',
#     'i',
#     'Epoch_year',
#     'Epoch_month',
#     'Epoch_day',
#     'H',
#     'G',
#     'Designation_and_name',
#     'Ref'
# ]

# Count the occurences of each Orbit_type
# {'C': 213, 'P': 618, 'A': 14, 'I': 1}


with open(asteroid_json_file) as json_file:
    asteroid_data: List = json.load(json_file)
    for j, asteroid_datum in enumerate(asteroid_data):

        # Get designation text (comes in various formats)
        desig: str = asteroid_datum['Designation_and_name']

        # Add to items to be output to csv file
        name_search_items.append(
            NameSearch(
                target=parse_target_name(desig)[1],
                comparison_text=desig,
                display_text=desig,
                body_type=parse_target_name(desig)[0]
            )
        )


###############################
# Save cleaned data to csv file
###############################

print(">>> Saving formatted data...")
with open(name_search_items_csv_file, 'w') as f:
    f.write("target_text,search_text,body_type\n")
    for item in name_search_items:
        item.__repr__()
        f.write(
            item.target+"," +
            item.comparison_text + "," +
            item.display_text + "," +
            item.body_type+"\n"
        )
