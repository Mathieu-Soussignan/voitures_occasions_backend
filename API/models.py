from sqlalchemy import Column, Integer, String, Float, ForeignKey
from API.database import Base
from sqlalchemy.orm import relationship

class Vehicule(Base):
    __tablename__ = "Vehicule"
    id = Column("ID_Vehicule", Integer, primary_key=True, index=True)
    marque_id = Column("Marque_ID", Integer, ForeignKey("Marque.ID_Marque"), index=True)
    modele = Column("Modele", String)
    annee = Column("Annee", Integer)
    kilometrage = Column("Kilometrage", Float)
    prix = Column("Prix", Float)
    etat = Column("Etat", String)
    carburant_id = Column("Carburant_ID", Integer, ForeignKey("Carburant.ID_Carburant"), index=True)
    transmission_id = Column("Transmission_ID", Integer, ForeignKey("Transmission.ID_Transmission"), index=True)

    # Relations
    carburant = relationship("Carburant", lazy="joined")
    transmission = relationship("Transmission", lazy="joined")

class Carburant(Base):
    __tablename__ = "Carburant"
    id_carburant = Column("ID_Carburant", Integer, primary_key=True, index=True)
    type = Column(String)

class Transmission(Base):
    __tablename__ = "Transmission"
    id_transmission = Column("ID_Transmission", Integer, primary_key=True, index=True)
    type = Column(String)

class Marque(Base):
    __tablename__ = "Marque"
    id_marque = Column("ID_Marque", Integer, primary_key=True, index=True)
    nom = Column(String)

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nom = Column(String, nullable=False)
    password = Column(String, nullable=False)