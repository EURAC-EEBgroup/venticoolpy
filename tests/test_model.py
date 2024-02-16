"""Test models."""

from vctlib.model import Building
from vctlib.constant import VENT_RATES_MU

__author__ = "OlgaSomova"
__copyright__ = "OlgaSomova"
__license__ = "MIT"


def test_inputs_model(snapshot):
    """Test Building model."""
    inputs = Building(
        bui_type='Apartment building',
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
        vent_rates_mu='1/h',
        time_control_on=0,
        time_control_off=24,
    )

    snapshot.assert_match(str(inputs.__dict__), "inputs.yml")

    properties = {
        'room_volume': inputs.room_volume,
        'average_u_value': inputs.average_u_value,
        'min_req_vent_rates': inputs.min_req_vent_rates,
        'lighting_power_density': inputs.lighting_power_density,
        'el_equipment_power_density': inputs.el_equipment_power_density,
        'occupancy_density': inputs.occupancy_density,
        'average_tot_int_gains': inputs.average_tot_int_gains,
        'nr_of_occupied_hrs': inputs.nr_of_occupied_hrs,
        'cint': inputs.cint,
    }

    inputs.vent_rates_mu = VENT_RATES_MU[1]
    properties['min_req_vent_rates_1'] = inputs.min_req_vent_rates

    inputs.vent_rates_mu = VENT_RATES_MU[2]
    properties['min_req_vent_rates_2'] = inputs.min_req_vent_rates

    inputs.vent_rates_mu = VENT_RATES_MU[3]
    properties['min_req_vent_rates_3'] = inputs.min_req_vent_rates

    snapshot.assert_match(str(properties), "properties_inputs.yml")
