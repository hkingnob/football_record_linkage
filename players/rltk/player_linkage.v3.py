"""
Links college football players from different data sources:
	rivals: https://n.rivals.com/api/content/prospects/1
	sportsreference college player data: https://www.sports-reference.com/cfb/play-index/pgl_finder.cgi?request=1&match=career&offset=

v3 updates:
	now utilizes results of team record linkage for more accurate player linkage

Only for a given year: 2014

July 17, 2018
"""

import sqlite3
import rltk
import csv
import time
import school_translations
import school
import match
import jaro_winkler_v7

table = school_translations.table
year_of_linkage = 2014
jaro_threshold_players = .95
jaro_threshold_schools = .9
jaro_threshold_hometown = .9

list_schools = jaro_winkler_v7.list_schools 	# list of school objects


# changes W to Western, E to Eastern, etc.
def replace_directions(school):
	school.replace("W ", "Western ")
	school.replace("E ", "Eastern ")
	school.replace("S ", "Southern ")
	school.replace("N ", "Northern ")

	return school

def get_canonical_source(school, source):

	# Neither of these sources have names that match the data we pulled, so just search the whole table
	if (source == "rivals" or source == "espn"):
		with open('results_jarowinkler.csv') as csv_file:
			csv_reader = csv.reader(csv_file)
			for row in csv_reader:					# Search through all the rows, if you find the right one set to canonical name
				for potential_school in row:
					if (school.lower() == potential_school.lower()):
						return row[0]

	# Match with the link_name
	if (source == "sportsref"):
		for x in list_schools:
			potential_school = x.match.link_name.replace('-', ' ')
			if (school.lower() == potential_school.lower()):
				return x.school_name

	if (source == "ncaa"):
		# TODO
		return school
	
	return school

"""
Converts to canonical name
Returns true if school_1.lower() == school_2.lower()
"""
def school_match(school_1, school_2, source_1, source_2):
	school_1 = get_canonical_source(school_1, source_1)
	school_2 = get_canonical_source(school_2, source_2)

	distance_score = rltk.jaro_winkler_similarity(school_1.lower(), school_2.lower())
	if (distance_score > jaro_threshold_schools):
		return True
	return False

# Note that sources are only for where school_1 and school_2 come from
def confirmed_match(name_1, name_2, school_1, school_2, hometown_1, hometown_2, source_1, source_2):
	if (not (name_1 and name_2 and school_1 and school_2)):
		return False

	# COMPARE HOMETOWNS
	if (hometown_1 and hometown_2):
		string1 = hometown_1.strip(" '()").lower()
		string2 = hometown_2.strip(" '()").lower()
		distance_score = rltk.jaro_winkler_similarity(string1, string2)
		if (distance_score < jaro_threshold_hometown):
			return False

	# COMPARE NAMES
	string1 = name_1.strip(" '()").lower()
	string2 = name_2.strip(" '()").lower()
	distance_score = rltk.jaro_winkler_similarity(string1, string2)

	# COMPARE SCHOOLS
	if (distance_score > jaro_threshold_players):
		if school_match(school_1, school_2, source_1, source_2):
			return True

		if ('/' in school_1):

			school_new = school_1.split('/')[0]
			if school_match(school_new, school_2, source_1, source_2):
				return True

			school_new = school_1.split('/')[1]
			if school_match(school_new, school_2, source_1, source_2):
				return True

		elif ('/' in school_2):
			school_new = school_2.split('/')[0]
			if school_match(school_1, school_new, source_1, source_2):
				return True

			school_new = school_2.split('/')[1]
			if school_match(school_1, school_new, source_1, source_2):
				return True

	return False

def link_rivals_sportsref(conn_linked, cur_linked):
	conn_rivals = sqlite3.connect("../rivals/players_rivals_full.db")
	cur_rivals = conn_rivals.cursor()
	conn_sportsref = sqlite3.connect("../sportsref/players_sportsref_full.db")
	cur_sportsref = conn_sportsref.cursor()	

	last_seen_index = 0

	for player_rivals in cur_rivals.execute("SELECT * from players WHERE in_linked_database is not 1 and row>? and recruit_year=?", (last_seen_index, year_of_linkage)).fetchall():
		name_r = player_rivals[1] + ' ' + player_rivals[2]
		print(player_rivals[0], end='\t')
		school_r = player_rivals[11]
		year_r = player_rivals[16]
		rivals_all_data = str(player_rivals)

		for player_sportsref in cur_sportsref.execute("SELECT * from players WHERE in_linked_database is not 1 and year_start>=?", (year_of_linkage,)).fetchall():
			name_s = player_sportsref[1]
			school_s = player_sportsref[4]
			year_s = player_sportsref[2]
			sportsref_all_data = str(player_sportsref)

			if (confirmed_match(name_r, name_s, school_r, school_s, "", "", "rivals", "sportsref")):
				print("match", end='')
				
				# ADD TO DATABASE
				cur_linked.execute("INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (name_r, name_s, "", school_r, school_s, "", year_r, player_rivals[3], player_rivals[12], str(player_sportsref), "", player_rivals[15], player_sportsref[0], "", player_rivals[0]))

				# MARK 1 IN IN_LINKED_DB COLUMN IN OG SOURCE DATABASE
				cur_rivals.execute("UPDATE players SET in_linked_database=1 WHERE row=?", (player_rivals[0],))
				cur_sportsref.execute("UPDATE players SET in_linked_database=1 WHERE row=?", (player_sportsref[0],))
				conn_linked.commit()
				break

		conn_rivals.commit()	
		conn_sportsref.commit()

		print()

# Link ncaa data to database
# Problem: With the data we have from only 2014 for college players, we'll get only freshman :/
def link_ncaa(conn_linked, cur_linked):
	conn_ncaa = sqlite3.connect("../ncaa/players_ncaa.db")
	cur_ncaa = conn_ncaa.cursor()

	for db_player in cur_linked.execute("SELECT * from players WHERE entering_year=2014").fetchall():
		name_db = db_player[0]		# name_rivals
		school_db = db_player[4]	# school_sportsref
		position = db_player[8]		# position (from rivals)

		for player_ncaa in cur_ncaa.execute("SELECT * from players WHERE in_linked_database is not 1 and entering_year=2014").fetchall():
			name_ncaa = player_ncaa[1]
			school_ncaa = player_ncaa[2]
			position_ncaa = player_ncaa[5]

# Link ESPN to database
def link_espn(conn_linked, cur_linked):
	conn_espn = sqlite3.connect("../espn/players_espn_full.v2.db")
	cur_espn = conn_espn.cursor()

	for db_player in cur_linked.execute("SELECT * from players WHERE entering_year=2014").fetchall():
		name_db = db_player[0]		# name_rivals
		school_db = db_player[4]	# school_sportsref
		hometown_db = db_player[7]	# hometown_rivals
		position_db = db_player[8]		# position (from rivals)
		row_db = db_player[-1]		# TODO - ADD ROW TO linked_players.db
		print(row_db, end='\t')

		for player_espn in cur_espn.execute("SELECT * from players WHERE year=2014 and in_linked_database is not 1").fetchall():
			name_espn = player_espn[0] + ' ' + player_espn[1]
			school_espn = player_espn[15]
			hometown_espn = player_espn[2]
			position_espn = player_espn[5]
			row_espn = player_espn[-2]

			if (confirmed_match(name_db, name_espn, school_db, school_espn, hometown_db, hometown_espn, "sportsref", "espn")):
				print("match", end='')

				# UPDATE DATABASES
				cur_espn.execute("UPDATE players SET in_linked_database=1 WHERE row=?", (row_espn,))
				# print("name= " + name_espn)
				cur_linked.execute("UPDATE players SET name_espn=?,school_espn=?,espn_all_data=?,row_espn=? WHERE row=?", (name_espn, school_espn, str(player_espn), row_espn, row_db))
				# cur_linked.execute("UPDATE players SET name_espn=? WHERE row=?", (name_espn, row_db))
				conn_espn.commit()
				conn_linked.commit()
				break
		print()


def main():
	conn_linked = sqlite3.connect("linked_players_2014.db")
	cur_linked = conn_linked.cursor()


	# link_rivals_sportsref(conn_linked, cur_linked)
	# link_ncaa(conn_linked, cur_linked)
	link_espn(conn_linked, cur_linked)

main()