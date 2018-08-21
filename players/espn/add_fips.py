"""
This add the fips code onto the end of the player database, using fips data pulled from census site
	so not using addfips API - should be slightly faster

7-9-18
"""

import sqlite3
import geocoder
from geopy import geocoders
import addfips
import time
import fips_dict
max_APIrequest_second = 10		# according to https://developers.google.com/maps/premium/previous-licenses/previous-faq#js_usage_limits

conn = sqlite3.connect('players_espn_full.db')		# connects to database
c = conn.cursor()

conn_counties = sqlite3.connect('county_translation.db')
c_counties = conn_counties.cursor()

af = addfips.AddFIPS()

start_time = 0
current_second_APIs = 0
total_api_requests = 0

# players = c.execute('''SELECT * FROM players''')
players = c.execute('''SELECT * FROM players WHERE row>137601''').fetchall()

for player in players:
	name_first = player[0]
	name_last = player[1]
	ID = player[10]
	city = player[2]
	state = player[3]
	year = player[9]
	row = player[-1]

	county = None
	fips = None

	print(str(row) + "\t" + year, end='\t')

# 	ADD IN COUNTY AND COUNTY FIPS
	if (city and state):
		# print(city + ", " + state, end='\t')
		entry = c_counties.execute("SELECT * FROM county_translation WHERE city=? AND state=?", (city, state)).fetchall()
		if (len(entry) > 0 and entry[0][3] != None):		# then it exists in county_tranlsation
			print("IN DB", end="\t\t")
			county = entry[0][2]
			fips = entry[0][3]
			# print(county + " " + fips)
		else:											# else, use API and add to dictionary
			print("API", end="\t\t")
			total_api_requests += 1

			if (current_second_APIs == max_APIrequest_second):
				while (time.time() - start_time < 1):			# wait until we've reached the next second
					print("\nWAITING")
					continue
				current_second_APIs = 0

			county = geocoder.google(city + ", " + state).county

			if (current_second_APIs == 0):
				start_time = time.time()
			current_second_APIs += 1

			if (county != None):
				county = county.replace(" County","")
				fips = fips_dict.fips_dict.get(county)
				if (fips != None):
					c_counties.execute("INSERT INTO county_translation VALUES (?,?,?,?)", (city, state, county, fips))
	
	# print(county + "\t" + ID)
	c.execute("UPDATE players SET county = ? WHERE ID = ?", (county, ID))
	c.execute("UPDATE players SET fips = ? WHERE ID = ?", (fips, ID))
	print(str(county) + "\t" + str(fips))
	
	conn.commit()
	conn_counties.commit()

print("\nTotal API requests: " + str(total_api_requests))
conn_counties.close()
conn.close()
