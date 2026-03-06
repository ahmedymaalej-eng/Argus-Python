import sqlite3
from datetime import datetime
from Models import Product


class DatabaseManager:
    #persistnce des données.
    def __init__(self, db_name="argus_project.db"):
        self.db_name = db_name
        self._create_table()
    
    def _get_connection(self):
        #connexion à la base
        return sqlite3.connect(self.db_name)
    
    def _create_table(self):
        #crée la table des prix
        query=""" 
        CREATE TABLE IF NOT EXISTS price_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        site_name TEXT NOT NULL,
        timestamp DETETIME NOT NULL
        )
        """
        with self._get_connection() as conn:
            conn.execute(query)
            conn.commit()
            print("[+] Base de données et table prêtes .")


    # MÉTHODE 1 : L'ancienne logique (Pillar 2)
    def save_product(self, product):
        """Sauvegarde via un objet Product complet"""
        query = "INSERT INTO price_history (product_name, price, site_name, timestamp) VALUES (?,?,?,?)"
        data = (product.name, product.current_price, "Argus-Web", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        try:
            with self._get_connection() as conn:
                conn.execute(query, data)
                conn.commit()
                print(f"[+] Succès : Objet '{product.name}' archivé.")
        except Exception as e:
            print(f"[-] Erreur SQL (save_product) : {e}")

    # MÉTHODE 2 : La nouvelle logique (Pillar 4 - Analyseur)
    def save_price(self, name, price, source):
        """Sauvegarde directe via paramètres (Utilisée par le nouvel Analyseur)"""
        query = "INSERT INTO price_history (product_name, price, site_name, timestamp) VALUES (?,?,?,?)"
        data = (name, price, source, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        try:
            with self._get_connection() as conn:
                conn.execute(query, data)
                conn.commit()
                print(f"[+] Succès : Prix de '{name}' ({price}€) enregistré.")
        except Exception as e:
            print(f"[-] Erreur SQL (save_price) : {e}")



    def get_product_history(self,name: str):
        #récupère l'historique, trié du plus récent au plus ancien
        query="""
        SELECT price,timestamp
        FROM price_history
        WHERE product_name=?
        ORDER BY timestamp DESC
        """
        try: 
            with self._get_connection() as conn:
                cursor=conn.execute(query,(name,))
                return cursor.fetchall() 
        except Exception as e:
            print(f"[-] Erreur SQL lors de la lecture : {e}")
            return

            