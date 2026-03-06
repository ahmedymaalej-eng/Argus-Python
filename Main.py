import logging
from Scrapers import AmazonScraper
from Database import DatabaseManager  # Assurez-vous que le nom dans Database.py est bien DatabaseManage
from Models import Product
from Analyzer import PriceAnalyzer

# Configuration des logs
logging.basicConfig(
    filename="argus.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def run_analysis():
    # 1. Initialisation des outils (Le "Cerveau", la "Base" et la "Main")
    db = DatabaseManager() 
    amazon = AmazonScraper()
    analyzer = PriceAnalyzer()

    # 2. Définition de la cible (Targets)
    targets = [
        {
            "name": "A Light in the Attic",
            "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
            "target_price": 40.0
        }
    ]

    print("[+] Lancement de l'analyse Argus...")

    # 3. Boucle de traitement unique
    for item in targets:
        try:
            logging.info(f"Démarrage pour {item['name']}")
            pprice = amazon.extract_price(item['url'])
            
            if pprice > 0:
                # Étape A : Sauvegarde en base de données
                db.save_price(item['name'], pprice, "Argus-Web")
                logging.info(f"Succès : {item['name']} à {pprice}€")
                
                # Étape B : Analyse décisionnelle immédiate
                analyzer.evaluate(item['name'], pprice, item['target_price'])
            else:
                logging.warning(f"Échec d'extraction pour {item['name']}")

        except Exception as e:
            logging.error(f"Erreur critique pour {item['name']} : {e}")
            print(f"[-] Erreur : {e}")

# Point d'entrée du programme
if __name__ == "__main__":
    run_analysis()
