"""Constants used throughout the simulation."""

BUILDING_TYPE = [
    'Apartment building',
    'Daycare center',
    'Detached house',
    'Hospital',
    'Hotel',
    'Office',
    'Restaurant',
    'School'
]

COMFORT_REQUIREMENTS = [
    'category I',
    'category II',
    'category III'
]

VENT_RATES_MU = [
    '1/h',
    'kg/s-m²',
    'm³/h',
    'm³/s'
]


Tmax_K1 = dict(zip(BUILDING_TYPE, [25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25]))
Tmax_K2 = dict(zip(BUILDING_TYPE, [26, 26, 26, 26, 26, 26, 26, 26]))
Tmax_K3 = dict(zip(BUILDING_TYPE, [27, 27, 27, 27, 27, 27, 27, 27]))

Tmin_K1 = dict(zip(BUILDING_TYPE, [21, 21, 21, 21, 21, 21, 21, 21]))
Tmin_K2 = dict(zip(BUILDING_TYPE, [20, 20, 20, 20, 20, 20, 20, 20]))
Tmin_K3 = dict(zip(BUILDING_TYPE, [18, 18, 18, 18, 18, 19, 19, 19]))

m2_per_person = dict(zip(BUILDING_TYPE, [28, 4, 42, 11, 28, 17, 6, 5.5]))
gain_per_person = dict(zip(BUILDING_TYPE, [126, 81, 126, 108, 126, 108, 170, 108]))
LIGHTING_POWER_DENSITY = dict(zip(BUILDING_TYPE, [8, 15, 8, 9, 8, 12, 20, 15]))
ELECTRIC_EQUIPMENT_POWER_DENSITY = dict(zip(BUILDING_TYPE, [3, 4, 2.4, 4, 3, 12, 4, 8]))


def get_t_min_k(comf_req):
    """Return TminK value given the building comfort requirements category."""
    index = COMFORT_REQUIREMENTS.index(comf_req)
    if index == 0:
        return Tmin_K1
    elif index == 1:
        return Tmin_K2
    elif index == 2:
        return Tmin_K3


def get_t_max_k(comf_req):
    """Return TmaxK value given the building comfort requirements category."""
    index = COMFORT_REQUIREMENTS.index(comf_req)
    if index == 0:
        return Tmax_K1
    elif index == 1:
        return Tmax_K2
    elif index == 2:
        return Tmax_K3


Ti_csp = 27  # TODO: value is const?

Air_properties_Cp = 1006
Air_properties_ro = 1.204
