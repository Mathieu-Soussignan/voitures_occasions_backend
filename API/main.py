from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from API import models, schemas, crud
from API.database import SessionLocal, engine
import joblib
import pandas as pd
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import sqlite3

# Utiliser un chemin absolu basé sur le dossier actuel
base_dir = os.path.dirname(os.path.abspath(__file__))
# Définir les chemins vers les fichiers CSV respectifs
year_brand_csv_path = os.path.join(base_dir, "../data/visualizations/year_brand_distribution.csv")
clustering_csv_path = os.path.join(base_dir, "../data/visualizations/clustering_data.csv")

# Lire les fichiers CSV avec leurs chemins respectifs
year_brand_df = pd.read_csv(year_brand_csv_path)
clustering_df = pd.read_csv(clustering_csv_path)

# Configurer le logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
router = APIRouter()

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Remplace "*" par l'URL de ton frontend en production pour plus de sécurité
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendance pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Charger les modèles nécessaires
random_forest_model = joblib.load("./models/random_forest_model.pkl")
logistic_model = joblib.load("./models/logistic_regression_model.pkl")

@app.get("/vehicules/", response_model=list[schemas.Vehicule])
def read_vehicules(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_vehicules(db, skip=skip, limit=limit)

@app.post("/vehicules/", response_model=schemas.Vehicule, status_code=201)
def create_vehicule(vehicule: schemas.VehiculeCreate, db: Session = Depends(get_db)):
    return crud.create_vehicule(db=db, vehicule=vehicule)

@app.put("/vehicules/{vehicule_id}", response_model=schemas.Vehicule)
def update_vehicule(vehicule_id: int, vehicule_update: schemas.VehiculeUpdate, db: Session = Depends(get_db)):
    db_vehicule = crud.update_vehicule(db=db, vehicule_id=vehicule_id, vehicule_update=vehicule_update)
    if db_vehicule is None:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return db_vehicule

@app.delete("/vehicules/{vehicule_id}", response_model=dict)
def delete_vehicule(vehicule_id: int, db: Session = Depends(get_db)):
    return crud.delete_vehicule(db=db, vehicule_id=vehicule_id)

class PredictRequest(BaseModel):
    kilometrage: float
    annee: int
    marque: str
    carburant: str
    transmission: str
    modele: str
    etat: str

    class Config:
        schema_extra = {
            "example": {
                "kilometrage": 15000,
                "annee": 2019,
                "marque": "Peugeot",
                "carburant": "Essence",
                "transmission": "Manuelle",
                "modele": "208",
                "etat": "Occasion"
            }
        }

@app.post("/predict_combined")
def predict_combined(request: PredictRequest):
    try:
        # Convertir les données de la requête en DataFrame
        input_data = pd.DataFrame([request.dict()])
        logging.info(f"Input data: {input_data}")

        # S'assurer que les colonnes correspondent aux colonnes utilisées lors de l'entraînement
        column_order = [
            'Kilométrage', 'Année', 'Marque', 'Type de Carburant', 
            'Transmission', 'Modèle', 'Etat'
        ]

        # Adapter les noms des colonnes à ceux du modèle
        input_data.columns = column_order
        logging.info(f"Input data with correct columns: {input_data}")

        # Prédiction du prix avec le modèle Random Forest
        predicted_price = random_forest_model.predict(input_data)
        logging.info(f"Predicted price: {predicted_price}")

        # Classification de la transaction (Bonne ou Mauvaise affaire) avec le modèle Logistique
        deal_classification = logistic_model.predict(input_data)
        label = "Bonne affaire" if deal_classification[0] == 1 else "Mauvaise affaire"
        logging.info(f"Classification: {label}")

        # Retourner les deux prédictions
        return {
            "predicted_price": float(predicted_price[0]),
            "deal_classification": label
        }
    
    except Exception as e:
        logging.error(f"Erreur lors de la prédiction combinée: {e}")
        raise HTTPException(status_code=400, detail="Erreur lors de la prédiction combinée")

# Endpoints CRUD pour les utilisateurs
@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_all_users(db, skip=skip, limit=limit)

@app.post("/users/", response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_user

@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_deleted = crud.delete_user(db=db, user_id=user_id)
    if user_deleted is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Utilisateur supprimé avec succès"}

# Utiliser des variables différentes pour chaque dataframe
@router.get("/data/year-brand-distribution")
def get_year_brand_distribution():
    # Connexion à la base de données SQLite
    conn = sqlite3.connect("voitures_aramisauto.db")
    
    # Requête SQL pour agréger les données par année et marque
    query = """
    SELECT m.Nom AS Marque, v.Annee, COUNT(*) AS Count
    FROM Vehicule v
    JOIN Marque m ON v.Marque_ID = m.ID_Marque
    GROUP BY m.Nom, v.Annee
    ORDER BY v.Annee, m.Nom;
    """
    
    # Exécuter la requête et charger les résultats dans un DataFrame
    year_brand_df = pd.read_sql_query(query, conn)
    
    # Fermer la connexion
    conn.close()
    
    # Voir les données agrégées avant de les renvoyer
    print("Aperçu des données agrégées par année et marque :")
    print(year_brand_df.head())
    
    # Convertir le DataFrame en liste de dictionnaires pour l'API
    response_data = year_brand_df.to_dict(orient="records")
    
    # Retourner les données au frontend
    return response_data


@router.get("/data/clustering")
def get_clustering_data():
    return clustering_df.to_dict(orient="records")

# Inclure le router
app.include_router(router)