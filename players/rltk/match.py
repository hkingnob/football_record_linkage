"""
Match class: school from a particular source with data from that source as attributes

June 19, 2018
"""

import states	# dictionary of states abbreviations and names in this directory
import re 		# regex library

class match:

	# Source - a string specifying which source the school comes from
	# Row - list with all the school's attributes
	def __init__(self, source, row):
		self.source = source

		self.school_name = row[0]	# ex: "Clemson"
		self.representation = ""	# ex: "Clemson Tigers Tigers"
		self.link = ""				# ex: "/cfb/schools/clemson/2017.html"
		self.link_name = ""			# ex: "clemson"
		self.name_mascot = ""		# ex: "Clemson Tigers"
		self.mascot = ""			# ex: "Tigers"
		self.espn_id = ""			# ex: "228"
		self.link_abbrev = ""		# ex: "CLEM"

		if (source == "sportsref"):
			self.attributes = ["link", "link_name", "name_mascot", "mascot"]
			self.link = row[1]
			self.link_name = row[2]
			self.name_mascot = row[3]
			self.mascot = row[4]

		if (source == "ncaa"):
			self.attributes = ["link", "name_mascot", "mascot", "ncaa_id"]
			self.link = row[2]
			self.name_mascot = row[3]
			self.mascot = row[4]
			self.ncaa_id = row[1]

		elif (source == "espn"):
			self.attributes = ["link", "link_name", "name_mascot", "mascot", "espn_id"]
			self.link = row[2]
			self.link_name = row[3]
			self.name_mascot = row[4]
			self.mascot = row[5]
			self.espn_id = row[1]

		elif (source == "247"):
			self.attributes = ["link", "link_abbrev", "link_name", "name_mascot", "mascot"]
			self.link = row[1]
			self.link_abbrev = row[2]
			self.link_name = row[3]
			self.name_mascot = row[0] + " " + row[5]	# row[0] (school_name) tends to be more completed, while row[4] is often an abbreviation
			self.mascot = row[5]

		elif (source == "rivals"):
			self.attributes = ["link"]
			self.link = row[1]
			self.name_mascot = self.school_name

		self.representation = self.get_representation()

	# Returns the string representation that will be used for the record linkage comparison
	def get_representation(self):
		if (self.source == "rivals"):
			self.representation = self.school_name
			# Note: The only scrapable data on this site was the link.
			# Given that it also has many more schools than just in the FBS, it's
			#	record linkage results will be very poor.

		else:
			# some normalization - change state abbreviation to full name
			for abbrev in re.findall("[\w\.]+", self.name_mascot):		# regex - only letters
				if len(abbrev) == 2 or abbrev == "St.":			# if first term in list is abbreviation
					for item in states.us_state_abbrev.items():
						if abbrev == item[1]:
							self.name_mascot = self.name_mascot.replace(abbrev, item[0])
							break
			self.representation = self.name_mascot + self.mascot

		return self.representation





