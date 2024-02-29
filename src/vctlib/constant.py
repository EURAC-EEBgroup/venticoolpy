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


Air_properties_Cp = 1006
Air_properties_ro = 1.204


VENTILATION_STRATEGY = [
    'Single-sided: buoyancy only',
    'Single-sided: buoyancy+wind',
    'Stack ventilation',
    'Cross ventilation',
]

WINDOW_OPENING_TYPE = [
    'side hung',
    'bottom hung',
    'top hung',
]

WINDOW_DESIGN_CV = [
    [0.33,	0.33,	0.26,	0.26,	0.18,	0.18,	0.11],
    [0.54,	0.54,	0.42,	0.42,	0.33,	0.33,	0.24],
    [0.62,	0.62,	0.52,	0.52,	0.46,	0.46,	0.33],
    [0.67,	0.67,	0.61,	0.61,	0.56,	0.56,	0.52],
    [0.68,	0.68,	0.65,	0.65,	0.63,	0.63,	0.59],
    [0.69,	0.69,	0.68,	0.68,	0.67,	0.67,	0.64],
]

comfort_categories_AK = dict(zip(COMFORT_REQUIREMENTS, [ 2, 3, 4])) # TODO: change name
comfort_categories_AL = dict(zip(COMFORT_REQUIREMENTS, [-3, -4, -5])) # TODO: change name

Qp_comfort_category = dict(zip(COMFORT_REQUIREMENTS, [10, 7, 4]))
Qa_comfort_category = dict(zip(COMFORT_REQUIREMENTS, [1, 0.7, 0.4]))