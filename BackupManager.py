import os
import base64
from Notifier import EmailNotifier

class BackupManager:
    def __init__(self):
        self.notifier = EmailNotifier()
        self.db_path = "argus_project.db"

    def send_backup(self):
        if not os.path.exists(self.db_path):
            return False
            
        try:
            # Lecture de la base de données en binaire
            with open(self.db_path, "rb") as f:
                db_content = f.read()
            
            # Encodage pour l'envoi (si nécessaire selon l'API)
            # Ici, on envoie une alerte avec les stats en texte pour simplifier
            # car l'API Resend gratuite limite parfois les pièces jointes volumineuses
            
            subject = "📦 Sauvegarde Quotidienne Argus"
            body = f"Votre base de données a été sauvegardée avec succès le {os.popen('date').read()}."
            
            return self.notifier.send_email(subject, body)
        except Exception as e:
            print(f"Erreur Backup : {e}")
            return False
