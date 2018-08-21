"""
Links college football players from different data sources:
	rivals: https://n.rivals.com/api/content/prospects/1
	sportsreference college player data: https://www.sports-reference.com/cfb/play-index/pgl_finder.cgi?request=1&match=career&offset=

v4 updates:
	Now doing 2011
	Includes all ESPN recruits from 2011, and rivals recruits and sportsref players to those

Only for a given year: 2014

July 19, 2018
"""

import sqlite3
import rltk
import csv
import time
import school_translations
import school
import match
import jaro_winkler_v7
from difflib import SequenceMatcher

start_index = 0
table = school_translations.table
year_of_linkage = 2014
jaro_threshold_players = .95
jaro_threshold_schools = .9
jaro_threshold_hometown = .9
position_substring_min = 3		# minimum length of matching substring to verify position if school==null, the example in mind here is "end"

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
		if (school in school_translations.table.keys()):
			school = school_translations.table[school]
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
	# First just try it without getting the canonical source
	distance_score = rltk.jaro_winkler_similarity(school_1.lower(), school_2.lower())
	if (distance_score > jaro_threshold_schools):
		return True

	school_1 = get_canonical_source(school_1, source_1)
	school_2 = get_canonical_source(school_2, source_2)

	distance_score = rltk.jaro_winkler_similarity(school_1.lower(), school_2.lower())
	if (distance_score > jaro_threshold_schools):
		return True
	return False

# Note that sources are only for where school_1 and school_2 come from
def confirmed_match(name_1, name_2, school_1, school_2, hometown_1, hometown_2, pos_1, pos_2, source_1, source_2):

	if (not (name_1 and name_2)):
		return False

	# COMPARE HOMETOWNS - if hometowns are present and more than jaro_threshold different, return false
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
	if (distance_score > jaro_threshold_players):

		# COMPARE POSITIONS IF NO SCHOOLS
		if (not (school_1 and school_2)): # if not school, use position
			if (pos_1 and pos_2):
				# return True if pos_1 and pos_2 share a substring of 3+ chars
				match_len = SequenceMatcher(None, pos_1, pos_2).find_longest_match(0, len(pos_1), 0, len(pos_2))[2]
				if (match_len >= position_substring_min):
					return True

			return False				# no school and no position -> no match

		# COMPARE SCHOOLS
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

# Add's ESPN 2011 data to database
def link_espn(conn_linked, cur_linked):
	conn_espn = sqlite3.connect("../espn/players_espn.db")
	cur_espn = conn_espn.cursor()
	i=0


	for player_espn in cur_espn.execute("SELECT * from players WHERE year=?", (year_of_linkage,)).fetchall():
		name_espn = player_espn[0] + ' ' + player_espn[1]
		school_espn = player_espn[15]
		hometown_espn = player_espn[2]
		position_espn = player_espn[5]
		row_espn = player_espn[-2]
		i+=1
		print(i)

		# UPDATE DATABASES
		cur_espn.execute("UPDATE players SET in_linked_database=2 WHERE row=?", (row_espn,))
		# print("name= " + name_espn)
		cur_linked.execute("INSERT INTO players VALUES (?,?,null,null,?,null,null,?,?,null,?,null,?,null,null,?,null,null)", (i,name_espn,school_espn,year_of_linkage,hometown_espn,position_espn,str(player_espn),row_espn))
		conn_espn.commit()
		conn_linked.commit()

# Links rivals data to espn data already in db
def link_rivals(conn_linked, cur_linked):
	conn_rivals = sqlite3.connect("../rivals/players_rivals_full.db")
	cur_rivals = conn_rivals.cursor()

	for db_player in cur_linked.execute("SELECT * from players WHERE row>?", (start_index,)).fetchall():
		row_db = db_player[0]
		name_db = db_player[1]
		school_db = db_player[4]
		hometown_db = db_player[8]
		position_db = db_player[10]
		print(row_db, end='\t')

		for rivals_player in cur_rivals.execute("SELECT * from players WHERE recruit_year=?", (year_of_linkage,)).fetchall():
			row_rivals = rivals_player[0]
			name_rivals = rivals_player[1] + ' ' + rivals_player[2]
			school_rivals = rivals_player[11]
			position_rivals = rivals_player[12]
			hometown_rivals = rivals_player[3]

			if (confirmed_match(name_db, name_rivals, school_db, school_rivals, hometown_db, hometown_rivals, position_db, position_rivals, "espn", "rivals")):
				print("match", end='')

				# ADD TO DATABASE
				cur_linked.execute("UPDATE players SET name_rivals=?, school_rivals=?, hometown_rivals=?, position_rivals=?, rivals_all_data=?, row_rivals=? WHERE row=?", (name_rivals,school_rivals,hometown_rivals,position_rivals,str(rivals_player),row_rivals,row_db))
				cur_rivals.execute("UPDATE players SET in_linked_database=2 WHERE row=?", (row_rivals,))
				conn_linked.commit()
				conn_rivals.commit()
				break
		print()

# Link sportsref data to espn/rivals data already in db
def link_sportsref(conn_linked, cur_linked):
	conn_sportsref = sqlite3.connect("../sportsref/players_sportsref_full.db")
	cur_sportsref = conn_sportsref.cursor()

	for db_player in cur_linked.execute("SELECT * from players WHERE row>?", (start_index,)).fetchall():
		row_db = db_player[0]
		name_db = db_player[1]
		school_db = db_player[4]
		print(row_db, end='\t')

		for player_sportsref in cur_sportsref.execute("SELECT * from players WHERE year_start>=?", (year_of_linkage,)).fetchall():
			name_s = player_sportsref[1]
			school_s = player_sportsref[4]
			row_s = player_sportsref[0]
			sportsref_all_data = str(player_sportsref)

			if (confirmed_match(name_db, name_s, school_db, school_s, "", "","","", "espn", "sportsref")):
				print("match", end="")

				# UPDATE DATABASE
				cur_linked.execute("UPDATE players SET name_sportsref=?, school_sportsref=?, sportsref_all_data=?, row_sportsref=? WHERE row=?", (name_s,school_s,sportsref_all_data,row_s,row_db))
				cur_sportsref.execute("UPDATE players SET in_linked_database=2 WHERE row=?", (row_s,))
				conn_linked.commit()
				# conn_sportsref.commit()
				break

		print()


def main():
	conn_linked = sqlite3.connect("linked_players_2014.v2.db")
	cur_linked = conn_linked.cursor()

	# link_espn(conn_linked, cur_linked)
	# link_rivals(conn_linked, cur_linked)
	link_sportsref(conn_linked, cur_linked)

main()