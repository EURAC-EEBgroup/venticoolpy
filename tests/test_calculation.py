try:
    from vctlib.calculation import get_main_dataframe
    from vctlib.model import Input
except:
    import os
    import sys
    sys.path.insert(1, '/home/osomova/Projects/vct/vctlib/src')
    from vctlib.model import Input
    from vctlib.calculation import get_main_dataframe


import pandas as pd
import os
import json
import numpy as np

__author__ = "OlgaSomova"
__copyright__ = "OlgaSomova"
__license__ = "MIT"


def test_snapshot_get_main_dataframe(snapshot):
    inputs = Input(
        bui_type = 'Apartment building',
        celing_to_floor_height = 2.7,
        envelope_area = 171.60,
        floor_area = 48.00,
        fenestration_area = 12.00,
        comfort_requirements = "category II",
        max_outdoor_rel_hum_accepted = 85,
        u_value_opaque = 0.315822914673981,
        u_value_fen = 2.984, 
        construction_mass = "medium",
        g_value_glazing_sys = 0.71,
        shading_control_setpoint = 120,
        shading_factor = 0,
        vent_rates_mu = '1/h',
        time_control_on = 0,
        time_control_off = 24,
    )
    df = get_main_dataframe(inputs)
    df_original = pd.read_csv("tests/data/original.csv")

    df = df.drop(columns=['Date', 'Time'])
    df_original = df_original.drop(columns=['Date', 'Time'])

    # Acceptable error = 1e-9
    error = 10 ** -9 
    result = {}
    for col in df.columns:
        if col in ['Day']:
            continue
        # TODO: 1-4 gennaio c'è errore in excel: primo gennaio ha due volte 1:00, e di conseguenza trasla altri giorni
        diff_array = [abs(x - y) < error for x, y in zip(df[col].values, df_original[col].values)]
        if not all(diff_array):
            assert False
    
    result = df.to_json().encode()
    snapshot.assert_match(result, 'apartment_building.yml')
    



def test_snapshot_building_2(snapshot):
    inputs = Input(
        bui_type = 'Apartment building',
        celing_to_floor_height = 2.4,
        envelope_area = 1696,
        floor_area = 242.00,
        fenestration_area = 197.00,
        comfort_requirements = "category II",
        max_outdoor_rel_hum_accepted = 87,
        u_value_opaque = 0.26,
        u_value_fen = 1.40, 
        construction_mass = "medium",
        g_value_glazing_sys = 0.68,
        shading_control_setpoint = 140,
        shading_factor = 0,
        vent_rates_mu = '1/h',
        time_control_on = 0,
        time_control_off = 24,
    )
    df = get_main_dataframe(inputs)
    df_original = pd.read_csv("tests/data/building_2.csv")

    df = df.drop(columns=['Date', 'Time'])
    df_original = df_original.drop(columns=['Date', 'Time'])

    # Acceptable error = 1e-9
    error = 10 ** -9 
    result = {}
    for col in df.columns:
        if col in ['Day']:
            continue
        diff_array = [abs(x - y) < error for x, y in zip(df[col].values, df_original[col].values)]
        if not all(diff_array):
            assert False
    
    result = df.to_json().encode()
    snapshot.assert_match(result, 'apartment_building2.yml')




def test_snapshot_office(snapshot):
    inputs = Input(
        bui_type = 'Office',
        celing_to_floor_height = 2.7,
        envelope_area = 171.60,
        floor_area = 48.00,
        fenestration_area = 12.00,
        comfort_requirements = "category I",
        max_outdoor_rel_hum_accepted = 85,
        u_value_opaque = 0.315822914673981,
        u_value_fen = 2.984, 
        construction_mass = "heavy",
        g_value_glazing_sys = 0.71,
        shading_control_setpoint = 50,
        shading_factor = 0,
        vent_rates_mu = '1/h',
        time_control_on = 8,
        time_control_off = 18,
    )
    df = get_main_dataframe(inputs)
    df_original = pd.read_csv("tests/data/office.csv")

    df = df.drop(columns=['Date', 'Time'])
    df_original = df_original.drop(columns=['Date', 'Time'])

    # Acceptable error = 1e-9
    error = 10 ** -9 
    result = {}
    for col in df.columns:
        if col in ['Day']:
            continue
        diff_array = [x - y for x, y in zip(df[col].values, df_original[col].values)]
        diff_array = [abs(x) < error for x in diff_array if x == x] # remove NaN values
        if not all(diff_array):
            assert False
    
    result = df.to_json().encode()
    snapshot.assert_match(result, 'office.yml')
