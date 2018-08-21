"""
This pulls data from sports-reference and puts it into a dictionary
keys: name
values: list of [link, link_name, name_mascot, mascot]
Also prints to a CSV file titled "sportsref_results.csv"

June 6, 2018

Runtime:
	~45 seconds

"""

import requests
import sys
import csv
from bs4 import BeautifulSoup
import re


url = "https://www.sports-reference.com/cfb/years/2017-standings.html"
r = requests.get(url)
tag_ratingspage = BeautifulSoup(r.content, "lxml")
tag_table = tag_ratingspage.find('tbody')

dict_schools = {}

csv_file = open("results_sportsref.csv", "w")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["school_name", "link", "link_name", "name_mascot", "mascot"]) # first row

for school in tag_table.find_all('tr'):

	# SITE 1

	# skip header rows
	if (school.find('th', class_=" over_header center")):
		continue
	if (school.find('th', class_="ranker sort_default_asc right")):
		continue

	# NAME
	school_name = school.a.text
	# print(str(counter) + " " + school_name)
	
	# LINK and LINK_NAME
	link = school.find('a')['href']
	link_name = link.split("/")[-2]
	
	# SITE 2

	url_team = re.sub("\.com/.*", ".com" + link, url)
	r = requests.get(url_team)
	tag_teampage = BeautifulSoup(r.content, "lxml")
	
	# NAME_MASCOT
	name_mascot = tag_teampage.h1.text.split('\n')[2]

	# MASCOT
	mascot = name_mascot.replace(school_name + " ", "")
	if mascot == name_mascot:
		mascot = name_mascot.split()[-1]	# best guess will have to do


	# add to dictionary and CSV file
	dict_schools[school_name] = [link, link_name, name_mascot, mascot]
	csv_writer.writerow([school_name, link, link_name, name_mascot, mascot])


csv_file.close()
