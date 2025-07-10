#!/usr/bin/env python3
"""
Serveur webhook simple pour déploiement automatique CertiSign
Ce script écoute les webhooks GitHub et déclenche le déploiement
"""

import os
import sys
import json
import subprocess
import hashlib
import hmac
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# Configuration
WEBHOOK_PORT = 9000
WEBHOOK_SECRET = "votre_secret_webhook_ici"  # À changer !
DEPLOY_SCRIPT = "/home/ssatl/Documents/Doc@uthANTIC/deploy.sh"
LOG_FILE = "/home/ssatl/Documents/Doc@uthANTIC/logs/webhook.log"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Gérer les requêtes POST du webhook GitHub"""
        try:
            # Lire le contenu de la requête
            content_length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(content_length)
            
            # Vérifier la signature si un secret est configuré
            if WEBHOOK_SECRET and WEBHOOK_SECRET != "votre_secret_webhook_ici":
                signature = self.headers.get('X-Hub-Signature-256')
                if not self.verify_signature(payload, signature):
                    logger.warning("Signature webhook invalide")
                    self.send_error(403, "Signature invalide")
                    return
            
            # Parser le JSON
            data = json.loads(payload.decode('utf-8'))
            
            # Vérifier si c'est un push sur la branche prod
            if self.is_prod_push(data):
                logger.info("Push détecté sur la branche prod - Déclenchement du déploiement")
                self.trigger_deployment()
                self.send_success_response()
            else:
                logger.info("Push ignoré (pas sur la branche prod)")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Push ignore (pas sur prod)')
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement du webhook: {e}")
            self.send_error(500, str(e))
    
    def verify_signature(self, payload, signature):
        """Vérifier la signature GitHub"""
        if not signature:
            return False
        
        expected_signature = 'sha256=' + hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def is_prod_push(self, data):
        """Vérifier si c'est un push sur la branche prod"""
        # Vérifier que c'est un événement push
        if 'ref' not in data:
            return False
        
        # Vérifier que c'est sur la branche prod
        return data['ref'] == 'refs/heads/prod'
    
    def trigger_deployment(self):
        """Déclencher le script de déploiement"""
        try:
            logger.info("Exécution du script de déploiement...")
            result = subprocess.run(
                ['bash', DEPLOY_SCRIPT],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("Déploiement réussi")
                logger.info(f"Sortie: {result.stdout}")
            else:
                logger.error(f"Échec du déploiement: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout du déploiement")
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du déploiement: {e}")
    
    def send_success_response(self):
        """Envoyer une réponse de succès"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'status': 'success',
            'message': 'Déploiement déclenché',
            'timestamp': datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_GET(self):
        """Gérer les requêtes GET (pour vérifier que le serveur fonctionne)"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""
        <html>
        <head><title>CertiSign Webhook Server</title></head>
        <body>
        <h1>🚀 CertiSign Webhook Server</h1>
        <p>Serveur en fonctionnement</p>
        <p>Port: {WEBHOOK_PORT}</p>
        <p>Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override pour utiliser notre logger"""
        logger.info(format % args)

def main():
    # Vérifier que le script de déploiement existe
    if not os.path.exists(DEPLOY_SCRIPT):
        logger.error(f"Script de déploiement non trouvé: {DEPLOY_SCRIPT}")
        sys.exit(1)
    
    # Créer le répertoire de logs s'il n'existe pas
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Démarrer le serveur
    server = HTTPServer(('', WEBHOOK_PORT), WebhookHandler)
    logger.info(f"🚀 Serveur webhook démarré sur le port {WEBHOOK_PORT}")
    logger.info(f"📝 Logs sauvegardés dans: {LOG_FILE}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Arrêt du serveur webhook")
        server.shutdown()

if __name__ == "__main__":
    main() 