"""
🧪 TEST D'INTÉGRATION DES MODÈLES ML
==================================
Test complet de l'intégration des modèles ML dans le système
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_integration import ml_integration
import json

def test_ml_integration():
    """Test complet de l'intégration ML"""
    print("🧪 DÉBUT DU TEST D'INTÉGRATION ML")
    print("=" * 50)
    
    # 1. Vérifier le statut des modèles
    print("\n1️⃣ Vérification du statut des modèles:")
    status = ml_integration.get_model_status()
    print(f"✅ Modèles chargés: {status['models_loaded']}")
    print(f"✅ Over/Under disponible: {status['over_under_available']}")
    print(f"✅ Baseline disponible: {status['baseline_available']}")
    
    if not status['models_loaded']:
        print("❌ Les modèles ne sont pas chargés - Arrêt du test")
        return False
    
    # 2. Données de test
    print("\n2️⃣ Test avec données de match:")
    test_match = {
        "team1": "Paris Saint Germain",
        "team2": "Manchester City",
        "league": "Champions League",
        "minute": 65,
        "score1": 2,
        "score2": 1,
        "match_time_seconds": 3900,
        "odds_1": 2.1,
        "odds_x": 3.4,
        "odds_2": 3.2,
        "odd": 2.0  # Cote pour Over/Under
    }
    
    print(f"📊 Match test: {test_match['team1']} vs {test_match['team2']}")
    print(f"⏱️ Minute: {test_match['minute']} | Score: {test_match['score1']}-{test_match['score2']}")
    
    # 3. Test prédiction 1X2
    print("\n3️⃣ Test prédiction 1X2:")
    try:
        pred_1x2 = ml_integration.predict_match_result(test_match)
        if "error" not in pred_1x2:
            print(f"✅ Prédiction: {pred_1x2['prediction']}")
            print(f"✅ Confiance: {pred_1x2['confidence']:.1%}")
            print(f"✅ Probabilités: {pred_1x2['probabilities']}")
        else:
            print(f"❌ Erreur: {pred_1x2['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 4. Test Over/Under
    print("\n4️⃣ Test Over/Under (ligne 2.5):")
    try:
        pred_ou = ml_integration.predict_over_under(test_match, 2.5)
        if "error" not in pred_ou:
            print(f"✅ Prédiction: {pred_ou['prediction']}")
            print(f"✅ Confiance: {pred_ou['confidence']:.1%}")
            print(f"✅ Over: {pred_ou['over_probability']:.1%} | Under: {pred_ou['under_probability']:.1%}")
        else:
            print(f"❌ Erreur: {pred_ou['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 5. Test Handicap
    print("\n5️⃣ Test Handicap (-1.5):")
    try:
        pred_hc = ml_integration.predict_handicap(test_match, -1.5)
        if "error" not in pred_hc:
            print(f"✅ Prédiction: {pred_hc['prediction']}")
            print(f"✅ Confiance: {pred_hc['confidence']:.1%}")
            print(f"✅ Home: {pred_hc['home_probability']:.1%} | Away: {pred_hc['away_probability']:.1%}")
        else:
            print(f"❌ Erreur: {pred_hc['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 6. Test toutes les prédictions
    print("\n6️⃣ Test toutes les prédictions:")
    try:
        all_preds = ml_integration.get_all_predictions(test_match)
        if "error" not in all_preds:
            print(f"✅ Match analysé: {all_preds['match_info']['team1']} vs {all_preds['match_info']['team2']}")
            print(f"✅ Nombre de prédictions: {len(all_preds['predictions'])}")
            
            for pred_type, pred_data in all_preds['predictions'].items():
                print(f"  • {pred_type}: {pred_data.get('prediction', 'N/A')} ({pred_data.get('confidence', 0):.1%})")
        else:
            print(f"❌ Erreur: {all_preds['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 TEST D'INTÉGRATION ML TERMINÉ")
    return True

if __name__ == "__main__":
    test_ml_integration()
