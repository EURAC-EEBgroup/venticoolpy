# venticoolpy

venticoolpy is ...
NB: this library is currently under development


## Getting started
First, generate and syncronize the virtual environment using *uv* package as follows:

```bash
cd <path_to_project>
    uv sync --all-groups --all-extras
```

## Test

You can execute the whole test suite by running

```bash
tox
```

If some snapshot test fail, you can inspect the differences with

```bash
tox -- -vv
```

## Package

You can build the progect package running

```bash
uv build
```


## Use

* Generate virtual environment 
* Install all dependencies
* Run tests
* Build the project package
* cd /dist folder. Copy generated .tar.gz file to another folder
* cd another folder and install venticoolpy library:
    ```bash
        pip install "venticoolpy[all] @ venticoolpy-<temp-version>.tar.gz"
    ```

* once venticoolpy library is installed, example of usage: 
```python

import pandas as pd
from venticoolpy.calculation import (
    Building,
    run_vct_simulation,
    get_annual_data,
    get_requirend_frequency_air_change_rate,
    get_vent_mode_over_year,
)
from venticoolpy.new_irradiation_SFA_Perez_newCalc import get_climate_data_w_vert_irrad_from_epw


building = Building(
    bui_type="Apartment building",
    ceiling_to_floor_height=2.7,
    envelope_area=171.60,
    floor_area=48.00,
    fenestration_area=12.00,
    orientation="S",
    comfort_requirements="category II",
    max_outdoor_rel_hum_accepted=85,
    u_value_opaque=0.3158,
    u_value_fen=2.984,
    construction_mass="medium",
    g_value_glazing_sys=0.71,
    shading_control_setpoint=120,
    shading_factor=0,
    time_control_on=0,
    time_control_off=24,
    ti_day_start=7,
    ti_night_start=24,
)

climate_file_path = "/path-to-file/file.epw"
climate_data = get_climate_data_w_vert_irrad_from_epw(climate_file_path, building.orientation)

df_with_calibration_month = run_vct_simulation(building, climate_data)
df = df_with_calibration_month[744:]  # remove calibration month

df_vent_mode = get_vent_mode_over_year(df)
df_freq_air_change = get_requirend_frequency_air_change_rate(df, building)
df_year = get_annual_data(df)

# Print results:
print(df_vent_mode)
print(df_freq_air_change)
print(df_year)

# Plot results:
from venticoolpy.plot import plot_vent_mode_over_year, plot_requirend_frequency_air_change_rate, plot_annual_data

plot_vent_mode_over_year(df_vent_mode)
plot_requirend_frequency_air_change_rate(df_freq_air_change)
plot_annual_data(df_year)

```



