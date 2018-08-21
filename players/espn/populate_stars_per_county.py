"""
This populates a sqlite3 database with star data per year.


Ex: McClean County has Brett Farve (2 stars), Dwayne Johnson (3 stars), and Shaq (4 stars) ---> 9 stars for McClean
later we can try to do it by stars relative to population

data pulled from ESPN

7-6-18
"""

import sqlite3
import geocoder
from geopy import geocoders
import addfips

conn_old = sqlite3.connect('players_espn_full.db')		# connects to database
cur_old = conn_old.cursor()

conn_new = sqlite3.connect('stars_per_county.db')		# connects to database
cur_new = conn_new.cursor()




stars_per_county = {}		# dict with (county, state, and fips matches to total stars)

players = cur_old.execute("SELECT * FROM players")
players = players.fetchall()

# LOOP THROUGH VALUES, COLLECT INFO, AND ADD TO DICTIONARY (SUMMING FOR DUPLICATES)
for player in players:

	row = player[-1]
	print(row)

	# COLLECT VALUES
	stars = player[7]
	county_fips = player[17]
	county = player[16]
	state = player[3]
	if (stars == None or county_fips == None):
		continue

	if ((county, state, county_fips) in stars_per_county):		# if in dictionary, add on stars
		stars_per_county[(county, state, county_fips)][0] += stars
		stars_per_county[(county, state, county_fips)][1] += 1
	else:														# else, set it equal to stars
		stars_per_county[(county, state, county_fips)] = [stars, 1]

for x in stars_per_county:
	stars_per_player = round(stars_per_county[x][0]/stars_per_county[x][1], 2)
	cur_new.execute("INSERT INTO full_stars_per_county VALUES (?,?,?,?,?,?)", (x[0],x[1],x[2],stars_per_county[x][0],stars_per_county[x][1],stars_per_player))

	conn_new.commit()


conn_old.close()
conn_new.close()
