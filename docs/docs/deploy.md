# Guide de déploiement

Ce guide explique comment déployer CertiSign dans différents environnements, de la configuration de développement jusqu'à la production.

## Prérequis

Avant de commencer le déploiement, assurez-vous d'avoir installé les éléments suivants :

- Docker et Docker Compose
- Git
- Un serveur Linux (Ubuntu 20.04 LTS ou plus récent recommandé)
- Un nom de domaine configuré (pour la production)
- Certificats SSL/TLS (pour la production)

## Options de déploiement

CertiSign peut être déployé de plusieurs façons :

1. **Déploiement local** - Pour le développement et les tests
2. **Déploiement sur un serveur unique** - Pour les petites installations
3. **Déploiement distribué** - Pour les installations à haute disponibilité
4. **Déploiement cloud** - Sur AWS, Azure, Google Cloud, etc.

## Déploiement avec Docker Compose

Le moyen le plus simple de déployer CertiSign est d'utiliser Docker Compose.

### Étape 1 : Cloner le dépôt

```bash
git clone https://github.com/certisign/certisign.git
cd certisign
```

### Étape 2 : Configuration

Créez les fichiers d'environnement nécessaires :

```bash
cp .env.example .env
```

Modifiez le fichier `.env` avec vos propres paramètres :

```
# Configuration générale
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY=votre_cle_secrete_complexe

# Configuration de la base de données
DB_HOST=postgres
DB_PORT=5432
DB_NAME=certisign
DB_USER=certisign_user
DB_PASSWORD=mot_de_passe_sécurisé

# Configuration Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=mot_de_passe_redis

# Configuration du serveur de mail
MAIL_HOST=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=noreply@yourdomain.com
MAIL_PASSWORD=mot_de_passe_email
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS=noreply@yourdomain.com
MAIL_FROM_NAME=CertiSign

# Configuration JWT
JWT_SECRET=votre_cle_jwt_secrete
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=1209600

# URLs de l'application
FRONTEND_URL=https://votre-domaine.com
BACKEND_URL=https://api.votre-domaine.com
```

### Étape 3 : Lancer les conteneurs

```bash
docker-compose up -d
```

Cette commande va :
- Construire les images Docker si nécessaire
- Créer et démarrer les conteneurs pour chaque service
- Configurer les réseaux et volumes

### Étape 4 : Configurer la base de données

```bash
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
```

### Étape 5 : Configurer le proxy inverse (Nginx)

Créez un fichier de configuration Nginx pour votre domaine :

```
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;
    
    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;
    
    # Configuration SSL optimisée
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    
    # HSTS (36000 secondes = 10 heures)
    add_header Strict-Transport-Security "max-age=36000" always;
    
    # Frontend
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Documentation
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Déploiement en haute disponibilité

Pour un environnement de production nécessitant une haute disponibilité, voici l'architecture recommandée :

```
                  +-----------------+
                  |   Load Balancer |
                  +--------+--------+
                           |
              +------------+------------+
              |                         |
     +--------v-------+       +---------v------+
     | Frontend Node 1 |       | Frontend Node 2|
     +----------------+        +----------------+
              |                         |
              |                         |
     +--------v-------+       +---------v------+
     | Backend Node 1 |        | Backend Node 2 |
     +--------+-------+        +--------+-------+
              |                         |
              |                         |
     +--------v------------------------v--------+
     |           Database Cluster               |
     |  (PostgreSQL with replication)           |
     +------------------------------------------+
              |                         |
     +--------v-------+       +---------v------+
     |   Redis Cluster |       |  Object Storage|
     +----------------+        +----------------+
```

### Configuration du Load Balancer

Utilisez HAProxy ou un service cloud comme AWS ELB, Azure Load Balancer ou Google Cloud Load Balancing.

Exemple de configuration HAProxy :

```
frontend http_front
   bind *:80
   stats uri /haproxy?stats
   default_backend http_back
   
frontend https_front
   bind *:443 ssl crt /etc/ssl/certs/certisign.pem
   default_backend https_back

backend http_back
   redirect scheme https if !{ ssl_fc }
   server web1 10.0.0.1:8080 check
   server web2 10.0.0.2:8080 check

backend https_back
   balance roundrobin
   cookie SERVERID insert indirect nocache
   server web1 10.0.0.1:8080 check cookie web1
   server web2 10.0.0.2:8080 check cookie web2
```

### Configuration de la réplication PostgreSQL

Exemple de configuration avec un primaire et un replica :

```bash
# Sur le serveur primaire
docker-compose -f docker-compose.prod.yml up -d postgres

# Sur le serveur replica
docker-compose -f docker-compose.replica.yml up -d postgres-replica
```

## Déploiement sur Kubernetes

Pour les grands déploiements, Kubernetes est recommandé.

### Prérequis

- Un cluster Kubernetes (AKS, GKE, EKS ou auto-hébergé)
- Helm
- kubectl

### Installation avec Helm

```bash
# Ajouter le dépôt Helm
helm repo add certisign https://charts.certisign.com
helm repo update

# Installer CertiSign
helm install certisign certisign/certisign \
  --namespace certisign \
  --create-namespace \
  --set global.domain=votre-domaine.com \
  --set global.environment=production \
  --set postgresql.auth.password=mot_de_passe_sécurisé \
  --set postgresql.auth.replicationPassword=mot_de_passe_réplication \
  --values values-production.yaml
```

## Configuration SSL/TLS

### Obtenir des certificats avec Let's Encrypt

Utilisez Certbot pour obtenir gratuitement des certificats SSL/TLS :

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

### Configuration manuelle des certificats

Si vous avez vos propres certificats :

```bash
sudo mkdir -p /etc/ssl/certisign
sudo cp votre-certificat.pem /etc/ssl/certisign/cert.pem
sudo cp votre-cle-privee.key /etc/ssl/certisign/privkey.pem
```

## Sauvegardes

Configurez des sauvegardes régulières pour garantir la sécurité des données :

```bash
# Sauvegarde de la base de données
docker-compose exec postgres pg_dump -U certisign_user certisign > backup_$(date +%Y-%m-%d).sql

# Sauvegarde des fichiers
tar -zcvf backup_files_$(date +%Y-%m-%d).tar.gz /path/to/certisign/data

# Envoi vers un stockage externe
rclone copy backup_*.* remote:certisign-backups/
```

## Surveillance et maintenance

### Prometheus et Grafana

Pour surveiller l'état du système, déployez Prometheus et Grafana :

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### Mises à jour

Pour mettre à jour l'application :

```bash
# Récupérer les dernières modifications
git pull

# Reconstruire et redémarrer les conteneurs
docker-compose down
docker-compose build
docker-compose up -d

# Appliquer les migrations de base de données
docker-compose exec django python manage.py migrate
```

## Dépannage

### Vérifier les logs

```bash
# Logs de tous les conteneurs
docker-compose logs

# Logs d'un service spécifique
docker-compose logs django
docker-compose logs frontend
```

### Problèmes courants

#### Le serveur ne répond pas

Vérifiez l'état des conteneurs :

```bash
docker-compose ps
```

#### Problèmes de base de données

Vérifiez les connexions à la base de données :

```bash
docker-compose exec postgres psql -U certisign_user -d certisign -c "SELECT count(*) FROM pg_stat_activity;"
```

#### Problèmes de certificats

Vérifiez la validité des certificats :

```bash
openssl x509 -in /etc/ssl/certisign/cert.pem -text -noout
```

## Annexes

### Liste complète des variables d'environnement

Consultez le fichier [.env.example](https://github.com/certisign/certisign/blob/main/.env.example) pour une liste complète des variables d'environnement configurables.

### Docker Compose complet

Consultez le fichier [docker-compose.prod.yml](https://github.com/certisign/certisign/blob/main/docker-compose.prod.yml) pour la configuration complète de production. 