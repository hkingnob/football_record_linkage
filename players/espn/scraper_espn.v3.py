"""
v3 updates:
	now stores data from individual team page (see below)
	should be robust enough to take most forms of incomplete data

This scrapes player recruit data from the ESPN database on
  http://www.espn.com/college-sports/football/recruiting/database
And stores it in a SQL Lite 3 database

June 27, 2018

Data to scrape:
	name_first
	name_last
	hometown
	home_state
	high_school
	position
	position_rank
	stars
	grade
	year

inividual team page:
	ID
	link_name
	height
	weight
	forty
	signed_school

"""

import requests
import sys
import re
import sqlite3
from bs4 import BeautifulSoup

# CREATE SQLITE DATABASE
conn = sqlite3.connect('players_espn_full.db')	# opens connection
cur = conn.cursor()							# instantiates a cursor


for year in ["2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020"]:
# for year in ["2015","2016","2017","2018","2019","2020"]:
	# year = "2018"
	url = re.sub("class/[0-9]{4}", "class/"+year, "http://www.espn.com/college-sports/football/recruiting/databaseresults/_/page/1/sportid/24/class/2020/starsfilter/GT/ratingfilter/GT/statuscommit/Commitments/statusuncommit/Uncommited")
	print("\n" + year)
	in_current_year = True
	page = 1
	if (year == "2015"):
		page = 88

	while (in_current_year):		# for each page

		print(str(page), end='\t', flush=True)

		url = re.sub("_/page/[0-9]+", "_/page/"+str(page), url)
		r = requests.get(url)
		if (r.status_code == 404):
			print("Bad Page 404")
			in_current_year = False
			continue
		soup = BeautifulSoup(r.content, "lxml")

		first_row = True
		table = soup.find(id="DatabaseSearch", class_="mod-tabbed-content mod-container mod-tabs bg-opaque pad-16 article")

		if (not table):			# if it's not showing up for whatever reason
			continue

		players = table.find_all('tr')
		if (len(players) == 2):			# by default there are 2 tr tags
			in_current_year = False
		for player in players:		# FOR PLAYERS IN YEAR
			
			# set everything equal to None, and if it's there change it
			city_state = None
			hometown = None
			home_state = None
			high_school = None
			position = None
			position_rank = None
			stars = None
			grade = None
			ID = None
			link_name = None
			height = None
			weight = None
			forty = None
			signed_school = None

			try:						# If names aren't there, move on to next row (maybe header row)				
				name_first = player.strong.text.split()[0]
				# print(name_first, end='\t')
				name_last = " ".join(player.strong.text.split()[1:])
			except:
				continue

			# LOCATION DATA
			home_tag = str(player.find_all('td')[1])
			reg_city_state = re.search('<td>(.+)<br/>', home_tag)
			if (reg_city_state):
				city_state = reg_city_state.group(1)	# ex: Decatur, IL
				hometown = city_state.split(",")[0]
				try:
					home_state = city_state.split(",")[1].strip()
				except:		# occassionally an "IndexError"
					continue

			# HIGH_SCHOOL
			reg_school = re.search('<br/>(.*)</td>', home_tag)
			if (reg_school):
				high_school = reg_school.group(1)

			# POSITION
			if (len(player.find_all('td')) > 2):
				pos = str(player.find_all('td')[2].text)
				position = re.sub('#[0-9]+ ', '', pos)

			# POSITION_RANK
			reg_rank = re.search('([0-9]+) \w', pos)
			if (reg_rank):
				position_rank = reg_rank.group(1)

			# STARS
			string_stars = str(player.find('ul', class_="mod-rating"))
			reg_stars = re.search('li class="star (\w+)-star"', string_stars)
			if (reg_stars):
				string_stars = reg_stars.group(1)
				stars = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}.get(string_stars)

			# GRADE
			grade = player.find_all('td')
			if (len(grade) > 4):
				grade = player.find_all('td')[4].text		# probably not the smartest idea to just go off of indeces


			# PLAYER PAGE
			link_player = player.find('div', class_="name").find('a')
			# print(link_player)

			if (link_player):
				link_player = link_player['href']
				ID = re.search('id/([0-9]+)/', link_player).group(1)
				link_name = link_player.split("/")[-1]
				
				r = requests.get(link_player)
				if (r.status_code == 404):
					print("Bad Page 404")
					continue
				soup = BeautifulSoup(r.content, "lxml")
				bio_stats = soup.find('div', class_="bio")

				if (bio_stats):
					bio_stats = bio_stats.text
				
					height = bio_stats.split(',')
					if (height):
						height = height[0].strip()

					weight = re.search('\d, (\d{3}) | ', bio_stats)
					if (weight):
						weight = weight.group(1)

					forty = re.search('40: ([\d\.]+)', bio_stats)
					if (forty):
						forty = forty.group(1)

					position = re.search('Position([\w ]+)', bio_stats)
					if (position):
						position = position.group(1)

					signed_school = re.search('Signed ([\w &]+)', bio_stats)		# originally there was no " " or & in the regex pattern
					if (signed_school):
						signed_school = signed_school.group(1)

			# Insert into database
			cur.execute("INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (name_first, name_last, hometown, home_state, high_school, position, position_rank, stars, grade, year, ID, link_name, height, weight, forty, signed_school))
		
		page += 1
		conn.commit()		# commits at the end of every page - so if it fucks up, just start from the last displayed number in output

	# exit()	# then check the v3 database and see how the output is

conn.close()




