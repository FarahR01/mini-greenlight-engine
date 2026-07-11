from app.db.database import engine, Base
from app.db import models  # noqa: F401 — needed so the table gets registered

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    init_db()