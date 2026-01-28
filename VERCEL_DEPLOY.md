# 🚀 Déploiement sur Vercel - ORACXPRED

## 📋 Configuration

L'application est configurée pour fonctionner sur Vercel avec :
- ✅ Initialisation automatique de l'admin au démarrage
- ✅ Hashage sécurisé des mots de passe avec bcrypt
- ✅ Base de données SQLite persistante

## 🔧 Fichiers de configuration

### `vercel.json`
Configuration Vercel pour router toutes les requêtes vers l'application Flask.

### `api/index.py`
Point d'entrée serverless pour Vercel qui importe l'application Flask.

## 👤 Compte Admin

Le compte admin est **créé automatiquement** au premier démarrage de l'application :

- **Username** : `ADMIN`
- **Password** : `ADMIN123`
- **Statut** : Administrateur avec plan VIP

### Accès Admin

Une fois déployé sur Vercel :
1. Allez sur : `https://votre-app.vercel.app/admin/login`
2. Connectez-vous avec : `ADMIN` / `ADMIN123`
3. **Changez immédiatement le mot de passe** après la première connexion !

## 🔐 Sécurité

- Les mots de passe sont automatiquement hashés avec bcrypt
- L'admin est créé avec tous les privilèges nécessaires
- Le compte est automatiquement approuvé (`is_approved=True`)

## 📝 Déploiement

### Via CLI Vercel

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer
vercel

# Déployer en production
vercel --prod
```

### Via GitHub

1. Connectez votre repo GitHub à Vercel
2. Vercel détectera automatiquement la configuration
3. L'application sera déployée avec l'admin créé automatiquement

## ⚠️ Notes importantes

1. **Base de données** : SQLite est utilisé par défaut. Pour la production, considérez une base de données externe (PostgreSQL, etc.)

2. **Variables d'environnement** : Si vous utilisez une base de données externe, configurez `DATABASE_URL` dans les variables d'environnement Vercel

3. **Sessions** : Les sessions Flask sont stockées en mémoire. Pour la production, utilisez un store de sessions externe (Redis, etc.)

4. **Première connexion** : Après le déploiement, connectez-vous immédiatement et changez le mot de passe admin par défaut

## 🐛 Dépannage

### L'admin ne fonctionne pas ?

1. Vérifiez les logs Vercel pour voir si l'admin a été créé
2. L'admin est créé automatiquement au premier démarrage
3. Si nécessaire, vous pouvez exécuter `create_admin.py` localement avant de déployer

### Erreur de connexion ?

- Vérifiez que le mot de passe est bien `ADMIN123` (en majuscules)
- Vérifiez que le compte admin existe dans la base de données
- Consultez les logs Vercel pour plus de détails
