# vctlib

VctLib is ...
NB: this library is currently under development


## Getting started
First, generate the virtual environment using *python3-venv* package as follows:

```bash
cd <path_to_project>
    python3 -m venv <virtual_env_name>
```

Once generated, use the following command to use the virtual environment:

```bash
    source < virtual_env_name >/bin/activate
```

Install all project's dependencies with

```bash
    pip install -r requirements.txt
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
tox -e build
```



## Use

* Generate virtual environment 
* Install all dependencies
* Run tests
* Build the project package
* cd /dist folder. Copy generated .tar.gz file to another folder
* cd another folder and install vctlib library:
    ```bash
        pip install vctlib-<temp-version>.tar.gz
    ```

* once vctlib library is installed, example of usage: 
```python

import pandas as pd
from vctlib.calculation import (
    Building,
    run_vct_simulation,
    get_climate_data_from_csv,
    get_climate_data_from_epw,
    get_annual_data,
    get_requirend_frequency_air_change_rate,
    get_vent_mode_over_year,
)

climate_file_path = "/path-to-file/file.epw"
if climate_file_path.endswith('.csv'):
    climate_data = get_climate_data_from_csv(climate_file_path)
elif climate_file_path.endswith('.epw'):
    climate_data = get_climate_data_from_epw(climate_file_path)
else: 
    climate_data = None

building = Building(
    bui_type="Apartment building",
    celing_to_floor_height=2.7,
    envelope_area=171.60,
    floor_area=48.00,
    fenestration_area=12.00,
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
    ti_hsp_day_start=7,
    ti_hsp_night_start=24,
)

df_with_calibration_month = run_vct_simulation(building, climate_data)
df = df_with_calibration_month[744:]  # remove calibration month

df_vent_mode = get_vent_mode_over_year(df)
df_freq_air_change = get_requirend_frequency_air_change_rate(df, building)
df_annual_data = get_annual_data(df)

# Print results:
print(df_vent_mode)
print(df_freq_air_change)
print(df_annual_data)

```



