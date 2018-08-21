"""
This creates a plotly choropleth based on the number of stars per player
given awarded to recruits from a given county.

"""

import sqlite3
import plotly.plotly as py 
import plotly
import plotly.figure_factory as ff 

# colorscale = [
#     'rgb(193, 193, 193)',
#     'rgb(239,239,239)',
#     'rgb(195, 196, 222)',
#     'rgb(144,148,194)',
#     'rgb(101,104,168)',
#     'rgb(65, 53, 132)'
# ]

colorscale = [
    'rgb(193, 193, 193)',
    'rgb(144,148,194)',
    'rgb(65, 53, 132)'
]

conn = sqlite3.connect('stars_per_county.db')		# connects to database
cur = conn.cursor()

# CONVERT STAR AND FIPS VALUES TO LIST
player_recruit_threshold = 5			# minimum number of players to be shown on map
values = cur.execute("SELECT avg_stars_per_player FROM full_stars_per_county WHERE player_recruits>?", (player_recruit_threshold,)).fetchall()
fips = cur.execute("SELECT fips FROM full_stars_per_county WHERE player_recruits>?", (player_recruit_threshold,)).fetchall()

list_values = []
list_fips = []

for tup in values:
	list_values.append(tup[0])

for tup in fips:
	list_fips.append(tup[0])

# print(values)
# we're going from roughly 1.7 to 4
binning_endpoints=[2.5, 3]
# binning_endpoints=[2, 2.5, 2.75, 3, 3.5]
# binning_endpoints=[1.1,2.1,3.1,4.1]

fig = ff.create_choropleth(fips=list_fips, values=list_values, binning_endpoints=binning_endpoints, colorscale=colorscale, legend_title="Aggregate ESPN Recruit Stars", title="Average Stars per Player per County 2006-2018")
plotly.offline.plot(fig, filename='player_stars_county.html')

cur.close()