ADMIN_BACKUP_TEMPLATE = """<!DOCTYPE html>
<html><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gestion des Backups - ORACXPRED</title>
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
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
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
        .backups-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .backups-table th, .backups-table td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        .backups-table th {
            background: #f5f5f5;
            font-weight: 600;
            color: #333;
        }
        .backups-table tr:hover {
            background: #f9f9f9;
        }
        .status-enabled {
            color: #4caf50;
            font-weight: 600;
        }
        .status-disabled {
            color: #f44336;
            font-weight: 600;
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
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>💾 Gestion des Backups</h1>
        <div class="top-links">
            <a href="/admin/dashboard">📊 Dashboard</a>
            <a href="/admin/oracx-admin">🎯 ORACX-ADMIN</a>
            <a href="/admin/logout">🚪 Déconnexion</a>
        </div>
    </div>

    {% if not persistence_enabled %}
    <div class="alert alert-warning">
        ⚠️ Le module de persistance n'est pas disponible. Les backups automatiques sont désactivés.
    </div>
    {% endif %}

    {% if db_stats %}
    <div class="container">
        <h2 style="margin-bottom: 20px; color: #333;">📊 Statistiques de la Base de Données</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ "%.2f"|format(db_stats.size_mb) }} MB</div>
                <div class="stat-label">Taille de la base</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ db_stats.tables|length }}</div>
                <div class="stat-label">Tables</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ db_stats.tables.get('users', 0) }}</div>
                <div class="stat-label">Utilisateurs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ db_stats.modified.strftime('%d/%m/%Y %H:%M') if db_stats.modified else '—' }}</div>
                <div class="stat-label">Dernière modification</div>
            </div>
        </div>
    </div>
    {% endif %}

    <div class="container">
        <h2 style="margin-bottom: 20px; color: #333;">🔧 Actions de Backup</h2>
        
        <form method="post" style="margin-bottom: 30px;">
            <input type="hidden" name="action" value="backup">
            <button type="submit" class="btn btn-primary" {% if not persistence_enabled %}disabled{% endif %}>
                💾 Créer un backup manuel
            </button>
        </form>

        {% if persistence_enabled %}
        <div class="alert alert-info">
            ℹ️ Les backups automatiques sont effectués toutes les 6 heures. Les backups de plus de 7 jours sont automatiquement supprimés.
        </div>
        {% endif %}
    </div>

    <div class="container">
        <h2 style="margin-bottom: 20px; color: #333;">📋 Backups Disponibles</h2>
        
        {% if backups %}
        <table class="backups-table">
            <thead>
                <tr>
                    <th>Nom du fichier</th>
                    <th>Taille</th>
                    <th>Date de création</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for backup in backups %}
                <tr>
                    <td>
                        <strong>{{ backup.name }}</strong>
                        {% if backup.metadata.get('backup_time') %}
                        <br><small style="color: #666;">{{ backup.metadata.backup_time }}</small>
                        {% endif %}
                    </td>
                    <td>{{ "%.2f"|format(backup.size / (1024*1024)) }} MB</td>
                    <td>{{ backup.created.strftime('%d/%m/%Y %H:%M:%S') }}</td>
                    <td>
                        <form method="post" style="display:inline;">
                            <input type="hidden" name="action" value="restore">
                            <input type="hidden" name="backup_name" value="{{ backup.name }}">
                            <button type="submit" class="btn btn-warning" 
                                    onclick="return confirm('Êtes-vous sûr de vouloir restaurer ce backup ? Cela remplacera la base de données actuelle.')">
                                🔄 Restaurer
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty-state">
            <div class="empty-state-icon">💾</div>
            <h3>Aucun backup disponible</h3>
            <p>Créez votre premier backup manuel ou attendez le prochain backup automatique.</p>
        </div>
        {% endif %}
    </div>
</body>
</html>"""
