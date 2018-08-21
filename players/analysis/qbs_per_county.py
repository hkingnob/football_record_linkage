"""
Analyzes the proportion of quarterbacks produced per county and creates:
	choropleth map
	CSV file with top 5 counties for qbs proportionally

7-11-18

dictionary:
	keys: (<fips>, <county>, <state>)
	items: (<|QB's|>, <|QB's|/|total_recruits|>)
"""

import sqlite3
import csv
import plotly
import random

#CREATE DICTIONARY WITH FIPS
conn = sqlite3.connect("../espn/players_espn_full.db")
cur = conn.cursor()

players = cur.execute("SELECT fips, county, home_state, position FROM players WHERE position='Quarterback' AND fips!='None'")
qbs_dict = {}
for tup in players:
	if ((tup[0], tup[1], tup[2])) in qbs_dict:
		qbs_dict[(tup[0], tup[1], tup[2])] = [qbs_dict[(tup[0], tup[1], tup[2])][0] + 1]
	else:
		qbs_dict[(tup[0], tup[1], tup[2])] = [1]

# APPEND TOTAL_RECRUITS FROM CSV TO ITEMS
with open('recruits_per_county.csv') as csv_file:
	read_csv = csv.reader(csv_file, delimiter=',')
	for row in read_csv:
		county = row[0]
		state = row[1]
		fips = row[2]
		total_recruits = row[3]

		# add on leading zeroes that somewhere got stripped away
		while (len(fips) < 5):
			fips = '0' + fips

		tup = (fips, county, state)
		if (tup in qbs_dict):		# if that county is in the qb dictionary as a key
			qbs_dict[tup].append(qbs_dict[tup][0]/int(total_recruits))	# set item[1] equal to total_recruits from county
			# PROBLEM: LINE ABOVE ISN'T GETTING ALL OF THE ENTRIES IN QBS_DICT
				# the issue is that in the CSV some fips are losing their trailing zeroes - same them as string, not int next time!

# Create list of counties with highest proportion QB's produced
qb_counties = []

for i in range(10):
	top_value = list(qbs_dict.keys())[0]

	for x in qbs_dict:				# insertion sort to find the top 10 values
		# if proportion_qbs > top_value(proportion_qbs) -> set new top_value
		print(str(x) + "\t" + str(qbs_dict[x]))
		if (qbs_dict[x][1] > qbs_dict[top_value][1]):	
			top_value = x
	qb_counties.append((top_value, qbs_dict[top_value]))		# add top_value to list
	del qbs_dict[top_value]										# remove top_value from qbs_dict

for x in qb_counties:
	print(x)



