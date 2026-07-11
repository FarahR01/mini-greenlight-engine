import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://greenlight:greenlight@localhost:5432/greenlight"
)

def make_engine(url: str = None):
    """Factory so tests can inject a different (e.g. SQLite in-memory) engine."""
    return create_engine(url or DATABASE_URL)

engine = make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()