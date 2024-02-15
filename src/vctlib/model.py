from vctlib.constant import BUILDING_TYPE, COMFORT_REQUIREMENTS, VENT_RATES_MU
from vctlib.constant import Air_properties_ro, LIGHTING_POWER_DENSITY, ELECTRIC_EQUIPMENT_POWER_DENSITY,\
    m2_per_person, gain_per_person


class Input(object):
    """
    Inputs for the simulation.

    Objects of this class should be managed immutably throughout the simulation.

    Parameters
    ----------
    - bui_type (a value equal to: 'Apartment building', 'Daycare center', 'Detached house', 'Hospital', 'Hotel', 'Office', 'Restaurant', 'School'; required):
    Building type. 

    - celing_to_floor_height (number; required):
    Ceiling to floor height; H (m).
    The net room height to calculate net room air volume V = H * S

    - envelope_area (number; required):
    Envelope area; Ae (m²).
    The sum of walls, windows, ceiling and floor area with outdoor boundary conditions. This area, multiplied by the average thermal trasmittance, is used to estimate the transmission.

    - floor_area (number; required):
    Floor area; Af (m²).
    The net floor area of the room to calculate net room air volume V = H * S and internal gains. 

    - fenestration_area (number; required):
    Fenestration area; Ag (m²).
    The glazing area on envelope used for the estimation of solar gains.

    - comfort_requirements (a value equal to: 'category I', 'category II', 'category III'; required):
    Comfort requirements. 
    Comfort requirements refer to the comfort categories defined by the EN 16798:1-2019 standard. 
    Reccomended input values given for each of the different comfort categories are included in the tool and automatically selected.

    - max_outdoor_rel_hum_accepted (number; required):
    Max. outdoor relatve humidity accepted; RHmax (%).

    - u_value_opaque (number; required):
    U-value of the opaque envelope; Uo (W/m²K).
    Average thermal transmittance of the opaque surfaces (wall, roof, floor) with outdoor boundary conditions.

    - u_value_fen (number; required):
    U-value of the fenestration; Uw (W/m²K).
    Thermal transmittance of the window (or average thermal transmittance of windows if the room has more than one window), considering both glazing system and frame.

    - construction_mass (a value equal to: 'heavy', 'light', 'medium'; required):
    Construction mass

    - g_value_glazing_sys (number; required):
    g value of the glazing system; g.
    Solar energy transmittance of the glazing system.

    - shading_control_setpoint (number; required):
    Shading control setpoint; Shd (W/m²).
    Shading is on if the specific beam plus diffuse solar radiation incident on the window exceeds this setpoint value (generally is between 40 and 150 W/m²).

    - shading_factor (number; required):
    Shading factor; Y:
    Shading factor due to exterior shading element (i.e. shutter, venetian blinds, roll up blinds..).

    - vent_rates_mu (a value equal to '1/h', 'kg/s-m²', 'm³/h', 'm³/s'; required):
    Unit of measurement according to which is defined the value of property min_req_vent_rates. 

    - time_control_on (integer; required):
    Time control on; ton; min 0, max 24.

    - time_control_off (integer; required):
    Time control off; toff; min 0, max 24.

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
    ):
        self.bui_type = bui_type
        self.celing_to_floor_height = celing_to_floor_height
        self.envelope_area = envelope_area
        self.floor_area = floor_area
        self.fenestration_area = fenestration_area
        self.comfort_requirements = comfort_requirements
        self.max_outdoor_rel_hum_accepted = max_outdoor_rel_hum_accepted
        self.u_value_opaque = u_value_opaque
        self.u_value_fen = u_value_fen
        self.construction_mass = construction_mass
        self.g_value_glazing_sys = g_value_glazing_sys
        self.shading_control_setpoint = shading_control_setpoint
        self.shading_factor = shading_factor
        self.vent_rates_mu = vent_rates_mu
        self.time_control_on = time_control_on
        self.time_control_off = time_control_off


    @property
    def room_volume(self):
        """Room volume; V (m³)"""
        return self.celing_to_floor_height * self.floor_area

    @property
    def average_u_value(self):
        """Average U Value; Uavg (W/m²K)"""
        value = (self.u_value_opaque*(self.envelope_area - self.fenestration_area) + self.u_value_fen*self.fenestration_area)/self.envelope_area
        return  value

    @property
    def min_req_vent_rates(self):
        """
        Min. required ventilation rates. 

        - qm;min (l/s-m²)
        - qm;min (1/h)

        Minimum required air change rates (l/s-m²) calculated according to IEQ standard (EN 16798:1-2019) or design requirements to determine the ventilation losses within the energy balance of the reference room.
        """
        vent_rate_1 = 0.41*2.7/3.6 # TODO: const value or not? 
        
        # TODO: remove? never used in calculations
        if self.vent_rates_mu == VENT_RATES_MU[0]: #1/h:
            vent_rate_2 = (vent_rate_1 * 3.6 * self.floor_area) / self.room_volume
        elif self.vent_rates_mu == VENT_RATES_MU[1]:
            vent_rate_2 = vent_rate_1 * 0.001 * Air_properties_ro
        elif self.vent_rates_mu == VENT_RATES_MU[2]:
            vent_rate_2 = vent_rate_1 * 3.6 * self.floor_area
        else:
            vent_rate_2 = vent_rate_1 * self.floor_area / 1000
        
        return vent_rate_1, vent_rate_2
    
    @property
    def lighting_power_density(self):
        """ 
        Lighting power density; Qlight (W/m²).
        The maximum lighting level per floor area. Internal gains due to lighting are calculated by multiplying the lighting power by the pre-defined load profiles. 
        """
        return LIGHTING_POWER_DENSITY[self.bui_type]
    
    @property
    def el_equipment_power_density(self):
        """
        Electric equipment power density; Qel_equip (W/m²).
        The maximum elecric eqipment level per floor area. Internal gains due to electric equipment are calculated by multiplying the lighting power by the pre-defined load profiles.
        """
        return ELECTRIC_EQUIPMENT_POWER_DENSITY[self.bui_type]

    @property 
    def occupancy_density(self):
        """
        Occupancy density; Qpeople (W/m²).
        The maximum floor area per person. Internal gains due to people are calculated by multiplying the maximum number of person by the pre-defined occupancy profiles.
        """
        # TODO: Need to multiply and divide by the same value?
        # return (self.floor_area / m2_per_person[self.bui_type] * gain_per_person[self.bui_type]) / self.floor_area
        return gain_per_person[self.bui_type] / m2_per_person[self.bui_type]
   
    @property
    def average_tot_int_gains(self):
        """ Avg. total internal gains; Qint (W/m²)."""
        # TODO: remove? takes the result of calculations. not used anywhere.
        return None 
   
    @property
    def nr_of_occupied_hrs(self):
        """ Nr of occupied hours."""
        return self.time_control_off - self.time_control_on
    
    @property
    def Cint(self):
        """Cint; (J/K)"""
        # TODO: first value is const?
        return 15479951.712 + 10000 * self.floor_area
