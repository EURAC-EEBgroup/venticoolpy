"""Test calculation functions."""

try:
    from vctlib.calculation import run_vct_simulation, get_climate_data_from_epw, \
        get_climate_data_from_csv, get_vent_mode_over_year, \
        get_requirend_frequency_air_change_rate, get_annual_data
    from vctlib.model import Building, ThermostaticalProperties
except ModuleNotFoundError: # TODO: remove try-except
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


def test_snapshot_building_simulation(snapshot):
    """Test Appartment building."""
    thermophys_prop = ThermostaticalProperties(
        external_wall_area=9.6+16.2+16.2+21.6,
        floor_area=6*8,
        roof_area=6*8,
        external_wall_r=1.797,
        floor_r=25.246,
        roof_r=2.992
    )
    inputs = Building(
        bui_type='Apartment building',
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
        vent_rates_mu='1/h',
        time_control_on=0,
        time_control_off=24,
        ti_hsp_day_start=7,
        ti_hsp_night_start=24
    )
    
    df = run_vct_simulation(inputs, thermophys_prop)

    df_original = pd.read_csv("tests/data/apartment_building.csv")
    df = df.drop(columns=['Date', 'Time', 'Day'])
    df_original = df_original.drop(columns=['Date', 'Time', 'Day'])
    
    # Acceptable error = 1e-9
    error = 10 ** -9
    
    result = {}
    for col in df.columns:
        diff = [abs(x - y) for x, y in zip(df[col].values, df_original[col].values)]
        diff_array = [abs(x - y) < error for x, y in
                      zip(df[col].values, df_original[col].values)]
        
        if col == 'Target indoor temperature for VCS':
            diff_array.pop(7236) # error in Excel file
            diff_array.pop(7668)
            diff_array.pop(7667)
                
        if not all(diff_array):
            raise AssertionError()

    result = df.to_json()
    snapshot.assert_match(result, 'apartment_building.json')


#####################################################################################


def test_sanapshot_Apartment_building_Vent_mode_over_year(snapshot):
    thermophys_prop = ThermostaticalProperties(
        external_wall_area=9.6+16.2+16.2+21.6,
        floor_area=6*8,
        roof_area=6*8,
        external_wall_r=1.797,
        floor_r=25.246,
        roof_r=2.992
    )
    inputs = Building(
        bui_type='Apartment building',
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
        vent_rates_mu='1/h',
        time_control_on=0,
        time_control_off=24,
        ti_hsp_day_start=7,
        ti_hsp_night_start=24
    )
    
    df_sim = run_vct_simulation(inputs, thermophys_prop)
    df_sim = df_sim[744:]
    df = get_vent_mode_over_year(df_sim)

    df_original = pd.read_csv("tests/data/results_vent_mode_over_year.csv", index_col=0)
    df.columns = ['0', '1', '2', '3']
    df_original.columns = ['0', '1', '2', '3']

    if not pd.concat([df,df_original]).drop_duplicates(keep=False).empty:
        raise AssertionError()

    result = df.to_json()
    snapshot.assert_match(result, "vent_mode_over_year.json")



def test_snapshot_Apartment_building_Freq_air_change_rate(snapshot):
    thermophys_prop = ThermostaticalProperties(
        external_wall_area=9.6+16.2+16.2+21.6,
        floor_area=6*8,
        roof_area=6*8,
        external_wall_r=1.797,
        floor_r=25.246,
        roof_r=2.992
    )
    inputs = Building(
        bui_type='Apartment building',
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
        vent_rates_mu='1/h',
        time_control_on=0,
        time_control_off=24,
        ti_hsp_day_start=7,
        ti_hsp_night_start=24
    )
    
    df_sim = run_vct_simulation(inputs, thermophys_prop)
    df_sim = df_sim[744:]
    df = get_requirend_frequency_air_change_rate(df_sim, inputs)

    df_original = pd.read_csv("tests/data/results_req_freq_air_change_rate.csv", index_col=0)
    error = 10 ** -15
    for col in df.columns: 
        if max(df[col].values -  df_original[col].values) > error: 
            raise AssertionError()
        
    result = df.to_json()
    snapshot.assert_match(result, "req_freq_air_change_rate.json")



def test_snapshot_Apartment_building_Annual_data(snapshot):
    thermophys_prop = ThermostaticalProperties(
        external_wall_area=9.6+16.2+16.2+21.6,
        floor_area=6*8,
        roof_area=6*8,
        external_wall_r=1.797,
        floor_r=25.246,
        roof_r=2.992
    )
    inputs = Building(
        bui_type='Apartment building',
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
        vent_rates_mu='1/h',
        time_control_on=0,
        time_control_off=24,
        ti_hsp_day_start=7,
        ti_hsp_night_start=24
    )
    
    df_sim = run_vct_simulation(inputs, thermophys_prop)
    df_sim = df_sim[744:]
    df = get_annual_data(df_sim)

    df_original = pd.read_csv("tests/data/results_annual_data.csv", index_col=0)
    error = 10 ** -12
    for col in df.columns: 
        if max(df[col].values -  df_original[col].values) > error: 
            raise AssertionError()

    result = df.to_json()
    snapshot.assert_match(result, "annual_data.json")



####################################################################################