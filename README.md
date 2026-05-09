# 💰 BudgetIQ — Personal Budget Tracker

A clean, fast web app to track personal expenses by category, set monthly budgets, and export data to CSV.

**Tech Stack:** Python · Flask · SQLite · HTML/CSS (no JS frameworks)  
**Deploy Target:** Railway.app (free tier)

---

## Features

- ➕ Add expenses with category, description & date
- 📊 Monthly dashboard with category breakdown & progress bars
- 🚨 Budget limits with over-budget warnings
- 📥 Export all expenses to CSV
- 📱 Fully responsive (mobile-friendly)

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/budget-tracker.git
cd budget-tracker
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

Visit **http://localhost:5000** in your browser.

---

## Deploy to Railway (Free)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: BudgetIQ MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/budget-tracker.git
git push -u origin main
```

### Step 2 — Deploy on Railway
1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `budget-tracker` repo
4. Railway auto-detects Python and runs `gunicorn` via the `Procfile`
5. Click **"Generate Domain"** under Settings → Networking → you get a free `.railway.app` URL

### Step 3 — Set Environment Variables (optional)
In Railway → Variables tab, you can set:
```
SECRET_KEY=your-random-secret-here
DATABASE_PATH=/data/budget.db
```

> ⚠️ **Note:** Railway's free tier uses ephemeral storage — the SQLite DB resets on redeploy. For persistent data, add a Railway **PostgreSQL** plugin (free) and update `app.py` to use `psycopg2`. For an MVP with personal use, the current setup is fine.

---

## Project Structure

```
budget-tracker/
├── app.py                  # Flask app + routes + DB logic
├── requirements.txt        # Python dependencies
├── Procfile                # Railway/Heroku start command
├── railway.toml            # Railway config
├── .gitignore
├── templates/
│   ├── base.html           # Nav, alerts, layout shell
│   ├── index.html          # Dashboard
│   └── budgets.html        # Budget management
└── static/
    ├── css/style.css       # All styles
    └── js/app.js           # Minimal JS utilities
```

---

## Upgrading to PostgreSQL (for persistent Railway deploys)

1. In Railway, add a **PostgreSQL** plugin to your project
2. Install: `pip install psycopg2-binary`
3. Replace SQLite connection in `app.py` with:
```python
import psycopg2, os
DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
```
4. Update `CREATE TABLE` SQL to PostgreSQL syntax (remove `AUTOINCREMENT` → use `SERIAL`)

---

## License

MIT — free to use and modify.
