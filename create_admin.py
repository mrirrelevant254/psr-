"""Create (or promote) an administrator account.

Usage (virtual environment activated):
    python create_admin.py
"""
import getpass

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    email = input("Admin e-mail: ").strip().lower()
    existing = User.query.filter_by(email=email).first()

    if existing:
        # Already registered through the website? Just promote that account.
        if existing.is_admin:
            print(f"'{email}' is already an admin.")
        else:
            existing.is_admin = True
            db.session.commit()
            print(f"Promoted '{email}' to administrator.")
    else:
        full_name = input("Full name: ").strip()
        password = getpass.getpass("Password: ")
        admin = User(email=email, full_name=full_name,
                     password=password, is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print(f"Administrator '{email}' created.")