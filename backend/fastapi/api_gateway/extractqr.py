import sys
import cv2
import numpy as np
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
from PIL import Image

def convert_pdf_to_images(pdf_path, dpi=400):
    """Convertit un PDF en images haute résolution."""
    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    
    for i, image in enumerate(images):
        img_path = f"page_{i}.png"
        image.save(img_path, "PNG")
        image_paths.append(img_path)
        print(f"✅ Image enregistrée : {img_path}")
    
    return image_paths

def preprocess_image(image_path):
    """Améliore l’image pour la détection du QR Code."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Appliquer un flou pour réduire le bruit
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Appliquer un filtre adaptatif pour améliorer le contraste
    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Détection des contours
    edges = cv2.Canny(image, 100, 200)
    
    processed_path = f"preprocessed_{image_path}"
    cv2.imwrite(processed_path, edges)
    print(f"✅ Image prétraitée enregistrée : {processed_path}")
    
    return processed_path

def extract_qr_code(image_path):
    """Extrait et lit un QR Code depuis une image."""
    image = Image.open(image_path)
    decoded_objects = decode(image)

    if decoded_objects:
        for obj in decoded_objects:
            return obj.data.decode('utf-8')
    
    # Vérification avec OpenCV si pyzbar échoue
    opencv_image = cv2.imread(image_path)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(opencv_image)
    
    if bbox is not None and data:
        return data
    
    return None

def main():
    if len(sys.argv) < 2:
        print("❌ Utilisation : python extractqr.py <fichier.pdf>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    image_paths = convert_pdf_to_images(pdf_file)

    found_qr = False
    for image_path in image_paths:
        preprocessed_path = preprocess_image(image_path)
        qr_data = extract_qr_code(preprocessed_path)

        if qr_data:
            print(f"🎉 QR Code détecté sur {image_path} : {qr_data}")
            found_qr = True
            break  # Arrête après la première détection

    if not found_qr:
        print("🚫 Aucun QR Code trouvé dans le document.")
        print("👉 Vérifie si le QR est bien visible dans preprocessed_page_0.png.")

if __name__ == "__main__":
    main()
