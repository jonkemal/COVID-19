#!/usr/bin/env python3

####################################################################
#                 Covid-19 Data Visualization Tool                 #
#                     Author: Jonathan Kemal                       #
#                Plotting/visualization functions.                 #
#               Inspired by and modified versions of:              #
#     https://plotly.com/python/county-choropleth/ (thanks!)       #
####################################################################
from datetime import date
from os.path import join

import plotly.figure_factory as ff

# This funciton will plot all requests atop one US map.
# Every county int he specified range for each request will
# be set to a color associated with the number of cases

# Two plots will be made: One for raw totals, one for population densities.
def plot_results(results: list, stat: str,
                 target_date: date, save_path: str) -> None:

    # Will use 5 bins and this color scheme.
    colorscale = ["#b7e0e4", "#b7e0e4", "#4989bc",
                  "#3d4b94", "#1d1d3b", "#030512"]
                  

    # What will ultimatedly be plotted: fips for each county in each range,
    # and the values (e.g. total cases in region).
    fips = []
    values = []

    # Create/slow the raw total plot.
    
    # Keep track of biggest value of stat to use for bin creation
    biggest_stat_value = 0
    for result in results:
        biggest_stat_value = max(biggest_stat_value, result['stat_total'])
        fips.extend(result['fips'])
        values.extend([result['stat_total']]*len(result['fips']))
    
    # Calculate bin size based on largest value in set
    bin_size = biggest_stat_value//5
    total_bins = [0]*5
    for i in range(5):
        total_bins[i] = (i + 1)*bin_size

    # If we specified a target date, output it on the title!
    if target_date:
        title = 'Total number of %s within specified distance of counties on %s' %(stat, target_date)
    else:
        title = 'Total number of %s within specified distance of counties for latest date.' %stat
        
    fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=total_bins, colorscale=colorscale,
    county_outline={'color': 'rgb(255,255,255)', 'width': 1.0}, round_legend_values=True,
    legend_title='Total number of %s' %stat,
    title=title)
    fig.layout.template = None

    # If save path selected, save file. Otherwise output to screen.
    if save_path:
        full_save_path = join(save_path, '%s_totals.png' %stat)
        print("Saving total stat figure to: %s" %full_save_path)
        fig.write_image(full_save_path)
    else:
        fig.show()

    # ===========
    # Create and show the densities plot.
    fips = []
    values = []

    # Create/slow the raw total plot.
    
    # Keep track of biggest value of stat density
    # meaning devided by population
    # All population densities will be per 100,000 people
    biggest_stat_density = 0.0
    for result in results:
        biggest_stat_density = max(biggest_stat_density, 100000.0*float(result['stat_total']/result['population']))
        fips.extend(result['fips'])
        values.extend([100000.0*float(result['stat_total']/result['population'])]*len(result['fips']))


    # Calculate bin size based on largest value in set
    bin_size = biggest_stat_density//5
    total_bins = [0]*5
    for i in range(5):
        total_bins[i] = (i + 1)*bin_size

    # If we specified a target date, output it on the title!
    if target_date:
        title = 'Number of %s per 100k people within specified distance of counties on %s' %(stat, target_date)
    else:
        title = 'Number of %s per 100k people within specified distance of counties for latest date.' %stat
        
    fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=total_bins, colorscale=colorscale,
    county_outline={'color': 'rgb(255,255,255)', 'width': 1.0}, round_legend_values=True,
    legend_title='Total number of %s' %stat,
    title=title)
    fig.layout.template = None
    # If save path selected, save file. Otherwise output to screen.
    if save_path:
        full_save_path = join(save_path, '%s_density.png' %stat)
        print("Saving desnity stat figure to: %s" %full_save_path)
        fig.write_image(full_save_path)
    else:
        fig.show()

    
