# -*- coding: utf-8 -*-
"""
Point d'entrée Vercel pour ORACXPRED MÉTAPHORE avec OAuth
"""
import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer l'application OAuth
from app_oauth import create_app

# Créer l'application
app = create_app()

# Handler Vercel
def handler(environ, start_response):
    """Handler pour Vercel serverless functions"""
    return app(environ, start_response)

# Export pour Vercel
app_handler = handler
