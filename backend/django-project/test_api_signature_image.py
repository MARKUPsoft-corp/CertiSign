#!/usr/bin/env python3
"""
Script de test pour vérifier que l'API retourne bien l'image de signature
après la correction du serializer.
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certisign_project.settings')
django.setup()

from documents.models import DocumentQRPosition
from documents.serializers import DocumentQRPositionSerializer
from django.test import RequestFactory

def test_api_signature_image():
    """Teste que l'API retourne bien l'image de signature"""
    
    print("🔍 Test de l'API pour l'image de signature")
    print("=" * 50)
    
    try:
        # Récupérer le document récemment créé
        document = DocumentQRPosition.objects.filter(
            document_name='acte-2.pdf'
        ).order_by('-created_at').first()
        
        if not document:
            print("❌ Document 'acte-2.pdf' non trouvé")
            return
        
        print(f"📄 Document trouvé: {document.document_name}")
        print(f"   ID: {document.id}")
        print(f"   Status: {document.status}")
        print(f"   Signature image (modèle): {document.signature_image}")
        print()
        
        # Créer une requête factice pour le serializer
        factory = RequestFactory()
        request = factory.get('/test/')
        
        # Tester le DocumentQRPositionSerializer
        print("🔧 Test du DocumentQRPositionSerializer")
        print("-" * 40)
        
        serializer = DocumentQRPositionSerializer(document, context={'request': request})
        data = serializer.data
        
        print("📊 Données retournées par l'API:")
        for key, value in data.items():
            if key in ['signature_image', 'signature_image_url']:
                print(f"   🔑 {key}: {value}")
            elif '_url' in key:
                print(f"   ✅ {key}: {value}")
            elif key in ['document_file', 'generated_pdf']:
                print(f"   🔒 {key}: {value} (write_only)")
            else:
                print(f"   📝 {key}: {value}")
        
        print()
        
        # Vérifier spécifiquement l'image de signature
        print("🎯 Vérification de l'image de signature")
        print("-" * 40)
        
        if 'signature_image' in data:
            if data['signature_image']:
                print("✅ signature_image est présent et non-null")
                print(f"   Valeur: {data['signature_image']}")
            else:
                print("⚠️  signature_image est présent mais null")
        else:
            print("❌ signature_image n'est pas dans la réponse de l'API")
        
        if 'signature_image_url' in data:
            if data['signature_image_url']:
                print("✅ signature_image_url est présent et non-null")
                print(f"   Valeur: {data['signature_image_url']}")
            else:
                print("⚠️  signature_image_url est présent mais null")
        else:
            print("❌ signature_image_url n'est pas dans la réponse de l'API")
        
        print()
        
        # Résumé
        print("📋 Résumé du test")
        print("-" * 40)
        
        has_signature_image = data.get('signature_image') is not None
        has_signature_url = data.get('signature_image_url') is not None
        
        if has_signature_image and has_signature_url:
            print("   🎉 API prête pour la signature !")
            print("   ✅ signature_image retourné par l'API")
            print("   ✅ signature_image_url disponible")
        elif has_signature_image:
            print("   ⚠️  signature_image OK mais signature_image_url manquant")
        elif has_signature_url:
            print("   ⚠️  signature_image_url OK mais signature_image manquant")
        else:
            print("   ❌ Problème : ni signature_image ni signature_image_url")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_api_signature_image()
    print("\n🏁 Test terminé") 