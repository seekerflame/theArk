import pytest
import os
import json
import tempfile
import sqlite3
from core.ledger import VillageLedger
from core.sensors import SensorRegistry
from core.energy import EnergyMonitor

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.remove(path)

@pytest.fixture
def mock_ledger(temp_db):
    return VillageLedger(temp_db)

@pytest.fixture
def temp_sensor_file():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.remove(path)

@pytest.fixture
def sensor_registry(temp_sensor_file):
    return SensorRegistry(temp_sensor_file)

@pytest.fixture
def energy_monitor(mock_ledger, sensor_registry):
    return EnergyMonitor(mock_ledger, sensors=sensor_registry)
