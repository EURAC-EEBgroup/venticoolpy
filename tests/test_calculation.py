"""Test calculation functions."""

import numpy as np
import pandas as pd
import json


from venticoolpy.calculation import (
    run_vct_simulation,
    get_climate_data_from_epw,
    get_climate_data_from_csv,
    get_vent_mode_over_year,
    get_requirend_frequency_air_change_rate,
    get_annual_data,
)
from venticoolpy.model import Building, ClimateData
from venticoolpy.new_irradiation_SFA_Perez_newCalc import get_climate_data_w_vert_irrad_from_epw

from inputs.functions import (
    get_appartment_bld_climate_data, 
    get_appartment_bld_thermophys_props, 
    get_appartment_building, 
    load_data_from_VCdesign
)



ERROR = 10**-8  # Acceptable error = 1e-8


def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame):
    """ Compare two dataframes with tolerance 1e-8 """
    arr1 = df1.values.astype(float)
    arr2 = df2.values.astype(float)

    are_equal = np.allclose(np.sort(arr1.flatten()), np.sort(arr2.flatten()), atol=ERROR, equal_nan=True)
    return are_equal



def test_snapshot_building_simulation(snapshot):
    """Test Appartment building."""
    building = Building(
        bui_type="Apartment building",
        celing_to_floor_height=2.7,
        envelope_area=171.60,
        floor_area=48.00,
        fenestration_area=12.00,
        comfort_requirements="category II",
        max_outdoor_rel_hum_accepted=85,
        u_value_opaque=0.3158229146739811,
        u_value_fen=2.984,
        construction_mass="medium",
        g_value_glazing_sys=0.71,
        shading_control_setpoint=120,
        shading_factor=0,
        time_control_on=0,
        time_control_off=24,
        ti_day_start=7,
        ti_night_start=24,
        select_internal_gains='basecase',
        select_vent_rates_calc="constant",
        my_c_int=15959951.712000001
    )
    climate_data = get_appartment_bld_climate_data()

    df = run_vct_simulation(building, climate_data)
    df_vent_mode = get_vent_mode_over_year(df[744:])
    df_freq_air_chg = get_requirend_frequency_air_change_rate(df[744:], building)
    df_year = get_annual_data(df[744:])

    csv_df_december = df.tail(744).to_csv(lineterminator="\n")
    csv_df_vent_mode = df_vent_mode.to_csv(lineterminator="\n")
    csv_df_freq_air_chg = df_freq_air_chg.to_csv(lineterminator="\n")
    csv_df_year = df_year.to_csv(lineterminator="\n")

    # TODO: add also 1 year simulation?
    snapshot.assert_match(csv_df_december, "simulation_december.csv")
    snapshot.assert_match(csv_df_vent_mode, "vent_mode_over_year.csv")
    snapshot.assert_match(csv_df_freq_air_chg, "req_freq_air_change_rate.csv")
    snapshot.assert_match(csv_df_year, "annual_data.csv")



####################################################################################

def run_test_building_example(filename, snapshot):
    (inputs, 
     climate_data, 
     _, 
     _, 
     _, 
     _) = load_data_from_VCdesign(filename)

    building_str = json.dumps(inputs.__dict__, indent=4, sort_keys=True)
    snapshot.assert_match(building_str, "building.json")

    # Run simulation
    df = run_vct_simulation(inputs, climate_data)
    df_vent_mode = get_vent_mode_over_year(df[744:])
    df_freq_air_change = get_requirend_frequency_air_change_rate(df[744:], inputs)
    df_annual_data = get_annual_data(df[744:])

    csv_df_december = df.tail(744).to_csv(lineterminator="\n")
    csv_df_vent_mode = df_vent_mode.to_csv(lineterminator="\n")
    csv_df_freq_air_chg = df_freq_air_change.to_csv(lineterminator="\n")
    csv_df_year = df_annual_data.to_csv(lineterminator="\n")

    snapshot.assert_match(csv_df_december, "simulation_december.csv")
    snapshot.assert_match(csv_df_vent_mode, "vent_mode_over_year.csv")
    snapshot.assert_match(csv_df_freq_air_chg, "req_freq_air_change_rate.csv")
    snapshot.assert_match(csv_df_year, "annual_data.csv")

    

def test_Simulation_VCdesign_Example21(snapshot):
    filename = "tests/inputs/data/VCdesign_Example21.xlsm"
    run_test_building_example(filename, snapshot)


def test_Simulation_VCdesign_Example31(snapshot):
    filename = "tests/inputs/data/VCdesign_Example31.xlsm"
    run_test_building_example(filename, snapshot)


def test_Simulation_VCdesign_Example41(snapshot):
    filename = "tests/inputs/data/VCdesign_Example41.xlsm"
    run_test_building_example(filename, snapshot)


def test_Simulation_VCdesign_Example51(snapshot):
    filename = "tests/inputs/data/VCdesign_Example51.xlsm"
    run_test_building_example(filename, snapshot)


def test_Simulation_VCdesign_Example61(snapshot):
    filename = "tests/inputs/data/VCdesign_Example61.xlsm"
    run_test_building_example(filename, snapshot)


def test_Simulation_VCdesign_Example62(snapshot):
    filename = "tests/inputs/data/VCdesign_Example62.xlsm"
    run_test_building_example(filename, snapshot)



# new irradiation calculation:

# TODO: add new unit tests

def test_simulation_dummy(snapshot):
    building = Building(
        bui_type="Apartment building",
        celing_to_floor_height=2.7,
        envelope_area=171.60,
        floor_area=48.00,
        fenestration_area=12.00,
        comfort_requirements="category II",
        max_outdoor_rel_hum_accepted=85,
        u_value_opaque=0.315822914673981,
        u_value_fen=2.984,
        construction_mass="medium",
        g_value_glazing_sys=0.71,
        shading_control_setpoint=120,
        shading_factor=0,
        time_control_on=0,
        time_control_off=24,
    )
     
    climate_filename = 'tests/inputs/data/climate/4A_London_TMY_2001-2020.epw'
    climate_data = get_climate_data_w_vert_irrad_from_epw(climate_filename, "SW")

    df = run_vct_simulation(building, climate_data)
    df_vent_mode = get_vent_mode_over_year(df[744:])
    df_freq_air_change = get_requirend_frequency_air_change_rate(df[744:], building)
    df_annual_data = get_annual_data(df[744:])

    snapshot.assert_match(df_vent_mode.to_json(), "test_simulation_dummy_df_vent_mode.yml")
    snapshot.assert_match(df_freq_air_change.to_json(), "test_simulation_dummy_df_freq_air_change.yml")
    snapshot.assert_match(df_annual_data.to_json(), "test_simulation_dummy_df_annual_data.yml")
