# BG Cleaner 🖼️✂️

**Professional background removal web app** — upload any image, get a clean white-background result instantly.

Built with **Flask**, **rembg** (AI-powered), and a polished drag-and-drop UI.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🎯 AI Background Removal | Uses `rembg` (U²-Net model) for pixel-perfect cutouts |
| ⬜ White Background Fill | Automatically replaces transparency with clean white |
| 📦 Batch Processing | Process up to 20 images at once, download as ZIP |
| 🖱️ Drag & Drop | Drag single or multiple images onto the page |
| ⚡ Fast | Processes images in seconds |
| 🔒 Private | Everything runs locally — no data leaves your machine |
| 📱 Responsive | Works on desktop, tablet, and mobile |
| 🆓 Free & Open Source | No watermarks, no limits, no accounts |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone <repo-url>
cd bg-cleaner
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 📦 Project Structure

```
bg-cleaner/
├── app.py                 # Flask entry point
├── Procfile               # Railway/Heroku process definition
├── render.yaml            # Render deployment blueprint
├── runtime.txt            # Python version pin
├── nixpacks.toml          # Railway build config
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # One-command Docker launch
├── .dockerignore           # Docker build exclusions
├── bg_cleaner.spec        # PyInstaller build spec
├── build.bat              # Windows build script
├── build.sh               # macOS/Linux build script
├── requirements.txt       # Python dependencies
├── app/
│   ├── __init__.py        # Flask app + API routes
│   ├── processor.py       # Background removal logic
│   ├── templates/
│   │   └── index.html     # Professional frontend UI
│   └── static/
│       └── style.css
├── uploads/               # Temp uploads (auto-cleaned)
├── results/               # Processed images (auto-cleaned)
└── README.md
```

---

## ☁️ Deploy to Cloud (Free)

Your whole team accesses it via a URL — no installs needed.

### Railway (Recommended — Easiest)

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → Sign up with GitHub
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your repo
5. Railway auto-detects Python and deploys
6. Click **Settings** → enable **Public Network**
7. Share the URL with your team!

> ✅ Free tier includes 500 hours/month. More than enough for a team.

### Render (Alternative)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → Sign up with GitHub
3. Click **New** → **Web Service**
4. Connect your repo
5. Settings:
   - **Build Command:** `pip install -r requirements.txt && python -c "from rembg import new_session; new_session('u2net')"`
   - **Start Command:** `python app.py`
   - **Instance Type:** Free
6. Click **Create Web Service**
7. Share the URL!

> ✅ Free tier spins down after inactivity — first request after sleep takes ~30s.

---

## 🐳 Deploy with Docker

Run with a single command — no Python install needed.

### One-liner (Docker)

```bash
docker compose up --build
```

Open **http://localhost:5000**.

### Or without Compose

```bash
docker build -t bg-cleaner .
docker run -p 5000:5000 bg-cleaner
```

### Stop

```bash
docker compose down
```

> **Note:** The first build downloads the AI model (~170 MB) and is cached. Subsequent starts are instant.

### Run in background

```bash
docker compose up -d --build
```

---

## 🖥️ Package as a Standalone App (.exe)

Share BG Cleaner as a single folder — no Python required for end users.

### Windows

```bat
build.bat
```

Output: `dist\BG Cleaner\BG Cleaner.exe`

### macOS / Linux

```bash
chmod +x build.sh
./build.sh
```

Output: `dist/BG Cleaner/BG Cleaner`

### How to Share

1. Run the build script above
2. Zip the `dist/BG Cleaner/` folder
3. Send the zip — the recipient just unzips and runs the `.exe`

> **Note:** First launch downloads the AI model (~170 MB). Subsequent launches are instant.

---

## 🔧 Configuration

| Env Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | random | Flask session secret |

---

## 📋 Requirements

- Python 3.9+
- ~200 MB disk for model download (first run only)

---

## 🤖 Tech Stack

- **Backend:** Flask + Gunicorn
- **AI Model:** rembg (U²-Net via onnxruntime)
- **Frontend:** Vanilla HTML/CSS/JS (no build step)
- **Image Processing:** Pillow

---

## 📄 License

MIT — use it however you like.
