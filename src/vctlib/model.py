"""Models."""
import pandas as pd
import numpy as np

from vctlib.constant import BUILDING_TYPE, COMFORT_REQUIREMENTS, VENT_RATES_MU, SELECT_INTERNAL_GAINS
from vctlib.constant import (
    Air_properties_ro,
    LIGHTING_POWER_DENSITY,
    ELECTRIC_EQUIPMENT_POWER_DENSITY,
    m2_per_person,
    gain_per_person,
    VENTILATION_STRATEGY,
    WINDOW_OPENING_TYPE,
    Qp_comfort_category,
    Qa_comfort_category,
    heat_cap_construction_type,
)


class BuildingCreateException(Exception):
    pass


class WindowDesignCreateException(Exception):
    pass


class ClimateData():
    """ TODO: Add desctription """
    # TODO: add ClimateData create exception

    def __init__(
        self,
        df_outdoor_dry_bulb_temperature,
        df_relative_humidity_outdoor_air,
        df_isol_tot,
    ):
        self.df_outdoor_dry_bulb_temperature=df_outdoor_dry_bulb_temperature
        self.df_relative_humidity_outdoor_air=df_relative_humidity_outdoor_air
        self.df_isol_tot=df_isol_tot

    @property
    def outdoor_dry_bulb_temperature(self):
        # add extra Decembre month
        df = self.df_outdoor_dry_bulb_temperature
        return np.append(df[8016:8760].values, df[0:8760].values)
    
    @property
    def relative_humidity_outdoor_air(self):
        df = self.df_relative_humidity_outdoor_air
        return np.append(df[8016:8760].values, df[0:8760].values)
    
    @property
    def isol_tot(self):
        df = self.df_isol_tot
        return np.append(df[8016:8760].values, df[0:8760].values)
    

# class Gains():
#     """ TODO: Add desctription """

#     def __init__(
#         self,
#         isol_tot: pd.DataFrame,
#         internal_gains: pd.DataFrame | None = None
#     ):
#         self.isol_tot=isol_tot
#         self.internal_gains=internal_gains


class Building(object):
    """
    Building info, inputs for the main vct simulation.

    Objects of this class should be managed immutably throughout the simulation.

    Parameters
    ----------
    - bui_type (a value equal to: 'Apartment building', 'Daycare center',
        'Detached house', 'Hospital', 'Hotel', 'Office', 'Restaurant',
        'School'; required):  
    Building type.

    - celing_to_floor_height (number; required):  
    Ceiling to floor height; H (m).
    The net room height to calculate net room air volume V = H * S

    - envelope_area (number; required):  
    Envelope area; Ae (m²).
    The sum of walls, windows, ceiling and floor area with outdoor boundary conditions.
    This area, multiplied by the average thermal trasmittance, is used to estimate the
    transmission.

    - floor_area (number; required):  
    Floor area; Af (m²).
    The net floor area of the room to calculate net room air volume V = H * S and
    internal gains.

    - fenestration_area (number; required):  
    Fenestration area; Ag (m²).
    The glazing area on envelope used for the estimation of solar gains.

    - comfort_requirements (a value equal to: 'category I', 'category II',
        'category III'; required):  
    Comfort requirements.
    Comfort requirements refer to the comfort categories defined by the
    EN 16798:1-2019 standard.
    Reccomended input values given for each of the different comfort categories
    are included in the tool and automatically selected.

    - max_outdoor_rel_hum_accepted (number; required):  
    Max. outdoor relatve humidity accepted; RHmax (%).

    - u_value_opaque (number; required):  
    U-value of the opaque envelope; Uo (W/m²K).
    Average thermal transmittance of the opaque surfaces (wall, roof, floor) with
    outdoor boundary conditions.

    - u_value_fen (number; required):  
    U-value of the fenestration; Uw (W/m²K).
    Thermal transmittance of the window (or average thermal transmittance of windows if
    the room has more than one window), considering both glazing system and frame.

    - construction_mass (a value equal to: 'heavy', 'light', 'medium'; required):  
    Construction mass

    - g_value_glazing_sys (number; required):  
    g value of the glazing system; g.
    Solar energy transmittance of the glazing system.

    - shading_control_setpoint (number; required):  
    Shading control setpoint; Shd (W/m²).
    Shading is on if the specific beam plus diffuse solar radiation incident on the
    window exceeds this setpoint value (generally is between 40 and 150 W/m²).

    - shading_factor (number; required):  
    Shading factor; Y:
    Shading factor due to exterior shading element (i.e. shutter, venetian blinds,
    roll up blinds..).

    - vent_rates_mu (a value equal to '1/h', 'kg/s-m²', 'm³/h', 'm³/s'; required):  
    Unit of measurement according to which is defined the value of property
    min_req_vent_rates.

    - time_control_on (integer; required):  
    Time control on; ton; min 0, max 24.

    - time_control_off (integer; required):  
    Time control off; toff; min 0, max 24.

    es: from 23:00 to 7:00 -> Ti_hsp_night, from 7:00 to 23:00 -> Ti_hsp_day
    - ti_hsp_day_start (integer; optional):  
        default 7:00
        TODO: add description

    - ti_hsp_night_start (integer; optional):  
        default 23:00
        TODO: add description
        NB! error in excel formula: ti_hsp_night_start = 24

    - my_min_req_vent_rates(float; optional):  
    default None
    Custom min required ventilation rates (otherwise it is obtained from other inputs). 
    Minimum required air change rates (l/s-m²) calculated according to IEQ standard
    (EN 16798:1-2019) or design requirements to determine the ventilation losses
    within the energy balance of the reference room.

    - my_lighting_power_density (float; optional):    
    default None.
    Custom lighting power density (otherwise it is calculated from other inputs).
    The maximum lighting level per floor area. Internal gains due to lighting are
    calculated by multiplying the lighting power by the pre-defined load profiles.
        
    - my_el_equipment_power_density(float; optional):  
    Custom electric equipment power density (otherwise it is obtained from other inputs); Qel_equip (W/m²).
    The maximum elecric eqipment level per floor area.
    Internal gains due to electric equipment are calculated
    by multiplying the lighting power by the pre-defined load profiles.

    - my_occupancy_gains_density(float; optional):  
    default None.
    Custom occupancy density (otherwise it is obtained from other inputs); Qpeople (W/m²).
    The maximum floor area per person.
    Internal gains due to people are calculated by
    multiplying the maximum number of person by the pre-defined occupancy profiles.

    - my_c_tot (float; optional):  
    default None.
    C thermal cap. totale (C [J/K]).
    If any, c_int is calculated as follows, otherwise it is obtained from construction_mass. 
        c_int = c_tot + 10000 * floor_area

    - my_c_int (float; optional):  
    default None.
    Cint. is the (lumped) internal thermal capacity (J/K).
    Otherwise it is obtained from other inputs.

    - select_internal_gains (a value equal to: 'basecase', 'of_bui_type'; optional):  
    default bui_type. 
    if basecase:  
        internal_gains = 200/ floor area.
    if of_bui_type: 
        internal_gains obtained from building type.

    """

    def __init__(
        self,
        bui_type,
        celing_to_floor_height,
        envelope_area,
        floor_area,
        fenestration_area,
        comfort_requirements,
        max_outdoor_rel_hum_accepted,
        u_value_opaque,
        u_value_fen,
        construction_mass,
        g_value_glazing_sys,
        shading_control_setpoint,
        shading_factor,
        vent_rates_mu,
        time_control_on,
        time_control_off,
        ti_hsp_day_start=7,
        ti_hsp_night_start=23,
        my_min_req_vent_rates=None, 
        my_lighting_power_density=None,
        my_el_equipment_power_density=None,
        my_occupancy_gains_density=None,
        my_c_tot=None,
        my_c_int=None,
        select_internal_gains=SELECT_INTERNAL_GAINS[1]
    ):
        """Collect all data needed for the simulation."""
        self.bui_type = bui_type
        self.celing_to_floor_height = celing_to_floor_height
        self.envelope_area = envelope_area
        self.floor_area = floor_area
        self.fenestration_area = fenestration_area
        self.comfort_requirements = comfort_requirements
        self.max_outdoor_rel_hum_accepted = max_outdoor_rel_hum_accepted
        self.u_value_opaque = (
            u_value_opaque  # TODO: remove. Take it from ThermostaticalProperties
        )
        self.u_value_fen = u_value_fen
        self.construction_mass = construction_mass
        self.g_value_glazing_sys = g_value_glazing_sys
        self.shading_control_setpoint = shading_control_setpoint
        self.shading_factor = shading_factor
        self.vent_rates_mu = vent_rates_mu
        self.time_control_on = time_control_on
        self.time_control_off = time_control_off

        self.ti_hsp_day_start = ti_hsp_day_start  # TODO: non serve più?
        self.ti_hsp_night_start = ti_hsp_night_start  # TODO: non serve più?
        self.my_min_req_vent_rates=my_min_req_vent_rates
        self.my_lighting_power_density=my_lighting_power_density
        self.my_el_equipment_power_density=my_el_equipment_power_density
        self.my_occupancy_gains_density=my_occupancy_gains_density
        self.my_c_tot=my_c_tot
        self.my_c_int=my_c_int
        self.select_internal_gains = select_internal_gains

        if (
            bui_type not in BUILDING_TYPE
            or comfort_requirements not in COMFORT_REQUIREMENTS
            or vent_rates_mu not in VENT_RATES_MU
            or select_internal_gains not in SELECT_INTERNAL_GAINS
        ):
            raise BuildingCreateException

    @property
    def room_volume(self):
        """Room volume; V (m³)."""
        return self.celing_to_floor_height * self.floor_area

    @property
    def average_u_value(self):
        """Average U Value; Uavg (W/m²K)."""
        value = (
            self.u_value_opaque * (self.envelope_area - self.fenestration_area)
            + self.u_value_fen * self.fenestration_area
        ) / self.envelope_area
        return value

    @property
    def min_req_vent_rates(self):
        """
        Min. required ventilation rates.

        - qm;min (l/s-m²)
        - qm;min (1/h)

        Minimum required air change rates (l/s-m²) calculated according to IEQ standard
        (EN 16798:1-2019) or design requirements to determine the ventilation losses
        within the energy balance of the reference room.
        """
        vent_rate_1 = (
            Qp_comfort_category[self.comfort_requirements]
            * self.floor_area
            / m2_per_person[self.bui_type]
            + Qa_comfort_category[self.comfort_requirements] * self.floor_area
        ) / self.floor_area

        if self.my_min_req_vent_rates is not None:
            vent_rate_1 = self.my_min_req_vent_rates
        
        # if self.vent_rates_mu == VENT_RATES_MU[0]:  # 1/h:
        #     vent_rate_2 = (vent_rate_1 * 3.6 * self.floor_area) / self.room_volume
        # elif self.vent_rates_mu == VENT_RATES_MU[1]:
        #     vent_rate_2 = vent_rate_1 * 0.001 * Air_properties_ro
        # elif self.vent_rates_mu == VENT_RATES_MU[2]:
        #     vent_rate_2 = vent_rate_1 * 3.6 * self.floor_area
        # else:
        #     vent_rate_2 = vent_rate_1 * self.floor_area / 1000

        vent_rate_2 = vent_rate_1 * 3.6 * self.floor_area # m3/h 

        return vent_rate_1, vent_rate_2 
        

    @property
    def lighting_power_density(self):
        """Lighting power density; Qlight (W/m²).

        The maximum lighting level per floor area. Internal gains due to lighting are
        calculated by multiplying the lighting power by the pre-defined load profiles.
        """
        if self.my_lighting_power_density is not None:
            return self.my_lighting_power_density
        return LIGHTING_POWER_DENSITY[self.bui_type]

    @property
    def el_equipment_power_density(self):
        """Electric equipment power density; Qel_equip (W/m²).

        The maximum elecric eqipment level per floor area.
        Internal gains due to electric equipment are calculated
        by multiplying the lighting power by the pre-defined load profiles.
        """
        if self.my_el_equipment_power_density is not None:
            return self.my_el_equipment_power_density
        return ELECTRIC_EQUIPMENT_POWER_DENSITY[self.bui_type]

    @property
    def occupancy_gains_density(self):
        """Occupancy density; Qpeople (W/m²).

        The maximum floor area per person.
        Internal gains due to people are calculated by
        multiplying the maximum number of person by the pre-defined occupancy profiles.
        """
        # TODO: Need to multiply and divide by the same value?
        # return (self.floor_area / m2_per_person[self.bui_type] * gain_per_person[self.bui_type]) / self.floor_area # noqa: E501
        if self.my_occupancy_gains_density is not None:
            return self.my_occupancy_gains_density
        return gain_per_person[self.bui_type] / m2_per_person[self.bui_type]

    @property
    def average_tot_int_gains(self):
        """Avg. total internal gains; Qint (W/m²)."""
        # TODO: remove? takes the result of calculations. not used anywhere.
        return None

    @property
    def nr_of_occupied_hrs(self):
        """Nr of occupied hours."""
        return self.time_control_off - self.time_control_on

    @property
    def c_int(self):
        """Cint. is the (lumped) internal thermal capacity (J/K)."""
        if self.my_c_int is not None:
            return self.my_c_int
        
        if self.my_c_tot is not None: 
            return self.my_c_tot + 10000 * self.floor_area
        
        value = (
            1.2 * self.room_volume
            + heat_cap_construction_type[self.construction_mass]
            * 1000
            * (self.envelope_area + self.floor_area * 2)
            * 0.3
        ) * 1000
        return value


class ThermostaticalProperties(object):
    """
    # TODO: Remove this obj

    Area (m²)
    R (m²K/W)
    """

    def __init__(
        self,
        external_wall_area,
        floor_area,
        roof_area,
        external_wall_r,
        floor_r,
        roof_r,
    ):
        self.external_wall_area = external_wall_area
        self.floor_area = floor_area
        self.roof_area = roof_area
        self.external_wall_r = external_wall_r
        self.floor_r = floor_r
        self.roof_r = roof_r

    @property
    def u_value_tot(self):
        """U (W/m²K)."""
        u_wall = 1 / (self.external_wall_r + 1 / (2.5 + 5.13))
        u_floor = 1 / (self.floor_r + 1 / (0.7 + 5.13))
        u_roof = 1 / (self.roof_r + 1 / (5 + 5.13))

        tot_area = self.external_wall_area + self.floor_area + self.roof_area
        tot_u_value = (
            u_wall * self.external_wall_area
            + u_floor * self.floor_area
            + u_roof * self.roof_area
        ) / tot_area

        return tot_u_value

    @property
    def c_tot(self):
        """C [J/K]."""
        c_wall = (
            0.1 * 1400 * 1000 * self.external_wall_area
            + 0.0615 * 10 * 1400 * self.external_wall_area
            + 0.009 * 530 * 900 * self.external_wall_area
        )

        c_floor = 0.08 * 1400 * 1000 * self.floor_area

        c_roof = (
            0.01 * 950 * 840 * self.roof_area
            + 0.1118 * 12 * 840 * self.roof_area
            + 0.019 * 530 * 900 * self.roof_area
        )

        return c_wall + c_floor + c_roof

    @property
    def c_int(self):
        return self.c_tot + 10000 * self.floor_area


class WindowDesign(object):
    """Class for Window design input data.

    Room depth
    Ventilation strategy
    Select window opening type
    Window maximum opening angle
    Window opening discharge coefficient
    Indoor temperature
    Indoor-outdoor temperature difference
    Wind speed
    Insect screen?
    Stack height - vertical distance between 2 openings
    Wind pressure coefficient - window 1
    Wind pressure coefficient - window 2
    """

    def __init__(
        self,
        room_depth,
        ventilation_strategy,
        window_opening_type,  # add const for window opending type
        window_maximum_opening_angle,
        window_opening_discharge_coeff,
        indoor_temperature,
        indoor_outdoor_temperature_diff,
        wind_speed,
        has_insect_screen,
        stack_height,
        wind_pressure_coeff_window_1,
        wind_pressure_coefficient_window_2,
    ):
        """Collect all data needed for Windows Design simulation."""
        self.room_depth = room_depth
        self.ventilation_strategy = ventilation_strategy
        self.window_opening_type = window_opening_type
        self.window_maximum_opening_angle = window_maximum_opening_angle
        self.window_opening_discharge_coeff = window_opening_discharge_coeff
        self.indoor_temperature = indoor_temperature
        self.indoor_outdoor_temperature_diff = indoor_outdoor_temperature_diff
        self.wind_speed = wind_speed
        self.has_insect_screen = has_insect_screen
        self.stack_height = stack_height
        self.wind_pressure_coeff_window_1 = wind_pressure_coeff_window_1
        self.wind_pressure_coefficient_window_2 = wind_pressure_coefficient_window_2

        if (
            ventilation_strategy not in VENTILATION_STRATEGY
            or window_opening_type not in WINDOW_OPENING_TYPE
        ):
            raise WindowDesignCreateException

    @property
    def indoor_temperature_K(self):
        """Convert Indoor temperature from C to K"""
        return self.indoor_temperature + 273.15
