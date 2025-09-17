# scripts/update_dhan_credentials.py
"""
Script to update Dhan credentials for a user in the database.
Usage:
  poetry run python scripts/update_dhan_credentials.py <user_id> <dhan_client_id> <dhan_access_token>
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import User, Base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL environment variable not set.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

if len(sys.argv) != 4:
    print("Usage: python update_dhan_credentials.py <user_id> <dhan_client_id> <dhan_access_token>")
    sys.exit(1)

user_id = sys.argv[1]
dhan_client_id = sys.argv[2]
dhan_access_token = sys.argv[3]

session = SessionLocal()
user = session.query(User).filter_by(id=user_id).first()
if not user:
    print(f"User with id {user_id} not found.")
    sys.exit(1)

user.dhan_client_id = dhan_client_id
user.dhan_access_token = dhan_access_token
session.commit()
print(f"Updated Dhan credentials for user {user_id}.")
session.close()
