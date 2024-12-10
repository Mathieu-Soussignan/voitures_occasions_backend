from fastapi import FastAPI, HTTPException, Depends, APIRouter, status
# from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from API import models, schemas, crud
from API.database import SessionLocal, engine
import joblib
import numpy as np
import pandas as pd
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
# from sklearn.model_selection import learning_curve
# import json

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

# Initialiser l'application FastAPI
app = FastAPI()
router = APIRouter()

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://voiture-occasions-frontend.vercel.app",
        "https://predict-car.vercel.app"
    ],  # Liste des URLs autorisées
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
random_forest_model = joblib.load("./models/random_forest_improved.pkl")
logistic_model = joblib.load("./models/gradient_boosting_classifier.pkl")

# Sécurité pour la clé secrète JWT
SECRET_KEY = "SECRET_JWT_KEY"  # Changez cela pour un secret sécurisé
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Endpoint de base pour vérifier le statut de l'API
@app.get("/")
def root():
    return {"message": "Bienvenue sur le backend de Voitures Occasions !"}

# Modèle pour la création d'un utilisateur
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Modèle pour la connexion d'un utilisateur
class UserLogin(BaseModel):
    username: str
    password: str

# Endpoint pour l'inscription
@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe déjà
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    # Hash du mot de passe
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Créer un nouvel utilisateur
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password.decode('utf-8')  # Assurez-vous d'utiliser hashed_password ici
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Endpoint pour la connexion
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Chercher l'utilisateur par le nom d'utilisateur
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur ou mot de passe incorrect")

    # Vérifier le mot de passe
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Nom d'utilisateur ou mot de passe incorrect")

    # Créer un token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": db_user.username,
        "exp": datetime.utcnow() + access_token_expires
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}

# Middleware pour authentifier l'utilisateur à l'aide du token JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur non trouvé")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")

    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur non trouvé")

    return db_user

# Endpoints CRUD pour les véhicules
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

# Endpoint pour prédire le prix du véhicule
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

# Endpoint protégé pour obtenir les informations sur l'utilisateur connecté
@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

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

# Endpoints pour les données de visualisation
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
    logging.info("Aperçu des données agrégées par année et marque :")
    logging.info(year_brand_df.head())
    
    # Convertir le DataFrame en liste de dictionnaires pour l'API
    response_data = year_brand_df.to_dict(orient="records")
    
    # Retourner les données au frontend
    return response_data

# @app.get("/learning-curve-random-forest", response_class=JSONResponse)
# async def get_learning_curve():
#     # Définir le chemin vers le fichier JSON
#     file_path = os.path.join(os.path.dirname(__file__), "../static/learning_curve.json")

#     # Charger les données depuis le fichier
#     try:
#         with open(file_path, "r") as file:
#             data = json.load(file)
#         return data
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="Fichier JSON introuvable.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

@router.get("/data/clustering")
def get_clustering_data():
    return clustering_df.to_dict(orient="records")

# Inclure le router avec un préfixe pour les données
app.include_router(router, prefix="/data")