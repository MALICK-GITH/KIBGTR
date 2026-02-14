"""
🎮 MODE DÉMONSTRATION HORS LIGNE
================================
Crée des données de match de démonstration quand l'API 1xbet n'est pas accessible
"""

import json
import random
from datetime import datetime, timedelta

def get_demo_matches():
    """Retourne une liste de matches de démonstration"""
    demo_matches = [
        {
            "I": 691877621,
            "O1": "Paris Saint Germain",
            "O2": "Manchester City",
            "LE": "Champions League",
            "MI": 65,
            "SC": {
                "FS": {"S1": 2, "S2": 1},
                "TS": 3900
            },
            "E": [
                {"G": 1, "T": 1, "C": 2.10},
                {"G": 1, "T": 2, "C": 3.40},
                {"G": 1, "T": 3, "C": 3.20}
            ]
        },
        {
            "I": 691877622,
            "O1": "Real Madrid",
            "O2": "Bayern Munich",
            "LE": "Champions League",
            "MI": 42,
            "SC": {
                "FS": {"S1": 1, "S2": 1},
                "TS": 2520
            },
            "E": [
                {"G": 1, "T": 1, "C": 1.95},
                {"G": 1, "T": 2, "C": 3.60},
                {"G": 1, "T": 3, "C": 3.80}
            ]
        },
        {
            "I": 691877623,
            "O1": "Liverpool",
            "O2": "Barcelona",
            "LE": "Champions League",
            "MI": 78,
            "SC": {
                "FS": {"S1": 3, "S2": 2},
                "TS": 4680
            },
            "E": [
                {"G": 1, "T": 1, "C": 1.85},
                {"G": 1, "T": 2, "C": 3.80},
                {"G": 1, "T": 3, "C": 4.20}
            ]
        }
    ]
    return demo_matches

def get_demo_match_by_id(match_id):
    """Retourne un match de démonstration par son ID"""
    matches = get_demo_matches()
    # Si l'ID correspond à un match de démo
    for match in matches:
        if match.get("I") == match_id:
            return match
    
    # Sinon, créer un match de démo aléatoire
    teams = [
        ("Paris Saint Germain", "Manchester City"),
        ("Real Madrid", "Bayern Munich"),
        ("Liverpool", "Barcelona"),
        ("Manchester United", "Chelsea"),
        ("AC Milan", "Inter Milan"),
        ("Borussia Dortmund", "RB Leipzig")
    ]
    
    leagues = ["Champions League", "Premier League", "La Liga", "Serie A", "Bundesliga"]
    
    team1, team2 = random.choice(teams)
    league = random.choice(leagues)
    minute = random.randint(15, 85)
    score1 = random.randint(0, 4)
    score2 = random.randint(0, 4)
    
    return {
        "I": match_id,
        "O1": team1,
        "O2": team2,
        "LE": league,
        "MI": minute,
        "SC": {
            "FS": {"S1": score1, "S2": score2},
            "TS": minute * 60
        },
        "E": [
            {"G": 1, "T": 1, "C": round(random.uniform(1.5, 3.0), 2)},
            {"G": 1, "T": 2, "C": round(random.uniform(3.0, 4.0), 2)},
            {"G": 1, "T": 3, "C": round(random.uniform(2.8, 4.5), 2)}
        ]
    }

def create_demo_response():
    """Crée une réponse de démonstration complète comme l'API 1xbet"""
    return {
        "Value": get_demo_matches(),
        "Success": True,
        "Message": "Données de démonstration - Mode hors ligne"
    }

def is_api_available():
    """Vérifie si l'API 1xbet est accessible"""
    try:
        from api_client import is_1xbet_available
        return is_1xbet_available(timeout=5, verify=False)
    except Exception:
        return False
