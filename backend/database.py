from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Database URL - defaults to PostgreSQL for production
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cricket_user:cricket_pass@localhost:5432/cricket_portal"
)

# For development, you can use SQLite:
# DATABASE_URL = "sqlite:///./cricket_portal.db"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base from shared models (fallback to local if shared not available)
try:
    from shared.models.base import Base
except ImportError:
    # Fallback: use existing models
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
