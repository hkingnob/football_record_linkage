"""
v6 updates:
	Prints out school_name for each as opposed to name_mascot
	Moves all potential matches to potential_matches section
	Shows top 3 options in potential_matches section if match_score < match_threshold
	No longer shows scores
	Print list alphabetically

This program computes the jaro_winkler similarity between references to
  college football teams on ESPN, NCAA, sports reference, 247sports,
  and rivals with the aim of record linkage.
It utilizes the rltk library (https://github.com/usc-isi-i2/rltk)

Scraper links:
	sportsref:	https://www.sports-reference.com/cfb/years/2017-standings.html
	ncaa:		https://stats.ncaa.org/team/inst_team_list?academic_year=2018&conf_id=-1&division=11&sport_code=MFB
	espn:		http://www.espn.com/college-football/teams
	247sports:	https://www.cbssports.com/college-football/teams/
	rivals:		https://n.rivals.com/team_rankings/2018/all-teams/football.html
					link pulled from rivals resource section - doesn't exactly match index page

June 25, 2018
"""

import rltk
import csv
import sys
import states
import re
import match
import school

# IMPORTANT VARIABLES THAT YOU MAY WANT TO CHANGE
match_threshold = .8	# minimimum score for a match, the highest false match jaro_wink score for 247 and espn is .78 (see results_jarowinkler_threshold.numbers)
# match_threshold = 1		# for levenshtein distance proofing
reference_source = "sportsref"	# the source to which all others are compared
source_list = ["sportsref", "ncaa", "espn", "247", "rivals"]
source_list.remove(reference_source)
list_schools = []

# Add matches from source to school object
def get_matches(school, source):
	with open('../' + source + '/results_' + source + '.csv') as csv_file:
		csv_reader = csv.reader(csv_file)
		is_head_row = True
		for row in csv_reader:
			if is_head_row:						# skip the one head row
				is_head_row = False
				continue
			my_match = match.match(source, row)


			# IMPORTANT LINE - CALCULATES SIMILARITY SCORE
			# rltk.jaro_winkler_similarity(s1, s2, <threshold for invoking prefix score>, <scaling factor for prefix score>, <length of prefix score>)
			if (source == "rivals" or reference_source == "rivals"):	# then we have to use school name
				# distance_score = rltk.levenshtein_similarity(school.school_name, my_match.school_name)
				distance_score = rltk.jaro_winkler_similarity(school.school_name, my_match.school_name, 0.6, 0.25, 1)
			else:
				# distance_score = rltk.levenshtein_similarity(school.representation, my_match.representation)
				distance_score = rltk.jaro_winkler_similarity(school.representation, my_match.representation, 0.6, 0.25, 1)


			eval("school.matches_" + source + ".append((my_match, distance_score))")

	school.sort_lists(source)
	csv_file.close()


def main():
	
	# read reference_source into a list of school objects
	with open('../' + reference_source + '/results_' + reference_source + '.csv') as csv_file:
		csv_reader = csv.reader(csv_file)
		is_head_row = True
		for row in csv_reader:
			if is_head_row:						# skip the one head row
				is_head_row = False
				continue
			list_schools.append(school.school(reference_source, row))
	csv_file.close()

	# get matches for reference_source for each source in source_list
	for source in source_list:						# for each source
		for myschool in list_schools:				# for each school
			get_matches(myschool, source)			# adds top 5 matches

	# determine if match needs to be manually reviewed in potential matches section
	for myschool in list_schools:
		if myschool.hasMatch(reference_source, match_threshold):		# if it has all matches across the sources, then no need to review
			myschool.show_in_potential_matches = False


	# OUTPUT LIST_SCHOOLS TO CSV FILE
	csv_file = open('results_jarowinkler.csv', 'w')
	csv_writer = csv.writer(csv_file)
	
	top_row = ["reference source (" + reference_source + ") school_name"]
	for source in source_list:
		top_row.append(source)
	csv_writer.writerow(top_row)

	# Sort list_schools alphabetically on name_mascot
	list_schools.sort(key=lambda x: x.name_mascot)

	# definitive matches
	for x in list_schools:
		printRow(csv_writer, x)
			
	# potential matches
	csv_writer.writerow([])
	csv_writer.writerow(["POTENTIAL MATCHES"])
	csv_writer.writerow([])
	for x in list_schools:
		if x.show_in_potential_matches:
			printRow_potential_mascot(csv_writer, x)

	csv_file.close()


# Prints name, representation, and distance score for each school
def printRow(csv_writer, x):
	row = [x.school_name]
	for source in source_list:		# for each source in source_list, get name_mascot and score
		if (not x.has_individual_match(reference_source, source, match_threshold)):
			row.append("")
		else:
			row.append(eval("x.matches_" + source + "[0][0].school_name"))

	csv_writer.writerow(row)


# Prints name, representation, and distance score for each school, and includes top 3 school options
def printRow_potential_mascot(csv_writer, x):
	row = ["\n" + x.school_name]
	for source in source_list:		# for each source in source_list, get name_mascot
		cell = ""
		if (not x.has_individual_match(reference_source, source, match_threshold)):
			for i in range(3):
				cell += eval("x.matches_" + source + "[" + str(i) + "][0].school_name") + "\n"
		cell = cell.strip()
		row.append(cell)

	csv_writer.writerow(row)
		

main()

