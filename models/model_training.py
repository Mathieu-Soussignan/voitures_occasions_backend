import pandas as pd
import joblib  # Importer Joblib pour sauvegarder les modèles
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score

# Charger les données
df = pd.read_csv('../data/cleaned/voitures_aramisauto_nettoye.csv')

# Encodage One-Hot des colonnes catégorielles
categorical_cols = df.select_dtypes(include=['object']).columns
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# Ajouter la variable binaire 'Prix_binaire'
threshold = df['Prix'].median()
df_encoded['Prix_binaire'] = (df['Prix'] > threshold).astype(int)

# Standardiser les données numériques
scaler = StandardScaler()
numeric_cols = df_encoded.select_dtypes(include=['int64', 'float64']).columns.drop('Prix_binaire')
df_encoded[numeric_cols] = scaler.fit_transform(df_encoded[numeric_cols])

# **Régression Logistique**
# Préparation des données pour la régression logistique
X_logistic = df_encoded.drop(columns=['Prix', 'Prix_binaire'])
y_logistic = df_encoded['Prix_binaire']

# Division des données en ensemble d'entraînement et de test
X_train_logistic, X_test_logistic, y_train_logistic, y_test_logistic = train_test_split(X_logistic, y_logistic, test_size=0.2, random_state=42)

# Entraînement du modèle de régression logistique
logistic_model = LogisticRegression(max_iter=1000)
logistic_model.fit(X_train_logistic, y_train_logistic)

# Sauvegarder le scaler
joblib.dump(scaler, "../models/scaler.pkl")

# Sauvegarde du modèle de régression logistique avec Joblib
joblib.dump(logistic_model, '../models/logistic_regression_model.pkl')

columns_after_encoding = df_encoded.columns
joblib.dump(columns_after_encoding, "../models/columns_after_encoding.pkl")

# Évaluation du modèle de régression logistique
y_pred_logistic = logistic_model.predict(X_test_logistic)
accuracy_logistic = accuracy_score(y_test_logistic, y_pred_logistic)
print("\nRégression Logistique :")
print(f"Accuracy : {accuracy_logistic:.2f}")