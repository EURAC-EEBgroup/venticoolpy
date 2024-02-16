import pandas as pd
import os
from statistics import mean
import datetime


try:
    from vctlib.constant import get_TminK, get_TmaxK
    from vctlib.constant import Ti_csp, Air_properties_Cp, Air_properties_ro
    from vctlib.model import Building
except:
    import os
    import sys
    sys.path.insert(1, '/home/osomova/Projects/vct/vctlib/src')
    from vctlib.constant import get_TminK, get_TmaxK
    from vctlib.constant import Ti_csp, Air_properties_Cp, Air_properties_ro
    from vctlib.model import Building


TOT_HOURS = 9504 # Total hours in simulation = December + 1 year -> (31+365)*24
HOURS_IN_YEAR = 8760 # 365*24
TOT_DAYS = 396 # 31 + 365
DAYS_IN_YEAR = 365



def get_simulation_year() -> pd.DataFrame:
    """ Create a DataFrame for a sumulation of lenght equal to December month + 1 standard year
        
        Returns: 
            pd.DataFrame with: 
            - Date
            - Month
            - Day
            - Time: integer (1, 2, ..., 24)
    """
    df = pd.DataFrame(index = range(TOT_HOURS))
    dates = pd.concat([
        pd.Series(pd.date_range(start='2011-12-01', end='{}-01-01'.format(2012), freq='h'))[0:744],
        pd.Series(pd.date_range(start='2011-01-01', end='{}-01-01'.format(2012), freq='h'))[0:8760],
    ])
    df['Date'] = dates.values

    df['Month'] = [d.month for d in dates]
    df['Day'] = [d.day for d in dates]
    df['Time'] = [d.hour+1 for d in dates]

    return df



def get_outdoor_climate_data() -> pd.DataFrame:
    """ Retrieve outdoor climate data.

    Parameters:
    ...

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
        - Outdoor dry-bulb temperature.  θe;a [°C]
        - Relative humidity of outdoor air.  ΦHU;e;a;t [%]
        - Daily mean outdoor temperature.  θe;a;mean [°C]
    """

    df = pd.DataFrame(index=range(TOT_HOURS))

    df['Outdoor dry-bulb temperature'] = pd.read_csv(os.path.join(os.getcwd(),'src/vctlib/temp_data/outdor_dry_bulb_temperature.csv'))
    outdoor_dry_bulb_temp = df['Outdoor dry-bulb temperature'].values

    df['Relative humidity of outdoor air'] = pd.read_csv('src/vctlib/temp_data/outdor_climate_data.csv')

    daily_mean_outdoor_temp = []
    for i in range(0, TOT_HOURS, 24):
        val = mean(outdoor_dry_bulb_temp[i:i+24])
        daily_mean_outdoor_temp.extend([val]*24)
    df['Daily mean outdoor temperature'] = daily_mean_outdoor_temp

    return df

    

def calc_thermal_comfort_data(
    building: Building, daily_mean_outdoor_temp
) -> pd.DataFrame:
    """ Calculate Thermal comfort data.
    
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
        val = (temp[i-24] + \
            temp[i-48]*0.8 +\
            temp[i-72]*0.6 +\
            temp[i-96]*0.5 +\
            temp[i-120]*0.4 +\
            temp[i-144]*0.3 +\
            temp[i-168]*0.2)/3.8
        outdoor_runnin_mean_temperature.extend([val]*24)

    full_year = outdoor_runnin_mean_temperature[-744:]
    full_year.extend(outdoor_runnin_mean_temperature)

    df['Outdoor runnin mean temperature'] = full_year

    T_minK = get_TminK(building.comfort_requirements)
    Ti_hsp_night = 10 #AF25
    Ti_hsp_day = T_minK[building.bui_type] #AF26

    #TODO Ti_hsp_night, Ti_hsp_day move to Building class
    # es from 23:00 to 7:00 -> Ti_hsp_night, from 7:00 to 23:00 -> Ti_hsp_day

    temp = [Ti_hsp_night]*7 + [Ti_hsp_day]*17
    lower_comfort_zone_limit = temp * TOT_DAYS

    upper_comfort_zone_limit = [Ti_csp] * TOT_HOURS

    temp = [mean([Ti_hsp_night, Ti_csp])]*7 + [mean([Ti_hsp_day, Ti_csp])]*17
    comfort_temperature = temp * TOT_DAYS

    df['Comfort temperature'] = comfort_temperature
    df['Lower comfort zone limit'] = lower_comfort_zone_limit
    df['Upper comfort zone limit'] = upper_comfort_zone_limit

    return df



def get_gains(building: Building) -> pd.DataFrame:
    """ Calculate solar and internal gains.

    Patameters: 
        - building obj

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
        - Solar gains.  Φsol [W/m²]
        - Internal gains.  Φint [W/m²]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    isol_tot = pd.read_csv(os.path.join(os.getcwd(),'src/vctlib/temp_data/isol_tot.csv'))
    isol_tot = isol_tot.iloc[:,0].values

    solar_gains = [
        x*(1-building.shading_factor)*building.g_value_glazing_sys*building.fenestration_area/building.floor_area
        for x in isol_tot
    ]
    df['Solar gains'] = solar_gains

    internal_gains = [200/building.floor_area] * TOT_HOURS #TODO 200 is const?
    df['Internal gains'] = internal_gains

    return df



def get_ventilation_rate(building:Building) -> pd.DataFrame:
    """ Calculate Ventilation rates.

    Parameters: 
        - building obj

    Returns:
        pd.DataFrame: A DataFrame with hourly values of:
        - Ventilation rate.  qV;t [m3/s]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    vent_rate_m3_s = building.min_req_vent_rates[0] * building.floor_area / 1000
    ventilation_rate = [vent_rate_m3_s] * TOT_HOURS
    df['Ventilation rate'] = ventilation_rate

    return df



def calc_free_float_mode(
    building: Building, 
    vent_rate_m3_s, 
    solar_gains, 
    internal_gains,
    outdoor_dry_bulb_temp
) -> pd.DataFrame:
    """ Performs the first set of calculations (Free Float Mode).

    Parameters: 
        - building obj
        - vent_rate_m3_s: ventilation rate [m³/s]
        - solar_gains: A list with hourly values of solar gains
        - internal_gains: A list with hourly values of internal gains
        - outdoor_dry_bulb_temp: A list with hourly values of Outdoor dry bulb temperature 
        All parameters (except building) are the outputs of the previous steps.

    Returns: 
        pd.DataFrame: A DataFrame with hourly values of: 
        - At [W/K]
        - Bt [W]
        - Internal temperature free float.  ϴint;0;t [°C]
        - Internal temperature calculated.  ϴint;t [°C]
    """
    df = pd.DataFrame(index=range(TOT_HOURS))

    # TODO thermostatical_properties -> formula?
    thermostatical_properties_P7 = 15479951.7120
    Cint = thermostatical_properties_P7 + 10000 * building.floor_area #C36

    At = Cint/3600 + (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s) + building.average_u_value*building.envelope_area
    # 0.5024087248366400000 # Excel
    # 0.5024087248366397    # Python

    internal_temperature_free_float = [None] * TOT_HOURS
    Bt = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        if i == 0:
            internal_temperature_free_float[0] = 20 # set first value

            Bt[0] = Cint/3600*internal_temperature_free_float[0] +\
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s+building.average_u_value*building.envelope_area)*outdoor_dry_bulb_temp[0]+\
                (solar_gains[0]+internal_gains[0])*building.floor_area
        else:
            Bt[i] = Cint/3600*internal_temperature_free_float[i-1] +\
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s+building.average_u_value*building.envelope_area)*outdoor_dry_bulb_temp[i]+\
                (solar_gains[i]+internal_gains[i])*building.floor_area

            internal_temperature_free_float[i] = Bt[i]/At

    df['At'] = [At] * TOT_HOURS
    df['Bt'] = Bt
    df['Internal temperature free float'] = internal_temperature_free_float
    df['Internal temperature calculated'] = internal_temperature_free_float

    return df



def calc_heating_and_cooling_needs_no_vcs(
    building: Building,
    vent_rate_m3_s,
    solar_gains,
    internal_gains,
    outdoor_dry_bulb_temp,
    At,
    lower_comfort_zone_limit,
    upper_comfort_zone_limit,
) -> pd.DataFrame:
    """ Performs the second set of calculations (Heating and Cooling needs, no VCS).

    Parameters: 
        - building obj
        - vent_rate_m3_s: ventilation rate [m³/s]
        - solar_gains: A list with hourly values of solar gains
        - internal_gains: A list with hourly values of internal gains
        - outdoor_dry_bulb_temp: A list with hourly values of Outdoor dry bulb temperature 
        - At: value of At
        - lower_comfort_zone_limit: A list with hourly values of Lower comfort zone limit
        - upper_comfort_zone_limit: A list with hourly values of Upper comfort zone limit
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

    Bt_no_vcs = [None]*TOT_HOURS
    internal_temperature_free_float_no_vcs = [None]*TOT_HOURS
    heating_cooling_load = [None]*TOT_HOURS
    internal_temperature_calc = [None]*TOT_HOURS

    thermostatical_properties_P7 = 15479951.7120
    Cint = thermostatical_properties_P7 + 10000 * building.floor_area

    for i in range(TOT_HOURS):
        if i == 0:
            internal_temperature_free_float_no_vcs[0] = 20
            Bt_no_vcs[0] = Cint/3600*internal_temperature_free_float_no_vcs[0] +\
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s + building.average_u_value*building.envelope_area)*outdoor_dry_bulb_temp[0]+\
                (solar_gains[0] + internal_gains[0])*building.floor_area

        else:
            Bt_no_vcs[i] = Cint/3600*internal_temperature_calc[i-1] +\
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s + building.average_u_value*building.envelope_area)*outdoor_dry_bulb_temp[i]+\
                (solar_gains[i] + internal_gains[i])*building.floor_area

            internal_temperature_free_float_no_vcs[i] = Bt_no_vcs[i]/At

        if internal_temperature_free_float_no_vcs[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load[i] = At*lower_comfort_zone_limit[i] - Bt_no_vcs[i]
        elif (
            internal_temperature_free_float_no_vcs[i]>=lower_comfort_zone_limit[i] and
            internal_temperature_free_float_no_vcs[i]<=upper_comfort_zone_limit[i]
        ):
            heating_cooling_load[i] = 0
        elif internal_temperature_free_float_no_vcs[i]>upper_comfort_zone_limit[i]:
            heating_cooling_load[i] = At*upper_comfort_zone_limit[i]-Bt_no_vcs[i]

        internal_temperature_calc[i] = (Bt_no_vcs[i] + heating_cooling_load[i])/At

    df['Ventilation rate.1'] = [vent_rate_m3_s] * TOT_HOURS
    df['At.1'] = [At] * TOT_HOURS
    df['Bt.1'] = Bt_no_vcs
    df['Internal temperature free float.1'] = internal_temperature_free_float_no_vcs
    df['Heating or cooling load'] = heating_cooling_load
    df['Internal temperature calculated.1'] = internal_temperature_calc

    return df
    


def calc_heating_and_cooling_needs_with_vcs(
    building: Building,
    vent_rate_m3_s,
    solar_gains,
    internal_gains,
    outdoor_dry_bulb_temp,
    At,
    lower_comfort_zone_limit,
    upper_comfort_zone_limit,
    relative_humidity_of_outdoor_air,
    heating_cooling_load,
    time
) -> pd.DataFrame:
    """ Performs the third set of calculations (Heating and Cooling needs, with VCS).

    Parameters: 
        - building obj
        - vent_rate_m3_s: ventilation rate [m³/s]
        - solar_gains: A list with hourly values of solar gains
        - internal_gains: A list with hourly values of internal gains
        - outdoor_dry_bulb_temp: A list with hourly values of Outdoor dry bulb temperature 
        - At: value of At
        - lower_comfort_zone_limit: A list with hourly values of Lower comfort zone limit
        - upper_comfort_zone_limit: A list with hourly values of Upper comfort zone limit
        - relative_humidity_of_outdoor_air: A list with hourly values of Relative humidity of outdoor air
        - heating_cooling_load: A list with hourly values of Heating or cooling load
        - time: A list with hourly values. A set of (1, 2, .., 24) for each day of simulation
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
                - Required cooling ventilation rate (VC mode 1 or 2).  ΔqV;vcs;req;t [m3/s]
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

    internal_temperature_free_float_with_vcs = [None] * TOT_HOURS
    Bt_with_vcs = [None] * TOT_HOURS
    heating_cooling_load_with_vcs = [None] * TOT_HOURS
    internal_temperature_calc_with_vcs = [None] * TOT_HOURS

    thermostatical_properties_P7 = 15479951.7120
    Cint = thermostatical_properties_P7 + 10000 * building.floor_area

    for i in range(TOT_HOURS):
        if i == 0:
            internal_temperature_free_float_with_vcs[0] = 20

            Bt_with_vcs[0] = Cint/3600*internal_temperature_free_float_with_vcs[0] + \
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s + building.average_u_value*building.envelope_area)*outdoor_dry_bulb_temp[0] +\
                (solar_gains[0] + internal_gains[0])*building.floor_area

        else:
            Bt_with_vcs[i] = Cint/3600*internal_temperature_calc_with_vcs[i-1] + \
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s + building.average_u_value*building.envelope_area)*outdoor_dry_bulb_temp[i] +\
                (solar_gains[i] + internal_gains[i])*building.floor_area

            internal_temperature_free_float_with_vcs[i] = Bt_with_vcs[i]/At

        if internal_temperature_free_float_with_vcs[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load_with_vcs[i] = At*lower_comfort_zone_limit[i] - Bt_with_vcs[i]
        elif (internal_temperature_free_float_with_vcs[i]>=lower_comfort_zone_limit[i]) and \
            (internal_temperature_free_float_with_vcs[i]<upper_comfort_zone_limit[i]):
            heating_cooling_load_with_vcs[i] = 0
        elif internal_temperature_free_float_with_vcs[i] > upper_comfort_zone_limit[i]:
            heating_cooling_load_with_vcs[i] = At*upper_comfort_zone_limit[i] - Bt_with_vcs[i]

        internal_temperature_calc_with_vcs[i] = (Bt_with_vcs[i] + heating_cooling_load_with_vcs[i])/At

    df['Ventilation rate without VCS'] = [vent_rate_m3_s]*TOT_HOURS
    df['At.2'] = [At] * TOT_HOURS
    df['Bt.2'] = Bt_with_vcs
    df['Internal temperature free float.2'] = internal_temperature_free_float_with_vcs
    df['Heating or cooling load "step 2"'] = heating_cooling_load_with_vcs
    df['Internal temperature calculated "Step2"'] = internal_temperature_calc_with_vcs

    vc_mode = [None] * TOT_HOURS
    delta_theta_crit = 3 #AF28
    for i in range(TOT_HOURS):
        if (time[i] >= building.time_control_on) and (time[i] <= building.time_control_off):
            if internal_temperature_free_float_with_vcs[i] < lower_comfort_zone_limit[i]:
                vc_mode[i] = 0
            elif (internal_temperature_free_float_with_vcs[i] >= lower_comfort_zone_limit[i]) and \
                    (internal_temperature_free_float_with_vcs[i] <= upper_comfort_zone_limit[i]):
                vc_mode[i] = 1
            elif (internal_temperature_free_float_with_vcs[i] > upper_comfort_zone_limit[i]) and \
                    (outdoor_dry_bulb_temp[i] <= (upper_comfort_zone_limit[i] - delta_theta_crit)) and \
                    (relative_humidity_of_outdoor_air[i] < building.max_outdoor_rel_hum_accepted):
                vc_mode[i] = 2
            else:
                vc_mode[i] = 3
        else:
            vc_mode[i] = None

    df['VC mode'] = vc_mode

    required_cooling_vent_rate = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        if vc_mode[i] == 2:
            required_cooling_vent_rate[i] = (Bt_with_vcs[i] - At*Ti_csp)/ \
                (Air_properties_Cp*Air_properties_ro*(Ti_csp - outdoor_dry_bulb_temp[i]))
        else:
            required_cooling_vent_rate[i] = 0

    actual_ventilation_rate = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        if vc_mode[i] == 2:
            actual_ventilation_rate[i] = required_cooling_vent_rate[i] + vent_rate_m3_s
        else:
            actual_ventilation_rate[i] = vent_rate_m3_s

    Avcs_t = [None]* TOT_HOURS
    for i in range(TOT_HOURS):
        Avcs_t[i] = Cint/3600 + \
            Air_properties_Cp*Air_properties_ro*actual_ventilation_rate[i] + \
            building.average_u_value*building.envelope_area

    Bvcs_t = [None] * TOT_HOURS
    internal_temperature_free_s4 = [None] * TOT_HOURS # s4 aka step 4
    heating_cooling_load_s4 = [None] * TOT_HOURS
    internal_temperature_calc_s4 = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        if i == 0:
            internal_temperature_free_s4[0] = 20
            Bvcs_t[0] = Cint/3600*internal_temperature_free_s4[0] + \
                (Air_properties_Cp*Air_properties_ro*actual_ventilation_rate[0] + building.average_u_value*building.envelope_area)*outdoor_dry_bulb_temp[0] + \
                (solar_gains[0] + internal_gains[0])*building.floor_area
        else:
            Bvcs_t[i] = Cint/3600*internal_temperature_calc_s4[i-1] + \
                (Air_properties_Cp*Air_properties_ro*actual_ventilation_rate[i] + building.average_u_value*building.envelope_area)*outdoor_dry_bulb_temp[i] + \
                (solar_gains[i] + internal_gains[i])*building.floor_area

            internal_temperature_free_s4[i] = Bvcs_t[i]/Avcs_t[i]

        if internal_temperature_free_s4[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load_s4[i] = Avcs_t[i]*lower_comfort_zone_limit[i] - Bvcs_t[i]
        elif (internal_temperature_free_s4[i]>=lower_comfort_zone_limit[i]) and \
            (internal_temperature_free_s4[i]<=upper_comfort_zone_limit[i]):
            heating_cooling_load_s4[i] = 0 
        elif internal_temperature_free_s4[i] > upper_comfort_zone_limit[i]:
            heating_cooling_load_s4[i] = Avcs_t[i]*upper_comfort_zone_limit[i] - Bvcs_t[i]

        internal_temperature_calc_s4[i] = (Bvcs_t[i] + heating_cooling_load_s4[i])/Avcs_t[i]


    HC_load_difference = [None] * TOT_HOURS
    for i in range(TOT_HOURS):
        HC_load_difference[i] = -(heating_cooling_load[i] - heating_cooling_load_s4[i])

    df['Required cooling ventilation rate (VC mode 1 or 2)'] = required_cooling_vent_rate
    df['Actual ventilation rate'] = actual_ventilation_rate
    df['Avcs;t'] = Avcs_t
    df['Bvcs;t'] = Bvcs_t
    df['Internal temperature free float.3'] = internal_temperature_free_s4
    df['Heating or cooling load.1'] = heating_cooling_load_s4
    df['Internal temperature calculated.2'] = internal_temperature_calc_s4
    df['HC load difference'] = HC_load_difference
    df['Target indoor temperature for VCS'] = [Ti_csp] * TOT_HOURS

    return df



def run_vct_simulation(inputs: Building) -> pd.DataFrame:

    df = get_simulation_year()

    ###############################################################
    #                 OUTDOOR CLIMATE DATA
    ###############################################################
    df_temp = get_outdoor_climate_data()
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    #                 THERMAL COMFORT DATA
    ###############################################################
    df_temp = calc_thermal_comfort_data(inputs, df['Daily mean outdoor temperature'].values)
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    #                         GAINS
    ###############################################################
    df_temp = get_gains(inputs)
    df = pd.concat([df, df_temp], axis=1)

    df_temp = get_ventilation_rate(inputs)
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    #           FREE FLOAT MODE (1st SET OF CALCULATIONS)
    ###############################################################
    vent_rate_m3_s=df['Ventilation rate'][0]
    solar_gains=df['Solar gains'].values
    internal_gains=df['Internal gains'].values
    outdoor_dry_bulb_temp=df['Outdoor dry-bulb temperature'].values
    
    df_temp = calc_free_float_mode(
        building=inputs,
        vent_rate_m3_s=vent_rate_m3_s,
        solar_gains=solar_gains,
        internal_gains=internal_gains,
        outdoor_dry_bulb_temp=outdoor_dry_bulb_temp
    )
    df = pd.concat([df, df_temp], axis=1)

    ###############################################################
    #  HEATING AND COOLING NEEDS, NO VCS (2nd SET OF CALCULATIONS)
    ###############################################################
    At=df['At'][0]
    lower_comfort_zone_limit=df['Lower comfort zone limit'].values
    upper_comfort_zone_limit=df['Upper comfort zone limit'].values
    
    df_temp = calc_heating_and_cooling_needs_no_vcs(
        building=inputs,
        vent_rate_m3_s=vent_rate_m3_s,
        solar_gains=solar_gains,
        internal_gains=internal_gains,
        outdoor_dry_bulb_temp=outdoor_dry_bulb_temp,
        At=At,
        lower_comfort_zone_limit=lower_comfort_zone_limit,
        upper_comfort_zone_limit=upper_comfort_zone_limit,
    )
    df = pd.concat([df, df_temp], axis=1)
    
    ###############################################################
    # HEATING AND COOLING NEEDS, WITH VCS (3rd SET OF CALCULATIONS)
    ###############################################################
    relative_humidity_of_outdoor_air = df['Relative humidity of outdoor air'].values
    heating_cooling_load = df['Heating or cooling load'].values
    time = df['Time'].values
    
    df_temp = calc_heating_and_cooling_needs_with_vcs(
        building=inputs,
        vent_rate_m3_s=vent_rate_m3_s,
        solar_gains=solar_gains,
        internal_gains=internal_gains,
        outdoor_dry_bulb_temp=outdoor_dry_bulb_temp,
        At=At,
        lower_comfort_zone_limit=lower_comfort_zone_limit,
        upper_comfort_zone_limit=upper_comfort_zone_limit,
        relative_humidity_of_outdoor_air=relative_humidity_of_outdoor_air,
        heating_cooling_load=heating_cooling_load,
        time=time
    )
    df = pd.concat([df, df_temp], axis=1)

    return df




def get_vent_mode_over_year(df: pd.DataFrame):
    df_vent = pd.DataFrame()
    df = df[744:] # remove additional month
    for i in range(1,13):
        values = []
        for j in range(4):
            values.append(df.loc[(df['Month'] == i) & (df['VC mode'] == j)].shape[0])
        
        df_vent[datetime.date(1900, i, 1).strftime('%B')] = values

    df_vent = df_vent.T
    for col in df_vent.columns:
        df_vent.loc["Year", col] = df_vent[col].sum()

    return df_vent


# TODO: chidere a GDM come calcolare la radiazione incidente diretta indiretta sulle facciare dell'edificio 
# input: radiazione tot orizzontale
# output desiderato: radiazione per 8 orientamenti

inputsobj = Building(
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

# run_vct_simulation(inputsobj)