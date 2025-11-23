"""Basic import test for the Streamlit app."""

import importlib


def test_app_imports():
    importlib.import_module("app.app")
