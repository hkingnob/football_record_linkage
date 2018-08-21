"""

Populates another table in espn database players_espn_full.db listed by county
Later makes that into a choropleth with that star data per county

7-12-18
"""

import csv
import plotly
import sqlite3
import plotly.plotly as py
import plotly
import plotly.figure_factory as ff

class location():

	def __init__(self, county, state, fips, total_recruits):
		self.county = county
		self.state = state
		self.fips = fips
		self.total_recruits = total_recruits

# Returns a new tuple of the updated items to be inserted into the table
# SET total_recruits=?, total_stars=?, no_stars=?, one_stars=?, two_stars=?, three_stars=?, four_stars=?, five_stars=?
# stars: number of stars for new player
def increment_tup(county_entry, stars, fips):
	total_recruits = county_entry[3] + 1
	if (stars == None):
			stars = 0
	total_stars = county_entry[4] + stars
	no_stars = county_entry[5]
	one_stars = county_entry[6]
	two_stars = county_entry[7]
	three_stars = county_entry[8]
	four_stars = county_entry[9]
	five_stars = county_entry[10]

	if (stars == 0):
		rt = (total_recruits, total_stars, no_stars+1,one_stars,two_stars,three_stars,four_stars,five_stars,fips)
	if (stars == 1):
		rt = (total_recruits, total_stars, no_stars,one_stars+1,two_stars,three_stars,four_stars,five_stars,fips)
	if (stars == 2):
		rt = (total_recruits, total_stars, no_stars,one_stars,two_stars+1,three_stars,four_stars,five_stars,fips)
	if (stars == 3):
		rt = (total_recruits, total_stars, no_stars,one_stars,two_stars,three_stars+1,four_stars,five_stars,fips)
	if (stars == 4):
		rt = (total_recruits, total_stars, no_stars,one_stars,two_stars,three_stars,four_stars+1,five_stars,fips)
	if (stars == 5):
		rt = (total_recruits, total_stars, no_stars,one_stars,two_stars,three_stars,four_stars,five_stars+1,fips)

	return rt

# Returns a new tuple of the items to be inserted into the table
# county text, state text, fips text, total_recruits number, total_stars number, no_stars number, one_stars number, two_stars number, three_stars number, four_stars number, five_stars number
def get_new_tup(player):
	county = player[0]
	state = player[1]
	fips = player[2]
	total_recruits = 1
	stars = player[3]
	if (stars == None):
		stars = 0
	stars = int(stars)

	if (stars == 0):
		rt = (county, state, fips, total_recruits, stars, 1,0,0,0,0,0)
	if (stars == 1):
		rt = (county, state, fips, total_recruits, stars, 0,1,0,0,0,0)
	if (stars == 2):
		rt = (county, state, fips, total_recruits, stars, 0,0,1,0,0,0)
	if (stars == 3):
		rt = (county, state, fips, total_recruits, stars, 0,0,0,1,0,0)
	if (stars == 4):
		rt = (county, state, fips, total_recruits, stars, 0,0,0,0,1,0)
	if (stars == 5):
		rt = (county, state, fips, total_recruits, stars, 0,0,0,0,0,1)

	return rt


def main():
	conn = sqlite3.connect("../espn/players_espn_full.db")
	cur = conn.cursor()

	# colorscale = [
	#     'rgb(193, 193, 193)',
	#     'rgb(239,239,239)',
	#     'rgb(195, 196, 222)',
	#     'rgb(144,148,194)',
	#     'rgb(101,104,168)',
	#     'rgb(65, 53, 132)'
	# ]

	# binning_endpoints=

	# CALCULATE STAR WEIGHT
	# weight = [1,1,1,1,1,1]		# unweighted
	# weight = [0,1,4,9,16,25]	# square star weight
	weight = [0,1,3,9,27,81]	# triple proportional weight

	num_stars = [0,0,0,0,0,0]

	weighted_stars = []
	counties = cur.execute("SELECT no_stars, one_stars, two_stars, three_stars, four_stars, five_stars, total_stars, fips  FROM counties")
	for x in counties:
		num_stars = [num_stars[0]+x[0], num_stars[1]+x[1], num_stars[2]+x[2], num_stars[3]+x[3], num_stars[4]+x[4], num_stars[5]+x[5]]

	# CREATE LIST OF FIPS
	# CREATE LIST OF STARS CORRESPONDING TO FIPS LIST
	fips_list = []
	counties = cur.execute("SELECT no_stars, one_stars, two_stars, three_stars, four_stars, five_stars, total_stars, total_recruits, fips  FROM counties")

	for x in counties:
		fips_list.append(x[-1])

		weighted_stars.append((x[0]*weight[0] + x[1]*weight[1] + x[2]*weight[2] + x[3]*weight[3] + x[4]*weight[4] + x[5]*weight[5])/int(x[-2]))	# per total recruits

	# PRINT OUT WEIGHTED_STAR
	# create list of tuples with fips_list and weighted_stars
	tups = []
	i=0
	for x in fips_list:
		tups.append((fips_list[i], weighted_stars[i]))
		i += 1

	print(sorted(tups, key=lambda tup:tup[1], reverse=True)[10:20])


	# CREATE CHOROPLETH
	# fig = ff.create_choropleth(fips=fips_list, values=weighted_stars, legend_title="Aggregate and Weighted ESPN Recruit Stars", title="Recruit Prospects per County 2006-2018")
	# plotly.offline.plot(fig, filename='title.html')

	# CREATE DATABASE WITH COUNTY, STATE, FIPS, TOTAL_RECRUITS, TOTAL_STARS, 1_STAR, 2_STAR, 3_STAR, 4_STAR, 5_STAR
	# players = cur.execute("SELECT county, home_state, fips, stars, row FROM players WHERE fips!='None'").fetchall()

	# # iterate through players. if fips present in counties, increment total_recruits, total_stars, and <number>_stars
	# #								if not present in counties, create new entry

	# for player in players:
	# 	county = player[0]
	# 	state = player[1]
	# 	fips = player[2]
	# 	stars = player[3]
	# 	row = player[4]
	# 	print(row)
		
	# 	county_entry = cur.execute("SELECT * FROM counties WHERE fips=?", (fips,)).fetchall()
	# 	if (len(county_entry) > 0):			# if in table, increment total_recruits, total_stars, and <number>_stars
	# 		new_row = increment_tup(county_entry[0], stars, fips)		# returns a tuple with proper variables
	# 		cur.execute("UPDATE counties SET total_recruits=?, total_stars=?, no_stars=?, one_stars=?, two_stars=?, three_stars=?, four_stars=?, five_stars=? WHERE fips=?", (new_row))
		
	# 	else:								# if not in table, create new entry
	# 		new_row = get_new_tup(player)
	# 		cur.execute("INSERT INTO counties VALUES (?,?,?,?,?,?,?,?,?,?,?)", (new_row))

	# 	conn.commit()

	# CREATE CHOROPLETH
	# we need list of 


	# # GET DATA FROM CSV FILE
	# with open('recruits_per_county.csv') as csv_file:
	# 	read_csv = csv.reader(csv_file, delimiter=',')
	# 	locations = []	# list of lcation objects
	# 	first_row = True
	# 	for row in read_csv:
	# 		if (first_row):
	# 			first_row = False
	# 			continue
	# 		locations.append(location(row[0], row[1], row[2], int(row[3])))

	# OUTPUT TO CSV FILE
	# output_file = open('recruits_per_county_sorted.csv', 'w')
	# csv_writer = csv.writer(output_file)
	# csv_writer.writerow(["county", "state", "fips", "total_recruits"])
	# for x in sorted(locations, key=lambda location:location.total_recruits, reverse=True):
# 	# print(x.county + "\t" + str(x.total_recruits))
# 	csv_writer.writerow([x.county, x.state, x.fips, x.total_recruits])

main()

