#!/usr/bin/env python3
"""
Script de test pour l'API docs.camgovca.cm
- Vérifie la signature avec traiter_controle.php
- Télécharge le PDF si le document est invalide
"""

import requests
import sys
import os
from datetime import datetime

class DocsAPITester:
    def __init__(self):
        self.base_url = "https://docs.camgovca.cm"
        self.verify_endpoint = "/src/traiter_controle.php"
        self.pdf_endpoint = "/pdf"
        
        # Configuration des sessions avec SSL
        self.session = requests.Session()
        # Accepter les certificats ANTIC
        self.session.verify = True
        
    def extract_document_id(self, qr_content):
        """Extrait l'ID du document depuis le contenu QR"""
        if len(qr_content) > 344:
            doc_id = qr_content[344:]
            if doc_id.startswith('DCS') and doc_id[3:].isdigit():
                return doc_id
        return None
    
    def verify_signature(self, android_signature):
        """Vérifie la signature via l'API traiter_controle.php"""
        print(f"🔍 Vérification de la signature...")
        print(f"📊 Taille du contenu QR: {len(android_signature)} caractères")
        
        doc_id = self.extract_document_id(android_signature)
        if not doc_id:
            return {"error": "ID de document invalide", "valid": False}
        
        print(f"📄 ID du document extrait: {doc_id}")
        
        try:
            url = f"{self.base_url}{self.verify_endpoint}"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'DocsAPI-Tester/1.0'
            }
            data = {
                'androidSignature': android_signature
            }
            
            print(f"🌐 Envoi de la requête vers: {url}")
            response = self.session.post(url, headers=headers, data=data, timeout=30)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"📝 Réponse brute: {repr(response.text[:200])}")
            
            if response.status_code == 200:
                response_text = response.text.strip()
                
                if "Document valide et authentique" in response_text:
                    return {
                        "valid": True,
                        "message": "Document valide et authentique",
                        "document_id": doc_id,
                        "response": response_text
                    }
                elif "Document Invalide" in response_text:
                    return {
                        "valid": False,
                        "message": "Document Invalide",
                        "document_id": doc_id,
                        "response": response_text
                    }
                else:
                    return {
                        "valid": False,
                        "message": "Réponse inattendue",
                        "document_id": doc_id,
                        "response": response_text
                    }
            else:
                return {
                    "error": f"Erreur HTTP {response.status_code}",
                    "valid": False,
                    "response": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Erreur de requête: {str(e)}",
                "valid": False
            }
    
    def download_pdf(self, document_id, save_path=None):
        """Télécharge le PDF du document"""
        print(f"📥 Téléchargement du PDF pour: {document_id}")
        
        try:
            url = f"{self.base_url}{self.pdf_endpoint}/{document_id}.pdf"
            print(f"🌐 URL du PDF: {url}")
            
            # Vérifier d'abord si le PDF existe
            head_response = self.session.head(url, timeout=30)
            print(f"📡 Status Code (HEAD): {head_response.status_code}")
            
            if head_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"PDF non trouvé (HTTP {head_response.status_code})"
                }
            
            # Obtenir les informations du fichier
            content_length = head_response.headers.get('Content-Length', 'Unknown')
            content_type = head_response.headers.get('Content-Type', 'Unknown')
            last_modified = head_response.headers.get('Last-Modified', 'Unknown')
            
            print(f"📄 Type: {content_type}")
            print(f"📊 Taille: {content_length} octets")
            print(f"📅 Dernière modification: {last_modified}")
            
            # Télécharger le fichier
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                # Déterminer le chemin de sauvegarde
                if not save_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = f"downloaded_{document_id}_{timestamp}.pdf"
                
                # Sauvegarder le fichier
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                print(f"✅ PDF sauvegardé: {save_path}")
                print(f"📊 Taille téléchargée: {file_size} octets")
                
                return {
                    "success": True,
                    "file_path": save_path,
                    "file_size": file_size,
                    "document_id": document_id
                }
            else:
                return {
                    "success": False,
                    "error": f"Échec du téléchargement (HTTP {response.status_code})"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Erreur de téléchargement: {str(e)}"
            }
    
    def test_full_workflow(self, qr_content):
        """Test du workflow complet"""
        print("=" * 60)
        print("🚀 DÉBUT DU TEST - API DOCS.CAMGOVCA.CM")
        print("=" * 60)
        
        # 1. Vérification de la signature
        verify_result = self.verify_signature(qr_content)
        
        print("\n" + "=" * 40)
        print("📋 RÉSULTAT DE LA VÉRIFICATION")
        print("=" * 40)
        
        for key, value in verify_result.items():
            print(f"{key}: {value}")
        
        # 2. Téléchargement du PDF si document valide et authentique
        if verify_result.get('valid', False) and 'document_id' in verify_result:
            print("\n" + "=" * 40)
            print("📥 TÉLÉCHARGEMENT DU PDF (Document valide)")
            print("=" * 40)
            
            download_result = self.download_pdf(verify_result['document_id'])
            
            for key, value in download_result.items():
                print(f"{key}: {value}")
        
        elif not verify_result.get('valid', False) and 'document_id' in verify_result:
            print(f"\n❌ Document invalide - Pas de téléchargement (ID: {verify_result['document_id']})")
        
        else:
            print("\n❌ Impossible de télécharger - ID de document manquant")
        
        print("\n" + "=" * 60)
        print("🏁 FIN DU TEST")
        print("=" * 60)

def main():
    # Contenu QR de test
    qr_test = "6a4bwlTuWADey5/qTmTo4fikMkBZMzajjRDL2kYGVp2JtWNMOWbs625EMvu8T7pZmdCfb/GNibF7SWWo4fHAHS2LNemtr9bEjOLZtD7ClBSqOVpsqeNQwP07kyLWBYk03GIAymC1Zh06ZnMr6DIpURknGcPyF/mocRhlk30lxhFIYIknlyRWLY+DOIWZ7A+phaHO3FxLCHKFdQ1Ly3l6dHowBGMiINxWt+ZpgjUN2I0k/d+0sqb8snGv9cQzo+sBSbVqg+gIuO3xUU+SRK3Dpj86BjTPP18gRRed9vLyaFYHxIDnl9bO6gAU/Dr421FuxRVOQoJ2sjR4m/cwHwERNQ==DCS2023011004322244271348"
    
    # Permettre de passer un contenu QR en argument
    if len(sys.argv) > 1:
        qr_test = sys.argv[1]
    
    # Créer le testeur et lancer le workflow
    tester = DocsAPITester()
    tester.test_full_workflow(qr_test)

if __name__ == "__main__":
    main() 