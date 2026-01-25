# 🗄️ **SYSTÈME DE PERSISTANCE ORACXPRED**

## 📋 **DESCRIPTION**

Le système de persistance ORACXPRED garantit que **toutes les données sont sauvegardées de manière permanente**, même après redémarrage du serveur ou réinitialisation.

---

## 🔧 **ARCHITECTURE**

### **Base de Données**
- **Chemin** : `data/oracxpred.db` (chemin absolu)
- **Type** : SQLite (compatible tous environnements)
- **Persistance** : Garantie sur disque dur

### **Système de Backup**
- **Automatique** : Toutes les 6 heures
- **Manuel** : Via interface admin ou script
- **Rétention** : 7 jours par défaut
- **Emplacement** : `backups/`

---

## 🚀 **FONCTIONNALITÉS**

### **1. Persistance Garantie**
```python
# La base de données est stockée dans data/oracxpred.db
# Chemin absolu créé automatiquement
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DB_PATH = os.path.join(DATA_DIR, 'oracxpred.db')
```

### **2. Backup Automatique**
- ✅ Toutes les 6 heures
- ✅ Métadonnées incluses
- ✅ Nettoyage automatique après 7 jours
- ✅ Vérification d'intégrité

### **3. Récupération**
- ✅ Restauration automatique si corruption
- ✅ Restauration manuelle via interface
- ✅ Export JSON des données

---

## 📁 **STRUCTURE DES FICHIERS**

```
fifa12345-main/
├── data/
│   └── oracxpred.db          # Base de données principale
├── backups/
│   ├── backup_20260124_014621.db
│   ├── backup_20260124_014621.db.meta
│   └── initial_backup.db
├── persistence_manager.py     # Gestionnaire de persistance
├── manage_persistence.py     # Script de gestion
└── fifa1.py                  # Application avec persistance intégrée
```

---

## 🛠️ **UTILISATION**

### **Démarrage**
```bash
python fifa1.py
# Le système crée automatiquement data/oracxpred.db
# Les backups sont créés automatiquement
```

### **Gestion des Backups**
```bash
# Voir le statut
python manage_persistence.py status

# Créer un backup manuel
python manage_persistence.py backup

# Lister les backups
python manage_persistence.py list

# Restaurer un backup
python manage_persistence.py restore

# Nettoyer les anciens backups
python manage_persistence.py cleanup

# Exporter les données
python manage_persistence.py export
```

### **Interface Admin**
- URL : `http://localhost:10000/admin/backup`
- Fonctionnalités :
  - ✅ Voir les statistiques
  - ✅ Créer des backups manuels
  - ✅ Restaurer des backups
  - ✅ Gérer la persistance

---

## 🔐 **SÉCURITÉ**

### **Protection des Données**
- ✅ Hashage bcrypt des mots de passe
- ✅ Backups chiffrés (optionnel)
- ✅ Logs d'accès et actions
- ✅ Vérification d'intégrité

### **Récupération**
- ✅ Détection automatique de corruption
- ✅ Restauration depuis dernier backup sain
- ✅ Export des données en JSON

---

## 📊 **STATISTIQUES**

### **Informations Disponibles**
- Taille de la base de données
- Nombre d'enregistrements par table
- Date de dernière modification
- Liste des backups disponibles
- Statut d'intégrité

### **Exemple de Sortie**
```
STATUT DU SYSTEME DE PERSISTANCE
==================================================
OK Intégrité: Base de données intacte
Base de données: C:\Users\KINGS\Downloads\fifa12345-main\data\oracxpred.db
Taille: 0.09 MB
Tables: 9
   users: 2 enregistrements
   system_logs: 15 enregistrements
Backups disponibles: 3
```

---

## 🔄 **PROCESSUS DE DÉMARRAGE**

### **1. Initialisation**
```
✅ Création du dossier data/
✅ Configuration de la base de données
✅ Vérification de l'intégrité
✅ Création du backup initial
✅ Démarrage du backup automatique
```

### **2. Vérification**
```
✅ Base de données accessible
✅ Permissions correctes
✅ Espace disque suffisant
✅ Module de persistance actif
```

---

## 🚨 **DÉPANNAGE**

### **Problèmes Courants**

#### **Base de données introuvable**
```bash
# Solution : Le système crée automatiquement data/oracxpred.db
# Vérifier les permissions
python manage_persistence.py status
```

#### **Backup échoué**
```bash
# Solution : Vérifier l'espace disque
# Créer manuellement
python manage_persistence.py backup
```

#### **Corruption**
```bash
# Solution : Restauration automatique
# Ou manuelle
python manage_persistence.py restore
```

---

## 📈 **PERFORMANCES**

### **Optimisations**
- ✅ Requêtes SQL optimisées
- ✅ Index automatiques
- ✅ Cache des prédictions
- ✅ Compression des backups

### **Surveillance**
- ✅ Taille de la base de données
- ✅ Nombre de backups
- ✅ Espace disque utilisé
- ✅ Temps de réponse

---

## 🎯 **POINTS CLÉS**

### **✅ Ce qui est garanti**
- **Persistance** : Les données survivent aux redémarrages
- **Backup** : Sauvegardes régulières automatiques
- **Récupération** : Restauration en cas de problème
- **Sécurité** : Protection des données sensibles

### **🔧 Ce qui est automatique**
- Création du dossier `data/`
- Initialisation de la base de données
- Configuration des backups
- Nettoyage des anciens backups
- Vérification d'intégrité

---

## 📞 **SUPPORT**

### **Commandes Utiles**
```bash
# Vérifier que tout fonctionne
python manage_persistence.py status

# Créer un backup avant modification
python manage_persistence.py backup

# Exporter toutes les données
python manage_persistence.py export
```

### **Logs**
- Logs système dans `SystemLog`
- Logs d'accès dans `AccessLog`
- Logs de persistance dans la console

---

**🎉 VOTRE SYSTÈME EST MAINTENANT 100% PERSISTANT !**

Toutes les données sont sauvegardées automatiquement et survivront aux redémarrages du serveur.
