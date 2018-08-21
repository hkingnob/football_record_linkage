"""
This pulls data from rivals and puts it into a CSV file
The data is actually coming from the textfile rivals.com_teams,
 which is the selection of text that contains team information from
 https://cdn.rivals.com/production/assets/application-293541f419d34b2b48fd8ae6f3c9cc688b7f8c24ae2bc66ea5a35e2dd177f877.js
 (a link from the resources section of https://n.rivals.com/team_rankings/2018/all-teams/football.html)

output: CSV file with list of school_name and their links
 		list of tuples with school_names and links

June 11, 2018

Bugs: One concern is that the number of teams outputted is 122, 22 more than
		what appeared on the orignial college football site. Additionally, not
		all the teams are college football fbs (or even football) (ex: Juco Basketball)

Runtime: immediate

"""

import csv
import re 		#regular expression
import sys

csv_file = open('results_rivals.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['school_name', 'link'])


teams_file = open("rivals.com_teams.txt", 'r')
teams = teams_file.read()

teams_list = re.findall('{title:\"([A-Za-z ]+)\",link:\"(//[a-z]+\.rivals\.com)\"}', teams)

for team in teams_list:
	csv_writer.writerow([team[0], team[1]])


csv_file.close()
teams_file.close()
