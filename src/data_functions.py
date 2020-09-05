#!/usr/bin/env python3

####################################################################
#                 Covid-19 Data Visualization Tool                 #
#                     Author: Jonathan Kemal                       #
#    Functions related to loading and processing COVID-19 data.    #
####################################################################

from datetime import date

from os.path import exists

from src.us_states import us_state_abbrev
from src.haversine import haversine

# Covid-19 Data class.
# Will handle verifying and loading input data.
# Will also include functions for basic calculations.
class CovidData:

    # Dictionary for storing NY times COVID19 counties data.
    covid_dict = {}

    # Dictionary for storing lon/lat of every county in US.
    # From Healthcare.gov dataset
    geo_dict = {}

    # List of first 4 columns expected in the counties data input file.
    # This will be verified with the header line from the input file.
    # The remaining column names will be considered the valid statistic types
    # that the user can request from this data file.

    # Note: This is done because the "live" vs "all" versions of the NY Times
    # data inputs contain different column names/stat types, and I want the
    # code to be more general in case new types of statistics are added later.
    # However, the assumption of the first 4 cols is hard coded (for now).
    counties_data_types = ['date', 'county', 'state', 'fips']
    num_fixed_types = len(counties_data_types)

    # List of geocode column names for verification purposes.
    # As above, derived from header line.
    geo_data_types = ['zip', 'primary_city', 'state', 'latitude', 'longitude',
                      'county', 'type', 'world_region', 'country',
                      'decommissioned', 'estimated_population', 'notes']

    def __init__(self, counties_path: str, geocodes_path:str,
                 target_date: date) -> None:

        # Load counties and geocode data.
        self.counties_path = counties_path
        self.geocodes_path = geocodes_path

        # Load target date:
        self.target_date = target_date

        # Will need a list of statistics names
        self.stat_names = []

        # Load counties and geo locations data.
        self.load_counties_data()
        self.load_geocodes_data()

    # Function to load and verify counties data.
    def load_counties_data(self) -> None:
        # If input path does not exist, raise fatal error (for now).
        # Future work: If file is missing, attempt to download automatically
        # using python requests library.
        if not exists(self.counties_path):
            raise RuntimeError("Error: Counties data file %s not found." %self.counties_path)

        # The input could be the NY times file containing all data, which
        # has limited statistic types, or the live version which has more
        # statistics.
        # As this file could (in thoery) be quite large, will read through it line by line
        with open(self.counties_path, 'r') as f:
            # Read the first line (header)
            line = f.readline()
            linenum = 1

            # Validate header and obtain types of statistics
            self.stat_names = self.validate_header(line, self.counties_data_types)
            # Read the rest of the file line by line.
            while line:
                line = f.readline()

                # Load line data into dictionary based on expected
                # and validated format.
                line_data = line.rstrip().split(',')

                # If there are not the expected number of comma-separated
                # entries, output error and skip the line:
                if len(line_data) != self.num_fixed_types + len(self.stat_names):
                    print("Warning: Incomplete data for line #%d" %linenum)
                    print("Skipping line: %s" %line)
                    linenum += 1
                    continue

                # If a target date was selected, compute the
                # current date as datetime object for comparison:
                if self.target_date:
                    year, month, day = line_data[0].split('-')
                    current_date = date(int(year), int(month), int(day))
                else:
                    current_date = None

                # If target date is slected, current date must be the target
                # or we skip the line.
                # If target date is NOT selected, we continue to process the
                # data under the assumption that only data for the
                # most recent date in the dataset is to be used.
                
                # NOTE: Each row of data contains the TOTAL of each statistic
                # for that date, NOT the contribution of that date.
                # Example: The number of cases on a date will always be >= the
                # number of cases for a previous date.
                # The dates are assumed to be in decending chronological order.
                
                # If there are multiple entries for a county, with no target
                # date selected, the most recent entry (corresponds to the
                # most recent date) will be added into the database. This should
                # not happen if the code is properly used and a warning will be
                # displayed.
                if self.target_date and current_date != self.target_date:
                    linenum += 1
                    continue

                # Assumptions of columns of these data.
                # Use map of state names to abbreviations imported above
                # to store the abbreviated state name internally.
                # (This is to be consistent with geo data set).
                county = line_data[1]
                state = us_state_abbrev[line_data[2]]
                fips = line_data[3]

                # Add to data dict by state.
                if not state in self.covid_dict:
                    self.covid_dict[state] = {}


                # If county hasn't been added yet, initialize it with
                # the fips value.
                if not county in self.covid_dict[state]:
                    self.covid_dict[state][county] = {'fips': fips}
                else:
                    # This shouldn't happen if code is properly used
                    # as it corresponds to a county already being added
                    # from an earlier date. Output warning and replace.
                    print("Warning: Data for %s/%s already loaded." %(
                           county, state))
                    print("Replacing with data for date: %s" %line_data[0])
                    self.covid_dict[state][county]['fips'] = fips

                # Loop over remaining statistics
                for i, stat in enumerate(self.stat_names):
                    # Value should be an integer.
                    # Will treat empty string (missing data) as 0.
                    value = line_data[i + self.num_fixed_types]
                    if not value:
                        value = 0
                    else:
                        value = int(value)
                    # Enter value for the stat name
                    self.covid_dict[state][county][stat] = value

                # Increment line num
                linenum += 1

    # Function to load and verify geocodes (lon/lat) data for each county.
    def load_geocodes_data(self) -> None:
        # If path does not exist, raise fatal error (for now).
        # Future work: If file is missing, attempt to download automatically
        # using python requests library.
        if not exists(self.counties_path):
            raise RuntimeError("Error: Geocodes data file %s not found." %self.counties_path)

        # Read through it line by line
        # Note: Will make some assumptions about the format of this csv file
        # In terms of the column numbers of the data we actually want.
        # Specifically: state, county, lat/lon, and estimated population
        # Given the nature of what this file repsents, I am assuming the
        # structure and content of this file should not change frequently.
        with open(self.geocodes_path, 'r') as f:
            # Read the first line (header)
            line = f.readline()
            linenum = 1

            # Read the rest of the file line by line.
            while line:
                line = f.readline()

                # Load line data into dictionary based on expected
                # and validated format.
                line_data = line.rstrip().split(',')

                # If there are not at least the expected number of colums,
                # Output a warning and skip the line.
                # Note: with this file, sometimes the data in the note columns
                # include commas, which result in more elements when split.
                # However, this should not affect our assumptions below.
                if len(line_data) < len(self.geo_data_types):
                    print("Warning: Incomplete data for line #%d" %linenum)
                    print("Skipping line: %s" %line)
                    linenum += 1
                    continue

                # Assumptions of where data is, make sure to store population
                # as an int and lat/lon as float.
                state = line_data[2]
                county = line_data[5]
                lat = float(line_data[3])
                lon = float(line_data[4])
                population = int(line_data[10])

                # The data in this file is actually for specific cities, so
                # there are often multiple entries per county.
                # However, each city has slightly different lat/lon cordinates
                # To choose which lat/lon to consider for the county, I will
                # keep track of the city with the highest estimated population.

                # Add to data dict by state.
                if not state in self.geo_dict:
                    self.geo_dict[state] = {}


                # If county hasn't been added yet, initalize it with above data.
                if not county in self.geo_dict[state]:
                    self.geo_dict[state][county] = {'lat': lat, 'lon': lon,
                                                    'population': population,
                                                    'largest_city': population}
                else:
                    # Otherwise:
                    # 1) Add current city population to total
                    # 2) If current population is larger than previous city max,
                    # update lat/lon and set a new largest_city population.
                    self.geo_dict[state][county]['population'] += population
                    if population > self.geo_dict[state][county]['largest_city']:
                        self.geo_dict[state][county]['lat'] = lat
                        self.geo_dict[state][county]['lon'] = lon
                        self.geo_dict[state][county]['largest_city'] = population
                        
                linenum += 1
                
    # Validate counties data header info
    def validate_header(self, header: str, data_names: list) ->None:

        # Compare each column of csv's name to expected value
        # based on counties_data_types above.
        # rstrip removes trailing newline character.
        data_types = header.rstrip().split(',')

        # If the first 4 columns are not as expected, throw an error.
        for i in range(self.num_fixed_types):
            if data_types[i].lower() != self.counties_data_types[i]:
                raise ValueError("Error: Column name %s does not match %s"
                                 %(data_types[i], self.counties_data_types[i]))

        # Return remaining data types.
        # This will serve as names of valid statistics for this input file.
        return data_types[self.num_fixed_types:]

    # Function to compute number of statistics within user selected range
    def compute_stats(self, request: dict, stat: str) -> dict:
        # Items of the request
        state = request['state']
        county = request['county']
        distance = request['distance']

        # If stat is not found in the previously computed list of
        # raise error.
        if stat not in self.stat_names:
            raise ValueError("Error: "
                             "Statistic %s not found in data inputs." %stat)
        print("Finding number of %s within %.2f [mi] for %s %s" %(stat, distance, county, state))

        # Results dictionary to return storing relevant information.
        # 1) statistic total
        # 2) population total
        # 3) statistic type
        # 3) counties in region
        # 4) fips for each county in region
        # 5) lat/lon for target county
        # 6) State/name of target county
        result = {'state': state, 'county': county,
                  'fips': list(), 'counties': list(),
                  'stat': stat, 'population': 0,
                  'stat_total': 0}

        # Verify state abbreviation is valid.
        if not state in self.geo_dict:
            raise ValueError("State %s not found in location data. " %state)

        # Verify that county is found in the state.
        if not county in self.geo_dict[state]:
            raise ValueError("County %s not found in state %s" %(county, state))

        # Store origin lat/lon coordinates:
        origin = (self.geo_dict[state][county]['lat'],
                  self.geo_dict[state][county]['lon'])
        result['cords'] = origin
        
        # Loop over each county in each state and compute haversine distance.
        for new_state in self.geo_dict:
            for new_county in self.geo_dict[new_state]:

                # Count entries in the geo database do not have names for
                # the county. I will skip these for now.
                if not new_county:
                    continue
                
                point = (self.geo_dict[new_state][new_county]['lat'],
                         self.geo_dict[new_state][new_county]['lon'])

                # Get distance between counties in miles
                dist = haversine(origin, point)

                # If distance is <= the inputted range
                # AND the county is in the NY times counties database
                # then add the stats info.
                
                # NOTE: It's okay if a county exists in the geo database but not
                # in the counties database. We'll just skip it.
                # However, if the county is not in the geo database, and lat/lon
                # cannot be determined, this is an error (as above).
                if dist <= distance and new_county in self.covid_dict[new_state]:
                    print("Dist between %s/%s in and %s/%s is %.2f [miles]" %(county, state, new_county, new_state, dist))
                    print("Adding %d cases to %d from %s/%s" %(self.covid_dict[new_state][new_county][stat], result['stat_total'], new_county, new_state))
                    result['stat_total'] += self.covid_dict[new_state][new_county][stat]
                    result['population'] += self.geo_dict[new_state][new_county]['population']
                    result['counties'].append((new_county, new_state))
                    result['fips'].append(self.covid_dict[new_state][new_county]['fips'])

        print("In total there are %d %s within %.2f [miles] of %s/%s, a region with %d people." %(
              result['stat_total'], stat, distance, county, state, result['population']))
        return result
