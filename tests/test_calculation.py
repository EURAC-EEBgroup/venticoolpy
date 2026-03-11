"""Test calculation functions."""

import numpy as np
import pandas as pd
import json


from venticoolpy.calculation import (
    run_vct_simulation,
    get_vent_mode_over_year,
    get_requirend_frequency_air_change_rate,
    get_annual_data,
)
from venticoolpy.model import Building, ClimateData
from venticoolpy.new_irradiation_SFA_Perez_newCalc import get_climate_data_w_vert_irrad_from_epw

from inputs.functions import (
    get_appartment_bld_climate_data, 
    load_climate_data_from_VCdesign
)



def test_snapshot_building_simulation(snapshot):
    """Test Appartment building."""
    building = Building(
        bui_type="Apartment building",
        ceiling_to_floor_height=2.7,
        envelope_area=171.60,
        floor_area=48.00,
        fenestration_area=12.00,
        orientation="N",
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

    snapshot.assert_match(csv_df_december, "simulation_december.csv")
    snapshot.assert_match(csv_df_vent_mode, "vent_mode_over_year.csv")
    snapshot.assert_match(csv_df_freq_air_chg, "req_freq_air_change_rate.csv")
    snapshot.assert_match(csv_df_year, "annual_data.csv")


####################################################################################


def test_Simulation_VCdesign_Example21(snapshot):

    inputs = Building(**{
        "bui_type": "Apartment building",
        "ceiling_to_floor_height": 2.6,
        "comfort_requirements": "category II",
        "construction_mass": "medium",
        "envelope_area": 7.8,
        "fenestration_area": 2,
        "orientation": "N",
        "floor_area": 14,
        "g_value_glazing_sys": 0.7,
        "max_outdoor_rel_hum_accepted": 85,
        "shading_control_setpoint": 120,
        "shading_factor": 0,
        "ti_csb": 50,
        "ti_day_start": 7,
        "ti_hsb": 15,
        "ti_night_start": 24,
        "time_control_off": 24,
        "time_control_on": 0,
        "u_value_fen": 1.2,
        "u_value_opaque": 0.21
    })

    filename = "tests/inputs/data/VCdesign_Example21.xlsm"
    climate_data = load_climate_data_from_VCdesign(filename)

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



def test_Simulation_VCdesign_Example31(snapshot):
    inputs = Building(**{
        "bui_type": "School",
        "ceiling_to_floor_height": 3,
        "comfort_requirements": "category II",
        "construction_mass": "light",
        "envelope_area": 30,
        "fenestration_area": 30,
        "orientation": "N",
        "floor_area": 50,
        "g_value_glazing_sys": 0.7,
        "max_outdoor_rel_hum_accepted": 85,
        "shading_control_setpoint": 120,
        "shading_factor": 0.3,
        "ti_csb": 50,
        "ti_day_start": 7,
        "ti_hsb": 15,
        "ti_night_start": 24,
        "time_control_off": 16,
        "time_control_on": 8,
        "u_value_fen": 3.5,
        "u_value_opaque": 3
    })

    filename = "tests/inputs/data/VCdesign_Example31.xlsm"
    climate_data= load_climate_data_from_VCdesign(filename)

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



def test_Simulation_VCdesign_Example41(snapshot):
    inputs = Building(**{
        "bui_type": "Apartment building",
        "ceiling_to_floor_height": 2.6,
        "comfort_requirements": "category II",
        "construction_mass": "medium",
        "envelope_area": 7.8,
        "fenestration_area": 1.5,
        "orientation": "N",
        "floor_area": 14,
        "g_value_glazing_sys": 0.7,
        "max_outdoor_rel_hum_accepted": 85,
        "shading_control_setpoint": 120,
        "shading_factor": 0.5,
        "ti_csb": 50,
        "ti_day_start": 7,
        "ti_hsb": 15,
        "ti_night_start": 24,
        "time_control_off": 16,
        "time_control_on": 8,
        "u_value_fen": 1.2,
        "u_value_opaque": 0.24
    })

    filename = "tests/inputs/data/VCdesign_Example41.xlsm"
    climate_data = load_climate_data_from_VCdesign(filename)

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



def test_Simulation_VCdesign_Example51(snapshot):
    inputs = Building(**{
        "bui_type": "Apartment building",
        "ceiling_to_floor_height": 2.6,
        "comfort_requirements": "category II",
        "construction_mass": "medium",
        "envelope_area": 7.8,
        "fenestration_area": 1.5,
        "orientation": "N",
        "floor_area": 14,
        "g_value_glazing_sys": 0.7,
        "max_outdoor_rel_hum_accepted": 85,
        "shading_control_setpoint": 120,
        "shading_factor": 0.5,
        "ti_csb": 50,
        "ti_day_start": 7,
        "ti_hsb": 15,
        "ti_night_start": 24,
        "time_control_off": 16,
        "time_control_on": 8,
        "u_value_fen": 1.2,
        "u_value_opaque": 0.24
    })

    filename = "tests/inputs/data/VCdesign_Example51.xlsm"
    climate_data = load_climate_data_from_VCdesign(filename)

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



def test_Simulation_VCdesign_Example61(snapshot):
    inputs = Building(**{
        "bui_type": "Hotel",
        "ceiling_to_floor_height": 2.6,
        "comfort_requirements": "category I",
        "construction_mass": "light",
        "envelope_area": 7.8,
        "fenestration_area": 1.5,
        "orientation": "N",
        "floor_area": 14,
        "g_value_glazing_sys": 0.7,
        "max_outdoor_rel_hum_accepted": 85,
        "shading_control_setpoint": 120,
        "shading_factor": 0,
        "ti_csb": 50,
        "ti_day_start": 7,
        "ti_hsb": 15,
        "ti_night_start": 24,
        "time_control_off": 16,
        "time_control_on": 8,
        "u_value_fen": 1.7,
        "u_value_opaque": 2.5
    })

    filename = "tests/inputs/data/VCdesign_Example61.xlsm"
    climate_data = load_climate_data_from_VCdesign(filename)

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



def test_Simulation_VCdesign_Example62(snapshot):
    inputs = Building(**{
        "bui_type": "Office",
        "ceiling_to_floor_height": 3,
        "comfort_requirements": "category I",
        "construction_mass": "medium",
        "envelope_area": 50,
        "fenestration_area": 25,
        "orientation": "N",
        "floor_area": 50,
        "g_value_glazing_sys": 0.7,
        "max_outdoor_rel_hum_accepted": 85,
        "shading_control_setpoint": 120,
        "shading_factor": 0,
        "ti_csb": 50,
        "ti_day_start": 7,
        "ti_hsb": 15,
        "ti_night_start": 24,
        "time_control_off": 16,
        "time_control_on": 8,
        "u_value_fen": 1.7,
        "u_value_opaque": 2.5
    })

    filename = "tests/inputs/data/VCdesign_Example62.xlsm"
    climate_data = load_climate_data_from_VCdesign(filename)

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

