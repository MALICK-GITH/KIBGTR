"""
Point d'entrée Vercel pour l'application Flask ORACXPRED
"""
import sys
import os

# Ajouter le répertoire parent au path pour les imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer l'application Flask
from app import app

# Vercel utilise automatiquement l'objet 'app' Flask
# L'application sera automatiquement initialisée avec l'admin au démarrage
