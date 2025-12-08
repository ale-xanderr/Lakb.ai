from sqlalchemy import create_engine
# Import Base, which contains the metadata of all your models
from storage.models import Base 

# Configuration: Use a SQLite file named 'lakb.db'
DATABASE_URL = "sqlite:///lakb.db" 

def setup_database():
    """
    Creates the SQLAlchemy engine and all tables defined in Base.metadata.
    """
    try:
        # Create the engine (connects to the database file)
        engine = create_engine(
            DATABASE_URL,
            # Required for SQLite when accessed by multiple threads (like a web app)
            connect_args={"check_same_thread": False} 
        )

        # Create all tables (Users and Places) if they do not already exist
        Base.metadata.create_all(bind=engine)

        print("---")
        print(f"✅ Database and tables created successfully at: {DATABASE_URL}")
        print("   Tables created: users, places")
        print("---")

    except Exception as e:
        print(f"❌ An error occurred during database setup: {e}")

if __name__ == "__main__":
    setup_database()