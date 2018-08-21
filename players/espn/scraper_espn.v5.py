"""
v5 updates:
	just finds the instances where school != NULL and update it based on ID

This scrapes player recruit data from the ESPN database on
  http://www.espn.com/college-sports/football/recruiting/database
And stores it in a SQL Lite 3 database

July 17, 2018

"""

import requests
import sys
import re
import sqlite3
from bs4 import BeautifulSoup

start_index = 47610

# CREATE SQLITE DATABASE
conn = sqlite3.connect('players_espn.db')	# opens connection
cur = conn.cursor()							# instantiates a cursor

for player in cur.execute("SELECT ID, link_name, row FROM players WHERE signed_school IS NOT NULL AND row>?", (start_index,)).fetchall():
	print(player[2])
	link_player = "http://www.espn.com/college-sports/football/recruiting/player/_/id/" + player[0] + "/" + player[1]
	r = requests.get(link_player)
	soup = BeautifulSoup(r.content, "lxml")
	tag = soup.find('div', class_="bio")
	signed_school = None
	if (tag):
		bio_stats = tag.text
		signed_school = re.search('Signed ([\w &]+)', bio_stats)

	if (signed_school):
		signed_school = signed_school.group(1)
		cur.execute("UPDATE players SET signed_school=? WHERE ID=?", (signed_school,player[0]))

conn.commit()
conn.close()
