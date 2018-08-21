"""
This pulls the NCAA football data and puts it into a dictionary
keys: school_name
values: list of attributes (ncaa_id, link, name_mascot, mascot)
June 22, 2018

Runtime: 9 minutes :'(

"""

import requests
import sys
import csv
import re
from bs4 import BeautifulSoup

csv_file = open('results_ncaa.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['school_name', 'ncaa_id 2018', "link", "name_mascot", "mascot"])

url = "https://stats.ncaa.org/team/inst_team_list?academic_year=2018&conf_id=-1&division=11&sport_code=MFB"
r = requests.get(url)
soup_teamsPage = BeautifulSoup(r.content, "lxml")

dict_schools = {}
counter = 1

table = soup_teamsPage.find('table')

for column in table.find_all('table'):

	for school in column.find_all('td'):

		school_name = school.text.strip()
		# print(str(counter) + " " + school_name)
		# counter += 1

		link = school.find('a')['href']
		link_full = "https://stats.ncaa.org" + link

		r = requests.get(link_full)
		soup_individualTeam = BeautifulSoup(r.content, "lxml")	# team page

		# id - note that this ID is just for 2017-18; it changes annually
		id_tag = soup_individualTeam.find('select', id="year_list")
		ncaa_id = id_tag.find('option')['value']

		name_mascot_long = soup_individualTeam.find('legend').text	# has "(3-9) ..." on the end
		name_mascot = re.sub('\([0-9]*-[0-9]*\).*', '', name_mascot_long).strip()

		# mascot
		mascot = name_mascot.replace(school_name, "").strip().split(',')[0]

		# ADD TO DICTIONARY AND CSV FILE
		dict_schools[school_name] = [ncaa_id, link, name_mascot, mascot]
		csv_writer.writerow([school_name, ncaa_id, link, name_mascot, mascot])

csv_file.close()


