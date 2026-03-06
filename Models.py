from dataclasses import dataclass,asdict # importe les outils pour créer des classes de données et les convertir
from datetime import datetime # importe le module pour gérer les dates et l'heure

@dataclass
class Product:
    name: str
    url: str
    target_price: float  
    current_price: float = 0.0
    last_update: str = ""

    #--------------------------

    def __post_init__(self):
        #validation et initialisation
        if not self.last_update:
            #On génère l'heure actuelle au format Année-Mois-Jour
            self.last_update=datetime.now().strftime("%Y-%M-%D %H:%M:%S")

        #---------------------
        if self.target_price <= 0:
            #soulève une erreur si le prix est négatif ou nul
            raise ValueError("Le prix cible doit être un numb5e positif .")
    #-----------
    def to_dict(self): #Méthode pour transformer l'objet en dictionnaire Python 
        #export JSON
        return asdict(self)# Utilise la fonctionasdict pour convertir proprement l'objet