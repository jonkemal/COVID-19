#!/usr/bin/env python3

####################################################################
#                 Covid-19 Data Visualization Tool                 # 
#        Compute covid 19 statistics for specified regions.        #
#                     Author: Jonathan Kemal                       #
#                                                                  #
#  Some simple unit tests for the core functions of the program.   #
####################################################################

import unittest
from os.path import join

from src.data_functions import CovidData

class TestInputsAndRequests(unittest.TestCase):
    # Use locations for files
    covid_data_path = join('input', 'us-counties-live.csv')
    geo_path = join('input', 'geocodes.csv')

    # Create and load data object for tests.
    data = CovidData(covid_data_path, geo_path, None)

    # Test a made up county.
    def test_madeup_county(self):
        state = "CA"
        county = "Notreal"
        request = {'county': county, 'state': state, 'distance': 100.0}
        try:
            self.data.compute_stats(request, "cases")
        except Exception:
            self.assertRaises(ValueError)

    # Test a madeup state.
    def test_madeup_state(self):
        state = "CAJON"
        county = "Notreal"
        request = {'county': county, 'state': state, 'distance': 100.0}
        try:
            self.data.compute_stats(request, "cases")
        except Exception:
            self.assertRaises(ValueError)

    # Test the result for Alameda county within 30 miles.
    # Should return 4 counties
    # Should return population of 3873655
    def test_alameda(self):
        state = "CA"
        county = "Alameda"
        request = {'county': county, 'state': state, 'distance': 30.0}
        result = self.data.compute_stats(request, "cases")
        self.assertEqual(len(result['counties']), 4)
        self.assertEqual(result['population'], 3873655)
        

if __name__ == '__main__':
    unittest.main()
