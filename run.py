#!/usr/bin/env python3

####################################################################
#                 Covid-19 Data Visualization Tool                 # 
#        Compute covid 19 statistics for specified regions.        #
#                     Author: Jonathan Kemal                       #
#                                                                  #
#       Input: NY Times Covid-19 data per county.                  #
#              Healthcare.gov list of locations of US counties.    #
####################################################################

import argparse
from datetime import date
from os.path import abspath, exists, join
from os import makedirs

from src.data_functions import CovidData
from src.plotting import plot_results

# Function that processes input csv and generates list of rquests.
def get_requests(input_path: str) -> list:

    # Read input csv and store data in internal list.
    # If it does not exist, fatal error.
    if not exists(input_path):
        raise RuntimeError("Input file does not exist: %s" %input_path)

    # Read each line and store requests info in dictionary.
    requests = []
    with open(input_path, 'r') as f:
        # Skip header:
        line = f.readline()
        line = f.readline().rstrip()
        while line:
            try:
                county, state, dist = line.split(',')
                # Make sure distance is < 1000 miles as required.
                if float(dist) > 1000.0:
                    raise ValueError("Distance must be < 1000 [miles].")

                # Append result to list of dicts.
                requests.append({'state': state,
                                 'county': county,
                                 'distance': float(dist)})
            except Exception as err:
                raise RuntimeError("Invalid input data: %s" %err)
            line = f.readline().rstrip()
    return requests

# Main function
def main():
    
    # Argument parser for command line arguments.
    description = 'Visualize COVID-19 data for specified region.'
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=formatter_class)

    # Path to csv containing NY times COVID-19 data for US counties.
    # Use abspath to get full OS filepath at input (can avoid some errors).
    # Default is a path to the "live" version (input/us-counties-live.csv).
    parser.add_argument('-D', '--counties-data',
                        dest='counties_data',
                        action='store',
                        type=abspath,
                        metavar='counties_data',
                        default=join('input', 'us-counties-live.csv'),
                        help='Path to csv containing NY Times counties data.',
                        required=False)

    # Path to csv containing geocodes for each US county.
    parser.add_argument('-G', '--geocodes',
                        dest='geocodes',
                        action='store',
                        type=abspath,
                        metavar='geocodes',
                        default=join('input', 'geocodes.csv'),
                        help='Path to Healthcare.gov data for US county geocodes.',
                        required=False)

    # Optional target date. Will load counties statistics data only for the
    # specified date. The "all" data version of the input file contains data
    # for every date since early march.
    parser.add_argument('-T', '--target-date',
                        dest='target_date',
                        action='store',
                        type=str,
                        metavar='target_date',
                        default=None,
                        help='Target date in yyyy-mm-dd format.',
                        required=False)

    # Optional path to save figures to.
    parser.add_argument('--save-path',
                        dest='save_path',
                        action='store',
                        type=abspath,
                        metavar='save_path',
                        default=None,
                        help='Optional path to save figures to. '
                              'Format will be stat_type_plot_type.png',
                        required=False)

    # Required type of statistic to analyze.
    # Much match a column in the NY times COVID-19 counties database.
    parser.add_argument('-S', '--statistic',
                        dest='statistic',
                        action='store',
                        type=str,
                        metavar='statistic',
                        default=None,
                        help='Statistic to analyze (eg. cases, deaths).',
                        required=True)
    
    # Required path to input csv file that specifies data search requests.
    # Each row will be of the format: county,state,miles
    parser.add_argument('-I', '--input',
                        dest='input_path',
                        action='store',
                        type=abspath,
                        metavar='input_path',
                        default=None,
                        help='Path to input csv file.',
                        required=True)
    
    # Parse the command line arguments.
    args = parser.parse_args()

    # If output path for images does not exist, make the dir
    if args.save_path:
        if not exists(args.save_path):
            makedirs(args.save_path)
    
    # If selected, convert target date to python datetime object.
    # If invalid entry, throw an error.
    if args.target_date:
        try:
            year, month, day = args.target_date.split('-')
            target_date = date(int(year), int(month), int(day))
        except Exception as err:
            print("Error: %s" %err)
            raise ValueError("Invalid Target date: %s" %args.target_date)
    else:
        target_date = None

    # Get list of requests
    requests = get_requests(args.input_path)
    
    # Create COVID-19 Data object and load data from csv files.
    data = CovidData(args.counties_data, args.geocodes,
                     target_date)

    # For each request obtained from the input file, calculate the
    # results and append it to a list of results
    results = []
    for request in requests:
        results.append(data.compute_stats(request, args.statistic))

    # Plot result using plotly county-choropleth
    plot_results(results, args.statistic, target_date, args.save_path)
    

if __name__ == '__main__':
        main()
