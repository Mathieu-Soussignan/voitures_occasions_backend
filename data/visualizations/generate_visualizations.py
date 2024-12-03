import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Charger le fichier nettoyé
df = pd.read_csv('./data/cleaned/voitures_aramisauto_nettoye.csv')

# Extraire les données nécessaires pour les visualisations

# 1. Données pour la distribution des années par marque
year_brand_distribution = df.groupby(["Année", "Marque"]).size().reset_index(name="Count")

# 2. Données pour le clustering (Kilométrage, Prix, Cluster)
X = df[["Kilométrage", "Prix"]]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
kmeans = KMeans(n_clusters=3, random_state=42)
df["Cluster"] = kmeans.fit_predict(X_scaled)
clustering_data = df[["Kilométrage", "Prix", "Cluster"]]

# Sauvegarder les données de visualisation dans des fichiers CSV distincts
year_brand_distribution.to_csv('year_brand_distribution.csv', index=False)
clustering_data.to_csv('clustering_data.csv', index=False)