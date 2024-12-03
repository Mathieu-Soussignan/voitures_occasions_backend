CREATE TABLE Marque (
    ID_Marque INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom TEXT NOT NULL
);

CREATE TABLE Carburant (
    ID_Carburant INTEGER PRIMARY KEY AUTOINCREMENT,
    Type TEXT NOT NULL
);

CREATE TABLE Transmission (
    ID_Transmission INTEGER PRIMARY KEY AUTOINCREMENT,
    Type TEXT NOT NULL
);

CREATE TABLE Vehicule (
    ID_Vehicule INTEGER PRIMARY KEY AUTOINCREMENT,
    Modele TEXT NOT NULL,
    Annee INTEGER NOT NULL,
    Kilometrage INTEGER NOT NULL,
    Prix REAL NOT NULL,
    Etat TEXT NOT NULL,
    Marque_ID INTEGER,
    Carburant_ID INTEGER,
    Transmission_ID INTEGER,
    FOREIGN KEY (Marque_ID) REFERENCES Marque(ID_Marque),
    FOREIGN KEY (Carburant_ID) REFERENCES Carburant(ID_Carburant),
    FOREIGN KEY (Transmission_ID) REFERENCES Transmission(ID_Transmission)
);