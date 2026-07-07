# ✦ GoldClip

**Android floating Ctrl+A / Ctrl+C / Ctrl+V / Ctrl+X tool**

Ek choti si gold ball screen pe rehti hai.  
Tap karo → buttons khulte hain → kisi bhi app mein kaam karo.

---

## Features

- `Ctrl+A` — Select All
- `Ctrl+C` — Copy
- `Ctrl+V` — Paste
- `Ctrl+X` — Cut
- Auto fade after 3 sec (15% opacity)
- Touch to wake back to full visibility
- Draggable anywhere on screen
- Works in WhatsApp, Chrome, Gmail, Notes — any app

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/GoldClip.git
```

Open in Android Studio → Build → Run

### Permissions needed
- `SYSTEM_ALERT_WINDOW` — overlay permission
- `BIND_ACCESSIBILITY_SERVICE` — Ctrl actions

---

## How to Use

1. App open karo
2. Accessibility Service ON karo (Step 1)
3. GoldClip Start karo (Step 2)
4. Koi bhi app kholna
5. ✦ Gold ball dikhegi screen ke right pe
6. Tap karo → 4 buttons khulenge
7. Text field pe focus karo → buttons use karo

---

## Project Structure

```
GoldClip/
└── app/src/main/
    ├── java/com/goldclip/app/
    │   ├── MainActivity.java
    │   ├── FloatingGoldService.java
    │   └── ClipboardAccessibilityService.java
    ├── res/
    │   ├── layout/
    │   │   ├── activity_main.xml
    │   │   └── floating_gold.xml
    │   ├── drawable/
    │   │   ├── bg_gold_ball.xml
    │   │   ├── bg_gold_btn.xml
    │   │   └── bg_gold_strip.xml
    │   ├── values/
    │   │   ├── strings.xml
    │   │   └── colors.xml
    │   └── xml/
    │       └── accessibility_service_config.xml
    └── AndroidManifest.xml
```

---

## License

MIT License — free to use and modify.
