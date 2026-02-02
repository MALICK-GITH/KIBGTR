#!/usr/bin/env python3
"""
🐍 SNAKE WIN - SYSTÈME DE PRÉDICTIONS AVANCÉ
=============================================
Intégration des modèles JSON et PKL pour des prédictions optimisées
"""

import json
import pickle
import os
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

class SnakeWinSystem:
    """🐍 SYSTÈME DE PRÉDICTIONS SNAKE WIN"""
    
    def __init__(self):
        self.version = "SNAKE-WIN-2024"
        self.modele_json_path = ".cursor/models/simple_model_20260127_130444.json"
        self.modele_pkl_path = ".cursor/models/simple_model_20260127_131144.pkl"
        self.modele_over_under_path = "api/model_over_under_handicap.joblib"
        self.modele_json = None
        self.modele_pkl = None
        self.modele_over_under = None
        self.predictions_historiques = []
        self.precision_moyenne = 0.0
        
        # Charger les modèles au démarrage
        self._charger_modeles()
    
    def _charger_modeles(self):
        """Charger les modèles JSON, PKL et Over/Under"""
        try:
            # Charger le modèle JSON
            if os.path.exists(self.modele_json_path):
                with open(self.modele_json_path, 'r', encoding='utf-8') as f:
                    self.modele_json = json.load(f)
                print(f"✅ Modèle JSON chargé: {len(self.modele_json)} résultats")
            
            # Charger le modèle PKL
            if os.path.exists(self.modele_pkl_path):
                with open(self.modele_pkl_path, 'rb') as f:
                    self.modele_pkl = pickle.load(f)
                print(f"✅ Modèle PKL chargé: {len(self.modele_pkl)} résultats")
            
            # Charger le modèle Over/Under Handicap
            if os.path.exists(self.modele_over_under_path):
                try:
                    import joblib
                    self.modele_over_under = joblib.load(self.modele_over_under_path)
                    print(f"✅ Modèle Over/Under Handicap chargé depuis {self.modele_over_under_path}")
                except ImportError:
                    print("⚠️ joblib non disponible, utilisation de pickle pour le modèle Over/Under")
                    with open(self.modele_over_under_path, 'rb') as f:
                        self.modele_over_under = pickle.load(f)
                    print(f"✅ Modèle Over/Under Handicap chargé avec pickle")
                
        except Exception as e:
            print(f"❌ Erreur chargement modèles: {e}")
    
    def analyser_match_snake_win(self, team1: str, team2: str, league: str, 
                                odds_data: Dict, contexte_temps_reel: Optional[Dict] = None,
                                paris_alternatifs: Optional[List[Dict]] = None) -> Dict:
        """🐍 ANALYSE COMPLÈTE SNAKE WIN"""
        
        print(f"🐍 SNAKE WIN ANALYSE: {team1} vs {team2}")
        
        # Analyse basée sur les modèles chargés
        analyse_json = self._analyser_avec_modele_json(odds_data)
        analyse_pkl = self._analyser_avec_modele_pkl(odds_data)
        analyse_over_under = self._analyser_avec_modele_over_under(odds_data)
        
        # Fusion des analyses
        prediction_fusionnee = self._fusionner_analyses(analyse_json, analyse_pkl, analyse_over_under)
        
        # Analyse contextuelle
        analyse_contexte = self._analyser_contexte(contexte_temps_reel, odds_data)
        
        # Analyse des paris alternatifs
        analyse_paris = self._analyser_paris_alternatifs(paris_alternatifs)
        
        # Score final Snake Win
        score_final = self._calculer_score_snake_win(
            prediction_fusionnee, analyse_contexte, analyse_paris
        )
        
        # Génération du rapport
        rapport = {
            "systeme": "SNAKE WIN",
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "match": f"{team1} vs {team2}",
            "league": league,
            "prediction_principale": prediction_fusionnee["resultat"],
            "confiance": prediction_fusionnee["confiance"],
            "score_snake_win": score_final,
            "analyse_json": analyse_json,
            "analyse_pkl": analyse_pkl,
            "analyse_over_under": analyse_over_under,
            "analyse_contexte": analyse_contexte,
            "analyse_paris": analyse_paris,
            "recommandations": self._generer_recommandations(score_final, prediction_fusionnee, analyse_paris)
        }
        
        # Sauvegarder dans l'historique
        self.predictions_historiques.append(rapport)
        
        return rapport
    
    def _analyser_avec_modele_json(self, odds_data: Dict) -> Dict:
        """Analyse basée sur le modèle JSON"""
        if not self.modele_json:
            return {"resultat": "N", "confiance": 0.3, "source": "JSON indisponible"}
        
        # Extraire les cotes
        cote_1 = odds_data.get('avg_odds_1', 2.0)
        cote_x = odds_data.get('avg_odds_x', 3.0)
        cote_2 = odds_data.get('avg_odds_2', 3.0)
        
        # Comparer avec les moyennes du modèle
        meilleur_match = None
        difference_minimale = float('inf')
        
        for resultat, stats in self.modele_json.items():
            diff_1 = abs(stats['avg_odds_1'] - cote_1)
            diff_x = abs(stats['avg_odds_x'] - cote_x)
            diff_2 = abs(stats['avg_odds_2'] - cote_2)
            
            difference_totale = diff_1 + diff_x + diff_2
            
            if difference_totale < difference_minimale:
                difference_minimale = difference_totale
                meilleur_match = resultat
        
        confiance = max(0.3, 1.0 - (difference_minimale / 10.0))
        
        return {
            "resultat": meilleur_match or "N",
            "confiance": confiance,
            "source": "modèle JSON",
            "difference": difference_minimale
        }
    
    def _analyser_avec_modele_pkl(self, odds_data: Dict) -> Dict:
        """Analyse basée sur le modèle PKL"""
        if not self.modele_pkl:
            return {"resultat": "N", "confiance": 0.3, "source": "PKL indisponible"}
        
        # Logique similaire au modèle JSON mais avec les données PKL
        cote_1 = odds_data.get('avg_odds_1', 2.0)
        cote_x = odds_data.get('avg_odds_x', 3.0)
        cote_2 = odds_data.get('avg_odds_2', 3.0)
        
        meilleur_match = None
        difference_minimale = float('inf')
        
        for resultat, stats in self.modele_pkl.items():
            diff_1 = abs(stats['avg_odds_1'] - cote_1)
            diff_x = abs(stats['avg_odds_x'] - cote_x)
            diff_2 = abs(stats['avg_odds_2'] - cote_2)
            
            difference_totale = diff_1 + diff_x + diff_2
            
            if difference_totale < difference_minimale:
                difference_minimale = difference_totale
                meilleur_match = resultat
        
        confiance = max(0.3, 1.0 - (difference_minimale / 10.0))
        
        return {
            "resultat": meilleur_match or "N",
            "confiance": confiance,
            "source": "modèle PKL",
            "difference": difference_minimale
        }
    
    def _analyser_avec_modele_over_under(self, odds_data: Dict) -> Dict:
        """Analyse basée sur le modèle Over/Under Handicap"""
        if not self.modele_over_under:
            return {"resultat": "N", "confiance": 0.3, "source": "Over/Under indisponible"}
        
        try:
            # Extraire les cotes pertinentes pour Over/Under
            cote_over_2_5 = odds_data.get('over_2_5', 2.0)
            cote_under_2_5 = odds_data.get('under_2_5', 1.8)
            handicap_home = odds_data.get('handicap_home', 0.0)
            handicap_away = odds_data.get('handicap_away', 0.0)
            
            # Préparation des features pour le modèle
            features = [
                cote_over_2_5,
                cote_under_2_5,
                handicap_home,
                handicap_away,
                odds_data.get('avg_odds_1', 2.0),
                odds_data.get('avg_odds_x', 3.0),
                odds_data.get('avg_odds_2', 3.0)
            ]
            
            # Prédiction avec le modèle
            if hasattr(self.modele_over_under, 'predict'):
                prediction = self.modele_over_under.predict([features])[0]
                probabilites = None
                if hasattr(self.modele_over_under, 'predict_proba'):
                    probabilites = self.modele_over_under.predict_proba([features])[0]
                
                # Interpréter la prédiction
                if prediction == 1:
                    resultat = "OVER_2_5"
                    confiance = probabilites[1] if probabilites else 0.7
                elif prediction == 0:
                    resultat = "UNDER_2_5"
                    confiance = probabilites[0] if probabilites else 0.7
                else:
                    resultat = "HANDICAP"
                    confiance = 0.6
                
                return {
                    "resultat": resultat,
                    "confiance": float(confiance),
                    "source": "modèle Over/Under Handicap",
                    "features": features,
                    "prediction_brute": int(prediction)
                }
            else:
                # Si le modèle n'a pas de méthode predict, utiliser une logique simple
                if cote_over_2_5 < cote_under_2_5:
                    return {
                        "resultat": "OVER_2_5",
                        "confiance": 0.65,
                        "source": "modèle Over/Under (logique simple)"
                    }
                else:
                    return {
                        "resultat": "UNDER_2_5",
                        "confiance": 0.65,
                        "source": "modèle Over/Under (logique simple)"
                    }
                    
        except Exception as e:
            print(f"❌ Erreur analyse Over/Under: {e}")
            return {"resultat": "N", "confiance": 0.3, "source": "erreur Over/Under"}
    
    def _fusionner_analyses(self, analyse_json: Dict, analyse_pkl: Dict, analyse_over_under: Dict) -> Dict:
        """Fusionner les analyses JSON, PKL et Over/Under"""
        
        # Compter les votes pour chaque résultat
        votes = {}
        confiance_totale = 0
        sources = []
        
        # Ajouter les votes de chaque modèle
        for analyse in [analyse_json, analyse_pkl, analyse_over_under]:
            resultat = analyse["resultat"]
            confiance = analyse["confiance"]
            source = analyse["source"]
            
            if resultat not in votes:
                votes[resultat] = {"count": 0, "confiance_sum": 0, "sources": []}
            
            votes[resultat]["count"] += 1
            votes[resultat]["confiance_sum"] += confiance
            votes[resultat]["sources"].append(source)
            confiance_totale += confiance
            sources.append(source)
        
        # Trouver le résultat avec le plus de votes
        resultat_gagnant = max(votes.keys(), key=lambda x: votes[x]["count"])
        
        # Calculer la confiance moyenne pour le résultat gagnant
        confiance_moyenne = votes[resultat_gagnant]["confiance_sum"] / votes[resultat_gagnant]["count"]
        
        # Ajuster la confiance selon le nombre de modèles d'accord
        if votes[resultat_gagnant]["count"] == 3:
            # Tous les modèles sont d'accord
            confiance_finale = min(0.98, confiance_moyenne + 0.25)
            accord = "COMPLET_SNAKE_WIN"
        elif votes[resultat_gagnant]["count"] == 2:
            # Deux modèles sur trois sont d'accord
            confiance_finale = min(0.85, confiance_moyenne + 0.15)
            accord = "MAJORITAIRE_2/3"
        else:
            # Un seul modèle, prendre le plus confiant
            confiance_finale = max(analyse_json["confiance"], analyse_pkl["confiance"], analyse_over_under["confiance"])
            accord = "MINORITAIRE_1/3"
        
        return {
            "resultat": resultat_gagnant,
            "confiance": confiance_finale,
            "accord": accord,
            "sources": sources,
            "votes_detail": votes,
            "analyse_over_under": analyse_over_under
        }
    
    def _analyser_contexte(self, contexte_temps_reel: Optional[Dict], odds_data: Dict) -> Dict:
        """Analyser le contexte du match"""
        if not contexte_temps_reel:
            return {"score_contexte": 0, "analyse": "Aucun contexte temps réel"}
        
        score1 = contexte_temps_reel.get('score1', 0)
        score2 = contexte_temps_reel.get('score2', 0)
        minute = contexte_temps_reel.get('minute', 0)
        
        total_buts = score1 + score2
        difference = abs(score1 - score2)
        
        score_contexte = 0
        
        # Analyse du score
        if total_buts >= 4:
            score_contexte += 20  # Match très offensif
        elif total_buts >= 2:
            score_contexte += 10  # Match équilibré
        
        # Analyse de la différence
        if difference >= 3:
            score_contexte += 15  # Équipe dominatrice
        elif difference >= 2:
            score_contexte += 10  # Avance significative
        
        # Analyse du temps
        if minute >= 75:
            score_contexte += 10  # Fin de match
        elif minute >= 60:
            score_contexte += 5   # Dernier tiers
        
        return {
            "score_contexte": score_contexte,
            "total_buts": total_buts,
            "difference": difference,
            "minute": minute,
            "analyse": f"Score {score1}-{score2} à la {minute}ème minute"
        }
    
    def _analyser_paris_alternatifs(self, paris_alternatifs: Optional[List[Dict]]) -> Dict:
        """Analyser les paris alternatifs"""
        if not paris_alternatifs:
            return {"score_paris": 0, "opportunites": [], "analyse": "Aucun pari alternatif"}
        
        score_paris = 0
        opportunites = []
        
        for pari in paris_alternatifs:
            # Vérifier que pari est bien un dictionnaire
            if not isinstance(pari, dict):
                continue
                
            cote = pari.get('cote', 0)
            type_pari = pari.get('type', '')
            
            # Identifier les opportunités intéressantes
            if cote > 2.0 and cote < 4.0:
                score_paris += 10
                opportunites.append(f"{type_pari}: {cote}")
            elif cote >= 4.0 and cote < 6.0:
                score_paris += 5
                opportunites.append(f"{type_pari}: {cote} (risque)")
        
        return {
            "score_paris": score_paris,
            "opportunites": opportunites,
            "total_paris": len(paris_alternatifs),
            "analyse": f"{len(opportunites)} opportunités identifiées"
        }
    
    def _calculer_score_snake_win(self, prediction_fusionnee: Dict, 
                                 analyse_contexte: Dict, analyse_paris: Dict) -> Dict:
        """Calculer le score final Snake Win"""
        
        # Score de base basé sur la confiance de prédiction
        score_base = prediction_fusionnee["confiance"] * 100
        
        # Ajout des scores contextuels
        score_total = score_base
        score_total += analyse_contexte.get("score_contexte", 0)
        score_total += analyse_paris.get("score_paris", 0)
        
        # Bonus Snake Win spécial
        if prediction_fusionnee["accord"] == "COMPLET":
            score_total += 25  # Bonus pour accord complet
        
        # Niveau de recommandation
        if score_total >= 150:
            niveau = "🐍 SNAKE WIN - TRÈS HAUTE CONFIANCE"
            couleur = "#00ff00"
        elif score_total >= 120:
            niveau = "✅ FORTE RECOMMANDATION"
            couleur = "#00aa00"
        elif score_total >= 90:
            niveau = "⚠️ RECOMMANDATION MODÉRÉE"
            couleur = "#ffaa00"
        else:
            niveau = "❌ FAIBLE CONFIANCE"
            couleur = "#ff0000"
        
        return {
            "score_total": round(score_total, 2),
            "score_base": round(score_base, 2),
            "score_contexte": analyse_contexte.get("score_contexte", 0),
            "score_paris": analyse_paris.get("score_paris", 0),
            "niveau": niveau,
            "couleur": couleur,
            "bonus_accord": 25 if prediction_fusionnee["accord"] == "COMPLET" else 0
        }
    
    def _generer_recommandations(self, score_final: Dict, prediction: Dict, 
                               analyse_paris: Dict) -> List[str]:
        """Générer les recommandations Snake Win"""
        recommandations = []
        
        # Recommandation principale
        if prediction["resultat"] == "1":
            recommandations.append(f"🐙 VICTOIRE ÉQUIPE 1 - Confiance: {prediction['confiance']:.1%}")
        elif prediction["resultat"] == "2":
            recommandations.append(f"🐙 VICTOIRE ÉQUIPE 2 - Confiance: {prediction['confiance']:.1%}")
        else:
            recommandations.append(f"🤝 MATCH NUL - Confiance: {prediction['confiance']:.1%}")
        
        # Recommandations basées sur le score
        if score_final["score_total"] >= 150:
            recommandations.append("🐍 SNAKE WIN: PARI FORT RECOMMANDÉ")
            recommandations.append("💰 Mise suggérée: 3-5 unités")
        elif score_final["score_total"] >= 120:
            recommandations.append("✅ PARI RECOMMANDÉ")
            recommandations.append("💰 Mise suggérée: 2-3 unités")
        elif score_final["score_total"] >= 90:
            recommandations.append("⚠️ PARI MODÉRÉ")
            recommandations.append("💰 Mise suggérée: 1-2 unités")
        else:
            recommandations.append("❌ PARI DÉCONSEILLÉ")
            recommandations.append("🛑 Attendre une meilleure opportunité")
        
        # Recommandations sur les paris alternatifs
        opportunites = analyse_paris.get("opportunites", [])
        if opportunites:
            recommandations.append(f"🎯 Opportunités alternatives: {', '.join(opportunites[:3])}")
        
        return recommandations
    
    def get_statistiques(self) -> Dict:
        """Obtenir les statistiques du système Snake Win"""
        total_predictions = len(self.predictions_historiques)
        
        if total_predictions == 0:
            return {
                "total_predictions": 0,
                "precision_moyenne": 0,
                "systeme": "SNAKE WIN",
                "version": self.version,
                "modeles_charges": {
                    "json": self.modele_json is not None,
                    "pkl": self.modele_pkl is not None
                }
            }
        
        # Calculer les statistiques de base
        predictions_correctes = sum(1 for p in self.predictions_historiques 
                                  if p.get("correct", False))
        
        return {
            "total_predictions": total_predictions,
            "predictions_correctes": predictions_correctes,
            "precision_moyenne": predictions_correctes / total_predictions if total_predictions > 0 else 0,
            "systeme": "SNAKE WIN",
            "version": self.version,
            "modeles_charges": {
                "json": self.modele_json is not None,
                "pkl": self.modele_pkl is not None
            }
        }

# Point d'entrée principal
def creer_snake_win_system():
    """Créer une instance du système Snake Win"""
    return SnakeWinSystem()

# Test du système
if __name__ == "__main__":
    snake_win = SnakeWinSystem()
    
    # Test d'analyse
    odds_test = {
        'avg_odds_1': 1.8,
        'avg_odds_x': 3.5,
        'avg_odds_2': 4.2
    }
    
    contexte_test = {
        'score1': 1,
        'score2': 0,
        'minute': 65
    }
    
    resultat = snake_win.analyser_match_snake_win(
        "Équipe A", "Équipe B", "Ligue Test", odds_test, contexte_test
    )
    
    print("🐍 RÉSULTAT SNAKE WIN:")
    print(json.dumps(resultat, indent=2, ensure_ascii=False))
