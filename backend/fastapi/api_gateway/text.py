import qrcode
from reportlab.pdfgen import canvas
# Données de la signature
data = "BRh73XscGBynvDAifr7Tbhpn5cbmbs/BGcGLv3m/uWtF6eNcR3eL/ST271jM+8chNSDDai/DmIaMi/PSdLx4u2TiDe5rGqmGQCc6W8VhvX6p0IFH4ekrWow+/3xR2A0wqd8yPKUWB4BqCmAFKOHmhsBfAdzJdWXDUowL33cP4qPxNLe7d2XdbmTP9+XqYcMuPwGYsHKfC+uDQmN9KFnN0uEBOaNV4giphwSM9thjOy2DcvpTQXgP2vyNmNzIMb4zaCQL4vG3YgaNccKpT27GzRW2Gt/v0vGHeCJt0pVoT5LeHimSTNXBdYDkSfciLeUb8dozsMFlhl//pt7Ef4l/Ag=="  # cela peut être un hash ou toute autre information

# Générer le QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(data)
qr.make(fit=True)

# Créer l'image du QR code
img = qr.make_image(fill='black', back_color='white')

# Sauvegarder l'image
img.save("signature_qr.png")

c = canvas.Canvas("/home/markup/Documents/design.pdf")
c.drawImage("signature_qr.png", 100, 750, width=100, height=100)
c.save()
