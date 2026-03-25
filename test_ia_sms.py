from PriceAnalyzer import PriceAnalyzer

def test_complete_flow():
    print("🚀 Lancement du test Argus IA + SMS...")
    
    analyzer = PriceAnalyzer()
    
    # Simulation de données (Produit, Prix actuel, Prix cible, Source)
    product = "Casque Sony WH-1000XM5"
    current_price = 250
    target_price = 300  # On met un prix cible plus haut pour forcer l'alerte
    source = "Amazon"
    
    # Simulation d'avis clients (3 positifs, 1 mitigé)
    fake_reviews = [
        "L'annulation de bruit est incroyable, je recommande !",
        "Meilleur casque que j'ai jamais eu.",
        "Le son est pur et la batterie tient longtemps.",
        "Un peu cher mais la qualité est au rendez-vous."
    ]
    
    print("🧠 Analyse du sentiment en cours...")
    triggered, verdict = analyzer.evaluate(product, current_price, target_price, source, fake_reviews)
    
    if triggered:
        print(f"✅ Succès ! Alerte déclenchée avec le verdict : {verdict}")
        print("📱 Vérifiez votre téléphone, le SMS doit être en route.")
    else:
        print("❌ L'alerte n'a pas été déclenchée. Vérifiez vos seuils de prix.")

if __name__ == "__main__":
    test_complete_flow()
