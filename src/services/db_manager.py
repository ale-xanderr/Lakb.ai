# src/services/db_manager.py
import os
import json
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from models.models import Base, Users, Places, Itinerary, Favorite, UserRole
from core.config import Config
from core.security import SecurityManager
from sqlalchemy.exc import SQLAlchemyError

DB_URL = os.getenv("DATABASE_URL", Config.DATABASE_URL)

class DBManager:
    def __init__(self, db_url: str = DB_URL, echo: bool = False):
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        self.engine = create_engine(db_url, echo=echo, connect_args=connect_args)
        self.SessionLocal = scoped_session(sessionmaker(bind=self.engine))

    def init_db(self):
        Base.metadata.create_all(self.engine)
        self.seed_data()

    def seed_data(self):
        session = self.SessionLocal()
        try:
            admin = session.query(Users).filter_by(email="admin@lakb.ai").first()
            if not admin:
                admin = Users(
                    username="admin",
                    email="admin@lakb.ai",
                    full_name="System Administrator",
                    password_hash=SecurityManager.hash_password("password123"),
                    role=UserRole.admin
                )
                session.add(admin)
                session.commit()

            # Add demo places if none exist (small curated list)
            if session.query(Places).count() == 0:
                demo_places = [
                    Places(name="Sunset Café", location="Boracay, Philippines", rating=4.6, description="Cozy cafe with sunset view", source="local"),
                    Places(name="White Beach", location="Boracay, Philippines", rating=4.8, description="Famous beach", source="local"),
                    Places(name="Local Vegan Eatery", location="Boracay, Philippines", rating=4.4, description="Vegan-friendly menu", source="local"),
                ]
                session.add_all(demo_places)
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    # -----------------------------
    # User helpers
    # -----------------------------
    def get_user_by_email(self, email: str):
        session = self.SessionLocal()
        try:
            return session.query(Users).filter_by(email=email).first()
        finally:
            session.close()

    def create_user(self, username: str, email: str, plain_password: str, full_name: str = None, role: UserRole = UserRole.traveler):
        session = self.SessionLocal()
        try:
            exists = session.query(Users).filter((Users.email == email) | (Users.username == username)).first()
            if exists:
                return None
            user = Users(
                username=username,
                email=email,
                full_name=full_name,
                password_hash=SecurityManager.hash_password(plain_password),
                role=role
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def update_user_last_login(self, user_id: int):
        session = self.SessionLocal()
        try:
            user = session.query(Users).get(user_id)
            if user:
                user.last_login = func.now()
                user.failed_attempts = 0
                user.locked_until = None
                session.commit()
        finally:
            session.close()

    # -----------------------------
    # Favorite helpers
    # -----------------------------
    def add_favorite(self, user_id: int, place_id: int, note: str = None):
        session = self.SessionLocal()
        try:
            fav = session.query(Favorite).filter_by(user_id=user_id, place_id=place_id).first()
            if fav:
                return fav
            fav = Favorite(user_id=user_id, place_id=place_id, note=note)
            session.add(fav)
            session.commit()
            session.refresh(fav)
            return fav
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def remove_favorite(self, user_id: int, place_id: int):
        session = self.SessionLocal()
        try:
            fav = session.query(Favorite).filter_by(user_id=user_id, place_id=place_id).first()
            if not fav:
                return False
            session.delete(fav)
            session.commit()
            return True
        finally:
            session.close()

    def get_favorites_for_user(self, user_id: int):
        session = self.SessionLocal()
        try:
            return session.query(Favorite).filter_by(user_id=user_id).all()
        finally:
            session.close()

    # -----------------------------
    # Itinerary helpers
    # -----------------------------
    def save_itinerary(self, user_id: int, title: str, metadata: dict):
        session = self.SessionLocal()
        try:
            it = Itinerary(user_id=user_id, title=title, itinerary_data=json.dumps(metadata))
            session.add(it)
            session.commit()
            session.refresh(it)
            return it
        finally:
            session.close()

    def get_itineraries_for_user(self, user_id: int):
        session = self.SessionLocal()
        try:
            return session.query(Itinerary).filter_by(user_id=user_id).all()
        finally:
            session.close()

    # -----------------------------
    # Places search (DB-backed local catalog, not API cache)
    # -----------------------------
    def search_places_local(self, keyword: str = None, min_rating: float = 0.0, limit: int = 20):
        session = self.SessionLocal()
        try:
            q = session.query(Places)
            if keyword:
                pattern = f"%{keyword}%"
                q = q.filter((Places.location.ilike(pattern)) | (Places.name.ilike(pattern)))
            if min_rating:
                q = q.filter(Places.rating >= min_rating)
            return q.limit(limit).all()
        finally:
            session.close()
