"""
Links college football players from different data sources:
	espn recruiting data: http://www.espn.com/college-sports/football/recruiting/database
	sportsreference college player data: https://www.sports-reference.com/cfb/play-index/pgl_finder.cgi?request=1&match=career&offset=


July 16, 2018
"""

import sqlite3
import time

# Returns True is school_e matches school_s, per the team record linkage done previously
def school_match(school_1, school_2):
	# Ideal solution:
		# create that translation table and pull from there. but first you need to see if the names of the teams for the players match any of the names you pulled for the teams
	# current (non-ideal) solution:
	if (school_1.strip("()'") == school_2.strip("()'")):
		return True
	return False

# Returns True if names are identical, years are identical, and schools match
def confirmed_match(name_1, name_2, year_1, year_2, school_1, school_2):
	if (str(year_1) == str(year_2)):
		if (name_1.strip(".'-").lower() == name_2.strip(".'-").lower()):
			# print("identical names!")
			if (school_match(school_1, school_2)):
				return True
	return False

def link_espn_sportsref(conn_linked, cur_linked):
	conn_espn = sqlite3.connect("../espn/players_espn_full.db")
	cur_espn = conn_espn.cursor()
	conn_sportsref = sqlite3.connect("../sportsref/players_sportsref_full.db")
	cur_sportsref = conn_sportsref.cursor()

	for player_espn in cur_espn.execute("SELECT name_first, name_last, hometown, position, year, forty, signed_school, row from players"):
		for player_sportsref in cur_sportsref.execute("SELECT row, name, year_start, school from players_sportsref"):

			# Actual Comparison based off of name, year, and school
			name_e = player_espn[0] + ' ' + player_espn[1]
			name_s = player_sportsref[1]
			year_e = player_espn[4]
			year_s = player_sportsref[2]
			school_e = player_espn[6]
			school_s = player_sportsref[3]
			# print(name_e + " " + name_s)
			# print(str(year_e) + " " + str(year_s))
			# print(school_e + " " + school_s)

			if (confirmed_match(name_e, name_s, year_e, year_s, school_e, school_s)):
				print("fuck")
				# ADD TO DATABASE

def link_rivals_sportsref(conn_linked, cur_linked):
	conn_rivals = sqlite3.connect("../rivals/players_rivals_full.db")
	cur_rivals = conn_rivals.cursor()
	conn_sportsref = sqlite3.connect("../sportsref/players_sportsref_full.db")
	cur_sportsref = conn_sportsref.cursor()	

	last_seen_index = 0

	for player_rivals in cur_rivals.execute("SELECT * from players WHERE row>?", (last_seen_index,)).fetchall():
		name_r = player_rivals[1] + ' ' + player_rivals[2]
		print(player_rivals[0], end='\t')
		year_r = player_rivals[16]
		school_r = player_rivals[11]
		rivals_all_data = str(player_rivals)

		for player_sportsref in cur_sportsref.execute("SELECT * from players_sportsref WHERE in_linked_database is not 1").fetchall():
			name_s = player_sportsref[1]
			year_s = player_sportsref[2]
			school_s = player_sportsref[4]
			sportsref_all_data = str(player_sportsref)

			if (confirmed_match(name_r, name_s, year_r, year_s, school_r, school_s)):
				print("match")
				
				# ADD TO DATABASE
				cur_linked.execute("INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?)", (name_r, school_r, year_r, player_rivals[3], player_rivals[12], str(player_sportsref), "", player_rivals[15], player_sportsref[0], "", player_rivals[0]))

				# MARK 1 IN IN_LINKED_DB COLUMN IN OG SOURCE DATABASE
				cur_rivals.execute("UPDATE players SET in_linked_database=1 WHERE row=?", (player_rivals[0],))
				cur_sportsref.execute("UPDATE players_sportsref SET in_linked_database=1 WHERE row=?", (player_sportsref[0],))
				conn_linked.commit()
				conn_rivals.commit()
				conn_sportsref.commit()
				break
				
		print()



def main():
	conn_linked = sqlite3.connect("linked_players.db")
	cur_linked = conn_linked.cursor()

	# link_espn_sportsref(conn_linked, cur_linked)

	link_rivals_sportsref(conn_linked, cur_linked)
	print("done")

main()