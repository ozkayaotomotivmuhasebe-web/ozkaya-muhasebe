from src.database.db import SessionLocal
from src.database.models import CreditCard
from datetime import datetime


class CreditCardService:
    """Kredi kartı yönetimi servisi"""
    
    @staticmethod
    def create_card(user_id, card_name, card_number_last4, card_holder, bank_name, 
                   card_limit, closing_day=1, due_day=15):
        """Yeni kredi kartı ekle"""
        session = SessionLocal()
        try:
            card = CreditCard(
                user_id=user_id,
                card_name=card_name,
                card_number_last4=card_number_last4,
                card_holder=card_holder,
                bank_name=bank_name,
                card_limit=card_limit,
                current_debt=0.0,
                available_limit=card_limit,
                closing_day=closing_day,
                due_day=due_day
            )
            session.add(card)
            session.commit()
            return card, "Başarılı"
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()
    
    @staticmethod
    def get_all_cards(user_id):
        """Tüm kredi kartlarını getir"""
        session = SessionLocal()
        try:
            cards = session.query(CreditCard).filter(
                CreditCard.user_id == user_id
            ).order_by(CreditCard.created_at.desc()).all()
            return cards
        finally:
            session.close()
    
    @staticmethod
    def get_active_cards(user_id):
        """Aktif kredi kartlarını getir"""
        session = SessionLocal()
        try:
            cards = session.query(CreditCard).filter(
                CreditCard.user_id == user_id,
                CreditCard.is_active == True
            ).order_by(CreditCard.created_at.desc()).all()
            return cards
        finally:
            session.close()
    
    @staticmethod
    def get_card_by_id(card_id):
        """ID'ye göre kart getir"""
        session = SessionLocal()
        try:
            return session.query(CreditCard).filter(CreditCard.id == card_id).first()
        finally:
            session.close()
    
    @staticmethod
    def update_card(card_id, **kwargs):
        """Kredi kartı bilgilerini güncelle"""
        session = SessionLocal()
        try:
            card = session.query(CreditCard).filter(CreditCard.id == card_id).first()
            if not card:
                return False, "Kredi kartı bulunamadı"
            
            for key, value in kwargs.items():
                if hasattr(card, key):
                    setattr(card, key, value)
            
            # Kullanılabilir limit hesapla
            if 'card_limit' in kwargs or 'current_debt' in kwargs:
                card.available_limit = card.card_limit - card.current_debt
            
            session.commit()
            return True, "Başarılı"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def delete_card(card_id):
        """Kredi kartı sil"""
        session = SessionLocal()
        try:
            card = session.query(CreditCard).filter(CreditCard.id == card_id).first()
            if not card:
                return False, "Kredi kartı bulunamadı"
            
            if card.current_debt > 0:
                return False, "Borcu olan kart silinemez!"
            
            session.delete(card)
            session.commit()
            return True, "Kredi kartı silindi"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def toggle_active(card_id):
        """Kartı aktif/pasif yap"""
        session = SessionLocal()
        try:
            card = session.query(CreditCard).filter(CreditCard.id == card_id).first()
            if not card:
                return False, "Kredi kartı bulunamadı"
            
            card.is_active = not card.is_active
            session.commit()
            status = "Aktif" if card.is_active else "Pasif"
            return True, f"Kart {status} yapıldı"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def get_card_statistics(user_id):
        """Kredi kartı istatistikleri"""
        session = SessionLocal()
        try:
            cards = session.query(CreditCard).filter(
                CreditCard.user_id == user_id,
                CreditCard.is_active == True
            ).all()
            
            total_limit = sum(card.card_limit for card in cards)
            total_debt = sum(card.current_debt for card in cards)
            total_available = sum(card.available_limit for card in cards)
            
            return {
                'total_cards': len(cards),
                'total_limit': total_limit,
                'total_debt': total_debt,
                'total_available': total_available,
                'usage_rate': (total_debt / total_limit * 100) if total_limit > 0 else 0
            }
        finally:
            session.close()
