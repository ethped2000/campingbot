import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("DATABASE_URL environment variable not set! Using SQLite (data will be lost on restart)")
    DATABASE_URL = "sqlite:///./test.db"
else:
    import logging
    logger = logging.getLogger(__name__)
    db_type = "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite"
    logger.info(f"Using {db_type} database: {DATABASE_URL[:50]}...")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
