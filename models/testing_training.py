import pandas as pd
import joblib  # Importer Joblib pour sauvegarder le modèle
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

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

# Préparation des données pour la régression Random Forest
X_regression = df_encoded.drop(columns=['Prix', 'Prix_binaire'])
y_regression = df_encoded['Prix']

# Division des données en ensemble d'entraînement et de test
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_regression, y_regression, test_size=0.2, random_state=42)

# Entraînement du modèle de régression Random Forest avec GridSearchCV pour optimisation des hyperparamètres
param_grid = {
    'n_estimators': [100, 200, 300, 400],
    'max_depth': [10, 14, 18, None],
    'max_features': ['sqrt', 'log2'],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Initialisation du modèle Random Forest
forest_model = RandomForestRegressor(random_state=42)

# Optimisation des hyperparamètres avec GridSearchCV
grid_search = GridSearchCV(estimator=forest_model, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)
grid_search.fit(X_train_reg, y_train_reg)

# Sauvegarde du modèle optimisé avec Joblib
joblib.dump(grid_search.best_estimator_, '../models/random_forest_model.pkl')

# Meilleurs hyperparamètres
best_params = grid_search.best_params_
print("\nMeilleurs hyperparamètres :")
print(best_params)

# Évaluation du modèle optimisé
y_pred_forest = grid_search.predict(X_test_reg)
mse_forest = mean_squared_error(y_test_reg, y_pred_forest)
r2_forest = r2_score(y_test_reg, y_pred_forest)
print("\nRégression avec Random Forest Optimisé :")
print(f"MSE : {mse_forest:.2f}")
print(f"R² : {r2_forest:.2f}")