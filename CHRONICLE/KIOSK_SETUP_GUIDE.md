# The Mirror: Kiosk Setup Guide

**Hardware: Raspberry Pi 4 + 10" Touchscreen**  
**Software: Chromium Kiosk Mode + Ark OS**

---

## Quick Start (For Bored Co-Founder Demo)

### 1. Hardware Requirements

- Raspberry Pi 4 (4GB+ RAM recommended)
- 10" USB-C Touchscreen (or any HDMI touch display)
- microSD Card (32GB+)
- Power supply (USB-C, 5V/3A)
- Case (optional, but recommended for deployment)

### 2. Software Setup

```bash
# 1. Flash Raspberry Pi OS Lite to SD card
# 2. Enable SSH and configure WiFi
# 3. SSH into the Pi and run:

sudo apt update && sudo apt upgrade -y
sudo apt install -y chromium-browser unclutter xdotool

# 4. Create kiosk startup script
cat > ~/kiosk.sh << 'EOF'
#!/bin/bash
xset s noblank
xset s off
xset -dpms

unclutter -idle 0.5 -root &

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences

/usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk http://YOUR_ARK_SERVER:3000/kiosk.html
EOF

chmod +x ~/kiosk.sh

# 5. Auto-start on boot (add to /etc/xdg/lxsession/LXDE-pi/autostart)
echo "@bash /home/pi/kiosk.sh" | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart
```

### 3. Network Configuration

The kiosk connects to your Ark OS server. Options:

- **Local Network**: Pi and server on same WiFi
- **Mesh VPN (NetBird)**: For distributed deployment
- **Offline Mode**: Kiosk caches quests locally

### 4. Content Flow

```
┌─────────────────────────────────────────────────┐
│                  THE MIRROR                     │
├─────────────────────────────────────────────────┤
│                                                 │
│     IDLE STATE                                  │
│     ┌─────────────────────────────────────┐     │
│     │                                     │     │
│     │          "Bored?"                   │     │
│     │                                     │     │
│     │       [Tap to explore]              │     │
│     │                                     │     │
│     └─────────────────────────────────────┘     │
│                    │                            │
│                    ▼ (User taps)                │
│     ACTIVE STATE                                │
│     ┌─────────────────────────────────────┐     │
│     │  ⚡ Quest Board    📍 Downtown      │     │
│     │                                     │     │
│     │  ┌─────────────────────────────┐    │     │
│     │  │ Help organize shop   2.5 AT│    │     │
│     │  └─────────────────────────────┘    │     │
│     │  ┌─────────────────────────────┐    │     │
│     │  │ Bar Crawl Bingo     0.5 AT │    │     │
│     │  └─────────────────────────────┘    │     │
│     │                                     │     │
│     │  [Post a Quest]  [Scan QR]          │     │
│     └─────────────────────────────────────┘     │
│                                                 │
│     Returns to IDLE after 2min inactivity       │
└─────────────────────────────────────────────────┘
```

---

## Value Proposition for Merchants

**Old Model (Ads)**: "Pay us $50/month to show your logo."  
**New Model (Quests)**: "Post a task, get free labor. Customers earn AT."

| Merchant Benefit | How It Works |
|------------------|--------------|
| Free Labor | Post micro-tasks ("Move boxes", "Fold napkins") |
| Foot Traffic | Customers come to complete quests |
| Community Cred | Seen as supporting local economy |
| Zero Risk | No upfront cost - pay in AT (which comes back) |

---

## Demo Script for Co-Founder Meeting

1. **Show the idle screen**: "This is what people see walking by."
2. **Tap 'Bored?'**: "One touch, they're in."
3. **Browse quests**: "These are real tasks from local businesses."
4. **Accept a quest**: "They earn AT, the merchant gets help."
5. **Post a quest**: "Merchants can post from their phone."
6. **The pitch**: "We're not selling ads. We're building a local labor market."

---

*"The Bored Board becomes The Mirror - a portal into the community economy."*
