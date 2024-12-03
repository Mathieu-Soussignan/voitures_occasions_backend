from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from . import models, schemas

# Fonction pour obtenir la liste des véhicules
def get_vehicules(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Vehicule).offset(skip).limit(limit).all()

# Fonction pour créer un nouveau véhicule
def create_vehicule(db: Session, vehicule: schemas.VehiculeCreate):
    db_vehicule = models.Vehicule(**vehicule.dict())
    db.add(db_vehicule)
    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule

# Fonction pour mettre à jour un véhicule
def update_vehicule(db: Session, vehicule_id: int, vehicule_update: schemas.VehiculeUpdate):
    db_vehicule = db.query(models.Vehicule).filter(models.Vehicule.id == vehicule_id).first()
    if not db_vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    update_data = vehicule_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vehicule, key, value)
    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule

# Fonction pour supprimer un véhicule
def delete_vehicule(db: Session, vehicule_id: int):
    try:
        # Rechercher le véhicule à supprimer
        db_vehicule = db.query(models.Vehicule).filter(models.Vehicule.id == vehicule_id).first()
        
        if not db_vehicule:
            raise HTTPException(status_code=404, detail="Véhicule non trouvé")

        # Supprimer le véhicule
        db.delete(db_vehicule)
        db.commit()

        # Retourner un simple message de confirmation
        return {"message": f"Véhicule avec ID {vehicule_id} supprimé avec succès"}

    except Exception as e:
        db.rollback()  # Annuler la transaction en cas d'erreur
        raise HTTPException(status_code=500, detail=f"Erreur serveur lors de la suppression du véhicule: {str(e)}")

# Fonction pour créer un nouvel utilisateur
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = models.User(email=user.email, nom=user.nom, password=hashed_password.decode('utf-8'))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Fonction pour obtenir un utilisateur par e-mail
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Fonction pour obtenir un utilisateur par ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Fonction pour obtenir tous les utilisateurs
def get_all_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

# Fonction pour mettre à jour les informations d'un utilisateur
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        if user_update.nom:
            db_user.nom = user_update.nom
        if user_update.email:
            db_user.email = user_update.email
        if user_update.password:
            hashed_password = bcrypt.hashpw(user_update.password.encode('utf-8'), bcrypt.gensalt())
            db_user.password = hashed_password.decode('utf-8')
        db.commit()
        db.refresh(db_user)
    return db_user

# Fonction pour supprimer un utilisateur
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    db.delete(db_user)
    db.commit()
    return True
