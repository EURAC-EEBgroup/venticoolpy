"""Test climate functions."""

import numpy as np
import pandas as pd

from venticoolpy.calculation import (
    get_climate_data_from_epw,
    get_climate_data_from_csv,
)
from venticoolpy.new_irradiation_SFA_Perez_newCalc import get_climate_data_w_vert_irrad_from_epw
from venticoolpy.new_irradiation_SFA_Perez_newCalc import ORIENTATION_AZIMUTH



def test_get_climate_data_from_epw(snapshot):
    filename = "tests/inputs/data/ITA_Bolzano.160200_IGDG.epw"
    climate_data = get_climate_data_from_epw(filename)

    df = pd.DataFrame(climate_data.__dict__)
    csv_str = df.to_csv(index=False, lineterminator="\n")

    snapshot.assert_match(csv_str, "climate_data_epw.csv")


def test_get_climate_data_from_csv(snapshot):
    filename = "tests/inputs/data/tmy_46.501_11.362_2005_2020.csv"
    climate_data = get_climate_data_from_csv(filename)

    df = pd.DataFrame(climate_data.__dict__)
    csv_str = df.to_csv(index=False, lineterminator="\n")

    snapshot.assert_match(csv_str, "climate_data_csv.csv")


def test_get_climate_data_v_irrad_from_epw(snapshot):
    filename = "tests/inputs/data/ITA_Bolzano.160200_IGDG.epw"
    climate_data = get_climate_data_w_vert_irrad_from_epw(filename, "N")

    df = pd.DataFrame(climate_data.__dict__)
    csv_str = df.to_csv(index=False, lineterminator="\n")

    snapshot.assert_match(csv_str, "climate_data_epw.csv")


def test_get_climate_data_Helsinki_Airport_epw(snapshot):
    filename = "tests/inputs/data/climate/FI-Helsinki-Airport-29740TM2.epw"
    for ori in ORIENTATION_AZIMUTH.keys():
        climate_data = get_climate_data_w_vert_irrad_from_epw(filename, ori)

        df = pd.DataFrame(climate_data.__dict__)
        csv_str = df.to_csv(index=False, lineterminator="\n")

        snapshot.assert_match(csv_str, f"{ori}_climate_data.csv")


def test_get_climate_data_Stuttgart_epw(snapshot):
    filename = "tests/inputs/data/climate/DEU_BW_Stuttgart.AP.107380_TMYx.2009-2023.epw"
    for ori in ORIENTATION_AZIMUTH.keys():
        climate_data = get_climate_data_w_vert_irrad_from_epw(filename, ori)

        df = pd.DataFrame(climate_data.__dict__)
        csv_str = df.to_csv(index=False, lineterminator="\n")

        snapshot.assert_match(csv_str, f"{ori}_climate_data.csv")

def test_get_climate_data_London_epw(snapshot):
    filename = "tests/inputs/data/climate/4A_London_TMY_2001-2020.epw"
    for ori in ORIENTATION_AZIMUTH.keys():
        climate_data = get_climate_data_w_vert_irrad_from_epw(filename, ori)

        df = pd.DataFrame(climate_data.__dict__)
        csv_str = df.to_csv(index=False, lineterminator="\n")

        snapshot.assert_match(csv_str, f"{ori}_climate_data.csv")

def test_get_climate_data_Helsinki_Lighthouse_epw(snapshot):
    filename = "tests/inputs/data/climate/FIN_US_Helsinki.Lighthouse.029890_TMYx.2009-2023.epw"
    for ori in ORIENTATION_AZIMUTH.keys():
        climate_data = get_climate_data_w_vert_irrad_from_epw(filename, ori)

        df = pd.DataFrame(climate_data.__dict__)
        csv_str = df.to_csv(index=False, lineterminator="\n")

        snapshot.assert_match(csv_str, f"{ori}_climate_data.csv")

def test_get_climate_data_Paris_epw(snapshot):
    filename = "tests/inputs/data/climate/FR-Paris-Orly-Airp-71490TM2.epw"
    for ori in ORIENTATION_AZIMUTH.keys():
        climate_data = get_climate_data_w_vert_irrad_from_epw(filename, ori)

        df = pd.DataFrame(climate_data.__dict__)
        csv_str = df.to_csv(index=False, lineterminator="\n")

        snapshot.assert_match(csv_str, f"{ori}_climate_data.csv")

def test_get_climate_data_Bordeaux_epw(snapshot):
    filename = "tests/inputs/data/climate/FRA_AC_Bordeaux.Merignac.AP.075100_TMYx.2009-2023.epw"
    for ori in ORIENTATION_AZIMUTH.keys():
        climate_data = get_climate_data_w_vert_irrad_from_epw(filename, ori)

        df = pd.DataFrame(climate_data.__dict__)
        csv_str = df.to_csv(index=False, lineterminator="\n")

        snapshot.assert_match(csv_str, f"{ori}_climate_data.csv")

def test_get_climate_data_Bolzano_epw(snapshot):
    filename = "tests/inputs/data/climate/ITA_Bolzano.160200_IGDG.epw"
    for ori in ORIENTATION_AZIMUTH.keys():
        climate_data = get_climate_data_w_vert_irrad_from_epw(filename, ori)

        df = pd.DataFrame(climate_data.__dict__)
        csv_str = df.to_csv(index=False, lineterminator="\n")

        snapshot.assert_match(csv_str, f"{ori}_climate_data.csv")

def test_get_climate_data_Roma_epw(snapshot):
    filename = "tests/inputs/data/climate/ITA_LZ_Roma-Ciampino.AP.162390_TMYx.2009-2023.epw"
    for ori in ORIENTATION_AZIMUTH.keys():
        climate_data = get_climate_data_w_vert_irrad_from_epw(filename, ori)

        df = pd.DataFrame(climate_data.__dict__)
        csv_str = df.to_csv(index=False, lineterminator="\n")

        snapshot.assert_match(csv_str, f"{ori}_climate_data.csv")



