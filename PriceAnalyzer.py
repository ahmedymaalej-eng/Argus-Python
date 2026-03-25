import os
from SMSNotifier import SMSNotifier 
from analyzer import SentimentAnalyzer # <--- On importe votre nouveau fichier !

class PriceAnalyzer:
    def __init__(self):
        # Configuration Twilio (inchangée)
        self.sms_notifier = SMSNotifier()
        self.TAUX_CHANGE = 0.68 
        self.sentiment_tool = SentimentAnalyzer() # Initialisation de l'IA

    def evaluate(self, product_name, current_price, target_price, source, reviews=[]):
        """Évalue le prix et la qualité via l'IA."""
        # Conversion monétaire
        analysis_price = current_price * self.TAUX_CHANGE if source == "eBay Canada" else current_price
        
        # Appel à l'IA pour obtenir le verdict sur les avis
        verdict = self.sentiment_tool.get_verdict(reviews)
        
        if analysis_price <= target_price:
            alerte_texte = (
                f"📉 ARGUS : {product_name} à {analysis_price:.2f}€ ({source})\n"
                f"🧠 IA : {verdict}"
            )
            self.sms_notifier.send_sms(alerte_texte) 
            return True, verdict
        
        return False, verdict
