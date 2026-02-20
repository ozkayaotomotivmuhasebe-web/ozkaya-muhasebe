from src.database.db import session_scope
from src.database.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import Optional

class AuthService:
    """Kimlik doğrulama"""
    
    @staticmethod
    def register_user(username: str, email: str, password: str, full_name: str) -> bool:
        """Kayıt ol"""
        with session_scope() as session:
            if session.query(User).filter_by(username=username).first():
                return False
            
            user = User(
                username=username, email=email,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
                full_name=full_name
            )
            session.add(user)
            return True
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """Giriş yap"""
        with session_scope() as session:
            user = session.query(User).filter_by(username=username, is_active=True).first()
            if user and check_password_hash(user.password_hash, password):
                user.last_login = datetime.now()
                return user
            return None
    
    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        """Kullanıcı al"""
        with session_scope() as session:
            return session.query(User).filter_by(id=user_id).first()
