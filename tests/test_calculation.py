"""Test calculation functions."""

import numpy as np
import pandas as pd

from vctlib.calculation import (
    run_vct_simulation,
    get_climate_data_from_epw,
    get_climate_data_from_csv,
    get_vent_mode_over_year,
    get_requirend_frequency_air_change_rate,
    get_annual_data,
)
from inputs.functions import (
    get_appartment_bld_climate_data, 
    get_appartment_bld_thermophys_props, 
    get_appartment_building, 
    load_data_from_VCdesign
)


__author__ = "OlgaSomova"
__copyright__ = "OlgaSomova"
__license__ = "MIT"


ERROR = 10**-8  # Acceptable error = 1e-8


def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame):
    """ Compare two dataframes with tolerance 1e-8 """
    arr1 = df1.values.astype(float)
    arr2 = df2.values.astype(float)

    are_equal = np.allclose(np.sort(arr1.flatten()), np.sort(arr2.flatten()), atol=ERROR, equal_nan=True)
    return are_equal


def test_get_climate_data_from_epw(snapshot):
    filename = "src/vctlib/temp_data/ITA_Bolzano.160200_IGDG.epw"
    df = get_climate_data_from_epw(filename)

    result = df.to_json()
    snapshot.assert_match(result, "climate_data_epw.json")


def test_get_climate_data_from_csv(snapshot):
    filename = "src/vctlib/temp_data/tmy_46.501_11.362_2005_2020.csv"
    df = get_climate_data_from_csv(filename)

    result = df.to_json()
    snapshot.assert_match(result, "climate_data_csv.json")


def test_snapshot_building_simulation(snapshot):
    """Test Appartment building."""
    thermophys_prop = get_appartment_bld_thermophys_props()
    inputs = get_appartment_building(thermophys_prop)
    climate_data = get_appartment_bld_climate_data()

    df = run_vct_simulation(inputs, climate_data, thermophys_prop)

    df_original = pd.read_csv("tests/inputs/data/apartment_building.csv")
    df = df.drop(columns=["Date", "Time", "Day"])
    df_original = df_original.drop(columns=["Date", "Time", "Day"])

    result = {}
    for col in df.columns:
        # diff = [abs(x - y) for x, y in zip(df[col].values, df_original[col].values)]
        diff_array = [
            abs(x - y) < ERROR for x, y in zip(df[col].values, df_original[col].values)
        ]

        if col == "Target indoor temperature for VCS":
            diff_array.pop(7236)  # error in Excel file
            diff_array.pop(7668)
            diff_array.pop(7667)

        if not all(diff_array):
            raise AssertionError()

    result = df.to_json()
    snapshot.assert_match(result, "apartment_building.json")


#####################################################################################


def test_sanapshot_Apartment_building_Vent_mode_over_year(snapshot):
    thermophys_prop = get_appartment_bld_thermophys_props()
    inputs = get_appartment_building(thermophys_prop)
    climate_data = get_appartment_bld_climate_data()

    df_sim = run_vct_simulation(inputs, climate_data, thermophys_prop)
    df = get_vent_mode_over_year(df_sim[744:])

    df_original = pd.read_csv("tests/inputs/data/results_vent_mode_over_year.csv", index_col=0)
    if not compare_dataframes(df, df_original):
        raise AssertionError()

    result = df.to_json()
    snapshot.assert_match(result, "vent_mode_over_year.json")


def test_snapshot_Apartment_building_Freq_air_change_rate(snapshot):
    thermophys_prop = get_appartment_bld_thermophys_props()
    inputs = get_appartment_building(thermophys_prop)
    climate_data = get_appartment_bld_climate_data()

    df_sim = run_vct_simulation(inputs, climate_data, thermophys_prop)
    df = get_requirend_frequency_air_change_rate(df_sim[744:], inputs)

    df_original = pd.read_csv(
        "tests/inputs/data/results_req_freq_air_change_rate.csv", index_col=0
    )
    if not compare_dataframes(df, df_original):
        raise AssertionError()

    result = df.to_json()
    snapshot.assert_match(result, "req_freq_air_change_rate.json")


def test_snapshot_Apartment_building_Annual_data(snapshot):
    thermophys_prop = get_appartment_bld_thermophys_props()
    inputs = get_appartment_building(thermophys_prop)
    climate_data = get_appartment_bld_climate_data()

    df_sim = run_vct_simulation(inputs, climate_data, thermophys_prop)
    df = get_annual_data(df_sim[744:])

    df_original = pd.read_csv("tests/inputs/data/results_annual_data.csv", index_col=0)
    if not compare_dataframes(df, df_original):
        raise AssertionError()

    result = df.to_json()
    snapshot.assert_match(result, "annual_data.json")


####################################################################################

def run_test_building_example(filename):
    (inputs, 
     climate_data, 
     df_orig_sim, 
     df_orig_vent_mode, 
     df_orig_freq_air_change, 
     df_orig_annual_data) = load_data_from_VCdesign(filename)

    # Run simulation
    df = run_vct_simulation(inputs, climate_data)
    df_vent_mode = get_vent_mode_over_year(df[744:])
    df_freq_air_change = get_requirend_frequency_air_change_rate(df[744:], inputs)
    df_annual_data = get_annual_data(df[744:])

    # Compare Main simulation results
    df_orig_sim = df_orig_sim.drop(columns=["D", "F", "G", "H", "AK", "AL"]) # drop Date, Month, Time, 'Same in other unit' columns
    df = df.drop(columns=["Date", "Time", "Day"])

    if not compare_dataframes(df, df_orig_sim): 
        raise AssertionError()

    # Compare Vent mode over year
    if not compare_dataframes(df_vent_mode, df_orig_vent_mode):
        raise AssertionError()

    # Compare Frequency air change rate
    df_orig_freq_air_change = df_orig_freq_air_change.drop(columns=['BA']) # drop extra column
    if not compare_dataframes(df_freq_air_change, df_orig_freq_air_change):
        raise AssertionError()

    # Compare sensible energy needs
    df_orig_annual_data = df_orig_annual_data.drop(columns=['BF', 'BH']) # drop extra columns
    if not compare_dataframes(df_annual_data, df_orig_annual_data):
        raise AssertionError()
    

# def test_Simulation_VCdesign_Example21():
#     filename = "tests/inputs/data/VCdesign_Example21.xlsm"
#     run_test_building_example(filename)


# def test_Simulation_VCdesign_Example31():
#     filename = "tests/inputs/data/VCdesign_Example31.xlsm"
#     run_test_building_example(filename)