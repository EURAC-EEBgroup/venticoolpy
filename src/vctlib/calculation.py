import pandas as pd
import os
from statistics import mean
import datetime

from vctlib.constant import get_TminK, get_TmaxK
from vctlib.constant import Ti_csp, Air_properties_Cp, Air_properties_ro
from vctlib.model import Input



def get_main_dataframe(inputs: Input):

    df = pd.DataFrame()
    dates = pd.concat([
        pd.Series(pd.date_range(start='2011-12-01', end='{}-01-01'.format(2012), freq='h'))[0:744],
        pd.Series(pd.date_range(start='2011-01-01', end='{}-01-01'.format(2012), freq='h'))[0:8760],
    ])

    df['Date'] = dates
    df.index = range(df.shape[0])

    df['Month'] = [d.month for d in dates]
    df['Day'] = [d.day for d in dates]
    df['Time'] = [d.hour+1 for d in dates]

    ###############################################################
    #                 OUTDOOR CLIMATE DATA
    ###############################################################
    df['Outdoor dry-bulb temperature'] = pd.read_csv(os.path.join(os.getcwd(),'src/vctlib/temp_data/outdor_dry_bulb_temperature.csv'))

    df['Relative humidity of outdoor air'] = pd.read_csv('src/vctlib/temp_data/outdor_climate_data.csv')
    relative_humidity_of_outdoor_air = df['Relative humidity of outdoor air'].values

    year_lenght = 8760
    sim_lenght = 9504
    daily_mean_outdoor_temp = []
    time = df['Time'].values
    outdoor_dry_bulb_temp = df['Outdoor dry-bulb temperature'].values
    for i in range(0, sim_lenght, 24):
        val = mean(outdoor_dry_bulb_temp[i:i+24])
        daily_mean_outdoor_temp.extend([val]*24)
    df['Daily mean outdoor temperature'] = daily_mean_outdoor_temp


    ###############################################################
    #                 THERMAL COMFORT DATA
    ###############################################################

    outdoor_runnin_mean_temperature = []
    temp = daily_mean_outdoor_temp[744:]
    for i in range(0, year_lenght, 24):
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

    T_minK = get_TminK(inputs.comfort_requirements)
    T_maxK = get_TmaxK(inputs.comfort_requirements)
    Ti_hsp_night = 10 #AF25
    Ti_hsp_day = T_minK[inputs.bui_type] #AF26

    #TODO Ti_hsp_night, Ti_hsp_day move to Input class
    # es from 23:00 to 7:00 -> Ti_hsp_night, from 7:00 to 23:00 -> Ti_hsp_day

    temp = [Ti_hsp_night]*7 + [Ti_hsp_day]*17
    sim_days = 31 + 365
    lower_comfort_zone_limit = temp * sim_days

    upper_comfort_zone_limit = [Ti_csp] * sim_lenght

    temp = [mean([Ti_hsp_night, Ti_csp])]*7 + [mean([Ti_hsp_day, Ti_csp])]*17
    comfort_temperature = temp * sim_days
    df['Comfort temperature'] = comfort_temperature
    df['Lower comfort zone limit'] = lower_comfort_zone_limit
    df['Upper comfort zone limit'] = upper_comfort_zone_limit


    ###############################################################
    #                         GAINS
    ###############################################################

    isol_tot = pd.read_csv(os.path.join(os.getcwd(),'src/vctlib/temp_data/isol_tot.csv'))
    isol_tot = isol_tot.iloc[:,0].values
    solar_gains = [
        x*(1-inputs.shading_factor)*inputs.g_value_glazing_sys*inputs.fenestration_area/inputs.floor_area
        for x in isol_tot
    ]
    df['Solar gains'] = solar_gains

    internal_gains = [200/inputs.floor_area] * sim_lenght #TODO 200 is const?
    df['Internal gains'] = internal_gains

    vent_rate_m3_s = inputs.min_req_vent_rates[0] * inputs.floor_area / 1000
    ventilation_rate = [vent_rate_m3_s] * sim_lenght
    df['Ventilation rate'] = ventilation_rate


    ###############################################################
    #           FREE FLOAT MODE (1st SET OF CALCULATIONS)
    ###############################################################
    At = []
    # TODO thermostatical_properties -> formula?
    thermostatical_properties_P7 = 15479951.7120
    Cint = thermostatical_properties_P7 + 10000 * inputs.floor_area #C36

    val = Cint/3600 + (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s) + inputs.average_u_value*inputs.envelope_area
    At = [val] * sim_lenght
    df['At'] = At
    # 0.5024087248366400000 # Excel
    # 0.5024087248366397    # Python

    # Internal temperature free float
    internal_temperature_free_float = [None] * sim_lenght

    Bt = [None]*sim_lenght
    for i in range(sim_lenght):
        if i == 0:
            internal_temperature_free_float[0] = 20 # set first value

            Bt[0] = Cint/3600*internal_temperature_free_float[0] +\
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s+inputs.average_u_value*inputs.envelope_area)*outdoor_dry_bulb_temp[0]+\
                (solar_gains[0]+internal_gains[0])*inputs.floor_area
        else:
            Bt[i] = Cint/3600*internal_temperature_free_float[i-1] +\
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s+inputs.average_u_value*inputs.envelope_area)*outdoor_dry_bulb_temp[i]+\
                (solar_gains[i]+internal_gains[i])*inputs.floor_area

            internal_temperature_free_float[i] = Bt[i]/At[0]

    df['Bt'] = Bt
    df['Internal temperature free float'] = internal_temperature_free_float
    df['Internal temperature calculated'] = internal_temperature_free_float


    ###############################################################
    #  HEATING AND COOLING NEEDS, NO VCS (2nd SET OF CALCULATIONS)
    ###############################################################

    df['Ventilation rate.1'] = [vent_rate_m3_s] * sim_lenght
    df['At.1'] = df['At']
    Bt_no_vcs = [None]*sim_lenght # Y
    internal_temperature_free_float_no_vcs = [None]*sim_lenght # Z
    heating_cooling_load = [None]*sim_lenght # AA
    internal_temperature_calc = [None]*sim_lenght # AB

    for i in range(sim_lenght):
        if i == 0:
            internal_temperature_free_float_no_vcs[0] = 20
            Bt_no_vcs[0] = Cint/3600*internal_temperature_free_float_no_vcs[0] +\
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s + inputs.average_u_value*inputs.envelope_area)*outdoor_dry_bulb_temp[0]+\
                (solar_gains[0] + internal_gains[0])*inputs.floor_area

        else:
            Bt_no_vcs[i] = Cint/3600*internal_temperature_calc[i-1] +\
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s + inputs.average_u_value*inputs.envelope_area)*outdoor_dry_bulb_temp[i]+\
                (solar_gains[i] + internal_gains[i])*inputs.floor_area

            internal_temperature_free_float_no_vcs[i] = Bt_no_vcs[i]/At[i]

        if internal_temperature_free_float_no_vcs[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load[i] = At[i]*lower_comfort_zone_limit[i] - Bt_no_vcs[i]
        elif (
            internal_temperature_free_float_no_vcs[i]>=lower_comfort_zone_limit[i] and
            internal_temperature_free_float_no_vcs[i]<=upper_comfort_zone_limit[i]
        ):
            heating_cooling_load[i] = 0
        elif internal_temperature_free_float_no_vcs[i]>upper_comfort_zone_limit[i]:
            heating_cooling_load[i] = At[i]*upper_comfort_zone_limit[i]-Bt_no_vcs[i]

        internal_temperature_calc[i] = (Bt_no_vcs[i] + heating_cooling_load[i])/At[i]

    df['Bt.1'] = Bt_no_vcs
    df['Internal temperature free float.1'] = internal_temperature_free_float_no_vcs
    df['Heating or cooling load'] = heating_cooling_load
    df['Internal temperature calculated.1'] = internal_temperature_calc
    
    ###############################################################
    # HEATING AND COOLING NEEDS, WITH VCS (3rd SET OF CALCULATIONS)
    ###############################################################

    internal_temperature_free_float_with_vcs = [None] * sim_lenght
    Bt_with_vcs = [None] * sim_lenght
    heating_cooling_load_with_vcs = [None] * sim_lenght
    internal_temperature_calc_with_vcs = [None] * sim_lenght
    for i in range(sim_lenght):
        if i == 0:
            internal_temperature_free_float_with_vcs[0] = 20

            Bt_with_vcs[0] = Cint/3600*internal_temperature_free_float_with_vcs[0] + \
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s + inputs.average_u_value*inputs.envelope_area)*outdoor_dry_bulb_temp[0] +\
                (solar_gains[0] + internal_gains[0])*inputs.floor_area

        else:
            Bt_with_vcs[i] = Cint/3600*internal_temperature_calc_with_vcs[i-1] + \
                (Air_properties_Cp*Air_properties_ro*vent_rate_m3_s + inputs.average_u_value*inputs.envelope_area)*outdoor_dry_bulb_temp[i] +\
                (solar_gains[i] + internal_gains[i])*inputs.floor_area

            internal_temperature_free_float_with_vcs[i] = Bt_with_vcs[i]/At[i]

        if internal_temperature_free_float_with_vcs[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load_with_vcs[i] = At[i]*lower_comfort_zone_limit[i] - Bt_with_vcs[i]
        elif (internal_temperature_free_float_with_vcs[i]>=lower_comfort_zone_limit[i]) and \
            (internal_temperature_free_float_with_vcs[i]<upper_comfort_zone_limit[i]):
            heating_cooling_load_with_vcs[i] = 0
        elif internal_temperature_free_float_with_vcs[i] > upper_comfort_zone_limit[i]:
            heating_cooling_load_with_vcs[i] = At[i]*upper_comfort_zone_limit[i] - Bt_with_vcs[i]

        internal_temperature_calc_with_vcs[i] = (Bt_with_vcs[i] + heating_cooling_load_with_vcs[i])/At[i]

    df['Ventilation rate without VCS'] = [vent_rate_m3_s]*sim_lenght
    df['At.2'] = df['At']
    df['Bt.2'] = Bt_with_vcs
    df['Internal temperature free float.2'] = internal_temperature_free_float_with_vcs
    df['Heating or cooling load "step 2"'] = heating_cooling_load_with_vcs
    df['Internal temperature calculated "Step2"'] = internal_temperature_calc_with_vcs

    vc_mode = [None] * sim_lenght
    delta_theta_crit = 3 #AF28
    for i in range(sim_lenght):
        if (time[i] >= inputs.time_control_on) and (time[i] <= inputs.time_control_off):
            if internal_temperature_free_float_with_vcs[i] < lower_comfort_zone_limit[i]:
                vc_mode[i] = 0
            elif (internal_temperature_free_float_with_vcs[i] >= lower_comfort_zone_limit[i]) and \
                    (internal_temperature_free_float_with_vcs[i] <= upper_comfort_zone_limit[i]):
                vc_mode[i] = 1
            elif (internal_temperature_free_float_with_vcs[i] > upper_comfort_zone_limit[i]) and \
                    (outdoor_dry_bulb_temp[i] <= (upper_comfort_zone_limit[i] - delta_theta_crit)) and \
                    (relative_humidity_of_outdoor_air[i] < inputs.max_outdoor_rel_hum_accepted):
                vc_mode[i] = 2
            else:
                vc_mode[i] = 3
        else:
            vc_mode[i] = None

    df['VC mode'] = vc_mode

    target_indoor_temperature_vcs_at = [Ti_csp] * sim_lenght

    required_cooling_vent_rate = [None] * sim_lenght
    for i in range(sim_lenght):
        if vc_mode[i] == 2:   # TODO:  target_indor_temperature_vcs_at == Ti_csp
            required_cooling_vent_rate[i] = (Bt_with_vcs[i] - At[i]*target_indoor_temperature_vcs_at[0])/ \
                (Air_properties_Cp*Air_properties_ro*(Ti_csp - outdoor_dry_bulb_temp[i]))
        else:
            required_cooling_vent_rate[i] = 0

    actual_ventilation_rate = [None] * sim_lenght
    for i in range(sim_lenght):
        if vc_mode[i] == 2:
            actual_ventilation_rate[i] = required_cooling_vent_rate[i] + vent_rate_m3_s
        else:
            actual_ventilation_rate[i] = vent_rate_m3_s

    Avcs_t = [None]* sim_lenght
    for i in range(sim_lenght):
        Avcs_t[i] = Cint/3600 + \
            Air_properties_Cp*Air_properties_ro*actual_ventilation_rate[i] + \
            inputs.average_u_value*inputs.envelope_area

    Bvcs_t = [None] * sim_lenght
    internal_temperature_free_s4 = [None] * sim_lenght # s4 aka step 4
    heating_cooling_load_s4 = [None] * sim_lenght
    internal_temperature_calc_s4 = [None] * sim_lenght
    for i in range(sim_lenght):
        if i == 0:
            internal_temperature_free_s4[0] = 20
            Bvcs_t[0] = Cint/3600*internal_temperature_free_s4[0] + \
                (Air_properties_Cp*Air_properties_ro*actual_ventilation_rate[0] + inputs.average_u_value*inputs.envelope_area)*outdoor_dry_bulb_temp[0] + \
                (solar_gains[0] + internal_gains[0])*inputs.floor_area
        else:
            Bvcs_t[i] = Cint/3600*internal_temperature_calc_s4[i-1] + \
                (Air_properties_Cp*Air_properties_ro*actual_ventilation_rate[i] + inputs.average_u_value*inputs.envelope_area)*outdoor_dry_bulb_temp[i] + \
                (solar_gains[i] + internal_gains[i])*inputs.floor_area

            internal_temperature_free_s4[i] = Bvcs_t[i]/Avcs_t[i]

        if internal_temperature_free_s4[i] < lower_comfort_zone_limit[i]:
            heating_cooling_load_s4[i] = Avcs_t[i]*lower_comfort_zone_limit[i] - Bvcs_t[i]
        elif (internal_temperature_free_s4[i]>=lower_comfort_zone_limit[i]) and \
            (internal_temperature_free_s4[i]<=upper_comfort_zone_limit[i]):
            heating_cooling_load_s4[i] = 0 
        elif internal_temperature_free_s4[i] > upper_comfort_zone_limit[i]:
            heating_cooling_load_s4[i] = Avcs_t[i]*upper_comfort_zone_limit[i] - Bvcs_t[i]

        internal_temperature_calc_s4[i] = (Bvcs_t[i] + heating_cooling_load_s4[i])/Avcs_t[i]


    HC_load_difference = [None] * sim_lenght
    for i in range(sim_lenght):
        HC_load_difference[i] = -(heating_cooling_load[i] - heating_cooling_load_s4[i])

    df['Required cooling ventilation rate (VC mode 1 or 2)'] = required_cooling_vent_rate
    df['Actual ventilation rate'] = actual_ventilation_rate
    df['Avcs;t'] = Avcs_t
    df['Bvcs;t'] = Bvcs_t
    df['Internal temperature free float.3'] = internal_temperature_free_s4
    df['Heating or cooling load.1'] = heating_cooling_load_s4
    df['Internal temperature calculated.2'] = internal_temperature_calc_s4
    df['HC load difference'] = HC_load_difference
    df['Target indoor temperature for VCS'] = target_indoor_temperature_vcs_at

    return df




def get_vent_mode_over_year(df):
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
