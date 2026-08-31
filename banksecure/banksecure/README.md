# 🏦 BankSecure — Banking Fraud Detection & Analysis System

A full-stack web application for managing banking data (customers, accounts,
merchants, transactions) and flagging potentially fraudulent transactions
using rule-based analysis. Built with **Flask**, **MySQL**, and vanilla
**HTML/CSS/JS**.

> Built as a portfolio project to demonstrate CRUD design, relational data
> modeling, server-side rendering with Jinja2, and simple rule-based fraud
> detection logic.

---

## ✨ Features

- **Dashboard** — at-a-glance stats (customers, accounts, transactions,
  fraud alerts) and the 5 most recent transactions.
- **Customer management** — add, edit, and delete customer records.
- **Account management** — create accounts linked to customers, with
  balance and status tracking.
- **Merchant management** — maintain a merchant directory by category
  and city.
- **Transaction management** — record and edit transactions between
  accounts and merchants.
- **Rule-based fraud detection** — a single click re-analyzes every
  transaction against three rules:
  1. Amount above ₹50,000 → **High risk**
  2. 5+ transactions on the same account within a 10-minute window →
     **High risk**
  3. Amount between ₹20,000–₹50,000 → **Medium risk**
- **Reports** — summary counts, high/medium risk breakdown, and a
  Chart.js bar chart of fraud alerts by risk level.
- Flash messages for success/error feedback on every form action.

---

## 🧱 Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Backend    | Python, Flask                        |
| Database   | MySQL (`mysql-connector-python`)     |
| Templating | Jinja2 (template inheritance)        |
| Frontend   | HTML5, CSS3, vanilla JavaScript      |
| Charts     | Chart.js                             |
| Config     | `python-dotenv`                      |

---

## 🗂 Project Structure

```
banksecure/
├── app.py                 # Flask application & routes
├── database.py            # DB connection helper (env-based config)
├── schema.sql              # Table definitions
├── seed_data.sql           # Sample demo data
├── requirements.txt
├── .env.example             # Copy to .env and fill in credentials
├── static/
│   ├── css/style.css
│   └── js/script.js
└── templates/
    ├── base.html            # Shared layout (sidebar, header, flashes)
    ├── index.html
    ├── customers.html
    ├── edit_customer.html
    ├── accounts.html
    ├── edit_account.html
    ├── merchants.html
    ├── edit_merchant.html
    ├── transactions.html
    ├── edit_transaction.html
    ├── fraud_detection.html
    └── reports.html
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+
- MySQL Server 8.0+ running locally (or accessible remotely)

### 2. Clone & install dependencies

```bash
git clone <your-repo-url>
cd banksecure
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials.

### 4. Create the database

```bash
mysql -u root -p < schema.sql
mysql -u root -p < seed_data.sql   # optional demo data
```

### 5. Run the app

```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser.

---

## 🔍 How Fraud Detection Works

Clicking **"Analyze Transactions"** (on the Dashboard or Fraud Detection
page) triggers `/analyze-fraud`, which:

1. Clears any previously generated alerts.
2. Re-scans every transaction against the three rules above.
3. Inserts a `fraud_alerts` row for each match, avoiding duplicate
   alerts for the same transaction.

This is intentionally simple, rule-based logic — a good foundation to
extend with statistical scoring, machine-learning models, or
per-customer spending baselines.

---

## 🛣 Possible Extensions

- User authentication / role-based access (admin vs. analyst)
- Pagination & search/filtering on large tables
- Export reports to CSV/PDF
- Replace rule-based detection with an anomaly-detection model
- REST API layer for a future SPA or mobile client

---

## ⚠️ Disclaimer

This project uses fictional data and is intended for **educational and
portfolio purposes only**. It is not a production-grade fraud detection
or banking system.
