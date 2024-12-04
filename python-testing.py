import sqlite3

# Connectez-vous à votre base de données SQLite (remplacez par le chemin vers votre base de données)
conn = sqlite3.connect('voitures_aramisauto.db')

# Créez un curseur pour exécuter des requêtes SQL
cursor = conn.cursor()

# Renommer la colonne "nom" en "username"
cursor.execute('ALTER TABLE Users RENAME COLUMN nom TO username;')

# Renommer la colonne "password" en "hashed_password"
cursor.execute('ALTER TABLE Users RENAME COLUMN password TO hashed_password;')

# Valider les modifications
conn.commit()

# Fermer la connexion à la base de données
conn.close()