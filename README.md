####################################################################
#                 Covid-19 Data Visualization Tool                 #
#                     Author: Jonathan Kemal                       #
####################################################################

### General Information

This is a small project meant to visualize COVID 19 data over specified regions.
Specifically, it will compute and display the number of a specified statistic (eg. cases, deaths..) within a specifed range of a selected county (in miles).

Example: Find all cases within 100 miles of Alameda, CA.

The user will provide a list of requests as input in a csv format.
The program will compute all the requested calculations and display them on the same plot.

Two types of plots are produced as output:
1) Raw totals of the statistic in the specified ranges (eg. total case counts)
2) The densities of the statistic in the specified ranges (eg. deaths per 100,000 people)

The plots visualize the results by color-coding every county that lies within a specified request.
Example: Every county wthin 100 miles of Alameda, CA will be lit up based on the FIPS.

### Inputs

This is a command line tool. The primary inputs are:

REQUIRED:
1) A path to the NY times covid data for each county (csv).
This can be either the live version (that specifies only the latest data)
or the "all" version which specifies totals for every day since the beginning of the pandemic.
NOTE: Examples found at input/us-counties-all.csv and input/us-counties-live.csv
Source: https://github.com/nytimes/covid-19-data

2) A path to the Healthcare.gov geocidies csv for reach county (csv). This is used to find the lat/long etc. for a given county.
Note: Example found at input/geocodes.csv
Source: https://data.healthcare.gov/dataset/Geocodes-USA-with-Counties/52wv-g36k/data

3) Type of statistic to find information about.

4) Path to input csv of requests to process.
The format of the input csv is:
#County,State,distance_in_miles
Note: Distance in miles must be < 1000.0 miles.
Note: Example in input/example_input.csv

OPTIONAL
5) Target Date: If you want to see results for a specific date in the past, you can specify a target date here.
This is useful when using the input csv that contains data for ALL dates instead of just the live version.
Note: statistics in the 'all' version are currently limited to cases and deaths.
Note: If this is not selected, the most recent date will be used.

6) Save Path: If you want to save the images to a path instead of outputting them to the screen, use this.

Example usage output:
% python3 run.py -I input/example1.csv -S cases --save-path output -h
usage: run.py [-h] [-D counties_data] [-G geocodes] [-T target_date] [--save-path save_path] -S statistic -I input_path

Visualize COVID-19 data for specified region.

optional arguments:
  -h, --help            show this help message and exit
  -D counties_data, --counties-data counties_data
                        Path to csv containing NY Times counties data. (default: input/us-counties-live.csv)
  -G geocodes, --geocodes geocodes
                        Path to Healthcare.gov data for US county geocodes. (default: input/geocodes.csv)
  -T target_date, --target-date target_date
                        Target date in yyyy-mm-dd format. (default: None)
  --save-path save_path
                        Optional path to save figures to. Format will be stat_type_plot_type.png (default: None)
  -S statistic, --statistic statistic
                        Statistic to analyze (eg. cases, deaths). (default: None)
  -I input_path, --input input_path
                        Path to input csv file. (default: None)

### Outputs
1) A plot of the raw total of a statistic over a list of specified regions.
2) A plot of the population density (stat/100000 people) over a list of specified regions.
Notes: Examples are found in:
example_output/cases_totals.png
example_output/cases_density.png
example_output/deaths_totals.png
example_output/deaths_density.png
These can be displayed to the screen instead of saved if requested.

### Installation:
In order to use the plotly plotting functions, some libraries need to be installed.
This installation should be straightforward using pip or conda

Specifically:

Using pip/pip3:
To create plots:
!pip install geopandas==0.3.0
!pip install pyshp==1.2.10
!pip install shapely==1.6.3

And to save the figures to the disk:
!pip install -U kaleido

Or Using conda:
conda install plotly
conda install geopandas

Disclaimer: I used the pip3 installation, I have not tested this with the conda approach.
More details from plotly documentation:
https://plotly.com/python/county-choropleth/
https://plotly.com/python/static-image-export/

### Assumptions and edge cases:

1) Counties of the same name exist across different states, so the internal database structures
   are organized first by state and then by county name.

2) The two databases do not always include the same counties.
  i) If a county is not located in the geolocations database, meaning a lat/long cannot be determined, it is treated as a fatal error.
  ii) If a county IS in the geolocations database but has no data in the covid19 database, that is okay. The code will continue accumulating information
      from other counties within the specified range of the county, even if that particular county isn't found.

3) The geolocations database actually occurs entries for each city in a county. Each city has different lat/long coordinates, as well as
   entries for the population. However, the covid19 database is for specific counties. This means a decision has to be made about which
   lat/long coordinates should be used to represent the county. I have done two things here:
   i) Keep track of the TOTAL estimaed population for every city in the county
   ii) Use the lat/lon of the most populated city in the county as the lan/lon for the county. This might not be perfectly fair, but I believe is
       sufficient for the purposes of this project.

4) I have made some assumptions regarding the formats of the csv input files.
   i) For the NY Times covid data, I assume the first 4 columns will be ['date', 'county', 'state', 'fips'].
      The types of available statistics are the elements that come aver this in the header line.
      This leaves flexibility if new types of statitics are added to these databases later.
   ii) For the Healthcare.gov geocities input file, I made some stick assumptions about which columns would
       contain the necessary data (state, county, lat, long). The assumption here is that this file will not
       change on a regular basis and the format can more or less be considered constant.
 
5) If a county name is not present, it is skipped (some counties are without names).

### Other Notes
1) To calculate the distance between coounties based on lat/long, I used the haversine formula.
   I grabbed code to do this from a public source and modified it slightly.
   Author: Wayne Dyck
   Link: https://gist.github.com/rochacbruno/2883505
2) I grabbed a public python dictionary to look up state abbreviations from state names. This was useful
   Author: Roger Allen
   Link: https://gist.github.com/rogerallen/1583593

### Future work/ideas
1) I would love to implement calculations based on date ranges, not merely the target date.
   For example, using the 'all' file as input, the code could compute the number of new cases each day within a date range.
   Then plots could be created showing how cases are rising/dropping over specified date ranges - all within the same specified distances
   from a source county. Publicly available data tends to be for specific states, counties, cities, etc. This would allow you to create similar
   spots within any mile range you want (under 1000 [miles]) from a specified US county.

2) Automatically download datasets (should be easy with python requests)

3) Improve the plots! Explore better color schemes, legend styles, output county names, etc.
   There are many ideas but the time/scope of this project is limited.

4) Some more in depth and clever unit tests would be nice!
