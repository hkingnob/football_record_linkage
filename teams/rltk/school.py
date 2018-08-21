"""
School class: school from the canonical school to which other schools will be matched.

Data:
	One match object (sportsref school)
	sportsref_match - list of 5 sportsref matches with greatest similarity
	ncaa_match	 	- ...
	espn_matches	- ...
	247_matches		- ...
	rivals_matches	- ...

June 19, 2018
"""

import match

class school:

	def __init__(self, source, row):
		self.match = match.match(source, row)
		self.school_name = self.match.school_name
		self.name_mascot = self.match.name_mascot
		self.representation = self.match.representation
		self.show_in_potential_matches = True

		# lists of tuples - (match, score)
		self.matches_sportsref = []
		self.matches_ncaa = []
		self.matches_espn = []
		self.matches_247 = []
		self.matches_rivals = []

	# Returns true if the first item in all of matches_<source> list has
	#   a score above match_threshold
	def hasMatch(self, reference_source, match_threshold):
		if (reference_source != "sportsref" and self.matches_sportsref[0][1] < match_threshold):
			return False

		if (reference_source != "ncaa" and self.matches_ncaa[0][1] < match_threshold):
			return False

		if (reference_source != "espn" and self.matches_espn[0][1] < match_threshold):
			return False

		if (reference_source != "247" and self.matches_247[0][1] < match_threshold):
			return False

		if (reference_source != "rivals" and self.matches_rivals[0][1] < 1):	# because of the lack of info rivals has, even a .95 can be a false match (Easter Michigan -> Western Michigan)
			return False

		if (reference_source == "rivals"):
			if (self.matches_sportsref[0][1] < 1 or self.matches_ncaa[0][1] < 1 or self.matches_espn[0][1] < 1 or self.matches_247[0][1] < 1):
				return False

		return True

	# Returns true if it has a match above the threshold for the given source
	def has_individual_match(self, reference_source, source, match_threshold):
		if (reference_source == "rivals" or source == "rivals"):
			if (self.matches_rivals[0][1] == 1):
				return True
		else:
			if (eval("self.matches_" + source + "[0][1]") >= match_threshold):
				return True
		return False

	def print_list_matches(self, source):
		for x in eval("self.matches_" + source):
			print("{:<20}".format(x[0].school_name) + "\t" + str(x[1]))

	# Sorts all lists on score (item[1]) - highest similarity score first
	# Only keeps first 5 elements in the list 
	def sort_lists(self, source):
		# ex: self.matches_espn.sort(reverse = True, key=lambda tup: tup[1])
		eval("self.matches_" + source + ".sort(reverse = True, key=lambda tup: tup[1])")

		if (source == "sportsref"):
			self.matches_sportsref = self.matches_sportsref[:10]

		if (source == "ncaa"):
			self.matches_ncaa = self.matches_ncaa[:10]

		if (source == "espn"):
			self.matches_espn = self.matches_espn[:10]

		elif (source == "247"):
			self.matches_247 = self.matches_247[:10]

		elif (source == "rivals"):
			self.matches_rivals = self.matches_rivals[:10]


