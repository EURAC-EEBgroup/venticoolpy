# Tutorials

After installing the library, the first step is to import it into your Python script or notebook.
This makes all the library’s functions and classes available for use.

```python
from venticoolpy.model import Building
from venticoolpy.calculation import (
    run_vct_simulation,
    get_vent_mode_over_year,
    get_requirend_frequency_air_change_rate,
    get_annual_data,
)
from venticoolpy.new_irradiation_SFA_Perez_newCalc import get_climate_data_w_vert_irrad_from_epw

```
If the import runs without errors, the library is correctly installed and ready to use.

Once the library is imported, the next step is to provide input values related to your reference room (building class) by editing these values for your case.

```python

 building = Building(
    bui_type="Apartment building",
    ceiling_to_floor_height=2.7,     # [m] ceiling to floor height 
    envelope_area=171.60,            # [m²] Gross envelope area (incl. both opaque and glazed area)
    floor_area=48.00,                # [m²] Net floor area
    fenestration_area=12.00,         # [m²] Total window area (incl. frame)
    orientation="N",                 # N, E, S, W, SE, SW, NE, NW direction the window faces, expressed relative to the cardinal directions
    comfort_requirements="category II", #target comfort category as defined by the EN 16798-1
    max_outdoor_rel_hum_accepted=85, # [%] max. outdoor relative humidity accepted
    u_value_opaque=0.316,            # [W/m²K] Average thermal transmittance of the opaque surfaces (wall, roof, floor) with outdoor boundary conditions
    u_value_fen=2.984,               # [W/m²K] Thermal transmittance of the window (or average thermal transmittance of windows if the room has more than one window), considering both glazing system and frame.
    construction_mass="medium",      # light / medium / heavy
    g_value_glazing_sys=0.71,        # [-] Solar heat gain coefficient of the window glazing system
    shading_control_setpoint=120,    # [W/m²] setpoint value for specific beam plus diffuse solar radiation incident on the window to activate shading
    shading_factor=0.0,              # Parameter indicating the presence of an external shading element and the surface of the window which is shaded by the shading element. 0..1 (0 = no shading reduction)
    time_control_on=0,               # [hour] 0–24 presence of the occupant within the thermal zone
    time_control_off=24,             # [hour] 0–24 presence of the occupant within the thermal zone
    ti_day_start=7,                  # [hour] 0–24 determine the disactivation of setback temperature setpoint
    ti_night_start=22,               # [hour] 0–24 determine the activation of setback temperature setpoint
    ti_hsb=15,                       # [°C] heating setback (during night) temperature 
    ti_csb=50,                       # [°C] cooling setback (during night) temperature 
    my_min_req_vent_rate=None,       # OPTIONAL - minimum required ventilation rate
    my_vent_rates_mu= None,          # Literal["l/s-m²", "1/h", "kg/s-m²", "m³/h", "m³/s"] = VENT_RATES_MU[0], # required if my_min_req_vent_rate is not None - unit of measure for the required ventilation rates input in my_min_req_vent_rate
    my_lighting_power_density=None,  # OPTIONAL - [W/m²] lighting power density
    my_el_equipment_power_density=None, # OPTIONAL - [W/m²] electric equipment power density
    my_occupancy_gains_density=None,    # OPTIONAL - [people/m²] Occupancy density
    my_c_int=None,                   # OPTIONAL -  [J/k] lumped internal thermal capacity 

    )
```

Load climate data by editing the .epw file path in the code
    
```python

climate_data = get_climate_data_w_vert_irrad_from_epw(
filename = "<path_to_climate_file>.epw", orientation=building.orientation
)

```
Run the calculation:

```python

df = run_vct_simulation(building, climate_data)
df_vent_mode = get_vent_mode_over_year(df[744:])
df_freq_air_chg = get_requirend_frequency_air_change_rate(df[744:], building)
df_year = get_annual_data(df[744:])

```
Print the results:

```python

print(df_vent_mode)
print(df_freq_air_chg)
print(df_year)

```
Plot the results:

```python

from venticoolpy.plot import plot_vent_mode_over_year, plot_requirend_frequency_air_change_rate
plot_vent_mode_over_year(df_vent_mode)
plot_requirend_frequency_air_change_rate(df_freq_air_chg)

```