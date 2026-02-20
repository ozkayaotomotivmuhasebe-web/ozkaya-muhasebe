from src.database.db import session_scope
from src.database.models import Cari
from typing import List, Optional, Tuple

class CariService:
    """Cari yönetimi"""
    
    @staticmethod
    def create_cari(user_id: int, name: str, cari_type: str = 'MÜŞTERİ', 
                    tax_number: str = None, email: str = None, phone: str = None,
                    address: str = None, balance: float = 0.0) -> Tuple[bool, str]:
        """Yeni cari oluştur"""
        try:
            with session_scope() as session:
                cari = Cari(
                    user_id=user_id, name=name, cari_type=cari_type,
                    tax_number=tax_number, email=email, phone=phone,
                    address=address, balance=balance
                )
                session.add(cari)
                session.flush()
                return True, "Cari başarıyla eklendi"
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    @staticmethod
    def get_caris(user_id: int) -> List[Cari]:
        """Tüm cariler"""
        with session_scope() as session:
            return session.query(Cari).filter_by(user_id=user_id, is_active=True).all()
    
    @staticmethod
    def get_cari(cari_id: int) -> Optional[Cari]:
        """Cari detayı"""
        with session_scope() as session:
            return session.query(Cari).filter_by(id=cari_id).first()
