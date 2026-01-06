#!/bin/bash
# QR Code Generator for First Friday Launch
# Creates printable QR codes for flyers

echo "🎨 Generating First Friday QR Codes..."

# Check if qrencode is installed
if ! command -v qrencode &> /dev/null
then
    echo "📦 Installing qrencode..."
    brew install qrencode
fi

# Create QR codes directory
mkdir -p web/qr_codes

# Main landing page QR (for flyers)
echo "📱 Generating landing page QR..."
qrencode -o web/qr_codes/first_friday_join.png -s 10 -m 2 "http://localhost:3000/join"

# Merchant QR codes
echo "🌭 Generating Rudy's QR..."
qrencode -o web/qr_codes/rudy_qr.png -s 8 "http://localhost:3000/m/rudy_hotdogs_001"

echo "🚗 Generating Your Detailing QR..."
qrencode -o web/qr_codes/detail_qr.png -s 8 "http://localhost:3000/m/detail_001"

# Kiosk QR (for Bored Board)
echo "📺 Generating Kiosk QR..."
qrencode -o web/qr_codes/kiosk_qr.png -s 10 "http://localhost:3000/kiosk.html"

echo "✅ QR codes generated in web/qr_codes/"
echo ""
echo "📋 To print:"
echo "  - Open web/qr_codes/first_friday_join.png"
echo "  - Print at actual size (should be ~3 inches)"
echo "  - Test scan from 2 feet away"
echo ""
echo "🖨️ For Staples/Vistaprint:"
echo "  1. Open Canva or design tool"
echo "  2. Import first_friday_join.png"
echo "  3. Add text from FIRST_FRIDAY_FLYER.md"
echo "  4. Export as PDF"
