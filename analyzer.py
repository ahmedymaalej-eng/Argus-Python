from textblob import TextBlob

class SentimentAnalyzer:
    """Moteur d'intelligence artificielle pour l'analyse des avis clients."""
    
    @staticmethod
    def get_verdict(reviews):
        """Transforme une liste de commentaires en un score de confiance."""
        if not reviews or len(reviews) == 0:
            return "⚖️ Analyse indisponible (pas d'avis)"
        
        # Fusion des textes pour une analyse globale
        full_text = " ".join(reviews)
        analysis = TextBlob(full_text)
        
        # Le score de polarité va de -1 (très négatif) à +1 (très positif)
        score = analysis.sentiment.polarity
        
        if score > 0.15:
            return f"✅ Fiable ({int(score*100)}%)"
        elif score < -0.1:
            return f"⚠️ Risqué ({int(score*100)}%)"
        else:
            return "🧐 Avis mitigés"
