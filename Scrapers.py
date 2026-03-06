from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import re

class BaseScraper(ABC):
    @abstractmethod
    def extract_price(self, url: str) -> float:
        pass

class AmazonScraper(BaseScraper):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def extract_price(self, url: str) -> float:
        try:
            # On laisse un petit délai pour faire "humain"
            time.sleep(1)
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, "html.parser")

            # Sélecteur spécifique pour le site de livres
            price_tag = soup.find("p", class_="price_color")
            
            if price_tag:
                price_str = price_tag.get_text().strip()
                # On garde les chiffres et le point (ex: £51.77 -> 51.77)
                clean_price = "".join(re.findall(r'[0-9.]+', price_str))
                return float(clean_price)
            
            return 0.0
        except Exception as e:
            print(f"[-] Erreur Scraper : {e}")
            return 0.0

class EbayScraper(AmazonScraper):
    pass
