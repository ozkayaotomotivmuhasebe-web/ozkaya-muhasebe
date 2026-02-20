from src.database.db import SessionLocal
from src.database.models import User
from werkzeug.security import generate_password_hash


class AdminService:
    """Admin işlemleri servisi"""
    
    @staticmethod
    def get_all_users():
        """Tüm kullanıcıları al"""
        session = SessionLocal()
        try:
            users = session.query(User).order_by(User.created_at.desc()).all()
            return users
        finally:
            session.close()
    
    @staticmethod
    def create_user(username, email, password, full_name, role='user'):
        """Yeni kullanıcı oluştur"""
        session = SessionLocal()
        try:
            # Ctrl: Kullanıcı zaten var mı?
            existing = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing:
                return None, "Kullanıcı adı veya e-posta zaten kullanılıyor"
            
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                full_name=full_name,
                role=role,
                can_view_dashboard=True,
                can_view_invoices=(role == 'admin'),
                can_view_caris=(role == 'admin'),
                can_view_banks=(role == 'admin'),
                can_view_credit_cards=(role == 'admin'),
                can_view_reports=(role == 'admin')
            )
            session.add(new_user)
            session.commit()
            return new_user, "Başarı"
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """Kullanıcıyı güncelle"""
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Kullanıcı bulunamadı"
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            session.commit()
            return True, "Başarı"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def delete_user(user_id):
        """Kullanıcıyı sil"""
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Kullanıcı bulunamadı"
            
            # Admin hesabını silmeme
            if user.role == 'admin' and user.username == 'admin':
                return False, "Ana Admin hesabı silinemez"
            
            session.delete(user)
            session.commit()
            return True, "Başarı"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def toggle_user_active(user_id):
        """Kullanıcıyı aktif/pasif yap"""
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Kullanıcı bulunamadı"
            
            user.is_active = not user.is_active
            session.commit()
            return True, f"Kullanıcı {'Aktif' if user.is_active else 'Pasif'} yapıldı"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def set_user_role(user_id, role):
        """Kullanıcının rolünü değiştir"""
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Kullanıcı bulunamadı"
            
            user.role = role
            # Admin ise tüm izinleri ver
            if role == 'admin':
                user.can_view_invoices = True
                user.can_view_caris = True
                user.can_view_banks = True
                user.can_view_credit_cards = True
                user.can_view_reports = True
            else:
                user.can_view_invoices = False
                user.can_view_caris = False
                user.can_view_banks = False
                user.can_view_credit_cards = False
                user.can_view_reports = False
            
            session.commit()
            return True, f"Rol '{role}' olarak değiştirildi"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
