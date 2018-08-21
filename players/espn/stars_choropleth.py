"""
This creates a plotly choropleth based on the number of stars
given awarded to recruits from a given county.

"""

import sqlite3
import plotly.plotly as py 
import plotly
import plotly.figure_factory as ff 

colorscale = [
    'rgb(193, 193, 193)',
    'rgb(239,239,239)',
    'rgb(195, 196, 222)',
    'rgb(144,148,194)',
    'rgb(101,104,168)',
    'rgb(65, 53, 132)'
]

conn = sqlite3.connect('stars_per_county.db')		# connects to database
cur = conn.cursor()

# CONVERT STAR AND FIPS VALUES TO LIST
values = cur.execute("""SELECT total_stars FROM full_stars_per_county""").fetchall()
fips = cur.execute("""SELECT fips FROM full_stars_per_county""").fetchall()

list_values = []
list_fips = []

for tup in values:
	list_values.append(tup[0])

for tup in fips:
	list_fips.append(tup[0])

# fips = ["12011","06037","48201"]
# values = [4, 8, 69]

# print(values)
binning_endpoints=[5, 10, 80, 200, 800]

fig = ff.create_choropleth(fips=list_fips, values=list_values, binning_endpoints=binning_endpoints, colorscale=colorscale, legend_title="Aggregate ESPN Recruit Stars", title="Total Stars per County 2006-2018")
plotly.offline.plot(fig, filename='full_stars_county.html')

cur.close()