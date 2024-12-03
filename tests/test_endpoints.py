import pytest
import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

# Helper Function: Créer un véhicule pour les tests
def create_test_vehicule():
    payload = {
        "marque_id": 1,
        "modele": "Test Modèle",
        "annee": 2023,
        "kilometrage": 1000,
        "prix": 25000,
        "etat": "Occasion",
        "carburant_id": 1,
        "transmission_id": 1
    }
    response = requests.post(f"{BASE_URL}/vehicules/", json=payload)
    assert response.status_code == 200 or response.status_code == 201, "Erreur lors de la création du véhicule de test"
    return response.json()["id"]

# Test de création d'un véhicule
def test_create_vehicule():
    vehicule_id = create_test_vehicule()
    assert vehicule_id is not None, "ID du véhicule non retourné après création"

# Test de lecture de tous les véhicules
def test_read_vehicules():
    endpoint = f"{BASE_URL}/vehicules/"
    response = requests.get(endpoint)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test de mise à jour d'un véhicule
def test_update_vehicule():
    vehicule_id = create_test_vehicule()
    endpoint = f"{BASE_URL}/vehicules/{vehicule_id}"
    payload = {
        "modele": "Modèle Mis à Jour",
        "prix": 27000
    }
    response = requests.put(endpoint, json=payload)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["prix"] == 27000

# Test de suppression d'un véhicule
def test_delete_vehicule():
    vehicule_id = create_test_vehicule()
    endpoint = f"{BASE_URL}/vehicules/{vehicule_id}"
    
    # Vérifier que le véhicule existe avant la suppression
    response_get = requests.get(endpoint)
    assert response_get.status_code == 200, f"Véhicule avec ID {vehicule_id} introuvable avant suppression."

    # Effectuer la suppression
    response_delete = requests.delete(endpoint)
    assert response_delete.status_code == 200, f"Échec de la suppression, code d'état: {response_delete.status_code}"
    
    # Vérifier que le véhicule n'existe plus après la suppression
    response_get_after = requests.get(endpoint)
    assert response_get_after.status_code == 404, "Le véhicule existe toujours après la suppression."

# Test de création d'un véhicule avec des champs manquants
def test_create_vehicule_missing_fields():
    endpoint = f"{BASE_URL}/vehicules/"
    payload = {
        "modele": "Nouveau Modèle",
        "annee": 2023
        # Manque d'autres champs obligatoires
    }
    response = requests.post(endpoint, json=payload)
    assert response.status_code == 422, "L'API n'a pas retourné le code 422 pour les champs obligatoires manquants"