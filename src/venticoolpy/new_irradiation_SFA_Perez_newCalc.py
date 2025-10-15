from epw.weather import Weather
import pandas as pd
import csv
import pvlib
from venticoolpy.model import ClimateData
from datetime import timezone

HOURS_IN_YEAR = 8760  # 365*24

ORIENTATION_AZIMUTH = {
    'N' : 0,
    'NE' : 45,
    'E' : 90,
    'SE' : 135,
    'S' : 180,
    'SW' : 225,
    'W' : 270,
    'NW' : 315,
}


def get_climate_data_w_vert_irrad_from_epw(filename, orientation='S'):
    # read weather data
    weather_data = Weather()
    weather_data.read(filename)

    # TODO: add some validation
    if weather_data.dataframe.shape[0] != HOURS_IN_YEAR:
        raise Exception("The data is invalid")
    
    location_name = weather_data.headers["LOCATION"][0]
    time_zone = float(weather_data.headers["LOCATION"][7])
    latitude = float(weather_data.headers["LOCATION"][5])
    longitude = float(weather_data.headers["LOCATION"][6])
    altitude = float(weather_data.headers["LOCATION"][8])

    # weather data for calculation with pvlib
    df_dni = weather_data.dataframe["Direct Normal Radiation"] #W/m2
    df_ghi = weather_data.dataframe["Global Horizontal Radiation"] #W/m2
    df_dhi = weather_data.dataframe["Diffuse Horizontal Radiation"] #W/m2
    df_extra_dni = weather_data.dataframe["Extraterrestrial Direct Normal Radiation"] #W/m2
   
    # Hourly timestamp for the year 
    times = pd.date_range('2005-01-01 01:00:00',periods=HOURS_IN_YEAR, freq='h',tz=f'Etc/GMT{int(-time_zone)}')

    # Shift timestamps to the centre of intervals
    times_centered = times - pd.Timedelta(minutes=30)
    
    # Calculation of solar position for getting irradiance values on a vertical surface
    df_solar_position = pvlib.solarposition.get_solarposition(
        time=times_centered,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude
    )

    # Surface azimuth for the vertical surface (based on orientation)
    surface_azimuth = ORIENTATION_AZIMUTH[orientation]

    # Surface tilt for vertical surface is 90 degrees
    surface_tilt = 90

    # Reset timestamps to the actual intervals
    times_ended = times

    df_solar_position.index = times_ended
    # Ensure weather dataframe uses datetime index

    # weather_data.dataframe.index = times  # Assign the correct timestamps
    df_dni.index = times_ended
    df_ghi.index = times_ended
    df_dhi.index = times_ended
    df_extra_dni.index = times_ended
    df_solar_position.index = times_ended


    # Use get_total_irradiance to calculate irradiance on vertical surface    
    total_irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt = surface_tilt,
        surface_azimuth = surface_azimuth,
        solar_zenith = df_solar_position['zenith'], #152.42730152243752
        solar_azimuth = df_solar_position['azimuth'],#37.84210665047942
        dni = df_dni,
        ghi = df_ghi,
        dhi = df_dhi,
        dni_extra = df_extra_dni,
        model='perez'
    )

    total_irradiance = total_irradiance.fillna(0)
    vertical_irradiance = (
        total_irradiance['poa_direct'] + 
        total_irradiance['poa_sky_diffuse']  
    )

    climate_data = ClimateData(
        df_outdoor_dry_bulb_temperature=weather_data.dataframe["Dry Bulb Temperature"], 
        df_relative_humidity_outdoor_air=weather_data.dataframe["Relative Humidity"],
        df_isol_tot=vertical_irradiance
    )

    return climate_data     




