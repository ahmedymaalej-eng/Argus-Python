from Database import DatabaseManager

class PriceAnalyzer:
    def __init__(self):
        self.db = DatabaseManager()

    def evaluate(self, product_name, current_price, target_price):
        print(f"\n--- ANALYSE : {product_name} ---")
        print(f"Prix actuel : {current_price}€ | Prix cible : {target_price}€")

        if current_price <= target_price:
            print(f"🟢 ALERTE : Le prix est optimal ! C'est le moment d'acheter.")
            return True
        else:
            economie_voulue = current_price - target_price
            print(f"🔴 ÉTAT : Le prix est encore trop élevé. (Écart : {economie_voulue:.2f}€)")
            return False
