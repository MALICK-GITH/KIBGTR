"""
🚀 LANCEMENT SIMPLIFIÉ - MODE DÉMO ACTIVÉ
========================================
Script pour démarrer l'application avec mode démo intégré
"""

import os
import sys
import ssl
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Désactiver les vérifications SSL pour éviter les erreurs
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

# Importer l'application
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask
    
    # Importer les modules nécessaires
    from app import app, ML_AVAILABLE, ml_integration, DEMO_MODE_AVAILABLE
    
    print("🚀 Démarrage de l'application ORACXPRED...")
    print(f"✅ Module ML disponible: {ML_AVAILABLE}")
    print(f"🎮 Mode démo disponible: {DEMO_MODE_AVAILABLE}")
    
    if ML_AVAILABLE:
        try:
            status = ml_integration.get_model_status()
            print(f"✅ Modèles ML chargés: {status['models_loaded']}")
            print(f"✅ Over/Under disponible: {status['over_under_available']}")
            print(f"✅ Baseline disponible: {status['baseline_available']}")
        except:
            print("⚠️  Erreur vérification statut ML")
    
    print("\n🌐 CARACTÉRISTIQUES ACTIVÉES:")
    print("  🤖 Prédictions Machine Learning (1X2, Over/Under, Handicap)")
    print("  🎮 Mode démonstration hors ligne")
    print("  🛡️  Gestion robuste des erreurs SSL")
    print("  📊 Interface web complète")
    
    print("\n🔄 LANCEMENT DU SERVEUR:")
    print("  🌐 Adresse: http://localhost:5000")
    print("  🎯 Accès direct aux matchs: http://localhost:5000/match/691877621")
    print("  ⚠️  Mode démo activé si l'API 1xbet est inaccessible")
    print("  🔧 Appuyez sur Ctrl+C pour arrêter")
    
    # Démarrer l'application
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000, 
        use_reloader=False,
        ssl_context=None
    )
    
except KeyboardInterrupt:
    print("\n🛑 Arrêt de l'application demandé")
except Exception as e:
    print(f"❌ Erreur lors du démarrage: {e}")
    print("\n🔧 SOLUTIONS:")
    print("  1. Vérifiez que Python est installé correctement")
    print("  2. Installez les dépendances: pip install -r requirements.txt")
    print("  3. Vérifiez que les fichiers modèles sont présents:")
    print("     - model_over_under_handicap.joblib")
    print("     - fifa_model_baseline.joblib")
    print("  4. Redémarrez avec: python start_demo.py")
