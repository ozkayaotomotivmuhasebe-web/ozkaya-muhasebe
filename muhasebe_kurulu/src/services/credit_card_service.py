from src.database.db import SessionLocal
from src.database.models import CreditCard
from datetime import datetime


class CreditCardService:
    """Kredi kartı yönetimi servisi"""

    @staticmethod
    def _recalculate_group_limits(session, card):
        """
        Ortak limitli grupdaki tüm kartların available_limit değerini güncelle.
        - Eğer kart bir parent kart ise: kendi borcu + tüm child kartların borçlarını düşer.
        - Eğer kart bir child kart ise: parent kartı bulup oradan hesaplar.
        """
        # Parent kartı bul
        if card.parent_card_id:
            parent = session.query(CreditCard).filter(CreditCard.id == card.parent_card_id).first()
        else:
            parent = card  # Kart zaten parent

        if not parent:
            return

        # Tüm child kartları topla
        children = session.query(CreditCard).filter(
            CreditCard.parent_card_id == parent.id
        ).all()

        # Toplam borç = parent borcu + tüm child borçları
        total_debt = parent.current_debt + sum(c.current_debt for c in children)
        shared_available = parent.card_limit - total_debt

        # Parent'ın available_limit'ini güncelle
        parent.available_limit = shared_available

        # Tüm child kartların available_limit'ini de güncelle (aynı değer)
        for child in children:
            child.available_limit = shared_available

    @staticmethod
    def create_card(user_id, card_name, card_number_last4, card_holder, bank_name,
                    card_limit, closing_day=1, due_day=15, parent_card_id=None):
        """Yeni kredi kartı ekle"""
        session = SessionLocal()
        try:
            # Child kart ise kendi limiti 0 olur, parent'ın limitini paylaşır
            card_limit_stored = 0.0 if parent_card_id else card_limit

            card = CreditCard(
                user_id=user_id,
                card_name=card_name,
                card_number_last4=card_number_last4,
                card_holder=card_holder,
                bank_name=bank_name,
                card_limit=card_limit_stored,
                current_debt=0.0,
                available_limit=0.0,
                closing_day=closing_day,
                due_day=due_day,
                parent_card_id=parent_card_id
            )
            session.add(card)
            session.flush()  # id ataması için

            # Ortak limit hesapla
            CreditCardService._recalculate_group_limits(session, card)

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
    def get_parent_cards(user_id):
        """Ortak limit için seçilebilecek ana kartları getir (parent_card_id == None olan aktif kartlar)"""
        session = SessionLocal()
        try:
            cards = session.query(CreditCard).filter(
                CreditCard.user_id == user_id,
                CreditCard.is_active == True,
                CreditCard.parent_card_id == None
            ).order_by(CreditCard.card_name).all()
            return cards
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

            # Child kart ise kendi limiti her zaman 0 kalır
            if card.parent_card_id:
                card.card_limit = 0.0

            # Ortak limit hesapla (tüm gruptaki kartlar güncellenir)
            CreditCardService._recalculate_group_limits(session, card)

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

            # Bu kart parent ise, bağlı ek kartlar var mı?
            children = session.query(CreditCard).filter(
                CreditCard.parent_card_id == card_id
            ).all()
            if children:
                child_names = ", ".join(c.card_name for c in children)
                return False, (f"Bu karta bağlı ek kartlar var: {child_names}\n"
                               f"Önce ek kartları silin veya bağlantıyı kaldırın.")

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
        """Kredi kartı istatistikleri (ortak limitler tek sayılır)"""
        session = SessionLocal()
        try:
            cards = session.query(CreditCard).filter(
                CreditCard.user_id == user_id,
                CreditCard.is_active == True
            ).all()

            # Sadece ana (parent_card_id == None) kartların limitlerini say
            # Ek kartlar aynı limiti paylaşır, çift sayılmasın
            total_limit = sum(
                card.card_limit for card in cards
                if card.parent_card_id is None
            )
            total_debt = sum(card.current_debt for card in cards)

            # Kullanılabilir limit: sadece ana kartların available_limit'ini topla
            total_available = sum(
                card.available_limit for card in cards
                if card.parent_card_id is None
            )

            return {
                'total_cards': len(cards),
                'total_limit': total_limit,
                'total_debt': total_debt,
                'total_available': total_available,
                'usage_rate': (total_debt / total_limit * 100) if total_limit > 0 else 0
            }
        finally:
            session.close()
