"""Test models."""

import pytest

from venticoolpy.model import Building, BuildingCreateException
from venticoolpy.constant import VENT_RATES_MU, SELECT_VENT_RATES_CALC


__author__ = "OlgaSomova"
__copyright__ = "OlgaSomova"
__license__ = "MIT"


def test_inputs_model(snapshot):
    """Test Building model."""
    inputs = Building(
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
        select_vent_rates_calc=SELECT_VENT_RATES_CALC[0]
    )

    snapshot.assert_match(str(inputs.__dict__), "inputs.yml")

    properties = {
        "room_volume": inputs.room_volume,
        "average_u_value": inputs.average_u_value,
        "min_req_vent_rate": inputs.min_req_vent_rate,
        "lighting_power_density": inputs.lighting_power_density,
        "el_equipment_power_density": inputs.el_equipment_power_density,
        "occupancy_gains_density": inputs.occupancy_gains_density,
        "average_tot_int_gains": inputs.average_tot_int_gains,
        "nr_of_occupied_hrs": inputs.nr_of_occupied_hrs,
        "c_int": inputs.c_int,
    }

    snapshot.assert_match(str(properties), "properties_inputs.yml")



def test_building_exception(snapshot):
    """Test Exception on create Building model."""
    with pytest.raises(BuildingCreateException) as exc:
        _ = Building(
            bui_type="type does not exist",
            celing_to_floor_height=2.7,
            envelope_area=171.60,
            floor_area=48.00,
            fenestration_area=12.00,
            comfort_requirements="category does not exist",
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
    assert exc.typename == "BuildingCreateException"


def test_custom_min_req_vent_rate(snapshot):
    """Test Custom Min Required Ventilation Rate."""

    inputs = Building(
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
        my_min_req_vent_rate=0.31, 
        my_vent_rates_mu=VENT_RATES_MU[0]
    )

    data = {}
    for mu in VENT_RATES_MU:
        inputs.my_vent_rates_mu = mu
        data[inputs.my_vent_rates_mu] = inputs.min_req_vent_rate

    snapshot.assert_match(str(data), "min_req_vent_rate.yml")
