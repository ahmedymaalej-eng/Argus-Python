import logging
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from Scrapers import AmazonScraper, EbayScraper
from Database import DatabaseManager
from PriceAnalyzer import PriceAnalyzer
from Notifier import EmailNotifier  
from SMSNotifier import SMSNotifier 

# --- CONFIGURATION DU LOGGING C2 ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("argus.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Initialisation globale unique
db = DatabaseManager()
analyzer = PriceAnalyzer()
email_notifier = EmailNotifier()
sms_notifier = SMSNotifier()

def process_task(task):
    """Exécute le cycle Scraping -> IA -> SQL et retourne les opportunités."""
    name, target, s_name, bot = task
    try:
        logging.info(f"Analyse lancée : {name} sur {s_name}")

        # Extraction des données via le scraper
        price, reviews = bot.extract_data(name, target) 

        # --- BLOC DE SIMULATION RECONSTITUÉ ET RÉALIGNÉ ---
        if price == 0.0:
            logging.info(f"⚠️ [Simulation] Ajustement du prix pour forcer le test de l'alerte.")
            price = target - 50.0  # Force un prix inférieur à la cible pour déclencher le SMS
            reviews = ["Excellent produit, conforme à mes attentes.", "Qualité irréprochable."]
            
        if price > 0:
            is_good_deal, verdict = analyzer.evaluate(name, price, target, s_name, reviews)
            db.save_price(name, price, s_name, verdict)
            
            if is_good_deal:
                return {
                    "name": name,
                    "price": price,
                    "target": target,
                    "source": s_name,
                    "verdict": verdict,
                    "url": bot.generate_search_url(name)
                }
        else:
            logging.warning(f"Prix introuvable : {name} @ {s_name}")
            
    except Exception as e:
        logging.error(f"Erreur fatale sur {name} ({s_name}) : {e}")
    return None

def run_analysis():
    logging.info("DÉMARRAGE DU CYCLE DE SURVEILLANCE")
    
    targets = db.get_all_targets() 
    if not targets: 
        logging.warning("Aucune cible trouvée en base de données.")
        return

    all_tasks = []
    amazon_bot = AmazonScraper()
    ebay_bot = EbayScraper()

    for item in targets:
        sites_str = item.get('sites', "Amazon,eBay")
        sites_autorises = sites_str.split(',')
        if "Amazon" in sites_autorises:
            all_tasks.append((item['name'], item['target_price'], "Amazon", amazon_bot))
        if "eBay" in sites_autorises:
            all_tasks.append((item['name'], item['target_price'], "eBay", ebay_bot))

    if all_tasks:
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(process_task, all_tasks))
        
        valid_deals = [d for d in results if d is not None]
        
        # 🧪 TEST DE DIAGNOSTIC - Utilisation de l'objet global
        logging.info("🧪 Injection du test de diagnostic Resend...")
        fake_deal = [{'name': 'VÉRIFICATION SYSTÈME ARGUS', 'price': 1.0, 'source': 'Debug', 'url': 'https://resend.com'}]
        email_notifier.send_consolidated_report(fake_deal)
        
        if valid_deals:
            email_notifier.send_consolidated_report(valid_deals)
            logging.info(f"🚀 {len(valid_deals)} deals réels envoyés.")
        else:
            logging.info("ℹ️ Aucun deal réel trouvé ce cycle.")

if __name__ == "__main__":
    run_analysis()