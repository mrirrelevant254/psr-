#  Murang'a County Public Service Request System (Mini eCitizen)

A modern, secure web application designed for the **Murang'a County Government**. It allows citizens to report public service issues (water, roads, sanitation) and enables county administrators to track, manage, and resolve these requests through a transparent, audited workflow.

## Key Features

### Citizen Portal
* **Secure Authentication:** Registration and login with session management.
* **Request Submission:** Detailed forms including Category, Sub-County (Ward), Location, and Description.
* **Image Uploads:** Optional photo attachments with strict server-side validation (extension, MIME type, and magic-byte content checks) to prevent malicious uploads.
* **Real-time Tracking:** Dashboard with color-coded status badges (Pending, In Progress, Resolved).
* **In-App Notifications:** Bell icon with unread counts; citizens are notified upon submission and every status change.
* **Fullscreen Lightbox:** Click-to-zoom photo viewer for inspecting attached evidence.

### Administrator Portal (Hidden URL)
* **Analytics Dashboard:** Live Chart.js visualizations (Open vs. Resolved, Requests per Category, Cases per Sub-County).
* **SLA & Overdue Tracking:** Automatic red flagging and dashboard counters for requests open longer than 7 days.
* **Request Queue:** Advanced filtering by status, category, and sub-county, plus free-text search.
* **Enforced Workflow:** Server-side status progression (Pending → In Progress → Resolved) with a complete audit trail.
* **Data Export:** One-click CSV download of the filtered queue for county reporting.

## Tech Stack
* **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy (SQLite)
* **Frontend:** Bootstrap 5, Bootstrap Icons, Chart.js (via CDN)
* **Security:** Flask-WTF (CSRF protection), strict file upload validation, role-based access control (RBAC)

## Project Structure
psr-system/
├── run.py                  # Application entry point
├── create_admin.py         # CLI tool to seed/promote admin accounts
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── instance/               # SQLite database (auto-created)
├── uploads/                # Securely stored citizen photos
└── app/
    ├── __init__.py         # App factory, config, and error handlers
    ├── models.py           # Database models and workflow constants
    ├── utils.py            # Shared helpers (image saving, validation)
    ├── citizen/            # Blueprint: citizen routes, forms, templates
    ├── admin/              # Blueprint: admin routes, analytics, queue
    ├── templates/          # Jinja2 HTML (partials, errors, role-specific)
    └── static/css/         # Custom CSS overrides
