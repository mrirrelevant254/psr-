# Public Service Requests (PSR) — Murang'a County

A Flask web application where citizens submit public service requests
(Water, Roads, Sanitation, Health, Other) and county administrators
track them through a Pending → In Progress → Resolved workflow.

## Features
- Citizen registration/login and request submission
- Sub-County (ward) tracking with per-ward analytics chart
- Admin dashboard with live Chart.js analytics and overdue (SLA > 7 days) counter
- Request queue with status/category/sub-county/search filters and CSV export
- Status workflow with full audit trail (status history)
- In-app citizen notifications on submission and every status change
- Overdue flagging: open requests older than 7 days get a red badge
- Custom 403/404 error pages

## Run
```bash
pip install flask flask-sqlalchemy flask-wtf
python run.py