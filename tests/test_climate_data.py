"""Test climate functions."""

import numpy as np
import pandas as pd

from venticoolpy.calculation import (
    get_climate_data_from_epw,
    get_climate_data_from_csv,
)
from venticoolpy.new_irradiation_SFA_Perez_newCalc import get_climate_data_w_vert_irrad_from_epw, get_climate_data_w_vert_irrad_from_csv




def test_get_climate_data_from_epw(snapshot):
    filename = "tests/inputs/data/ITA_Bolzano.160200_IGDG.epw"
    climate_data = get_climate_data_from_epw(filename)

    df = pd.DataFrame(climate_data.__dict__)
    csv_str = df.to_csv(index=False)

    snapshot.assert_match(csv_str, "climate_data_epw.csv")


def test_get_climate_data_from_csv(snapshot):
    filename = "tests/inputs/data/tmy_46.501_11.362_2005_2020.csv"
    climate_data = get_climate_data_from_csv(filename)

    df = pd.DataFrame(climate_data.__dict__)
    csv_str = df.to_csv(index=False)

    snapshot.assert_match(csv_str, "climate_data_csv.csv")


def test_get_climate_data_v_irrad_from_epw(snapshot):
    filename = "tests/inputs/data/ITA_Bolzano.160200_IGDG.epw"
    climate_data = get_climate_data_w_vert_irrad_from_epw(filename, "N")

    df = pd.DataFrame(climate_data.__dict__)
    csv_str = df.to_csv(index=False)

    snapshot.assert_match(csv_str, "climate_data_epw.csv")



def test_get_climate_data_v_irrad_from_csv(snapshot):
    filename = "tests/inputs/data/tmy_46.501_11.362_2005_2020.csv"
    climate_data = get_climate_data_w_vert_irrad_from_csv(filename, "N")

    df = pd.DataFrame(climate_data.__dict__)
    csv_str = df.to_csv(index=False)

    snapshot.assert_match(csv_str, "climate_data_csv.csv")