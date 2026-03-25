import nltk
import logging
from textblob import TextBlob

# Configuration du logging pour monitorer l'IA sur Render
logger = logging.getLogger(__name__)

# Protocole de déploiement automatique des ressources NLTK
def initialize_nltk():
    resources = ['punkt', 'averaged_perceptron_tagger', 'brown']
    for res in resources:
        try:
            nltk.data.find(f'tokenizers/{res}' if res == 'punkt' else f'corpora/{res}')
        except LookupError:
            logger.info(f"[+] Initialisation de la ressource NLTK : {res}")
            nltk.download(res, quiet=True)

initialize_nltk()

class SentimentAnalyzer:
    """Moteur d'intelligence artificielle pour l'analyse sémantique des avis clients."""
    
    @staticmethod
    def get_verdict(reviews):
        """
        Analyse une liste de commentaires pour générer un score de confiance prédictif.
        
        Args:
            reviews (list): Liste de chaînes de caractères (avis extraits).
            
        Returns:
            str: Verdict formaté avec indicateur visuel et pourcentage de fiabilité.
        """
        if not reviews or not isinstance(reviews, list) or len(reviews) == 0:
            return "⚖️ Analyse indisponible (données d'avis insuffisantes)"
        
        try:
            # Fusion des textes pour une analyse de sentiment globale
            # On limite à 5000 caractères pour éviter de saturer l'analyse
            full_text = " ".join([str(r) for r in reviews])[:5000]
            
            # Initialisation du moteur TextBlob
            analysis = TextBlob(full_text)
            
            # Le score de polarité oscille entre -1 (déceptif) et +1 (excellent)
            score = analysis.sentiment.polarity
            
            # Conversion du score brut en pourcentage de confiance (0-100)
            confidence = int(abs(score) * 100)
            
            # Logique de décision heuristique (Seuils de confiance C2)
            if score > 0.15:
                return f"✅ Fiable ({confidence}%)"
            elif score < -0.1:
                return f"⚠️ Risqué (Indice de négativité : {confidence}%)"
            else:
                return "🧐 Avis mitigés ou neutralité sémantique"
                
        except Exception as e:
            logger.error(f"[-] Erreur moteur IA : {e}")
            return "❌ Erreur lors de l'analyse sémantique"
