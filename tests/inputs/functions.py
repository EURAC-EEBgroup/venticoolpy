"""
    Functions to get the test inputs data from VCdesign Excel files. 
"""

import pandas as pd
import re
from openpyxl import load_workbook
from openpyxl.utils import get_column_interval

from vctlib.model import Building, ClimateData, ThermostaticalProperties, SELECT_VENT_RATES_CALC


def get_appartment_bld_climate_data() -> ClimateData:
    outdoor_dry_bulb_temperature = pd.read_csv("tests/inputs/data/outdor_dry_bulb_temperature.csv")
    relative_humidity_outdoor_air = pd.read_csv("tests/inputs/data/outdor_climate_data.csv")
    isol_tot = pd.read_csv("tests/inputs/data/isol_tot.csv")

    climate_data = ClimateData(
        df_outdoor_dry_bulb_temperature=outdoor_dry_bulb_temperature,
        df_relative_humidity_outdoor_air=relative_humidity_outdoor_air,
        df_isol_tot=isol_tot
    )
    return climate_data


def get_appartment_bld_thermophys_props() -> ThermostaticalProperties:
    thermophys_prop = ThermostaticalProperties(
        external_wall_area=9.6 + 16.2 + 16.2 + 21.6,
        floor_area=6 * 8,
        roof_area=6 * 8,
        external_wall_r=1.797,
        floor_r=25.246,
        roof_r=2.992,
    )
    return thermophys_prop


def get_appartment_building(thermophys_prop: ThermostaticalProperties) -> Building:
    building = Building(
        bui_type="Apartment building",
        celing_to_floor_height=2.7,
        envelope_area=171.60,
        floor_area=48.00,
        fenestration_area=12.00,
        comfort_requirements="category II",
        max_outdoor_rel_hum_accepted=85,
        u_value_opaque=thermophys_prop.u_value_tot,
        u_value_fen=2.984,
        construction_mass="medium",
        g_value_glazing_sys=0.71,
        shading_control_setpoint=120,
        shading_factor=0,
        time_control_on=0,
        time_control_off=24,
        ti_hsp_day_start=7,
        ti_hsp_night_start=24,
        select_internal_gains='basecase',
        select_vent_rates_calc=SELECT_VENT_RATES_CALC[0]
    )
    return building


def load_data_from_VCdesign(filename):

    def load_workbook_range(range_string, ws):
        col_start, col_end = re.findall("[A-Z]+", range_string)

        data_rows = []
        for row in ws[range_string]:
            data_rows.append([cell.value for cell in row])

        return pd.DataFrame(data_rows, columns=get_column_interval(col_start, col_end))


    wb = load_workbook(filename, data_only=True)
    # Load Inputs
    sh = wb["WEATHER FILE"]
    outdoor_dry_bulb_temperature = load_workbook_range('D20:D8779', sh)
    relative_humidity_outdoor_air = load_workbook_range('F20:F8779', sh)
    isol_tot = load_workbook_range('K20:K8779', sh)

    climate_data = ClimateData(
        df_outdoor_dry_bulb_temperature=outdoor_dry_bulb_temperature,
        df_relative_humidity_outdoor_air=relative_humidity_outdoor_air,
        df_isol_tot=isol_tot,
    )

    sh = wb["VCP"]
    inputs = Building(
        bui_type=sh["C6"].value,
        celing_to_floor_height=sh["C7"].value,
        envelope_area=sh["C8"].value,
        floor_area=sh["C9"].value,
        fenestration_area=sh["C10"].value,
        comfort_requirements=sh["C12"].value,
        max_outdoor_rel_hum_accepted=sh["C13"].value,
        u_value_opaque=sh["C16"].value,
        u_value_fen=sh["C17"].value,
        construction_mass=sh["C19"].value,
        g_value_glazing_sys=sh["C20"].value,
        shading_control_setpoint=sh["C21"].value,
        shading_factor=sh["C22"].value,
        # vent_rates_mu=sh["D24"].value,
        time_control_on=sh["C32"].value,
        time_control_off=sh["C33"].value,
        ti_hsp_day_start=7,
        ti_hsp_night_start=24,
        select_vent_rates_calc=SELECT_VENT_RATES_CALC[0]
    )

    # load Results
    df_orig_sim = load_workbook_range('D41:AT9544', sh)
    df_orig_vent_mode = load_workbook_range('AT6:AW18', sh)
    df_orig_freq_air_change = load_workbook_range('AY6:BB15', sh)
    df_orig_annual_data = load_workbook_range('BE6:BK17', sh)

    return inputs, climate_data, df_orig_sim, df_orig_vent_mode, df_orig_freq_air_change, df_orig_annual_data