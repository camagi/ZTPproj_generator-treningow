import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Uzyskanie ścieżki do folderu, w którym znajduje się ten plik
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'workout_app.db')}"

# "check_same_thread": False is needed only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
