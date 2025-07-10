# 🚀 Guide de Déploiement Automatique CertiSign

Ce guide vous explique comment configurer le déploiement automatique pour que vos `push` locaux déclenchent automatiquement une mise à jour sur le serveur de production.

## 📋 Vue d'ensemble

Le système de déploiement automatique permet :
- ✅ Push local → Déploiement automatique sur le serveur
- ✅ Arrêt/redémarrage automatique des services
- ✅ Mise à jour des dépendances
- ✅ Application des migrations Django
- ✅ Logs détaillés de chaque déploiement

## 🔧 Installation sur le Serveur

### 1. Transférer les fichiers sur le serveur

Connectez-vous à votre serveur et transférez les fichiers de déploiement :

```bash
# Sur votre machine locale, transférer les fichiers
scp deploy.sh ssatl@ppd.camgovca.cm:/home/ssatl/Documents/Doc@uthANTIC/
scp webhook_server.py ssatl@ppd.camgovca.cm:/home/ssatl/Documents/Doc@uthANTIC/
scp check_and_deploy.sh ssatl@ppd.camgovca.cm:/home/ssatl/Documents/Doc@uthANTIC/
scp certisign-webhook.service ssatl@ppd.camgovca.cm:/home/ssatl/
```

### 2. Rendre les scripts exécutables

```bash
chmod +x /home/ssatl/Documents/Doc@uthANTIC/deploy.sh
chmod +x /home/ssatl/Documents/Doc@uthANTIC/webhook_server.py
chmod +x /home/ssatl/Documents/Doc@uthANTIC/check_and_deploy.sh
```

### 3. Créer le répertoire de logs

```bash
mkdir -p /home/ssatl/Documents/Doc@uthANTIC/logs
```

## 🌐 Option 1: Déploiement via Webhooks GitHub (Recommandé)

### Étape 1: Configurer le secret webhook

Modifiez le fichier `webhook_server.py` :

```python
WEBHOOK_SECRET = "votre_secret_securise_ici"  # Remplacez par un secret fort
```

### Étape 2: Installer le service systemd

```bash
sudo cp /home/ssatl/certisign-webhook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable certisign-webhook.service
sudo systemctl start certisign-webhook.service
```

### Étape 3: Vérifier le statut du service

```bash
sudo systemctl status certisign-webhook.service
```

### Étape 4: Configurer le webhook GitHub

1. Allez sur votre repository GitHub
2. Settings → Webhooks → Add webhook
3. Payload URL: `http://ppd.camgovca.cm:9000`
4. Content type: `application/json`
5. Secret: Le même que dans `webhook_server.py`
6. Events: "Just the push event"
7. Active: ✅

### Étape 5: Ouvrir le port firewall (si nécessaire)

```bash
sudo ufw allow 9000
```

## ⏰ Option 2: Déploiement via Cron Job

Si vous préférez ne pas utiliser les webhooks, vous pouvez utiliser un cron job :

### Ajouter une tâche cron

```bash
crontab -e
```

Ajoutez cette ligne pour vérifier toutes les 5 minutes :

```bash
*/5 * * * * /home/ssatl/Documents/Doc@uthANTIC/check_and_deploy.sh
```

## 🔧 Configuration avancée

### Modifier les chemins (si nécessaire)

Si vos chemins sont différents, modifiez ces variables dans les scripts :

**Dans `deploy.sh` :**
```bash
PROJECT_DIR="/home/ssatl/Documents/Doc@uthANTIC"
```

**Dans `webhook_server.py` :**
```python
DEPLOY_SCRIPT = "/home/ssatl/Documents/Doc@uthANTIC/deploy.sh"
LOG_FILE = "/home/ssatl/Documents/Doc@uthANTIC/logs/webhook.log"
```

### Notifications par email (optionnel)

Pour recevoir des notifications par email :

1. Installez `mailutils` :
```bash
sudo apt install mailutils
```

2. Décommentez les lignes de notification dans `check_and_deploy.sh`

## 📊 Surveillance et Logs

### Voir les logs de déploiement

```bash
tail -f /home/ssatl/Documents/Doc@uthANTIC/logs/deploy.log
```

### Voir les logs du webhook

```bash
tail -f /home/ssatl/Documents/Doc@uthANTIC/logs/webhook.log
```

### Voir les logs du service systemd

```bash
sudo journalctl -u certisign-webhook.service -f
```

## 🧪 Tester le déploiement

### Test manuel du script de déploiement

```bash
cd /home/ssatl/Documents/Doc@uthANTIC
./deploy.sh
```

### Test du webhook (avec curl)

```bash
curl -X POST http://localhost:9000 \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/prod"}'
```

### Vérifier que le webhook server fonctionne

Ouvrez dans un navigateur : `http://ppd.camgovca.cm:9000`

## 🚀 Utilisation

Une fois configuré, le déploiement automatique fonctionne ainsi :

1. **Vous faites un push local :**
   ```bash
   git add .
   git commit -m "Nouvelle fonctionnalité"
   git push origin prod
   ```

2. **GitHub envoie un webhook au serveur**

3. **Le serveur exécute automatiquement :**
   - Arrêt des services CertiSign
   - Pull des changements
   - Mise à jour des dépendances
   - Migrations Django
   - Redémarrage des services

4. **Vos changements sont en ligne ! 🎉**

## ⚠️ Dépannage

### Le webhook ne fonctionne pas

1. Vérifiez le statut du service :
   ```bash
   sudo systemctl status certisign-webhook.service
   ```

2. Vérifiez les logs :
   ```bash
   sudo journalctl -u certisign-webhook.service
   ```

3. Testez la connectivité :
   ```bash
   curl http://localhost:9000
   ```

### Le déploiement échoue

1. Vérifiez les logs de déploiement :
   ```bash
   cat /home/ssatl/Documents/Doc@uthANTIC/logs/deploy.log
   ```

2. Testez manuellement :
   ```bash
   cd /home/ssatl/Documents/Doc@uthANTIC
   ./deploy.sh
   ```

### Permissions SSH

Assurez-vous que l'utilisateur `ssatl` peut accéder au repository :

```bash
cd /home/ssatl/Documents/Doc@uthANTIC
git pull origin prod  # Doit fonctionner sans demander de mot de passe
```

## 🔒 Sécurité

- ✅ Utilisez toujours un secret fort pour les webhooks
- ✅ Limitez l'accès au port webhook via firewall
- ✅ Surveillez les logs régulièrement
- ✅ Testez les déploiements en environnement de développement d'abord

## 📝 Maintenance

### Rotation des logs

Ajoutez cette configuration logrotate dans `/etc/logrotate.d/certisign` :

```
/home/ssatl/Documents/Doc@uthANTIC/logs/*.log {
    weekly
    rotate 52
    compress
    delaycompress
    missingok
    notifempty
    create 644 ssatl ssatl
}
```

---

🎉 **Félicitations ! Votre système de déploiement automatique est maintenant configuré !** 