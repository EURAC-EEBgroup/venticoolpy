"""Test calculation functions."""

try:
    from vctlib.calculation import run_vct_simulation, get_climate_data_from_epw, \
        get_climate_data_from_csv, get_vent_mode_over_year, \
        get_requirend_frequency_air_change_rate, get_annual_data
    from vctlib.model import Building, ThermostaticalProperties
except ModuleNotFoundError:
    import sys
    sys.path.insert(1, '/home/osomova/Projects/vct/vctlib/src')
    from vctlib.model import Building, ThermostaticalProperties
    from vctlib.calculation import run_vct_simulation, get_climate_data_from_epw, \
        get_climate_data_from_csv, get_vent_mode_over_year, \
        get_requirend_frequency_air_change_rate, get_annual_data


import pandas as pd

__author__ = "OlgaSomova"
__copyright__ = "OlgaSomova"
__license__ = "MIT"



def test_get_climate_data_from_epw(snapshot):
    filename = 'src/vctlib/temp_data/ITA_Bolzano.160200_IGDG.epw'
    df = get_climate_data_from_epw(filename)
    
    result = df.to_json()
    snapshot.assert_match(result, "climate_data_epw.json")


def test_get_climate_data_from_csv(snapshot):
    filename = 'src/vctlib/temp_data/tmy_46.501_11.362_2005_2020.csv'
    df = get_climate_data_from_csv(filename)
    
    result = df.to_json()
    snapshot.assert_match(result, "climate_data_csv.json")
