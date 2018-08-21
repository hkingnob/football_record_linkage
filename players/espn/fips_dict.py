"""
This populates a dictionary of all the fips/county pairs in the US

Code from (and much love to): https://gist.github.com/cjwinchester/a8ff5dee9c07d161bdf4

"""

import requests
import csv
import json

# Creates a dict of FIPS codes (keys) of U.S. counties (values)
fips_dict = {}
r = requests.get("http://www2.census.gov/geo/docs/reference/codes/files/national_county.txt")
reader = csv.reader(r.text.splitlines(), delimiter=',')    
for line in reader:
    fips_dict[line[3].replace(" County","")] = line[1] + line[2] 
