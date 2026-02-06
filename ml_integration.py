"""
🤖 MODULE D'INTÉGRATION DES MODÈLES MACHINE LEARNING
==================================================
Intègre les modèles de prédiction FIFA dans le système de paris
"""

import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

class MLIntegration:
    """Classe principale pour l'intégration des modèles ML"""
    
    def __init__(self):
        self.model_over_under = None
        self.model_baseline = None
        self.models_loaded = False
        self.load_models()
    
    def load_models(self):
        """Charge les modèles ML depuis les fichiers joblib"""
        try:
            # Charger le modèle Over/Under Handicap
            if os.path.exists("model_over_under_handicap.joblib"):
                self.model_over_under = joblib.load("model_over_under_handicap.joblib")
                print("✅ Modèle Over/Under Handicap chargé")
            else:
                print("❌ Fichier model_over_under_handicap.joblib introuvable")
            
            # Charger le modèle Baseline
            if os.path.exists("fifa_model_baseline.joblib"):
                self.model_baseline = joblib.load("fifa_model_baseline.joblib")
                print("✅ Modèle Baseline FIFA chargé")
            else:
                print("❌ Fichier fifa_model_baseline.joblib introuvable")
            
            self.models_loaded = bool(self.model_over_under and self.model_baseline)
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des modèles: {e}")
            self.models_loaded = False
    
    def predict_match_result(self, match_data):
        """
        Prédit le résultat d'un match (1/X/2) avec le modèle baseline
        
        Args:
            match_data: dict avec données du match (minute, scores, cotes, équipes, ligue)
            
        Returns:
            dict: prédiction avec probabilités
        """
        if not self.model_baseline:
            return {"error": "Modèle baseline non disponible"}
        
        try:
            # Préparer les features pour le modèle baseline
            features = self._prepare_baseline_features(match_data)
            
            # Faire la prédiction
            prediction = self.model_baseline.predict(features)[0]
            probabilities = self.model_baseline.predict_proba(features)[0]
            
            # Récupérer les classes
            classes = self.model_baseline.classes_
            
            # Construire le résultat
            result = {
                "prediction": prediction,
                "probabilities": {
                    classes[i]: float(probabilities[i]) 
                    for i in range(len(classes))
                },
                "confidence": float(max(probabilities)),
                "timestamp": datetime.now().isoformat(),
                "model_type": "baseline_1x2"
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Erreur prédiction baseline: {str(e)}"}
    
    def predict_over_under(self, match_data, line=2.5):
        """
        Prédit Over/Under pour une ligne donnée
        
        Args:
            match_data: dict avec données du match
            line: ligne de Over/Under (défaut 2.5)
            
        Returns:
            dict: prédiction Over/Under
        """
        if not self.model_over_under:
            return {"error": "Modèle Over/Under non disponible"}
        
        try:
            # Préparer les features pour le modèle Over/Under
            features = self._prepare_over_under_features(match_data, line)
            
            # Extraire le modèle et les colonnes
            model = self.model_over_under["model"]
            columns = self.model_over_under["columns"]
            
            # Créer le DataFrame avec les bonnes colonnes
            df_features = pd.DataFrame([features], columns=columns)
            
            # Faire la prédiction
            prediction = model.predict(df_features)[0]
            probability = model.predict_proba(df_features)[0]
            
            result = {
                "prediction": "Over" if prediction == 1 else "Under",
                "line": line,
                "over_probability": float(probability[1]) if len(probability) > 1 else 0.0,
                "under_probability": float(probability[0]) if len(probability) > 0 else 0.0,
                "confidence": float(max(probability)),
                "timestamp": datetime.now().isoformat(),
                "model_type": "over_under_handicap"
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Erreur prédiction Over/Under: {str(e)}"}
    
    def predict_handicap(self, match_data, handicap=-1.5):
        """
        Prédit le résultat d'un handicap
        
        Args:
            match_data: dict avec données du match
            handicap: valeur du handicap (défaut -1.5)
            
        Returns:
            dict: prédiction handicap
        """
        if not self.model_over_under:
            return {"error": "Modèle Handicap non disponible"}
        
        try:
            # Préparer les features pour le modèle Handicap
            features = self._prepare_handicap_features(match_data, handicap)
            
            # Extraire le modèle et les colonnes
            model = self.model_over_under["model"]
            columns = self.model_over_under["columns"]
            
            # Créer le DataFrame avec les bonnes colonnes
            df_features = pd.DataFrame([features], columns=columns)
            
            # Faire la prédiction
            prediction = model.predict(df_features)[0]
            probability = model.predict_proba(df_features)[0]
            
            result = {
                "prediction": "Home" if prediction == 1 else "Away",
                "handicap": handicap,
                "home_probability": float(probability[1]) if len(probability) > 1 else 0.0,
                "away_probability": float(probability[0]) if len(probability) > 0 else 0.0,
                "confidence": float(max(probability)),
                "timestamp": datetime.now().isoformat(),
                "model_type": "over_under_handicap"
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Erreur prédiction Handicap: {str(e)}"}
    
    def _prepare_baseline_features(self, match_data):
        """Prépare les features pour le modèle baseline"""
        # Créer un DataFrame avec les features attendues
        features = pd.DataFrame({
            "minute": [match_data.get("minute", 0)],
            "score1": [match_data.get("score1", 0)],
            "score2": [match_data.get("score2", 0)],
            "odds_1": [match_data.get("odds_1", 2.0)],
            "odds_x": [match_data.get("odds_x", 3.0)],
            "odds_2": [match_data.get("odds_2", 2.5)],
            "team1": [match_data.get("team1", "Unknown")],
            "team2": [match_data.get("team2", "Unknown")],
            "league": [match_data.get("league", "Unknown")]
        })
        return features
    
    def _prepare_over_under_features(self, match_data, line):
        """Prépare les features pour le modèle Over/Under"""
        return [
            match_data.get("match_time_seconds", 0),
            match_data.get("score1", 0),
            match_data.get("score2", 0),
            match_data.get("score1", 0) + match_data.get("score2", 0),  # total_current
            match_data.get("odd", 2.0),  # cote pour Over/Under
            line  # ligne de Over/Under
        ]
    
    def _prepare_handicap_features(self, match_data, handicap):
        """Prépare les features pour le modèle Handicap"""
        return [
            match_data.get("match_time_seconds", 0),
            match_data.get("score1", 0),
            match_data.get("score2", 0),
            match_data.get("score1", 0) + match_data.get("score2", 0),  # total_current
            match_data.get("odd", 2.0),  # cote pour handicap
            handicap  # valeur du handicap
        ]
    
    def get_all_predictions(self, match_data):
        """
        Obtient toutes les prédictions disponibles pour un match
        
        Args:
            match_data: dict avec données complètes du match
            
        Returns:
            dict: toutes les prédictions disponibles
        """
        results = {
            "match_info": {
                "team1": match_data.get("team1", "Unknown"),
                "team2": match_data.get("team2", "Unknown"),
                "league": match_data.get("league", "Unknown"),
                "minute": match_data.get("minute", 0),
                "score1": match_data.get("score1", 0),
                "score2": match_data.get("score2", 0)
            },
            "predictions": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Prédiction 1X2
        baseline_pred = self.predict_match_result(match_data)
        if "error" not in baseline_pred:
            results["predictions"]["1x2"] = baseline_pred
        
        # Prédictions Over/Under (lignes courantes)
        for line in [0.5, 1.5, 2.5, 3.5]:
            ou_pred = self.predict_over_under(match_data, line)
            if "error" not in ou_pred:
                results["predictions"][f"over_under_{line}"] = ou_pred
        
        # Prédictions Handicap (handicaps courants)
        for handicap in [-1.5, -1.0, 0, +1.0, +1.5]:
            hc_pred = self.predict_handicap(match_data, handicap)
            if "error" not in hc_pred:
                results["predictions"][f"handicap_{handicap}"] = hc_pred
        
        return results
    
    def get_model_status(self):
        """Retourne le statut des modèles chargés"""
        return {
            "models_loaded": self.models_loaded,
            "over_under_available": self.model_over_under is not None,
            "baseline_available": self.model_baseline is not None,
            "timestamp": datetime.now().isoformat()
        }

# Instance globale pour l'application
ml_integration = MLIntegration()
