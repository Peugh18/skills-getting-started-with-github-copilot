"""Fixtures compartidas para los tests de FastAPI"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Proporciona un cliente de prueba para la aplicación FastAPI"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Resetea las actividades a su estado inicial antes de cada test"""
    # Resetear participantes de todas las actividades
    for activity in activities.values():
        activity["participants"] = []
    yield
    # Limpiar después del test
    for activity in activities.values():
        activity["participants"] = []


@pytest.fixture
def sample_email():
    """Email de prueba"""
    return "estudiante@mergington.edu"


@pytest.fixture
def sample_activity_name():
    """Nombre de actividad válida para pruebas"""
    return "Chess Club"
