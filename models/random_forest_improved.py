import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Charger les données
df = pd.read_csv('../data/cleaned/voitures_aramisauto_nettoye.csv')

# Suppression des valeurs aberrantes sur les prix (valeurs en dehors de 1.5x l'écart interquartile)
Q1 = df['Prix'].quantile(0.25)
Q3 = df['Prix'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['Prix'] >= Q1 - 1.5 * IQR) & (df['Prix'] <= Q3 + 1.5 * IQR)]

# Séparer les caractéristiques catégorielles et numériques
categorical_cols = df.select_dtypes(include=['object']).columns
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.drop('Prix')

# Préparation des données
X = df.drop(columns=['Prix'])
y = df['Prix']

# Division des données en ensemble d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Création du préprocesseur avec ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ]
)

# Pipeline pour la régression Random Forest
forest_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(random_state=42))
])

# Entraînement du modèle de régression Random Forest avec GridSearchCV
param_grid = {
    'regressor__n_estimators': [200, 300, 400, 500],
    'regressor__max_depth': [10, 14, 18, None],
    'regressor__max_features': ['sqrt', 'log2'],
    'regressor__min_samples_split': [2, 5, 10],
    'regressor__min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(estimator=forest_pipeline, param_grid=param_grid, cv=10, n_jobs=-1, verbose=2, scoring='r2')
grid_search.fit(X_train, y_train)

# Meilleur modèle et ses paramètres
best_model = grid_search.best_estimator_
print("Meilleurs paramètres :", grid_search.best_params_)

# Évaluation sur le jeu de test
y_pred = best_model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"RMSE : {rmse:.2f}")
print(f"MAE : {mae:.2f}")
print(f"R² : {r2:.2f}")

# Validation croisée avec le meilleur modèle
cv_scores = cross_val_score(best_model, X_train, y_train, cv=10, scoring='r2', n_jobs=-1)
print("Scores R² en validation croisée :", cv_scores)
print("Score R² moyen :", np.mean(cv_scores))

# Sauvegarde du modèle
joblib.dump(best_model, '../models/random_forest_improved.pkl')
print("Modèle Random Forest amélioré sauvegardé avec succès.")

# Importance des features
preprocessor.fit(X_train)
regressor = best_model.named_steps['regressor']
feature_names = numeric_cols.tolist() + list(preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_cols))
feature_importances = pd.DataFrame({
    'Feature': feature_names,
    'Importance': regressor.feature_importances_
}).sort_values(by='Importance', ascending=False)
print("Importance des features :")
print(feature_importances)