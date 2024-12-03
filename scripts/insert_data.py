import sqlite3
import pandas as pd

# Charger les données du fichier CSV
df = pd.read_csv('../data/cleaned/voitures_aramisauto_nettoye.csv')

# Se connecter à la base de données SQLite
conn = sqlite3.connect('voitures_aramisauto.db')
cursor = conn.cursor()

# Insérer les marques dans la table Marque
marques = df['Marque'].str.split(' ', n=1).str[0].unique()
for marque in marques:
    cursor.execute("INSERT OR IGNORE INTO Marque (Nom) VALUES (?)", (marque,))

# Insérer les types de carburant dans la table Carburant
types_carburant = df['Type de Carburant'].unique()
for carburant in types_carburant:
    cursor.execute("INSERT OR IGNORE INTO Carburant (Type) VALUES (?)", (carburant,))

# Insérer les types de transmission dans la table Transmission
types_transmission = df['Transmission'].unique()
for transmission in types_transmission:
    cursor.execute("INSERT OR IGNORE INTO Transmission (Type) VALUES (?)", (transmission,))

# Insérer les véhicules dans la table Vehicule
for _, row in df.iterrows():
    marque = row['Marque'].split(' ', 1)[0]

    # Récupérer l'ID de la marque correspondante
    cursor.execute("SELECT ID_Marque FROM Marque WHERE Nom = ?", (marque,))
    marque_id = cursor.fetchone()[0]

    # Récupérer l'ID du type de carburant correspondant
    cursor.execute("SELECT ID_Carburant FROM Carburant WHERE Type = ?", (row['Type de Carburant'],))
    carburant_id = cursor.fetchone()[0] if row['Type de Carburant'] != "Non spécifié" else None

    # Récupérer l'ID du type de transmission correspondant
    cursor.execute("SELECT ID_Transmission FROM Transmission WHERE Type = ?", (row['Transmission'],))
    transmission_id = cursor.fetchone()[0] if row['Transmission'] != "Non spécifié" else None

    # Insérer le véhicule
    cursor.execute("""
        INSERT INTO Vehicule (Modele, Annee, Kilometrage, Prix, Etat, Marque_ID, Carburant_ID, Transmission_ID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row['Marque'], row['Année'], row['Kilométrage'], row['Prix'],
        row['Etat'], marque_id, carburant_id, transmission_id
    ))

# Sauvegarder les modifications et fermer la connexion
conn.commit()
conn.close()