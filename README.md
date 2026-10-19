<div align="center">
  <h1> Murang'a County Public Service Request System</h1>
  <p><strong>Mini eCitizen Platform built with Flask</strong></p>
  <p>
    <a href="https://github.com/mrirrelevant254/psr-"><strong>View Source Code on GitHub »</strong></a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/Framework-Flask-green.svg" alt="Flask">
    <img src="https://img.shields.io/badge/UI-Bootstrap_5-purple.svg" alt="Bootstrap">
  </p>
</div>

---

A modern, secure web application designed for the **Murang'a County Government**. It allows citizens to report public service issues (water, roads, sanitation) and enables county administrators to track, manage, and resolve these requests through a transparent, audited workflow.

###  Live Demo
**[Click here to view the live application](https://mrirrelevant.pythonanywhere.com)**

- **Citizen Portal:** [https://mrirrelevant.pythonanywhere.com/](https://mrirrelevant.pythonanywhere.com/)
- **Admin Portal (Hidden):** [https://mrirrelevant.pythonanywhere.com/admin/login](https://mrirrelevant.pythonanywhere.com/admin/login)

---

##  Key Features

###  Citizen Portal
* **Secure Authentication:** Registration and login with secure session management and hashed passwords.
* **Request Submission:** Detailed forms including Category, Sub-County (Ward), Location, and Description.
* **Strict Image Uploads:** Optional photo attachments with server-side validation (extension, MIME type, and magic-byte content checks) to prevent malicious file uploads.
* **Real-time Tracking:** Dashboard with color-coded status badges (Pending, In Progress, Resolved).
* **In-App Notifications:** Bell icon with unread counts; citizens are automatically notified upon submission and every status change.
* **Fullscreen Lightbox:** Click-to-zoom photo viewer for inspecting attached evidence.

###  Administrator Portal (Hidden URL)
* **Analytics Dashboard:** Clean horizontal progress bars (Open vs. Resolved, Requests by Category, Cases per Sub-County).
* **SLA & Overdue Tracking:** Automatic red flagging and dashboard counters for requests open longer than 7 days.
* **Request Queue:** Advanced filtering by status, category, and sub-county, plus free-text search.
* **Enforced Workflow:** Server-side status progression (Pending → In Progress → Resolved) with a complete audit trail.
* **Data Export:** One-click CSV download of the filtered queue for county reporting.
* **Smart Routing:** Admins who accidentally use the citizen login page are safely redirected to the admin portal.

---

##  Tech Stack
* **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy (SQLite)
* **Frontend:** Bootstrap 5, Bootstrap Icons (via CDN)
* **Security:** Werkzeug password hashing, Flask-WTF (CSRF protection), strict file upload validation, role-based access control (RBAC)

---

##  Project Structure
```text
psr-/
├── run.py                  # Application entry point
├── create_admin.py         # CLI tool to seed/promote admin accounts
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── instance/               # SQLite database (auto-created)
├── uploads/                # Citizen photos (auto-created)
└── app/
    ├── __init__.py         # App factory, config, and error handlers
    ├── models.py           # Database models and workflow constants
    ├── utils.py            # Shared helpers (image saving, validation)
    ├── citizen/            # Blueprint: citizen routes, forms, templates
    ├── admin/              # Blueprint: admin routes, analytics, queue
    ├── templates/          # Jinja2 HTML (partials, errors, role-specific)
    └── static/             # Custom CSS and images (e.g., county logo)

##  Installation & Setup

**Prerequisites:** Python 3.10+ and Git.

**Windows (Command Prompt):**
```bat
git clone https://github.com/mrirrelevant254/psr-.git
cd psr-
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python create_admin.py
python run.py
```
** macOS / Linux:**
```bash
git clone https://github.com/mrirrelevant254/psr-.git
cd psr-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python create_admin.py
python run.py
```

`create_admin.py` prompts for an e-mail, full name and password. If the e-mail already belongs to a registered citizen, that account is promoted to administrator.

> The SQLite database (`instance/`) and the `uploads/` folder are created automatically on first run
## Portals & Access
=======
##  Portals & Access

| Portal        | URL                                    | Visibility                  |
|---------------|----------------------------------------|-----------------------------|
| Citizen       | http://127.0.0.1:5000/                 | Public (Login & Register)   |
| Administrator | http://127.0.0.1:5000/admin/login      | Hidden (direct URL only)    |

> The admin portal is intentionally not linked from the public UI, to simulate a government intranet. Go directly to `/admin/login` and sign in with the credentials you created via `create_admin.py`.

## Request Workflow

```text
[Pending] ──(Admin)──> [In Progress] ──(Admin)──> [Resolved]
    │                       │                         │
    └─ Notifies citizen     └─ Notifies citizen       └─ Notifies citizen
```

Every status change is recorded in an audit trail.

## Author
**Geofry mwangi Burugu**
Murang'a County Government demo.
