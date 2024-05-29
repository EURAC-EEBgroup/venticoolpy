"""Ventilative Cooling Potential simulation functions."""

import pandas as pd
from statistics import mean
import datetime
from epw.weather import Weather
import csv
import sys
import bisect
import os
import numpy as np

try:
    from vctlib.constant import get_t_min_k, get_t_max_k
    from vctlib.constant import (
        COMFORT_REQUIREMENTS, 
        comfort_categories_AK,
        comfort_categories_AL,
        SELECT_INTERNAL_GAINS,
    )
    from vctlib.constant import Air_properties_Cp, Air_properties_ro
    from vctlib.constant import VENTILATION_STRATEGY, WINDOW_DESIGN_CV
    from vctlib.model import Building, ThermostaticalProperties, ClimateData, WindowDesign
except ModuleNotFoundError:  # TODO: remove try-except
    import sys

    sys.path.insert(1, "/home/osomova/Projects/vct/vctlib/src")
    from vctlib.constant import get_t_min_k, get_t_max_k
    from vctlib.constant import Air_properties_Cp, Air_properties_ro
    from vctlib.constant import (
        COMFORT_REQUIREMENTS,
        comfort_categories_AK,
        comfort_categories_AL,
    )
    from vctlib.constant import VENTILATION_STRATEGY, WINDOW_DESIGN_CV
    from vctlib.constant import SELECT_INTERNAL_GAINS
    from vctlib.model import Building, ThermostaticalProperties, ClimateData, WindowDesign


TOT_HOURS = 9504  # Total hours in simulation = December + 1 year -> (31+365)*24
HOURS_IN_YEAR = 8760  # 365*24
TOT_DAYS = 396  # 31 + 365
DAYS_IN_YEAR = 365


def get_simulation_year() -> pd.DataFrame:
    """Create a DataFrame for a sumulation.

    Lenght is equal to December month + 1 standard year

    Returns:
        pd.DataFrame with:
        - Date
        - Month
        - Day
        - Time: integer (1, 2, ..., 24)
    """
    df = pd.DataFrame(index=range(TOT_HOURS))
    dates = pd.concat(
        [
            pd.Series(
                pd.date_range(start="2011-12-01", end="{}-01-01".format(2012), freq="h")
            )[0:744],
            pd.Series(
                pd.date_range(start="2011-01-01", end="{}-01-01".format(2012), freq="h")
            )[0:8760],
        ]
    )
    df["Date"] = dates.values

    df["Month"] = [d.month for d in dates]
    df["Day"] = [d.day for d in dates]
    df["Time"] = [d.hour + 1 for d in dates]

    return df


def get_climate_data_from_epw(filename) -> ClimateData:
    weather_data = Weather()
    weather_data.read(filename)

    # TODO: add some validation
    if weather_data.dataframe.shape[0] != HOURS_IN_YEAR:
        raise Exception("The data is invalid")

    climate_data = ClimateData(
        df_outdoor_dry_bulb_temperature=weather_data.dataframe["Dry Bulb Temperature"], 
        df_relative_humidity_outdoor_air=weather_data.dataframe["Relative Humidity"],
        df_isol_tot=weather_data.dataframe["Global Horizontal Radiation"]
    )

    return climate_data


def get_climate_data_from_csv(filename) -> ClimateData:
    skiprows = None
    with open(filename, "r") as file:
        csvreader = csv.reader(file)
        index = 0
        for row in csvreader:
            if row[0] == "time(UTC)":
                skiprows = index
                break
            index += 1

    weather_data = pd.read_csv(filename, skiprows=skiprows, nrows=HOURS_IN_YEAR)

    if weather_data.shape[0] != HOURS_IN_YEAR:
        raise Exception("The data is invalid")

    climate_data = ClimateData(
        df_outdoor_dry_bulb_temperature=weather_data["T2m"], 
        df_relative_humidity_outdoor_air=weather_data["RH"],
        df_isol_tot=weather_data["G(h)"]
    )

    return climate_data


def get_internal_gains(building: Building):
    """Retrieve internal gains according to building type"""
    
    if building.select_internal_gains == SELECT_INTERNAL_GAINS[0]: # basecase
        internal_gains = [200 / building.floor_area] * TOT_HOURS
    else: 
        all_internal_gains = pd.read_csv(f"{os.getcwd()}/src/vctlib/internal_gains.csv")
        internal_gains = all_internal_gains[building.bui_type]
        internal_gains = np.append(internal_gains[8016:8760].values, internal_gains[0:8760].values)

    return internal_gains


def get_outdoor_climate_data(claimate_data: ClimateData) -> pd.DataFrame:
    """Retrieve outdoor climate data.

    Parameters:
        # TODO: update

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
        - Outdoor dry-bulb temperature.  θe;a [°C]
        - Relative humidity of outdoor air.  ΦHU;e;a;t [%]
        - Daily mean outdoor temperature.  θe;a;mean [°C]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    df["Outdoor dry-bulb temperature"] = claimate_data.outdoor_dry_bulb_temperature
    outdoor_dry_bulb_temp = df["Outdoor dry-bulb temperature"].values

    df["Relative humidity of outdoor air"] = claimate_data.relative_humidity_outdoor_air

    daily_mean_outdoor_temp = []
    for i in range(0, TOT_HOURS, 24):
        val = mean(outdoor_dry_bulb_temp[i : i + 24])
        daily_mean_outdoor_temp.extend([val] * 24)
    df["Daily mean outdoor temperature"] = daily_mean_outdoor_temp

    return df


def calc_thermal_comfort_data(
    building: Building, daily_mean_outdoor_temp
) -> pd.DataFrame:
    """Calculate Thermal comfort data.

    Parameters:
        - building obj

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
        - Outdoor runnin mean temperature.  Θrm [°C]
        - Comfort temperature.  Θc [°C]
        - Lower comfort zone limit.  Θint;set;H;t [°C]
        - Upper comfort zone limit.  Θint;set;C;t [°C]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    outdoor_runnin_mean_temperature = []
    temp = daily_mean_outdoor_temp[744:]
    for i in range(0, HOURS_IN_YEAR, 24):
        val = (
            temp[i - 24]
            + temp[i - 48] * 0.8
            + temp[i - 72] * 0.6
            + temp[i - 96] * 0.5
            + temp[i - 120] * 0.4
            + temp[i - 144] * 0.3
            + temp[i - 168] * 0.2
        ) / 3.8
        outdoor_runnin_mean_temperature.extend([val] * 24)

    full_year = outdoor_runnin_mean_temperature[-744:]
    full_year.extend(outdoor_runnin_mean_temperature)

    df["Outdoor runnin mean temperature"] = full_year

    t_min_k = get_t_min_k(building.comfort_requirements)
    Ti_hsp = t_min_k[building.bui_type]

    t_max_k = get_t_max_k(building.comfort_requirements)
    Ti_csp = t_max_k[building.bui_type]

    AL10 = comfort_categories_AL[building.comfort_requirements]
    AK10 = comfort_categories_AK[building.comfort_requirements]
    lower_comfort_zone_limit = [None] * TOT_HOURS
    upper_comfort_zone_limit = [None] * TOT_HOURS
    comfort_temperature = [None] * TOT_HOURS

    i = 0
    for i in range(TOT_HOURS):
        if full_year[i] > 10:
            lower_comfort_zone_limit[i] = 0.33 * full_year[i] + 18.8 + AL10
            upper_comfort_zone_limit[i] = 0.33 * full_year[i] + 18.8 + AK10
            comfort_temperature[i] = 0.33 * full_year[i] + 18.8
        else:
            lower_comfort_zone_limit[i] = Ti_hsp
            upper_comfort_zone_limit[i] = Ti_csp
            comfort_temperature[i] = (Ti_hsp + Ti_csp) / 2

    df["Comfort temperature"] = comfort_temperature
    df["Lower comfort zone limit"] = lower_comfort_zone_limit
    df["Upper comfort zone limit"] = upper_comfort_zone_limit

    return df


def get_gains(building: Building, climate_data: ClimateData) -> pd.DataFrame:
    """Calculate solar and internal gains.

    Patameters:
        - building obj

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
        - Solar gains.  Φsol [W/m²]
        - Internal gains.  Φint [W/m²]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    isol_tot = climate_data.isol_tot

    solar_gains = [
        x
        * (1 - building.shading_factor)
        * building.g_value_glazing_sys
        * building.fenestration_area
        / building.floor_area
        for x in isol_tot
    ]
    df["Solar gains"] = solar_gains

    internal_gains = get_internal_gains(building)

    df["Internal gains"] = internal_gains # TODO: add to inputs

    return df


def get_ventilation_rate(building: Building) -> pd.DataFrame:
    """Calculate Ventilation rates.

    Parameters:
        - building obj

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
        - Ventilation rate.  qV;t [m3/s]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    vent_rate_m3_s = building.min_req_vent_rates[0] * building.floor_area / 1000
    ventilation_rate = [vent_rate_m3_s] * TOT_HOURS
    df["Ventilation rate"] = ventilation_rate

    return df


def calc_free_float_mode(
    building: Building,
    c_int,  # TODO: change name
    vent_rate_m3_s,
    solar_gains,
    internal_gains,
    outdoor_dry_bulb_temp,
) -> pd.DataFrame:
    """Perform the first set of calculations (Free Float Mode).

    Parameters:
        - building obj
        - c_int: # TODO: add description
        - vent_rate_m3_s: ventilation rate [m³/s]
        - solar_gains: A list with hourly values of solar gains
        - internal_gains: A list with hourly values of internal gains
        - outdoor_dry_bulb_temp: A list with hourly values of Outdoor dry bulb
          temperature
        All parameters (except building) are the outputs of the previous steps.

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
        - At [W/K]
        - Bt [W]
        - Internal temperature free float.  ϴint;0;t [°C]
        - Internal temperature calculated.  ϴint;t [°C]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    a_t = (
        c_int / 3600
        + (Air_properties_Cp * Air_properties_ro * vent_rate_m3_s)
        + building.average_u_value * building.envelope_area
    )
    # 0.5024087248366400000 # Excel
    # 0.5024087248366397    # Python

    internal_temperature_free_float = [None] * TOT_HOURS
    b_t = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        if i == 0:
            internal_temperature_free_float[0] = 20  # set first value

            b_t[0] = (
                c_int / 3600 * internal_temperature_free_float[0]
                + (
                    Air_properties_Cp * Air_properties_ro * vent_rate_m3_s
                    + building.average_u_value * building.envelope_area
                )
                * outdoor_dry_bulb_temp[0]
                + (solar_gains[0] + internal_gains[0]) * building.floor_area
            )
        else:
            b_t[i] = (
                c_int / 3600 * internal_temperature_free_float[i - 1]
                + (
                    Air_properties_Cp * Air_properties_ro * vent_rate_m3_s
                    + building.average_u_value * building.envelope_area
                )
                * outdoor_dry_bulb_temp[i]
                + (solar_gains[i] + internal_gains[i]) * building.floor_area
            )

            internal_temperature_free_float[i] = b_t[i] / a_t

    df["At"] = [a_t] * TOT_HOURS
    df["Bt"] = b_t
    df["Internal temperature free float"] = internal_temperature_free_float
    df["Internal temperature calculated"] = internal_temperature_free_float

    return df


def calc_heating_and_cooling_needs_no_vcs(
    building: Building,
    c_int,
    vent_rate_m3_s,
    solar_gains,
    internal_gains,
    outdoor_dry_bulb_temp,
    a_t,
    lower_comfort_zone_limit,
    upper_comfort_zone_limit,
) -> pd.DataFrame:
    """Perform the second set of calculations (Heating and Cooling needs, no VCS).

    Parameters:
        - building obj
        - c_int: # TODO: add description
        - vent_rate_m3_s: ventilation rate [m³/s]
        - solar_gains: A list with hourly values of solar gains
        - internal_gains: A list with hourly values of internal gains
        - outdoor_dry_bulb_temp: A list with hourly values of Outdoor dry bulb
            temperature
        - a_t: value of At
        - lower_comfort_zone_limit: A list with hourly values of Lower comfort zone
            limit
        - upper_comfort_zone_limit: A list with hourly values of Upper comfort zone
            limit
        All parameters (except building) are the outputs of the previous steps.

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
            - Ventilation rate.  qV;t [m3/s]
            - At  [W/K]
            - Bt  [W]
            - Internal temperature free float.  ϴint;0;t [°C]
            - Heating or cooling load.  ΦHC;t [W]
            - Internal temperature calculated.  ϴint;t [°C]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    bt_no_vcs = [None] * TOT_HOURS
    internal_temperature_free_float_no_vcs = [None] * TOT_HOURS
    heating_cooling_load = [None] * TOT_HOURS
    internal_temperature_calc = [None] * TOT_HOURS

    for i in range(TOT_HOURS):
        if i == 0:
            internal_temperature_free_float_no_vcs[0] = 20
            bt_no_vcs[0] = (
                c_int / 3600 * internal_temperature_free_float_no_vcs[0]
                + (
                    Air_properties_Cp * Air_properties_ro * vent_rate_m3_s
                    + building.average_u_value * building.envelope_area
                )
                * outdoor_dry_bulb_temp[0]
                + (solar_gains[0] + internal_gains[0]) * building.floor_area
            )

        else:
            bt_no_vcs[i] = (
                c_int / 3600 * internal_temperature_calc[i - 1]
                + (
                    Air_properties_Cp * Air_properties_ro * vent_rate_m3_s
                    + building.average_u_value * building.envelope_area
                )
                * outdoor_dry_bulb_temp[i]
                + (solar_gains[i] + internal_gains[i]) * building.floor_area
            )

            internal_temperature_free_float_no_vcs[i] = bt_no_vcs[i] / a_t

        if internal_temperature_free_float_no_vcs[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load[i] = a_t * lower_comfort_zone_limit[i] - bt_no_vcs[i]
        elif (
            internal_temperature_free_float_no_vcs[i] >= lower_comfort_zone_limit[i]
            and internal_temperature_free_float_no_vcs[i] <= upper_comfort_zone_limit[i]
        ):
            heating_cooling_load[i] = 0
        elif internal_temperature_free_float_no_vcs[i] > upper_comfort_zone_limit[i]:
            heating_cooling_load[i] = a_t * upper_comfort_zone_limit[i] - bt_no_vcs[i]

        internal_temperature_calc[i] = (bt_no_vcs[i] + heating_cooling_load[i]) / a_t

    df["Ventilation rate.1"] = [vent_rate_m3_s] * TOT_HOURS
    df["At.1"] = [a_t] * TOT_HOURS
    df["Bt.1"] = bt_no_vcs
    df["Internal temperature free float.1"] = internal_temperature_free_float_no_vcs
    df["Heating or cooling load"] = heating_cooling_load
    df["Internal temperature calculated.1"] = internal_temperature_calc

    return df


def calc_heating_and_cooling_needs_with_vcs(
    building: Building,
    c_int,
    vent_rate_m3_s,
    solar_gains,
    internal_gains,
    outdoor_dry_bulb_temp,
    a_t,
    lower_comfort_zone_limit,
    upper_comfort_zone_limit,
    relative_humidity_of_outdoor_air,
    heating_cooling_load,
    time,
) -> pd.DataFrame:
    """Perform the third set of calculations (Heating and Cooling needs, with VCS).

    Parameters:
        - building obj
        - vent_rate_m3_s: ventilation rate [m³/s]
        - solar_gains: A list with hourly values of solar gains
        - internal_gains: A list with hourly values of internal gains
        - outdoor_dry_bulb_temp: A list with hourly values of Outdoor dry bulb
          temperature
        - a_t: value of At
        - lower_comfort_zone_limit: A list with hourly values of Lower comfort zone
          limit
        - upper_comfort_zone_limit: A list with hourly values of Upper comfort zone
          limit
        - relative_humidity_of_outdoor_air: A list with hourly values of Relative
          humidity of outdoor air
        - heating_cooling_load: A list with hourly values of Heating or cooling load
        - time: A list with hourly values. A set of (1, 2, .., 24) for each day of
          simulation
        All parameters (except building) are the outputs of the previous steps.

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
            - Ventilation rate without VCS.  qV;t [m3/s]
            - At  [W/K]
            - Bt  [W]
            step 1:
                - Internal temperature free float.  ϴint;0;t [°C]
            step 2:
                - Heating or cooling load "step 2".  ΦHC;step2;t [W]
                - Internal temperature calculated "Step2".  ϴint;step2;t [°C]
            step 3:
                - VC mode
                - Required cooling ventilation rate (VC mode 1 or 2).  ΔqV;vcs;req;t
                  [m3/s]
            step 4:
                - Actual ventilation rate.  qV;vcs;t [m3/s]
                - Avcs;t  [W/K]
                - Bvcs;t  [W]
                - Internal temperature free float.  ϴint;0;t [°C]
                - Heating or cooling load.  ΦHC;vcs;t [W]
                - Internal temperature calculated.  ϴint;vcs;t [°C]
                - HC load difference.  ΔΦHC;vcs;t [W]
                - Target indoor temperature for VCS.  ϴint;set;vcs;t [°C]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    int_temp_free_float_with_vcs = [None] * TOT_HOURS
    bt_with_vcs = [None] * TOT_HOURS
    heating_cooling_load_with_vcs = [None] * TOT_HOURS
    internal_temperature_calc_with_vcs = [None] * TOT_HOURS

    for i in range(TOT_HOURS):
        if i == 0:
            int_temp_free_float_with_vcs[0] = 20

            bt_with_vcs[0] = (
                c_int / 3600 * int_temp_free_float_with_vcs[0]
                + (
                    Air_properties_Cp * Air_properties_ro * vent_rate_m3_s
                    + building.average_u_value * building.envelope_area
                )
                * outdoor_dry_bulb_temp[0]
                + (solar_gains[0] + internal_gains[0]) * building.floor_area
            )

        else:
            bt_with_vcs[i] = (
                c_int / 3600 * internal_temperature_calc_with_vcs[i - 1]
                + (
                    Air_properties_Cp * Air_properties_ro * vent_rate_m3_s
                    + building.average_u_value * building.envelope_area
                )
                * outdoor_dry_bulb_temp[i]
                + (solar_gains[i] + internal_gains[i]) * building.floor_area
            )

            int_temp_free_float_with_vcs[i] = bt_with_vcs[i] / a_t

        if int_temp_free_float_with_vcs[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load_with_vcs[i] = (
                a_t * lower_comfort_zone_limit[i] - bt_with_vcs[i]
            )
        elif (int_temp_free_float_with_vcs[i] >= lower_comfort_zone_limit[i]) and (
            int_temp_free_float_with_vcs[i] < upper_comfort_zone_limit[i]
        ):
            heating_cooling_load_with_vcs[i] = 0
        elif int_temp_free_float_with_vcs[i] > upper_comfort_zone_limit[i]:
            heating_cooling_load_with_vcs[i] = (
                a_t * upper_comfort_zone_limit[i] - bt_with_vcs[i]
            )

        internal_temperature_calc_with_vcs[i] = (
            bt_with_vcs[i] + heating_cooling_load_with_vcs[i]
        ) / a_t

    df["Ventilation rate without VCS"] = [vent_rate_m3_s] * TOT_HOURS
    df["At.2"] = [a_t] * TOT_HOURS
    df["Bt.2"] = bt_with_vcs
    df["Internal temperature free float.2"] = int_temp_free_float_with_vcs
    df['Heating or cooling load "step 2"'] = heating_cooling_load_with_vcs
    df['Internal temperature calculated "Step2"'] = internal_temperature_calc_with_vcs

    vc_mode = [None] * TOT_HOURS
    delta_theta_crit = 3  # AF28
    for i in range(TOT_HOURS):
        if (time[i] >= building.time_control_on) and (
            time[i] <= building.time_control_off
        ):
            if int_temp_free_float_with_vcs[i] < lower_comfort_zone_limit[i]:
                vc_mode[i] = 0
            elif (int_temp_free_float_with_vcs[i] >= lower_comfort_zone_limit[i]) and (
                int_temp_free_float_with_vcs[i] <= upper_comfort_zone_limit[i]
            ):
                vc_mode[i] = 1
            elif (
                (int_temp_free_float_with_vcs[i] > upper_comfort_zone_limit[i])
                and (
                    outdoor_dry_bulb_temp[i]
                    <= (upper_comfort_zone_limit[i] - delta_theta_crit)
                )
                and (
                    relative_humidity_of_outdoor_air[i]
                    < building.max_outdoor_rel_hum_accepted
                )
            ):
                vc_mode[i] = 2
            else:
                vc_mode[i] = 3
        else:
            vc_mode[i] = None

    df["VC mode"] = vc_mode

    required_cooling_vent_rate = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        if vc_mode[i] == 2:
            required_cooling_vent_rate[i] = (
                bt_with_vcs[i] - a_t * upper_comfort_zone_limit[i]
            ) / (
                Air_properties_Cp
                * Air_properties_ro
                * (upper_comfort_zone_limit[i] - outdoor_dry_bulb_temp[i])
            )
        else:
            required_cooling_vent_rate[i] = 0

    actual_ventilation_rate = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        if vc_mode[i] == 2:
            actual_ventilation_rate[i] = required_cooling_vent_rate[i] + vent_rate_m3_s
        else:
            actual_ventilation_rate[i] = vent_rate_m3_s

    a_vcs_t = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        a_vcs_t[i] = (
            c_int / 3600
            + Air_properties_Cp * Air_properties_ro * actual_ventilation_rate[i]
            + building.average_u_value * building.envelope_area
        )

    b_vcs_t = [None] * TOT_HOURS
    internal_temperature_free_s4 = [None] * TOT_HOURS  # s4 aka step 4
    heating_cooling_load_s4 = [None] * TOT_HOURS
    internal_temperature_calc_s4 = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        if i == 0:
            internal_temperature_free_s4[0] = 20
            b_vcs_t[0] = (
                c_int / 3600 * internal_temperature_free_s4[0]
                + (
                    Air_properties_Cp * Air_properties_ro * actual_ventilation_rate[0]
                    + building.average_u_value * building.envelope_area
                )
                * outdoor_dry_bulb_temp[0]
                + (solar_gains[0] + internal_gains[0]) * building.floor_area
            )
        else:
            b_vcs_t[i] = (
                c_int / 3600 * internal_temperature_calc_s4[i - 1]
                + (
                    Air_properties_Cp * Air_properties_ro * actual_ventilation_rate[i]
                    + building.average_u_value * building.envelope_area
                )
                * outdoor_dry_bulb_temp[i]
                + (solar_gains[i] + internal_gains[i]) * building.floor_area
            )

            internal_temperature_free_s4[i] = b_vcs_t[i] / a_vcs_t[i]

        if internal_temperature_free_s4[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load_s4[i] = (
                a_vcs_t[i] * lower_comfort_zone_limit[i] - b_vcs_t[i]
            )
        elif (internal_temperature_free_s4[i] >= lower_comfort_zone_limit[i]) and (
            internal_temperature_free_s4[i] <= upper_comfort_zone_limit[i]
        ):
            heating_cooling_load_s4[i] = 0
        elif internal_temperature_free_s4[i] > upper_comfort_zone_limit[i]:
            heating_cooling_load_s4[i] = (
                a_vcs_t[i] * upper_comfort_zone_limit[i] - b_vcs_t[i]
            )

        internal_temperature_calc_s4[i] = (
            b_vcs_t[i] + heating_cooling_load_s4[i]
        ) / a_vcs_t[i]

    hc_load_difference = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        hc_load_difference[i] = -(heating_cooling_load[i] - heating_cooling_load_s4[i])

    df["Required cooling ventilation rate (VC mode 1 or 2)"] = (
        required_cooling_vent_rate
    )
    df["Actual ventilation rate"] = actual_ventilation_rate
    df["Avcs;t"] = a_vcs_t
    df["Bvcs;t"] = b_vcs_t
    df["Internal temperature free float.3"] = internal_temperature_free_s4
    df["Heating or cooling load.1"] = heating_cooling_load_s4
    df["Internal temperature calculated.2"] = internal_temperature_calc_s4
    df["HC load difference"] = hc_load_difference
    df["Target indoor temperature for VCS"] = upper_comfort_zone_limit

    return df


def run_vct_simulation(
    inputs: Building, 
    climate_data: ClimateData,
    thermophysical_props: ThermostaticalProperties | None = None
) -> pd.DataFrame:
    """Perform main VCT simulation.

    Returns:
        pd.DataFrame: A DataFrame with hourly simulation
    """
    df = get_simulation_year()

    ###############################################################
    #                 OUTDOOR CLIMATE DATA
    ###############################################################
    df_temp = get_outdoor_climate_data(climate_data)
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    #                 THERMAL COMFORT DATA
    ###############################################################
    df_temp = calc_thermal_comfort_data(
        inputs, df["Daily mean outdoor temperature"].values
    )
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    #                         GAINS
    ###############################################################
    df_temp = get_gains(inputs, climate_data)
    df = pd.concat([df, df_temp], axis=1)

    df_temp = get_ventilation_rate(inputs)
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    #           FREE FLOAT MODE (1st SET OF CALCULATIONS)
    ###############################################################
    vent_rate_m3_s = df["Ventilation rate"][0]
    solar_gains = df["Solar gains"].values
    internal_gains = df["Internal gains"].values
    outdoor_dry_bulb_temp = df["Outdoor dry-bulb temperature"].values
    c_int = inputs.c_int
    if thermophysical_props is not None:
        c_int = thermophysical_props.c_int

    df_temp = calc_free_float_mode(
        building=inputs,
        c_int=c_int,
        vent_rate_m3_s=vent_rate_m3_s,
        solar_gains=solar_gains,
        internal_gains=internal_gains,
        outdoor_dry_bulb_temp=outdoor_dry_bulb_temp,
    )
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    #  HEATING AND COOLING NEEDS, NO VCS (2nd SET OF CALCULATIONS)
    ###############################################################
    a_t = df["At"][0]
    lower_comfort_zone_limit = df["Lower comfort zone limit"].values
    upper_comfort_zone_limit = df["Upper comfort zone limit"].values

    df_temp = calc_heating_and_cooling_needs_no_vcs(
        building=inputs,
        c_int=c_int,
        vent_rate_m3_s=vent_rate_m3_s,
        solar_gains=solar_gains,
        internal_gains=internal_gains,
        outdoor_dry_bulb_temp=outdoor_dry_bulb_temp,
        a_t=a_t,
        lower_comfort_zone_limit=lower_comfort_zone_limit,
        upper_comfort_zone_limit=upper_comfort_zone_limit,
    )
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    # HEATING AND COOLING NEEDS, WITH VCS (3rd SET OF CALCULATIONS)
    ###############################################################
    relative_humidity_of_outdoor_air = df["Relative humidity of outdoor air"].values
    heating_cooling_load = df["Heating or cooling load"].values
    time = df["Time"].values

    df_temp = calc_heating_and_cooling_needs_with_vcs(
        building=inputs,
        c_int=c_int,
        vent_rate_m3_s=vent_rate_m3_s,
        solar_gains=solar_gains,
        internal_gains=internal_gains,
        outdoor_dry_bulb_temp=outdoor_dry_bulb_temp,
        a_t=a_t,
        lower_comfort_zone_limit=lower_comfort_zone_limit,
        upper_comfort_zone_limit=upper_comfort_zone_limit,
        relative_humidity_of_outdoor_air=relative_humidity_of_outdoor_air,
        heating_cooling_load=heating_cooling_load,
        time=time,
    )
    df = pd.concat([df, df_temp], axis=1)
    return df


def get_vent_mode_over_year(df_sim: pd.DataFrame):
    """Calculate Ventilative mode over year given results of VCT simulation."""
    df = pd.DataFrame()
    for i in range(1, 13):
        values = []
        for j in range(4):
            values.append(
                df_sim.loc[(df_sim["Month"] == i) & (df_sim["VC mode"] == j)].shape[0]
            )

        df[datetime.date(1900, i, 1).strftime("%B")] = values

    df = df.T
    for col in df.columns:
        df.loc["Year", col] = df[col].sum()

    return df


def get_requirend_frequency_air_change_rate(df_sim: pd.DataFrame, building: Building):
    """Frequency of air change rate required to provide potential comfort."""

    df = pd.DataFrame()
    df.index = ["2", "4", "6", "8", "10", "12", "14", "16", "18", ">18"]

    df_sim = df_sim.loc[df_sim["VC mode"] == 2]

    values = [
        x * 3600 / building.room_volume
        for x in df_sim["Required cooling ventilation rate (VC mode 1 or 2)"].values
    ]
    df_sim["Required cooling ventilation rate"] = values

    frequency = []
    for index, _ in df.iterrows():
        if index == ">18":
            frequency.append(
                df_sim.loc[
                    df_sim["Required cooling ventilation rate"].between(
                        18, sys.maxsize, "neither"
                    ),
                    "Required cooling ventilation rate",
                ].count()
            )
        else:
            i = int(index)
            frequency.append(
                df_sim.loc[
                    df_sim["Required cooling ventilation rate"].between(
                        i - 2, i, "right"
                    ),
                    "Required cooling ventilation rate",
                ].count()
            )

    df["frequency"] = frequency
    tot_frequency = sum(frequency)
    df["frequency_percentage"] = [x / tot_frequency for x in frequency]

    cumulative_percentage = []
    for i in range(len(frequency)):
        cumulative_percentage.append(sum(frequency[: i + 1]) / tot_frequency)
    df["cumulative_percentage"] = cumulative_percentage

    return df


def get_annual_data(df_sim: pd.DataFrame):
    """
    Heating no VCP [kWh]
    Cooling no VCP [kWh]
    Heating VCP [kWh]
    Cooling VCP [kWh]
    Top,actual temperature [°C]
    """

    df = pd.DataFrame(index=range(1, 13))
    cols = [
        "Heating no VCP",
        "Cooling no VCP",
        "Heating VCP",
        "Cooling VCP",
        "Top,actual temperature",
    ]
    df[cols] = pd.DataFrame([[None] * len(cols)], index=df.index)

    for i, _ in df.iterrows():
        value = (
            df_sim.loc[
                (df_sim["Month"] == i) & (df_sim["Heating or cooling load"] > 0)
            ]["Heating or cooling load"].sum()
            / 1000
        )
        df.loc[i, "Heating no VCP"] = value

        value = (
            df_sim.loc[
                (df_sim["Month"] == i) & (df_sim["Heating or cooling load"] < 0)
            ]["Heating or cooling load"].sum()
            / 1000
        )
        df.loc[i, "Cooling no VCP"] = abs(value)

        value = (
            df_sim.loc[
                (df_sim["Month"] == i) & (df_sim["Heating or cooling load.1"] > 0)
            ]["Heating or cooling load.1"].sum()
            / 1000
        )
        df.loc[i, "Heating VCP"] = value

        value = (
            df_sim.loc[
                (df_sim["Month"] == i) & (df_sim["Heating or cooling load.1"] < 0)
            ]["Heating or cooling load.1"].sum()
            / 1000
        )
        df.loc[i, "Cooling VCP"] = abs(value)

        value = df_sim.loc[df_sim["Month"] == i][
            "Internal temperature calculated.1"
        ].mean()
        df.loc[i, "Top,actual temperature"] = value

    return df


def run_window_design_simulation(
    win_des: WindowDesign, building: Building, df_air_change: pd.DataFrame
) -> pd.DataFrame:
    # TODO: se index ">18", in Excel c'è errore, come si dovrebbe calcolare in questo caso?
    # l17 = df_air_change.index[df_air_change['cumulative_percentage'] > 0.95].tolist()[0] # TODO: restore 0.95
    l17 = df_air_change.index[df_air_change["cumulative_percentage"] > 0.65].tolist()[0]
    if l17 == '>18':
        l17 = 20 # TODO: value if ">18"?
    else: 
        l17 = int(l17)

    max_required_airflow_rate_for_ventilative_cooling = l17 * building.room_volume
    required_airflow_rate_for_iaq = (
        building.min_req_vent_rates[1] * building.room_volume
    )
    room_height = building.celing_to_floor_height

    index_df = [
        0.25,
        0.5,
        0.75,
        1,
        1.25,
        1.5,
        1.75,
        2,
        2.25,
        2.5,
        2.75,
        3,
        3.25,
        3.5,
        3.75,
        4,
    ]
    df = pd.DataFrame(index=index_df)

    # TODO: change variable names

    col_F = df.index

    col_I = []
    for item in col_F:
        if win_des.ventilation_strategy == VENTILATION_STRATEGY[0]:
            val = (3 * required_airflow_rate_for_iaq / 3600) / (
                win_des.window_opening_discharge_coeff
                * (
                    (9.81 * win_des.indoor_outdoor_temperature_diff * item)
                    / win_des.indoor_temperature_K
                )
                ** 0.5
            )
        elif win_des.ventilation_strategy == VENTILATION_STRATEGY[1]:
            val = (2 * required_airflow_rate_for_iaq / 3600) / (
                win_des.window_opening_discharge_coeff
                * (
                    0.001 * win_des.wind_speed**2
                    + 0.0035 * item * win_des.indoor_outdoor_temperature_diff
                    + 0.01
                )
                ** 0.5
            )
        elif win_des.ventilation_strategy == VENTILATION_STRATEGY[2]:
            val = (
                (required_airflow_rate_for_iaq / 3600)
                * (2**0.5)
                / (
                    win_des.window_opening_discharge_coeff
                    * (
                        (
                            2
                            * 9.81
                            * win_des.stack_height
                            * win_des.indoor_outdoor_temperature_diff
                        )
                        / win_des.indoor_temperature_K
                    )
                    ** 0.5
                )
            )
        elif win_des.ventilation_strategy == VENTILATION_STRATEGY[3]:
            temp = win_des.wind_pressure_coeff_window_1 * Air_properties_ro * (
                win_des.wind_speed
            ) ** 2 - 2 * (
                0.5
                * Air_properties_ro
                * (win_des.wind_speed) ** 2
                * (
                    win_des.wind_pressure_coeff_window_1
                    + win_des.wind_pressure_coefficient_window_2
                )
                / 2
            )
            val = (required_airflow_rate_for_iaq / 3600) / (
                win_des.window_opening_discharge_coeff
                * (abs(temp) / Air_properties_ro) ** 0.5
            )
        col_I.append(val)

    # J
    col_J = []
    for item in col_F:
        if win_des.ventilation_strategy == VENTILATION_STRATEGY[0]:
            val = (3 * max_required_airflow_rate_for_ventilative_cooling / 3600) / (
                win_des.window_opening_discharge_coeff
                * (
                    (9.81 * win_des.indoor_outdoor_temperature_diff * item)
                    / win_des.indoor_temperature_K
                )
                ** 0.5
            )
        elif win_des.ventilation_strategy == VENTILATION_STRATEGY[1]:
            val = (2 * max_required_airflow_rate_for_ventilative_cooling / 3600) / (
                win_des.window_opening_discharge_coeff
                * (
                    0.001 * win_des.wind_speed**2
                    + 0.0035 * item * win_des.indoor_outdoor_temperature_diff
                    + 0.01
                )
                ** 0.5
            )
        elif win_des.ventilation_strategy == VENTILATION_STRATEGY[2]:
            val = (
                (max_required_airflow_rate_for_ventilative_cooling / 3600)
                * (2**0.5)
                / (
                    win_des.window_opening_discharge_coeff
                    * (
                        (
                            2
                            * 9.81
                            * win_des.stack_height
                            * win_des.indoor_outdoor_temperature_diff
                        )
                        / win_des.indoor_temperature_K
                    )
                    ** 0.5
                )
            )
        elif win_des.ventilation_strategy == VENTILATION_STRATEGY[3]:
            temp = win_des.wind_pressure_coeff_window_1 * Air_properties_ro * (
                win_des.wind_speed
            ) ** 2 - 2 * (
                0.5
                * Air_properties_ro
                * (win_des.wind_speed) ** 2
                * (
                    win_des.wind_pressure_coeff_window_1
                    + win_des.wind_pressure_coefficient_window_2
                )
                / 2
            )
            val = (max_required_airflow_rate_for_ventilative_cooling / 3600) / (
                win_des.window_opening_discharge_coeff
                * (abs(temp) / Air_properties_ro) ** 0.5
            )
        col_J.append(val)

    # K
    col_H = []
    for index, val_j in zip(df.index, col_J):
        col_H.append((val_j / index) / index)

    col_G = []
    for index, val_i in zip(df.index, col_I):
        col_G.append((val_i / index) / index)

    const_index_window_opening = [10, 20, 30, 45, 60, 90]
    const_index_whmax = [0.0, 0.4, 0.5, 0.9, 1.0, 2.0, 2.1]

    temp = 1
    if win_des.has_insect_screen:
        temp = 0.9

    col_K = []
    row_index = bisect.bisect_left(
        const_index_window_opening, win_des.window_maximum_opening_angle
    )
    row_index = -1 if row_index == len(const_index_window_opening) else row_index
    for h in col_H:
        col_index = bisect.bisect_left(const_index_whmax, h)
        col_index = -1 if col_index == len(const_index_whmax) else col_index
        k = WINDOW_DESIGN_CV[row_index][col_index] * temp
        col_K.append(k)

    col_L = []
    for g in col_G:
        col_index = bisect.bisect_left(const_index_whmax, g)
        col_index = -1 if col_index == len(const_index_whmax) else col_index
        l = WINDOW_DESIGN_CV[row_index][col_index] * temp
        col_L.append(l)

    col_M = []
    for j, k in zip(col_J, col_K):
        col_M.append(j / k)

    col_N = []
    for i, l in zip(col_I, col_L):
        col_N.append(i / l)

    col_O = []
    for m in col_M:
        col_O.append(m / building.floor_area)

    col_P = []
    for m, f in zip(col_M, col_F):
        col_P.append(m / f)

    col_Q = []
    for n, f in zip(col_N, col_F):
        col_Q.append(n / f)

    # TODO: change column names
    df["col_G"] = col_G
    df["col_H"] = col_H
    df["col_I"] = col_I
    df["col_J"] = col_J
    df["col_K"] = col_K
    df["col_L"] = col_L
    df["col_M"] = col_M
    df["col_N"] = col_N
    df["col_O"] = col_O
    df["col_P"] = col_P
    df["col_Q"] = col_Q

    return df
