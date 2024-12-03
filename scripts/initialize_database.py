from API.database import engine
from API import models

# Créer les tables dans la base de données
models.Base.metadata.create_all(bind=engine)

print("Tables créées avec succès")