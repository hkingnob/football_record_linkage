"""
This pulls football data from 247sports and puts it into a dictionary

keys: school_name
values: list of [link, link_abbr, link_name, name_team_page, mascot]
Also prints to a CSV file titled "results_247.csv"

June 11, 2018
	
Runtime: 3 minutes 30 seconds

"""

import requests
import sys
import csv
from bs4 import BeautifulSoup
# import pandas as pd
import re

url = "https://www.cbssports.com/college-football/teams/"
r = requests.get(url)
tag_listpage = BeautifulSoup(r.content, "lxml")
tag_table = tag_listpage.find('table')

dict_schools = {}

csv_file = open("results_247.csv", "w")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["school_name", "link", "link_abbr", "link_name", "name_team_page", "mascot"])

for tag_conference in tag_table.find_all('td'):
	for school in tag_conference.find_all('tr'):

		if school.get("class") == ['title'] or school.a == None:
			continue # if conference or blank, continue

		# SITE 1

		# SCHOOL_NAME
		school_name = school.a.text
		# print(str(counter) + " " + school_name)

		# LINK
		link = school.find('a')['href']
		link = link.replace("/collegefootball", "")

		# LINK_ABBR and LINK_NAME
		link_abbr = link.split("/")[-2]
		link_name = link.split("/")[-1]

		# SITE 2

		url_team = url.replace("/teams/", link)
		r = requests.get(url_team)
		tag_teampage = BeautifulSoup(r.content, "lxml")


		# NAME_TEAM_PAGE and MASCOT
		name_team_page = tag_teampage.find('span', class_="superText").text
		mascot = tag_teampage.find('span', class_="subText").text


		# ADD TO DICTIONARY AND CSV FILE
		dict_schools[school_name] = [link, link_abbr, link_name, name_team_page, mascot]
		csv_writer.writerow([school_name, link, link_abbr, link_name, name_team_page, mascot])

csv_file.close()

