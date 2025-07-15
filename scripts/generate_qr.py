# scripts/generate_qr.py
import qrcode

url = "https://xodrops.com/drops/eighth_seal"  # Adjust to actual deployed URL if needed
img = qrcode.make(url)
img.save("public/drops/eighth_seal/assets/qr.png")
print("✅ QR code saved to: public/drops/eighth_seal/assets/qr.png")
