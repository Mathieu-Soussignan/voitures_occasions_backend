from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Initialiser le driver
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

voitures = []

# Scraper chaque page
for current_page in range(1, 101):
    try:
        url = f"https://www.aramisauto.com/achat/occasion?page={current_page}"
        driver.get(url)
        time.sleep(3)

        print(f"Scraping page {current_page}")
        
        annonces = driver.find_elements(By.CLASS_NAME, "item")

        for annonce in annonces:
            try:
                # Extraire la marque et le modèle
                marque_modele = annonce.find_element(By.CLASS_NAME, 'product-card-vehicle-information__title').text

                # Extraire le prix
                prix = annonce.find_element(By.CLASS_NAME, 'heading-l').text

                # Extraire les autres informations (année, kilométrage, état)
                details_brut = annonce.find_element(By.CLASS_NAME, 'product-card-vehicle-information__bottom').text
                details = details_brut.split("\u2022")
                details = [detail.strip() for detail in details]

                annee = details[0] if len(details) > 0 else "Non spécifié"
                kilometrage = details[1] if len(details) > 1 else "Non spécifié"
                etat = details[2] if len(details) > 2 else "Non spécifié"

                # Nouvelle méthode pour extraire le type de carburant et la transmission
                try:
                    type_carburant = "Non spécifié"
                    transmission = "Non spécifié"
                    
                    detail_elements = annonce.find_elements(By.CLASS_NAME, 'product-card-vehicle-information__details--light')
                    
                    for element in detail_elements:
                        text = element.text.strip()
                        
                        # Vérifie la transmission sans continue
                        if text.endswith('Auto.') or text.endswith('Manuelle'):
                            transmission = text.split()[-1]
                        
                        # Vérifie le carburant avec .lower()
                        if any(fuel in text.lower() for fuel in ['diesel', 'essence', 'électrique', 'hybride']):
                            type_carburant = text.split()[0]
                            
                except Exception as e:
                    print(f"Erreur lors de l'extraction des détails: {e}")
                    type_carburant = "Non spécifié"
                    transmission = "Non spécifié"
                # Ajouter les informations au DataFrame
                voitures.append({
                    'Marque/Modèle': marque_modele,
                    'Année': annee,
                    'Kilométrage': kilometrage,
                    'Etat': etat,
                    'Prix': prix,
                    'Type de Carburant': type_carburant,
                    'Transmission': transmission
                })
                
            except Exception as e:
                print(f"Erreur lors de l'extraction: {e}")
                
    except Exception as e:
        print(f"Erreur lors de la pagination: {e}")
        break

# Créer un DataFrame et sauvegarder dans un fichier CSV
df = pd.DataFrame(voitures)
df.to_csv('voitures_aramisauto.csv', index=False)

# Fermer le driver
driver.quit()