"""
🛠️ FONCTIONS DE GESTION D'ERREURS POUR LES MATCHS
================================================
Fonctions pour gérer les erreurs de connexion à l'API 1xbet
"""

def render_match_error(match_id, user, error_type, error_message):
    """Affiche une page d'erreur pour les matchs"""
    
    # Données de démo pour les prédictions ML
    demo_match_data = {
        "team1": "Paris Saint Germain",
        "team2": "Manchester City", 
        "league": "Champions League",
        "minute": 65,
        "score1": 2,
        "score2": 1,
        "match_time_seconds": 3900,
        "odds_1": 2.1,
        "odds_x": 3.4,
        "odds_2": 3.2
    }
    
    # Obtenir les prédictions ML même en mode démo
    ml_predictions = None
    try:
        from app import ML_AVAILABLE, ml_integration
        if ML_AVAILABLE and ml_integration.models_loaded:
            ml_predictions = ml_integration.get_all_predictions(demo_match_data)
    except:
        ml_predictions = {"error": "Prédictions indisponibles"}
    
    # HTML pour les prédictions ML
    ml_html = ""
    if ml_predictions and "error" not in ml_predictions:
        ml_html = f"""
    <div style='background: linear-gradient(135deg, #16a085 0%, #27ae60 100%); color: white; padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
        <h3>🤖 PRÉDICTIONS MACHINE LEARNING (MODE DÉMO)</h3>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 15px 0;'>
            <div style='font-weight: bold; margin-bottom: 10px;'>📊 Match: {ml_predictions['match_info']['team1']} vs {ml_predictions['match_info']['team2']}</div>
            <div style='font-size: 12px; opacity: 0.9;'>Ligue: {ml_predictions['match_info']['league']} | Minute: {ml_predictions['match_info']['minute']} | Score: {ml_predictions['match_info']['score1']}-{ml_predictions['match_info']['score2']}</div>
        </div>"""
        
        # Afficher prédiction 1X2 si disponible
        if "1x2" in ml_predictions["predictions"]:
            pred_1x2 = ml_predictions["predictions"]["1x2"]
            ml_html += f"""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 10px 0;'>
            <div style='font-weight: bold; margin-bottom: 8px;'>🎯 RÉSULTAT 1X2:</div>
            <div style='font-size: 18px; font-weight: bold;'>{pred_1x2['prediction']}</div>
            <div style='font-size: 14px; margin-top: 5px;'>Confiance: {pred_1x2['confidence']:.1%}</div>
        </div>"""
        
        ml_html += "</div>"
    
    error_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Erreur Match {match_id} - ORACXPRED</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .error-header {{ background: #e74c3c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
            .error-info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .back-btn {{ background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }}
            .back-btn:hover {{ background: #2980b9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="error-header">
                <h1>⚠️ Erreur de Connexion API</h1>
                <p>Match ID: {match_id}</p>
            </div>
            
            <div class="error-info">
                <h3>Type d'erreur:</h3>
                <p><strong>{error_type}</strong></p>
                
                <h3>Message:</h3>
                <p>{error_message}</p>
                
                <h3>Solutions possibles:</h3>
                <ul>
                    <li>Vérifiez votre connexion internet</li>
                    <li>Réessayez dans quelques instants</li>
                    <li>L'API 1xbet est temporairement indisponible</li>
                </ul>
            </div>
            
            {ml_html}
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="back-btn">🏠 Accueil</a>
                <a href="/match/{match_id}" class="back-btn">🔄 Réessayer</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return error_template

def render_match_demo(match_id, user):
    """Affiche une page de démo quand aucun match n'est trouvé"""
    
    demo_data = {
        "team1": "Paris Saint Germain",
        "team2": "Manchester City",
        "league": "Champions League",
        "minute": 65,
        "score1": 2,
        "score2": 1
    }
    
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Match {match_id} - Mode Démonstration</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .demo-header {{ background: #f39c12; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
            .match-info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .back-btn {{ background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="demo-header">
                <h1>🎮 Mode Démonstration</h1>
                <p>Aucun match trouvé pour l'ID {match_id}</p>
            </div>
            
            <div class="match-info">
                <h3>Match de démonstration:</h3>
                <p><strong>{demo_data['team1']}</strong> vs <strong>{demo_data['team2']}</strong></p>
                <p>Ligue: {demo_data['league']}</p>
                <p>Score: {demo_data['score1']} - {demo_data['score2']}</p>
                <p>Minute: {demo_data['minute']}</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="back-btn">🏠 Accueil</a>
                <a href="/match/{match_id}" class="back-btn">🔄 Réessayer</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return template
