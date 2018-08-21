"""
Pulls recruiting data from https://n.rivals.com/api/content/prospects/1
	and plops it into sqlite3 database players_rivals_full.db

"""

import sqlite3
import requests
import json
from bs4 import BeautifulSoup

conn = sqlite3.connect('players_rivals_full.db')		# connects to database
cur = conn.cursor()

last_seen_index = 248334
last_seen_index = last_seen_index//1000*1000 # brings it back to the nearest 1000 (the last commit)

for i in range(last_seen_index, 250000):
	i += 1
	url = "https://n.rivals.com/api/content/prospects/" + str(i)
	r = requests.get(url)
	print(i)
	try:
		player_dict = json.loads(r.text)
	except:
		n = None
		cur.execute("""INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (n,n,n,n,n,n,n,n,n,n,n,n,n,n,n,n,n,n,n))
		continue

	row = i
	first_name = player_dict.get("first_name")
	last_name = player_dict.get("last_name")
	try:
		hometown = player_dict.get("hometown").split(',')[0]
	except:
		hometown = None
	try:
		home_state = player_dict.get("hometown").split(',')[1].replace(",","").strip()
	except:
		home_state = None
	high_school = player_dict.get("highschool_name")
	position_group_abbreviation = player_dict.get("position_group_abbreviation")
	stars = player_dict.get("stars")
	url = player_dict.get("url")
	height = player_dict.get("height")
	weight = player_dict.get("weight")
	college = player_dict.get("committed_college_name")
	position = player_dict.get("position")
	rivals_rating = player_dict.get("rivals_rating")
	sport_school_id = player_dict.get("sport_school_id")
	recruit_year = player_dict.get("recruit_year")
	national_rank = player_dict.get("national_rank")
	state_rank = player_dict.get("state_rank")
	all_data = r.text

	cur.execute("""INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (row, first_name, last_name, hometown, home_state, high_school, position_group_abbreviation, stars, url, height, weight, college, position, rivals_rating, sport_school_id, all_data, recruit_year, national_rank, state_rank))
	if (i%1000==0):
		conn.commit()

conn.close()