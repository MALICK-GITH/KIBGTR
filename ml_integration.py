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
        self.model_dir = os.path.dirname(os.path.abspath(__file__))
        self.metrics = {
            "predictions_total": 0,
            "predictions_error": 0,
            "last_error": None,
            "last_prediction_at": None
        }
        self.load_models()
    
    def load_models(self):
        """Charge les mod??les ML depuis les fichiers joblib"""
        self.model_over_under = None
        self.model_baseline = None

        over_under_path = os.path.join(self.model_dir, "model_over_under_handicap.joblib")
        baseline_path = os.path.join(self.model_dir, "fifa_model_baseline.joblib")

        # Charger le mod??le Over/Under Handicap
        if os.path.exists(over_under_path):
            try:
                self.model_over_under = joblib.load(over_under_path)
                print("??? Mod??le Over/Under Handicap charg??")
            except Exception as e:
                print(f"??? Erreur chargement model_over_under_handicap.joblib: {e}")
        else:
            print("??? Fichier model_over_under_handicap.joblib introuvable")

        # Charger le mod??le Baseline
        if os.path.exists(baseline_path):
            try:
                self.model_baseline = joblib.load(baseline_path)
                print("??? Mod??le Baseline FIFA charg??")
            except Exception as e:
                print(f"??? Erreur chargement fifa_model_baseline.joblib: {e}")
        else:
            print("??? Fichier fifa_model_baseline.joblib introuvable")

        # Au moins un mod??le charg??
        self.models_loaded = bool(self.model_over_under or self.model_baseline)

    def _record_metric(self, ok, error_message=None):
        """Met ?? jour les m??triques internes"""
        self.metrics["predictions_total"] += 1
        self.metrics["last_prediction_at"] = datetime.now().isoformat()
        if not ok:
            self.metrics["predictions_error"] += 1
            self.metrics["last_error"] = error_message

    def _coerce_int(self, value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _coerce_float(self, value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _coerce_str(self, value, default="Unknown"):
        if value is None:
            return default
        value_str = str(value).strip()
        return value_str if value_str else default

    def _sanitize_match_data(self, match_data):
        """Nettoie et s??curise les donn??es de match pour ??viter les erreurs ML"""
        if not isinstance(match_data, dict):
            return None, ["match_data_invalid"]

        warnings = []

        minute = self._coerce_int(match_data.get("minute", 0), 0)
        if minute < 0:
            minute = 0
            warnings.append("minute_clamped_min")
        elif minute > 140:
            minute = 140
            warnings.append("minute_clamped_max")

        score1 = self._coerce_int(match_data.get("score1", 0), 0)
        score2 = self._coerce_int(match_data.get("score2", 0), 0)
        score1 = max(0, score1)
        score2 = max(0, score2)

        match_time_seconds = self._coerce_int(match_data.get("match_time_seconds", minute * 60), minute * 60)
        match_time_seconds = max(0, match_time_seconds)

        odds_1 = self._coerce_float(match_data.get("odds_1", 2.0), 2.0)
        odds_x = self._coerce_float(match_data.get("odds_x", 3.0), 3.0)
        odds_2 = self._coerce_float(match_data.get("odds_2", 2.5), 2.5)
        odd = self._coerce_float(match_data.get("odd", 2.0), 2.0)

        # S??curit?? sur les cotes
        if odds_1 <= 1.0:
            odds_1 = 2.0
            warnings.append("odds_1_reset")
        if odds_x <= 1.0:
            odds_x = 3.0
            warnings.append("odds_x_reset")
        if odds_2 <= 1.0:
            odds_2 = 2.5
            warnings.append("odds_2_reset")
        if odd <= 1.0:
            odd = 2.0
            warnings.append("odd_reset")

        sanitized = {
            "team1": self._coerce_str(match_data.get("team1"), "Unknown"),
            "team2": self._coerce_str(match_data.get("team2"), "Unknown"),
            "league": self._coerce_str(match_data.get("league"), "Unknown"),
            "minute": minute,
            "score1": score1,
            "score2": score2,
            "match_time_seconds": match_time_seconds,
            "odds_1": odds_1,
            "odds_x": odds_x,
            "odds_2": odds_2,
            "odd": odd
        }

        return sanitized, warnings

    def predict_match_result(self, match_data):
        """
        Prédit le résultat d'un match (1/X/2) avec le modèle baseline
        
        Args:
            match_data: dict avec données du match (minute, scores, cotes, équipes, ligue)
            
        Returns:
            dict: prédiction avec probabilités
        """
        if not self.model_baseline:
            self._record_metric(False, "model_baseline_unavailable")
            return {"error": "Mod??le baseline non disponible"}
        
        sanitized, warnings = self._sanitize_match_data(match_data)
        if not sanitized:
            error_message = "Donnees du match invalides"
            self._record_metric(False, error_message)
            return {"error": error_message}
        
        try:
            features = self._prepare_baseline_features(sanitized)
            prediction = self.model_baseline.predict(features)[0]
            probabilities = self.model_baseline.predict_proba(features)[0]
            classes = self.model_baseline.classes_
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
            self._record_metric(True)
            return result
        
        except Exception as e:
            error_message = f"Erreur pr??diction baseline: {str(e)}"
            self._record_metric(False, error_message)
            return {"error": error_message}

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
            self._record_metric(False, "model_over_under_unavailable")
            return {"error": "Mod??le Over/Under non disponible"}
        
        sanitized, warnings = self._sanitize_match_data(match_data)
        if not sanitized:
            error_message = "Donnees du match invalides"
            self._record_metric(False, error_message)
            return {"error": error_message}
        
        line_value = self._coerce_float(line, 2.5)
        if line_value <= 0:
            line_value = 2.5
        
        try:
            features = self._prepare_over_under_features(sanitized, line_value)
            model = self.model_over_under["model"]
            columns = self.model_over_under["columns"]
            df_features = pd.DataFrame([features], columns=columns)
            prediction = model.predict(df_features)[0]
            probability = model.predict_proba(df_features)[0]
            result = {
                "prediction": "Over" if prediction == 1 else "Under",
                "line": line_value,
                "over_probability": float(probability[1]) if len(probability) > 1 else 0.0,
                "under_probability": float(probability[0]) if len(probability) > 0 else 0.0,
                "confidence": float(max(probability)),
                "timestamp": datetime.now().isoformat(),
                "model_type": "over_under_handicap"
            }
            self._record_metric(True)
            return result
        
        except Exception as e:
            error_message = f"Erreur pr??diction Over/Under: {str(e)}"
            self._record_metric(False, error_message)
            return {"error": error_message}

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
            self._record_metric(False, "model_handicap_unavailable")
            return {"error": "Mod??le Handicap non disponible"}
        
        sanitized, warnings = self._sanitize_match_data(match_data)
        if not sanitized:
            error_message = "Donnees du match invalides"
            self._record_metric(False, error_message)
            return {"error": error_message}
        
        handicap_value = self._coerce_float(handicap, -1.5)
        
        try:
            features = self._prepare_handicap_features(sanitized, handicap_value)
            model = self.model_over_under["model"]
            columns = self.model_over_under["columns"]
            df_features = pd.DataFrame([features], columns=columns)
            prediction = model.predict(df_features)[0]
            probability = model.predict_proba(df_features)[0]
            result = {
                "prediction": "Home" if prediction == 1 else "Away",
                "handicap": handicap_value,
                "home_probability": float(probability[1]) if len(probability) > 1 else 0.0,
                "away_probability": float(probability[0]) if len(probability) > 0 else 0.0,
                "confidence": float(max(probability)),
                "timestamp": datetime.now().isoformat(),
                "model_type": "over_under_handicap"
            }
            self._record_metric(True)
            return result
        
        except Exception as e:
            error_message = f"Erreur pr??diction Handicap: {str(e)}"
            self._record_metric(False, error_message)
            return {"error": error_message}

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
        sanitized, warnings = self._sanitize_match_data(match_data)
        if not sanitized:
            return {"error": "Donnees du match invalides"}

        results = {
            "match_info": {
                "team1": sanitized.get("team1", "Unknown"),
                "team2": sanitized.get("team2", "Unknown"),
                "league": sanitized.get("league", "Unknown"),
                "minute": sanitized.get("minute", 0),
                "score1": sanitized.get("score1", 0),
                "score2": sanitized.get("score2", 0)
            },
            "predictions": {},
            "timestamp": datetime.now().isoformat()
        }
        
        baseline_pred = self.predict_match_result(sanitized)
        if "error" not in baseline_pred:
            results["predictions"]["1x2"] = baseline_pred
        
        for line in [0.5, 1.5, 2.5, 3.5]:
            ou_pred = self.predict_over_under(sanitized, line)
            if "error" not in ou_pred:
                results["predictions"][f"over_under_{line}"] = ou_pred
        
        for handicap in [-1.5, -1.0, 0, +1.0, +1.5]:
            hc_pred = self.predict_handicap(sanitized, handicap)
            if "error" not in hc_pred:
                results["predictions"][f"handicap_{handicap}"] = hc_pred
        
        return results

    def get_model_status(self):
        return {
            "models_loaded": self.models_loaded,
            "over_under_available": self.model_over_under is not None,
            "baseline_available": self.model_baseline is not None,
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat()
        }

