"""
🚀 LANCEMENT RAPIDE DE L'APPLICATION
==================================
Script pour démarrer l'application sans erreurs de base de données
"""

import os
import sys
from flask import Flask

# Désactiver temporairement SQLAlchemy pour éviter les erreurs de connexion
os.environ['SQLALCHEMY_DISABLE'] = '1'

# Importer l'application après avoir configuré l'environnement
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Importer les modules nécessaires
    from app import app, ML_AVAILABLE, ml_integration
    
    print("🚀 Démarrage de l'application ORACXPRED...")
    print(f"✅ Module ML disponible: {ML_AVAILABLE}")
    
    if ML_AVAILABLE:
        status = ml_integration.get_model_status()
        print(f"✅ Modèles ML chargés: {status['models_loaded']}")
    
    # Démarrer l'application sur le port 5000
    print("🌐 Lancement du serveur web sur http://localhost:5000")
    print("🔄 Appuyez sur Ctrl+C pour arrêter")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    
except KeyboardInterrupt:
    print("\n🛑 Arrêt de l'application demandé")
except Exception as e:
    print(f"❌ Erreur lors du démarrage: {e}")
    print("🔧 Vérifiez que tous les modules sont installés: pip install -r requirements.txt")
