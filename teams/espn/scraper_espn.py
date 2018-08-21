"""
This pulls the ESPN football data and puts it into a dictionary
keys: school_name
values: list of attributes (ID, link, name_mascot, mascot)
June 12, 2018

Runtime: 1 minute

"""

import requests
import sys
import csv
from bs4 import BeautifulSoup


csv_file = open('results_espn.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['school_name', 'ESPN_id', "link", "link_name", "name_mascot", "mascot"])

url = "http://www.espn.com/college-football/teams"
r = requests.get(url)
soup_teamsPage = BeautifulSoup(r.content, "lxml")

dict_schools = {}
counter = 1

all_schools = soup_teamsPage.find('div', class_="span-2")

for conference in all_schools.find_all('div', class_="mod-container mod-open-list mod-teams-list-medium mod-no-footer"):

	for school_section in conference.find_all('li'):

		# SITE 1

		# name, conference
		school_name = school_section.h5.text
		# print(str(counter+1) + " " + school_name)

		# get and split the URL
		link = school_section.find('a', class_="bi")['href']
		list_link = link.split('/')

		# id
		id = list_link[-2]

		# link_text - the part following "http://www.espn.com/college-football/team"
		link_text = link.split("team")[1][2:]

		# link_name
		link_name = link.split("/")[-1]
		
		# SITE 2

		# name_mascot
		r1 = requests.get(link)
		soup_individualTeam = BeautifulSoup(r1.content, "lxml")	# team page
		name_mascot = soup_individualTeam.find('li', class_="team-name").span.text

		# mascot
		# some normalization to make "St" become "State"
		# just for internal purposes to remove school_name from name_mascot
		name_plus_space = school_name.replace("St", "State")
		name_plus_space = school_name.replace("Stateate", "State")
		name_plus_space += " "
		mascot = name_mascot.replace(name_plus_space, "")
		if mascot == name_mascot:
			mascot = name_mascot.split()[-1]	# best guess for mascot


		# ADD TO DICTIONARY AND CSV FILE
		dict_schools[school_name] = [id, link_text, link_name, name_mascot, mascot]
		csv_writer.writerow([school_name, id, link_text, link_name, name_mascot, mascot])

csv_file.close()
