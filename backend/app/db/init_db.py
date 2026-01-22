"""
Initialize database - create all tables
"""
from app.db.session import engine, Base
from app.models.models import (
    Organization,
    User,
    Document,
    Category,
    Transaction,
    ClassificationHistory
)


def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
