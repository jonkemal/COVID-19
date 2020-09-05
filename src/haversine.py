#!/usr/bin/env python3

####################################################################
#                 Covid-19 Data Visualization Tool                 #
# Haversine formula to calculate the great-circle distance between #
#         two locations based on their lat/long coordinates.       #
#     Borrowed from Wayne Duck's public github repo (thanks!)      #
####################################################################

# Haversine formula example in Python
# Author: Wayne Dyck
# Link: https://gist.github.com/rochacbruno/2883505

import math

def haversine(origin: tuple, destination: tuple) -> float:
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    # Currently d is in km. We want it in miles
    return d/1.60934 # 1.60934 [km/mi]
