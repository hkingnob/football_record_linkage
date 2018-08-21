"""

Scrapes sportsreference for college football player data and exports data to sqlit3 table
total of 47923 players
7/11/18

"""

import requests
import sqlite3
from bs4 import BeautifulSoup

conn = sqlite3.connect("players_sportsref_full.db")
cur = conn.cursor()

url = "https://www.sports-reference.com/cfb/play-index/pgl_finder.cgi?request=1&match=career&offset="
done = False
offset = 47923//100*100			# last seen number 

while not done:
	r = requests.get(url + str(offset))
	if (r.status_code == 404):
		continue
	soup = BeautifulSoup(r.content, 'lxml')
	table = soup.find("body").find("tbody")
	if (not table):
		continue

	for player in table.find_all('tr', attrs={'class':False}):		# for each non-header row
		row = player.find('th').text
		print(row)
		name = player.find('a').text
		year_start = player.find(attrs={'data-stat':"year_min"}).text
		year_end = player.find(attrs={'data-stat':"year_max"}).text
		school = player.find(attrs={'data-stat':"school_name"}).text
		career_wins = player.find(attrs={'data-stat':"wins"}).text
		career_losses = player.find(attrs={'data-stat':"losses"}).text
		games_played = player.find(attrs={'data-stat':"counter"}).text
		link = player.find('a')['href']

		# add in player stats to sqlite3 table. we could add player_page stats later
		cur.execute("INSERT INTO players_sportsref VALUES (?,?,?,?,?,?,?,?,?)", (row,name,year_start,year_end,school,career_wins,career_losses,games_played,link))
	
		conn.commit()
	offset += 100

conn.close()