"""
Point d'entrée Vercel pour l'application Flask FIFA Prediction System
"""
import sys
import os
from flask import Flask

# Ajouter le répertoire parent au path pour les imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer l'application Flask
from app import app

# Désactiver le mode debug pour Vercel
app.debug = False

# Vercel serverless handler
def handler(request):
    """Handler pour Vercel serverless functions"""
    return app(request.environ, lambda status, headers: None)

# Exporter pour Vercel
app_handler = app

# Forcer la configuration de l'application pour Vercel
if not app.config.get('TESTING'):
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
