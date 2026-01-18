# First Friday Flyer Design (Print-Ready)

**Design for Staples/Vistaprint - 8.5"x11" flyer**

---

## Front Side

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                      [LARGE QR CODE]                    │
│                                                         │
│                ═══════════════════════                  │
│                                                         │
│                        BORED?                           │
│                                                         │
│              Turn Your Time Into Money                  │
│                                                         │
│    ⚡ Do Quests → Earn AT → Spend Local → 0% Fees      │
│                                                         │
│                ═══════════════════════                  │
│                                                         │
│   📍 First Friday | February 6, 2026                    │
│   🌐 ark.local/join                                     │
│                                                         │
│   Scan to start your first quest                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Design Notes

- **QR Code**: Points to `http://ark.local/join` (or localhost for testing)
- **Color Scheme**: Purple gradient (matches brand)
- **Font**: Bold, modern sans-serif
- **Size**: QR should be 3"x3" minimum (scannable from 2 feet away)

---

## Back Side

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              HOW IT WORKS                               │
│                                                         │
│   1️⃣ SCAN → Open the app                               │
│   2️⃣ QUEST → Help a local business                     │
│   3️⃣ EARN → Get paid in AT (Abundance Token)           │
│   4️⃣ SPEND → Use it at Rudy's, detailing, & more       │
│                                                         │
│              ───────────────────                        │
│                                                         │
│              WHAT IS AT?                                │
│                                                         │
│   • 1 AT = 1 hour of verified work                     │
│   • No bank account needed                             │
│   • 0% transaction fees                                │
│   • You own your wallet                                │
│                                                         │
│              ───────────────────                        │
│                                                         │
│              WHERE TO SPEND                             │
│                                                         │
│   🌭 Rudy's Hot Dogs                                    │
│   🚗 Eternal Detailing                                  │
│   ☕ More coming soon...                                │
│                                                         │
│              ───────────────────                        │
│                                                         │
│   Questions? Scan the QR or visit ark.local            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Print Specs

| Setting | Value |
|---------|-------|
| Size | 8.5" x 11" (US Letter) |
| Paper | 100lb Glossy Cardstock |
| Color | Full Color (CMYK) |
| Quantity | 50-100 for First Friday |
| Finish | UV Coating (weather-resistant) |

---

## QR Code Generation

```bash
# Install qrencode if needed
brew install qrencode

# Generate QR code
qrencode -o first_friday_qr.png -s 10 "http://localhost:3000/join"

# For production, replace with:
# qrencode -o first_friday_qr.png -s 10 "https://yourarkurl.com/join"
```

---

## Estimated Cost

- **Staples**: ~$0.50/flyer x 50 = **$25**
- **Vistaprint**: Bulk discount = **$15-20** for 100

---

## Distribution Strategy

1. **First Friday Event**: Hand out at entrance
2. **Rudy's Stand**: Leave stack for customers
3. **Your Detailing Clients**: Include in every detail
4. **Coffee Shops**: Ask to post on bulletin boards
5. **Thrift Walk Vendors**: Give to participating vendors

---

*"One scan = one potential user. 50 flyers = 50 chances."*
