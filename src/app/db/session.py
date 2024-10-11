from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base  # Import Base from base.py

import tempfile
temp_dir = tempfile.TemporaryDirectory()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_dir.name}/test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()