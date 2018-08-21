#!/bin/bash

# Runs all the scraper scripts in the sportsref, espn, 247, rivals, and ncaa directories

cd sportsref
python3 scraper_sportsref.py

cd ../espn
python3 scraper_espn.py

cd ../247
python3 scraper_247.py

cd ../rivals
python3 scraper_rivals.py

cd ../ncaa
python3 scraper_ncaa.py
