import os
import pytest

import venticoolpy


def test_venticoolpy_import():
    assert venticoolpy.__version__ is not None, "Missing VentiCoolPy version"


def test_venticoolpy_data_module():
    assert hasattr(venticoolpy, "data"), "Missing data module in VentiCoolPy"
