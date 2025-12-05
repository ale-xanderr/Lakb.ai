# C:\Users\Rence\Downloads\Lakb.ai-main\src\storage\database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Configuration: Use the same database path as setup_db.py
DATABASE_URL = "sqlite:///lakb.db" 

# Create the engine (interface to the database)
engine = create_engine(
    DATABASE_URL,
    # Required for SQLite when accessed by multiple threads (like a web app)
    connect_args={"check_same_thread": False}
)

# Configure the Session Factory
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,  
    bind=engine       
)

@contextmanager
def get_db():
    """
    Context manager that provides a database session. 
    Guarantees the session is closed even if errors occur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()