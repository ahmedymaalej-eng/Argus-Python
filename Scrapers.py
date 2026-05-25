import requests
from bs4 import BeautifulSoup
import time, re, logging, random
from abc import ABC, abstractmethod

def fetch_with_retry(url):
    
    # Liste de User-Agents pour alterner  
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]
      
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }

    try:
        # Pause plus longue pour ne pas paraître suspect
        time.sleep(random.uniform(3, 7))
        res = requests.get(url, headers=headers, timeout=15)
        return res if res.status_code == 200 else None
    except:
        return None

class BaseScraper(ABC):
    @abstractmethod
    def extract_data(self, keyword: str): pass
    @abstractmethod
    def generate_search_url(self, keyword: str): pass

class AmazonScraper(BaseScraper):
    def generate_search_url(self, keyword):
        """Génère l'URL de recherche standard pour Amazon France."""
        return f"https://www.amazon.fr/s?k={keyword.replace(' ', '+')}"

    def extract_data(self, keyword: str, target: float):
        """
        Extrait le prix organique le plus pertinent tout en filtrant les accessoires.
        L'argument 'target' est désormais OBLIGATOIRE pour le filtrage intelligent.
        """
        url = self.generate_search_url(keyword)
        res = fetch_with_retry(url)
        
        if not res: 
            return 0.0, []
            
        soup = BeautifulSoup(res.text, "lxml")
        
        # Sélecteur robuste pour le premier prix principal affiché
        price_tag = soup.select_one(".a-price-whole")
        # Récupération optionnelle du titre pour la validation IA
        title_tag = soup.select_one("h2 a span")
        
        if price_tag:
            try:
                # Nettoyage rigoureux : suppression des séparateurs de milliers et espaces
                raw_price = price_tag.get_text().replace('\xa0', '').replace(' ', '').replace(',', '').strip()
                price = float(raw_price)

                # --- PROTOCOLE DE SÉCURITÉ C2 (PRICE FLOOR) ---
                # On évince les résultats dont le prix est inférieur à 30% de la cible 
                # (ex: un câble à 20€ pour une console ciblée à 300€)
                if price < (target * 0.3):
                    logging.warning(f"⚠️ Artefact détecté pour {keyword} : {price}€ ignoré (Seuil accessoire).")
                    return 0.0, []

                title = title_tag.get_text() if title_tag else "Produit Amazon"
                logging.info(f"✅ Analyse Amazon fructueuse : {title[:40]}... | {price}€")
                
                return price, [f"Source : Amazon | {title[:40]}..."]
                
            except (ValueError, AttributeError) as e:
                logging.error(f"[-] Échec du parsing de prix sur Amazon : {e}")
                
        return 0.0, []

class EbayScraper(BaseScraper):
    def generate_search_url(self, keyword):
        return f"https://www.ebay.fr/sch/i.html?_nkw={keyword.replace(' ', '+')}&_sop=12&LH_TitleDesc=0"

    # AJOUT de l'argument target ici
    def extract_data(self, keyword: str, target: float):
        url = self.generate_search_url(keyword)
        res = fetch_with_retry(url)
        
        if not res: 
            return 0.0, []
            
        soup = BeautifulSoup(res.text, "lxml")
        items = soup.select(".s-item__wrapper")
        
        for item in items:
            title_tag = item.select_one(".s-item__title")
            if not title_tag or "tous les objets" in title_tag.get_text().lower():
                continue

            price_tag = item.select_one(".s-item__price")
            condition_tag = item.select_one(".SECONDARY_INFO")
            condition = condition_tag.get_text().lower() if condition_tag else ""

            if title_tag and price_tag:
                title = title_tag.get_text().lower()
                price_text = price_tag.get_text()
                
                # Regex robuste pour les formats européens
                price_match = re.search(r'(\d+[\s.]?\d*[.,]\d+)', price_text)
                
                if price_match:
                    raw_price = price_match.group(1).replace(' ', '').replace('.', '').replace(',', '.')
                    try:
                        price = float(raw_price)
                        
                        # --- FILTRE DE SÉCURITÉ C2 (PRICE FLOOR) ---
                        # On ignore tout ce qui est en dessous de 30% du prix cible
                        if price < (target * 0.3):
                            logging.warning(f"⚠️ Accessoire suspecté pour {keyword} ({price}€ < {target*0.3}€). Ignoré.")
                            continue

                        # Logique de pertinence sémantique
                        keywords = keyword.lower().split()
                        is_relevant = all(k in title for k in keywords)
                        is_broken = any(x in condition for x in ["pièces", "non fonctionnel", "parts"])

                        if is_relevant and not is_broken:
                            logging.info(f"✅ Objet conforme trouvé : {title} | {price}€")
                            return price, [f"Source : eBay | {title[:40]}..."]
                            
                    except ValueError:
                        continue
                        
        logging.warning(f"[-] Aucun résultat organique pertinent sur eBay pour : {keyword}")
        return 0.0, []
    