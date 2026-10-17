# Public Service Request System (Mini eCitizen-style)

A Flask web application where **citizens** report public-service issues
(broken streetlights, water problems, garbage collection…) and **admins**
drive them through a `Pending → In Progress → Resolved` workflow.

## Features

| Area | What it does |
|---|---|
| Authentication | Citizen registration & login, hashed passwords, session management |
| Submit request | Category, location, description + **optional photo** (type/size validated) |
| Citizen dashboard | Own requests, newest first, colour-coded status badges |
| Request detail | Full info, photo, and a **status-change timeline (audit trail)** |
| Admin analytics | Open vs resolved cards + Chart.js doughnut & bar charts |
| Admin queue | All requests with status/category filters + free-text search |
| Workflow | Status advances one step at a time, **enforced server-side** |
| Bonus | CSV export, audit trail, Chart.js analytics, search/filters, CLI admin seeder, CSRF protection, custom 403/404 pages |

## Tech stack
Python 3.10+ · Flask · Flask-SQLAlchemy (SQLite) · Flask-Login · Flask-WTF ·
Bootstrap 5 + Bootstrap Icons · Chart.js (all front-end assets via CDN)

## Project structure
```
psr-system/
├── run.py                  # entry point (python run.py)
├── config.py               # settings: secrets, DB URI, upload rules
├── requirements.txt
├── README.md
├── instance/               # SQLite database (auto-created)
├── uploads/                # citizen-uploaded photos (git-ignored)
└── app/
    ├── __init__.py         # app factory + CLI commands + error pages
    ├── extensions.py       # db / login_manager / csrf
    ├── models.py           # User, ServiceRequest, StatusHistory + constants
    ├── utils.py            # helpers: image saving, badges, @admin_required
    ├── auth/               # blueprint: register / login / logout
    ├── citizen/            # blueprint: dashboard / submit / detail
    ├── admin/              # blueprint: analytics / queue / status / CSV
    ├── templates/          # Jinja HTML (sub-folder per blueprint)
    └── static/css/         # custom CSS on top of Bootstrap
```

## Setup

```bash
# 1. Clone / copy the project, then:
python -m venv venv
venv\Scripts\activate          # Windows   (macOS/Linux: source venv/bin/activate)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create an administrator account (interactive prompts)
flask --app run create-admin

# 4. Run the development server
python run.py
```
Open **http://127.0.0.1:5000** — register a citizen through the UI; admins are
created only via the CLI command above.

## Request workflow
```
Pending  →  In Progress  →  Resolved
   (admin advances one step per action; every change is recorded
    in status_history with who/when/optional note)
```

## Manual test guide
1. Register → login as citizen → submit 2 requests (one with a photo).
2. Badges show *Pending*; detail page shows the timeline.
3. Login as admin → Analytics shows open vs resolved + charts.
4. Queue: filter by status/category, search by location/e-mail.
5. Advance a request twice → citizen sees *Resolved* + full history.
6. Citizen visits `/admin/` → friendly **403** page.
7. Admin clicks **CSV** → filtered spreadsheet downloads.

## 📸 Screenshots
*(optional: add a `docs/screenshots/` folder and embed images here)*

## 👤 Author
<your name> — built as a graded project (code quality · functionality · UI/UX · docs · bonus).
