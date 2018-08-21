"""
This scrapes the NCAA site for college football player data.
Grateful to code pulled from https://github.com/brendanlong/ncaa-predict/blob/master/fetch_csvs.py.

# Also apprently this just pulled 2014 data, not really sure why.

July 13, 2018
"""

import requests
import sqlite3
from bs4 import BeautifulSoup
import csv

id_names = {}
attributes = []

def post_form(url, post_data=None):
    headers = {
        "user-agent":
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, "
            "like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "referrer": url,
    }
    if post_data is not None:
        res = requests.post(url, data=post_data, headers=headers)
    else:
        res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res

# Returns a dictionary of id:school_name of ncaa_schools.csv (currently found in desktop)
def get_team_ids():
	with open('ncaa_schools.csv') as csv_file:
		csv_reader = csv.reader(csv_file)
		is_head_row = True
		for row in csv_reader:
			if is_head_row:
				is_head_row = False
				continue
			id_names[row[0]] = row[1]


def main():

	conn = sqlite3.connect("players_ncaa.db")
	cur = conn.cursor()

	SEARCH_URL = "http://web1.ncaa.org/stats/StatsSrv/careersearch"
	RECORDS_URL = "http://web1.ncaa.org/stats/exec/records"
	TEAM_URL = "http://web1.ncaa.org/stats/StatsSrv/careerteam"
	get_team_ids()	# populates global dictionary with id:name pair

	# for year in [2007,2008,2009,2010,2011,2012,2013,2014]:


	# STAGE 1

	year = 2007
	ID = "8"

	page = post_form(TEAM_URL, {
                "academicYear": str(year),
                "orgId": int(ID),				# 8 for bama, just an example
                "sportCode": "MFB",
                "sortOn": "0",
                "doWhat": "display",
                "playerId": "-100",
                "coachId": "-100",
                "division": "1",
                "idx": ""
                })

	school = "Alabama"

	soup = BeautifulSoup(page.content, 'lxml')
	# if (ID == "8"):
	# 	print(soup.prettify())
	# 	print(soup.find_all('table', class_="statstable"))
	if (len(soup.find_all('table', class_="statstable"))) < 2:
		print("table list length less than 2")
		exit()
	table = soup.find_all('table', class_="statstable")[1]	# first table is team stats

	# if there's <5 entries in the table, there's no player data
	if (len(table.find_all('tr')) < 5):
		print("less than 5 entries")
		exit()
		
	print(school + '\t' + str(year))	# only prints schools that have data

	i = 0
	for player in table.find_all('tr'):
		i += 1
		# if (i==3):
		# 	for att in player.find_all('td'):
		# 		attributes.append(att.text.strip())
		if (i<4):
			continue

		name = player.find(attrs={'title':"Click to have career stats displayed"}).text
		name = " ".join(name.split(", ")[::-1])
		class_ = player.find_all('td')[1].text.strip()
		year = player.find_all('td')[2].text.strip()
		position = player.find_all('td')[3].text.strip()
		row = i
		
		# get blob - all data per player
		blob = []
		for att in player.find_all('td'):
			blob.append(att.text.strip())

		cur.execute("INSERT INTO players VALUES (?,?,?,?,?,?,?)", (row-3, name, school, class_, year, position, str(blob)))
	conn.commit()	# commits after every team is loaded
	# exit()

	# STAGE 2
	print("STAGE2")

	year = 2007
	ID = "9"

	page = post_form(TEAM_URL, {
                "academicYear": str(year),
                "orgId": int(ID),				# 8 for bama, just an example
                "sportCode": "MFB",
                "sortOn": "0",
                "doWhat": "display",
                "playerId": "-100",
                "coachId": "-100",
                "division": "1",
                "idx": ""
                })

	school = "Alabama St."


	soup = BeautifulSoup(page.content, 'lxml')
	# if (ID == "8"):
	# 	print(soup.prettify())
	# 	print(soup.find_all('table', class_="statstable"))
	if (len(soup.find_all('table', class_="statstable"))) < 2:
		print("table list length less than 2")
		exit()
	table = soup.find_all('table', class_="statstable")[1]	# first table is team stats

	# if there's <5 entries in the table, there's no player data
	if (len(table.find_all('tr')) < 5):
		print("less than 5 entries")
		exit()
		
	print(school + '\t' + str(year))	# only prints schools that have data

	i = 0
	for player in table.find_all('tr'):
		i += 1
		# if (i==3):
		# 	for att in player.find_all('td'):
		# 		attributes.append(att.text.strip())
		if (i<4):
			continue

		name = player.find(attrs={'title':"Click to have career stats displayed"}).text
		name = " ".join(name.split(", ")[::-1])
		class_ = player.find_all('td')[1].text.strip()
		year = player.find_all('td')[2].text.strip()
		position = player.find_all('td')[3].text.strip()
		row = i
		
		# get blob - all data per player
		blob = []
		for att in player.find_all('td'):
			blob.append(att.text.strip())

		cur.execute("INSERT INTO players VALUES (?,?,?,?,?,?,?)", (row-3, name, school, class_, year, position, str(blob)))
		
	conn.commit()	# commits after every team is loaded
	# exit()
		





main()