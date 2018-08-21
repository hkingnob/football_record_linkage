"""
v0 features:
	matches with levenshtein similarity (insertions, eliminations, substitutions)
	matches on name_mascot + mascot
	replaces state abbrev with full name

	
Success: Matches all but 3 schools
	Florida Intl Golden PanthersPanthers    13	Georgia State PanthersPanthers
	BYU CougarsCougars                      7	Houston CougarsCougars
	LSU TigersTigers                        6	Auburn TigersTigers

This program computes the levenshtein distance between references to
  college football teams on ESPN and on sports reference with the aim
  of record linkage.
It utilizes the rltk library (https://github.com/usc-isi-i2/rltk)
Sorting on name_mascot

June 18, 2018

data structure: dict_lev_distance dictionary
	keys:	ESPN schools
	values:	list of (sportsref school, lev_distance) tuples


"""

import rltk
import csv
import sys
import states
import re

# replace state abbreviation with full name
def get_full_name( name_mascot ):
	for abbrev in re.findall("[\w]+", name_mascot):		# regex - only letters
		if len(abbrev) == 2:			# if first term in list is abbreviation
			for item in states.us_state_abbrev.items():
				if abbrev == item[1]:
					name_mascot = name_mascot.replace(abbrev, item[0])
					break
	return name_mascot			


def main():

	csv_file = open('levenshtein_matches_espn_sportsref.csv')
	csv_writer = csv.csv_writer(csv_file)
	csv_writer.writerow(["ESPN school_name", "ESPN representation", "Levenshtein "])

	# read SportsReference file into a list of schools
	list_schools = []
	with open('results_sportsref.csv') as csv_file:
		csv_reader = csv.reader(csv_file)
		is_head_row = True
		for school in csv_reader:
			if is_head_row:						# skip the one head row
				is_head_row = False
				continue
			list_schools.append(get_full_name(school[3] + school[4]))	# *2 mascot

	dict_lev_distance = {}

	with open('results_espn.csv') as csv_file:
		csv_reader = csv.reader(csv_file)
		is_head_row = True

		for school in csv_reader:				# for each school in ESPN
			ref_1 = get_full_name(school[4] + school[5])	# *2 mascot
			if is_head_row:						# skip the one head row
				is_head_row = False
				continue

			dict_lev_distance[ref_1] = []		# create new list for each school in espn

			for ref_2 in list_schools:			# for each school_mascot in sportsref list
				lev_distance = rltk.levenshtein_similarity(ref_1, ref_2)
				dict_lev_distance[ref_1].append(((ref_2), lev_distance))

			temp_list = dict_lev_distance[ref_1]
			temp_list.sort(reverse = True, key=lambda temp_list: temp_list[1])
			dict_lev_distance[ref_1] = temp_list

	# OUTPUT
	print("{:<40}".format("Actual entity (ESPN)") + "lev\t" + "sportsref match name\n")
	for key, value in sorted(dict_lev_distance, key=dict_lev_distance.get[0][1])
	# for key, value in dict_lev_distance.items():
		if value[0][1] == 1:						#only print those that don't match identically
			print("{:<40}".format(key) + "\t" + value[0][0])
		else:
			print("{:<40}".format(key) + str(value[0][1]) + "\t" + value[0][0])

	csv_writer.closer()

main()



