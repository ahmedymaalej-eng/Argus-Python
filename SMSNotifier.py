from twilio.rest import Client
import logging
import os
from dotenv import load_dotenv
load_dotenv()


class SMSNotifier:
    def __init__(self):
        # REMPLACEZ LES VALEURS CI-DESSOUS PAR VOS CLÉS TWILIO RÉELLES
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = "+13612139521"
        self.my_phone = "+14387950071"

        if not all([self.account_sid, self.auth_token, self.twilio_number]):
            logging.error("[-] SMS CONFIG MANQUANTE : Vérifiez vos clés Twilio.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logging.info("[+] Client Twilio initialisé.")
            except Exception as e:
                logging.error(f"[-] Connexion Twilio impossible : {e}")
                self.client = None

    def send_sms(self, message):
        if not self.client:
            logging.error("[-] Client SMS non initialisé.")
            return False
        
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=self.my_phone
            )
            logging.info(f"[+] SMS envoyé ! SID: {msg.sid}")
            return True
        except Exception as e:
            logging.error(f"[-] Échec Twilio : {e}")
            return False
