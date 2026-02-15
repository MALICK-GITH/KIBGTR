ADMIN_CLOUD_TEMPLATE = """<!DOCTYPE html>
<html><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Stockage Cloud - ORACXPRED</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }
        .header h1 {
            color: #333;
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .top-links {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .top-links a {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .top-links a:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        .provider-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .provider-card {
            border: 2px solid #e0e0e0;
            border-radius: 16px;
            padding: 25px;
            background: #f9f9f9;
        }
        .provider-card.active {
            border-color: #4caf50;
            background: #f1f8e9;
        }
        .provider-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .provider-name {
            font-size: 20px;
            font-weight: 600;
            color: #333;
        }
        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-active {
            background: #4caf50;
            color: white;
        }
        .status-inactive {
            background: #f44336;
            color: white;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .btn-success {
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        .btn-warning {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        .alert {
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .alert-info {
            background: #e3f2fd;
            color: #1976d2;
            border-left: 4px solid #1976d2;
        }
        .alert-warning {
            background: #fff3e0;
            color: #f57c00;
            border-left: 4px solid #f57c00;
        }
        .alert-success {
            background: #e8f5e8;
            color: #4caf50;
            border-left: 4px solid #4caf50;
        }
        .cloud-backups {
            margin-top: 30px;
        }
        .backup-item {
            background: #f5f5f5;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .backup-info {
            flex: 1;
        }
        .backup-name {
            font-weight: 600;
            color: #333;
        }
        .backup-meta {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background-color: #4caf50;
        }
        input:checked + .slider:before {
            transform: translateX(26px);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>☁️ Stockage Cloud</h1>
        <div class="top-links">
            <a href="/admin/dashboard">📊 Dashboard</a>
            <a href="/admin/backup">💾 Backups</a>
            <a href="/admin/oracx-admin">🎯 ORACX-ADMIN</a>
            <a href="/admin/logout">🚪 Déconnexion</a>
        </div>
    </div>

    {% if not cloud_enabled %}
    <div class="alert alert-warning">
        ⚠️ Le module de stockage cloud n'est pas disponible. Installez les dépendances nécessaires.
    </div>
    {% endif %}

    <div class="container">
        <h2 style="margin-bottom: 20px; color: #333;">🌤️ Configuration du Stockage Cloud</h2>
        
        {% if cloud_status %}
        <div class="provider-grid">
            <!-- Google Drive -->
            <div class="provider-card {% if cloud_status.providers.google_drive.enabled %}active{% endif %}">
                <div class="provider-header">
                    <div class="provider-name">📁 Google Drive</div>
                    <div class="status-badge {% if cloud_status.providers.google_drive.enabled %}status-active{% else %}status-inactive{% endif %}">
                        {% if cloud_status.providers.google_drive.enabled %}Actif{% else %}Inactif{% endif %}
                    </div>
                </div>
                
                <form method="post">
                    <input type="hidden" name="action" value="setup_google_drive">
                    <div class="form-group">
                        <label>Credentials JSON:</label>
                        <textarea name="credentials" rows="4" placeholder='{"client_id": "...", "client_secret": "..."}'>{{ cloud_status.providers.google_drive.credentials | default('', true) }}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        {% if cloud_status.providers.google_drive.enabled %}Mettre à jour{% else %}Configurer{% endif %}
                    </button>
                </form>
            </div>

            <!-- Dropbox -->
            <div class="provider-card {% if cloud_status.providers.dropbox.enabled %}active{% endif %}">
                <div class="provider-header">
                    <div class="provider-name">📦 Dropbox</div>
                    <div class="status-badge {% if cloud_status.providers.dropbox.enabled %}status-active{% else %}status-inactive{% endif %}">
                        {% if cloud_status.providers.dropbox.enabled %}Actif{% else %}Inactif{% endif %}
                    </div>
                </div>
                
                <form method="post">
                    <input type="hidden" name="action" value="setup_dropbox">
                    <div class="form-group">
                        <label>Access Token:</label>
                        <input type="text" name="access_token" placeholder="sl.xxxxxxxx" value="{{ cloud_status.providers.dropbox.access_token | default('', true) }}">
                    </div>
                    <button type="submit" class="btn btn-primary">
                        {% if cloud_status.providers.dropbox.enabled %}Mettre à jour{% else %}Configurer{% endif %}
                    </button>
                </form>
            </div>

            <!-- FTP -->
            <div class="provider-card {% if cloud_status.providers.ftp.enabled %}active{% endif %}">
                <div class="provider-header">
                    <div class="provider-name">🌐 FTP</div>
                    <div class="status-badge {% if cloud_status.providers.ftp.enabled %}status-active{% else %}status-inactive{% endif %}">
                        {% if cloud_status.providers.ftp.enabled %}Actif{% else %}Inactif{% endif %}
                    </div>
                </div>
                
                <form method="post">
                    <input type="hidden" name="action" value="setup_ftp">
                    <div class="form-group">
                        <label>Hôte:</label>
                        <input type="text" name="host" value="{{ cloud_status.providers.ftp.host | default('', true) }}">
                    </div>
                    <div class="form-group">
                        <label>Utilisateur:</label>
                        <input type="text" name="username" value="{{ cloud_status.providers.ftp.username | default('', true) }}">
                    </div>
                    <div class="form-group">
                        <label>Mot de passe:</label>
                        <input type="password" name="password" placeholder="••••••••">
                    </div>
                    <div class="form-group">
                        <label>Dossier:</label>
                        <input type="text" name="folder" value="{{ cloud_status.providers.ftp.folder | default('/oracxpred', true) }}">
                    </div>
                    <button type="submit" class="btn btn-primary">
                        {% if cloud_status.providers.ftp.enabled %}Mettre à jour{% else %}Configurer{% endif %}
                    </button>
                </form>
            </div>
        </div>

        <!-- Synchronisation Automatique -->
        <div style="margin-top: 30px;">
            <h3 style="margin-bottom: 20px; color: #333;">🔄 Synchronisation Automatique</h3>
            
            <form method="post">
                <input type="hidden" name="action" value="toggle_auto_sync">
                <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                    <label class="switch">
                        <input type="checkbox" name="auto_sync" {% if cloud_status.auto_sync.enabled %}checked{% endif %}>
                        <span class="slider"></span>
                    </label>
                    <span>Synchronisation automatique (toutes les {{ cloud_status.auto_sync.interval_hours }} heures)</span>
                </div>
                <button type="submit" class="btn btn-warning">Appliquer</button>
            </form>
        </div>

        <!-- Synchronisation Manuelle -->
        <div style="margin-top: 30px;">
            <h3 style="margin-bottom: 20px; color: #333;">⚡ Synchronisation Manuelle</h3>
            
            <form method="post">
                <input type="hidden" name="action" value="sync_now">
                <button type="submit" class="btn btn-success">
                    🚀 Synchroniser maintenant
                </button>
            </form>
        </div>

        <!-- Backups Cloud -->
        {% if cloud_status.backups %}
        <div class="cloud-backups">
            <h3 style="margin-bottom: 20px; color: #333;">☁️ Backups dans le Cloud</h3>
            
            {% for backup in cloud_status.backups %}
            <div class="backup-item">
                <div class="backup-info">
                    <div class="backup-name">{{ backup.filename }}</div>
                    <div class="backup-meta">
                        {{ backup.provider }} • {{ backup.size }} • {{ backup.date }}
                    </div>
                </div>
                <a href="{{ backup.download_url }}" class="btn btn-primary">Télécharger</a>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% else %}
        <div class="alert alert-info">
            ℹ️ Configurez au moins un provider de stockage cloud pour commencer la synchronisation.
        </div>
        {% endif %}
    </div>
</body>
</html>"""
