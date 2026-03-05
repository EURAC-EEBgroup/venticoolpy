import json

from venticoolpy.model import Building
from venticoolpy.calculation import run_vct_simulation, get_vent_mode_over_year, get_requirend_frequency_air_change_rate
from venticoolpy.plot import plot_vent_mode_over_year, plot_requirend_frequency_air_change_rate


from inputs.functions import (
    get_appartment_bld_climate_data, 
)


def test_plots(snapshot):
    building = Building(
        bui_type="Apartment building",
        celing_to_floor_height=2.7,
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

    vent_mode_chart = plot_vent_mode_over_year(df_vent_mode, display="none")
    spec = vent_mode_chart.to_dict()  # Vega-Lite spec as a dict
    snapshot.assert_match(json.dumps(spec, sort_keys=True, indent=2), "vent_mode_chart.vl.json")

    freq_air_chg_chart = plot_requirend_frequency_air_change_rate(df_freq_air_chg, display="none")
    spec = freq_air_chg_chart.to_dict()  # Vega-Lite spec as a dict
    snapshot.assert_match(json.dumps(spec, sort_keys=True, indent=2), "freq_air_chg_chart.vl.json")