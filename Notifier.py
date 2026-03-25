import requests
import logging
import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

class EmailNotifier:
    def __init__(self):
        """
        Initialisation du vecteur de communication via Resend.
        Extraction de la clé API depuis l'environnement pour une sécurité maximale.
        """
        # Récupération sécurisée de la clé
        self.api_key = os.getenv("RESEND_API_KEY")
        self.url = "https://api.resend.com/emails"
        
        # Configuration des émetteurs et destinataires
        self.from_email = "onboarding@resend.dev"
        self.to_email = "ahmed.y.maalej@gmail.com"

        # Vérification d'intégrité au démarrage
        if not self.api_key:
            logging.error("[-] ERREUR CRITIQUE : RESEND_API_KEY est introuvable dans le fichier .env")

    def send_consolidated_report(self, valid_deals):
        """Génère et expédie un rapport d'opportunités au format Premium HTML."""
        if not valid_deals:
            return False

        subject = f"🦅 ARGUS IA : {len(valid_deals)} OPPORTUNITÉS DÉTECTÉES"
        
        # Construction dynamique des lignes du tableau
        rows_html = ""
        for d in valid_deals:
            # Sécurité sur l'URL pour éviter les liens brisés
            url = d.get('url', 'https://www.google.com')
            
            rows_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 15px; font-size: 14px;">
                    <strong style="color: #2c3e50;">{d['name']}</strong><br>
                    <span style="color: #95a5a6; font-size: 12px;">{d['source']}</span>
                </td>
                <td style="padding: 15px; text-align: center;">
                    <span style="background-color: #27ae60; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;">
                        {d['price']}€
                    </span>
                </td>
                <td style="padding: 15px; text-align: right;">
                    <a href="{url}" style="background-color: #3498db; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: bold;">
                        VOIR L'OFFRE
                    </a>
                </td>
            </tr>
            """

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="background-color: #0b0e14; padding: 30px; text-align: center;">
                    <h1 style="color: #00ffcc; margin: 0; font-size: 24px; letter-spacing: 2px;">ARGUS INTELLIGENCE</h1>
                    <p style="color: #bdc3c7; margin: 10px 0 0; font-size: 14px; text-transform: uppercase;">Rapport de Veille Stratégique</p>
                </div>
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #34495e;">Bonjour <b>Ahmed Yassine</b>,</p>
                    <p style="font-size: 14px; color: #7f8c8d;">Le cycle de surveillance est terminé. Voici les actifs identifiés :</p>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                        <thead>
                            <tr style="text-align: left; border-bottom: 2px solid #34495e;">
                                <th style="padding: 10px; color: #34495e; font-size: 13px;">PRODUIT</th>
                                <th style="padding: 10px; color: #34495e; font-size: 13px; text-align: center;">PRIX</th>
                                <th style="padding: 10px; color: #34495e; font-size: 13px; text-align: right;">ACTION</th>
                            </tr>
                        </thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                </div>
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #bdc3c7; border-top: 1px solid #eee;">
                    <p>© 2026 Système Argus - Ahmed Yassine Maalej<br>Développement Python Expert C2</p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._execute_send(subject, full_html)

def _execute_send(self, subject, html_body):
    """Protocole de transport sécurisé vers l'API Resend (Niveau C2)."""
    if not self.api_key:
        logging.error("[-] Abandon de l'envoi : Clé API absente.")
        return False

    # Utilisation d'accolades simples pour des dictionnaires valides
    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": self.from_email,
        "to": [self.to_email],
        "subject": subject,
        "html": html_body
    }

    try:
        response = requests.post(self.url, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            logging.info(f"[+] SUCCÈS : Rapport expédié avec succès via Resend.")
            return True
        else:
            logging.error(f"[-] ÉCHEC RESEND {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logging.error(f"[-] ERREUR RÉSEAU : {e}")
        return False
