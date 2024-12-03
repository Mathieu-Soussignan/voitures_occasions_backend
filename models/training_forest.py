import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

# Charger les données
df = pd.read_csv('../data/cleaned/voitures_aramisauto_nettoye.csv')

# Séparer les caractéristiques catégorielles et numériques
categorical_cols = df.select_dtypes(include=['object']).columns
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.drop('Prix')

# Ajouter la variable binaire 'Prix_binaire'
threshold = df['Prix'].median()
df['Prix_binaire'] = (df['Prix'] > threshold).astype(int)

# **Régression Logistique**
# Préparation des données pour la régression logistique
X_logistic = df.drop(columns=['Prix', 'Prix_binaire'])
y_logistic = df['Prix_binaire']

# Division des données en ensemble d'entraînement et de test
X_train_logistic, X_test_logistic, y_train_logistic, y_test_logistic = train_test_split(X_logistic, y_logistic, test_size=0.2, random_state=42)

# Création du préprocesseur avec ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ]
)

# Pipeline pour la régression logistique
logistic_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Entraînement du modèle de régression logistique
logistic_pipeline.fit(X_train_logistic, y_train_logistic)

# **Régression avec Random Forest**
X_regression = df.drop(columns=['Prix', 'Prix_binaire'])
y_regression = df['Prix']

# Division des données en ensemble d'entraînement et de test
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_regression, y_regression, test_size=0.2, random_state=42)

# Pipeline pour la régression Random Forest
forest_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(random_state=42))
])

# Entraînement du modèle de régression Random Forest avec GridSearchCV pour optimisation des hyperparamètres
param_grid = {
    'regressor__n_estimators': [100, 200, 300, 400],
    'regressor__max_depth': [10, 14, 18, None],
    'regressor__max_features': ['sqrt', 'log2'],
    'regressor__min_samples_split': [2, 5, 10],
    'regressor__min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(estimator=forest_pipeline, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)
grid_search.fit(X_train_reg, y_train_reg)

# Sauvegarde des pipelines avec Joblib
joblib.dump(logistic_pipeline, '../models/logistic_regression_model.pkl')
joblib.dump(grid_search.best_estimator_, '../models/random_forest_model.pkl')

print("Modèles et préprocesseur sauvegardés avec succès.")