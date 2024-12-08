import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

# Charger les données
df = pd.read_csv('../data/cleaned/voitures_aramisauto_nettoye.csv')

# Vérifier si la colonne 'Prix_binaire' existe, sinon la créer
if 'Prix_binaire' not in df.columns:
    threshold = df['Prix'].median()
    df['Prix_binaire'] = (df['Prix'] > threshold).astype(int)

# Définir les caractéristiques et la cible
X = df.drop(columns=['Prix', 'Prix_binaire'])  # Supprimer la cible et la colonne binaire si existante
y = df['Prix']

# Définir les colonnes catégorielles et numériques
categorical_cols = X.select_dtypes(include=['object']).columns
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns

# Préprocesseur pour le prétraitement des données
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ]
)

# Pipeline pour le modèle Random Forest
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(
        n_estimators=300, 
        max_depth=18, 
        max_features='sqrt', 
        random_state=42
    ))
])

# Calculer les learning curves
train_sizes, train_scores, test_scores = learning_curve(
    model_pipeline, X, y, cv=5, scoring='neg_mean_squared_error', n_jobs=-1, train_sizes=np.linspace(0.1, 1.0, 10)
)

# Calculer les moyennes et écarts-types des scores
train_mean = -train_scores.mean(axis=1)
train_std = train_scores.std(axis=1)
test_mean = -test_scores.mean(axis=1)
test_std = test_scores.std(axis=1)

# Tracer la courbe
plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_mean, label="Training Error", color="blue", marker="o")
plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.2, color="blue")

plt.plot(train_sizes, test_mean, label="Validation Error", color="green", marker="s")
plt.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.2, color="green")

plt.title("Learning Curve - Random Forest")
plt.xlabel("Training Set Size")
plt.ylabel("Mean Squared Error")
plt.legend(loc="best")
plt.grid()
plt.show()