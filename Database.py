import sqlite3
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="argus_project.db"):
        self.db_name = db_name
        self._create_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_name)
        # Indispensable pour transformer les lignes SQL en dictionnaires Python
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Initialise la structure avec les colonnes 'verdict' et 'sites'."""
        with self._get_connection() as conn:
            # Table des cibles (avec support multi-sites)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    target_price REAL,
                    sites TEXT DEFAULT 'Amazon,eBay'
                )
            """)
            
            # Table de l'historique
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT,
                    price REAL,
                    source TEXT,
                    verdict TEXT DEFAULT 'N/A',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # --- MIGRATIONS AUTOMATIQUES (Éviter les erreurs Column Not Found) ---
            try:
                conn.execute("ALTER TABLE targets ADD COLUMN sites TEXT DEFAULT 'Amazon,eBay'")
            except sqlite3.OperationalError:
                pass # Déjà existant
                
            try:
                conn.execute("ALTER TABLE price_history ADD COLUMN verdict TEXT DEFAULT 'N/A'")
            except sqlite3.OperationalError:
                pass # Déjà existant

    def add_target(self, name, target_price, sites="Amazon,eBay"):
        """Ajoute ou met à jour une cible avec les sources sélectionnées."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO targets (name, target_price, sites) 
                    VALUES (?, ?, ?)
                """, (name, target_price, sites))
                logging.info(f"✅ Cible ajoutée/mise à jour : {name} ({sites})")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'ajout de la cible : {e}")

    def remove_target(self, name):
        """Supprime une cible de la surveillance."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM targets WHERE name = ?", (name,))
            logging.info(f"🗑️ Cible supprimée : {name}")

    def get_all_targets(self):
        """Récupère toutes les cibles sous forme de liste de dictionnaires."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM targets")
            return [dict(row) for row in cursor.fetchall()]

    def save_price(self, name, price, source, verdict="N/A"):
        """Enregistre le prix et le verdict de l'IA dans l'historique."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO price_history (product_name, price, source, verdict) VALUES (?, ?, ?, ?)",
                    (name, price, source, verdict)
                )
                logging.info(f"💾 Historique mis à jour pour {name} ({price}€ - {verdict})")
        except Exception as e:
            logging.error(f"❌ Erreur lors de la sauvegarde du prix : {e}")
