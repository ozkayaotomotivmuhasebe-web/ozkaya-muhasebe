from src.database.db import SessionLocal
from src.database.models import Transaction, Cari, BankAccount, CreditCard, TransactionType, PaymentMethod
from datetime import datetime, date
from sqlalchemy import func


class TransactionService:
    """İşlem yönetimi servisi - Tüm işlemleri buradan yönetiriz"""
    
    @staticmethod
    def create_transaction(user_id, transaction_date, transaction_type, payment_method,
                          customer_name, description, amount, **kwargs):
        """
        Yeni işlem oluştur ve ilgili hesapları otomatik güncelle
        
        Args:
            user_id: Kullanıcı ID
            transaction_date: İşlem tarihi
            transaction_type: İşlem türü (GIDER, GELIR, vb.)
            payment_method: Ödeme yöntemi (NAKIT, BANKA, KREDI_KARTI, CARI)
            customer_name: Müşteri/Tedarikçi adı
            description: Açıklama
            amount: Tutar
            **kwargs: İsteğe bağlı alanlar (cari_id, bank_account_id, credit_card_id, vb.)
        """
        session = SessionLocal()
        try:
            # İşlem oluştur
            transaction = Transaction(
                user_id=user_id,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                payment_method=payment_method,
                customer_name=customer_name,
                description=description,
                amount=amount,
                cari_id=kwargs.get('cari_id'),
                bank_account_id=kwargs.get('bank_account_id'),
                credit_card_id=kwargs.get('credit_card_id'),
                subject=kwargs.get('subject'),
                payment_type=kwargs.get('payment_type'),
                person=kwargs.get('person'),
                notes=kwargs.get('notes')
            )
            session.add(transaction)
            session.flush()  # ID'yi al
            
            # Otomatik hesap güncellemeleri
            TransactionService._update_related_accounts(session, transaction, transaction_type, 
                                                       payment_method, amount, kwargs)
            
            session.commit()
            return transaction, "Başarılı"
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()
    
    @staticmethod
    def _update_related_accounts(session, transaction, transaction_type, payment_method, amount, kwargs):
        """İlgili hesapları otomatik güncelle"""
        
        # CARİ HESAP GÜNCELLEMESİ
        # Cari seçilmişse veya ödeme yöntemi CARI ise
        if kwargs.get('cari_id') or payment_method == PaymentMethod.CARI:
            cari_id = kwargs.get('cari_id')
            if cari_id:
                cari = session.query(Cari).filter(Cari.id == cari_id).first()
                if cari:
                    if transaction_type in [TransactionType.GELIR, TransactionType.KESILEN_FATURA]:
                        cari.balance += amount  # Alacak arttı (müşteriden alacağımız para)
                    elif transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA]:
                        cari.balance -= amount  # Borç arttı (tedarikçiye borcumuz)
        
        # BANKA HESABI GÜNCELLEMESİ
        # Sadece ödeme yöntemi BANKA ise ve banka seçilmişse
        if payment_method == PaymentMethod.BANKA and kwargs.get('bank_account_id'):
            bank = session.query(BankAccount).filter(
                BankAccount.id == kwargs['bank_account_id']
            ).first()
            if bank:
                if transaction_type in [TransactionType.GELIR, TransactionType.KESILEN_FATURA]:
                    bank.balance += amount  # Para bankaya girdi
                elif transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA, 
                                         TransactionType.KREDI_KARTI_ODEME, TransactionType.KREDI_ODEME]:
                    bank.balance -= amount  # Para bankadan çıktı
        
        # KREDİ KARTI GÜNCELLEMESİ
        # Sadece ödeme yöntemi KREDİ_KARTI ise ve kart seçilmişse
        if payment_method == PaymentMethod.KREDI_KARTI and kwargs.get('credit_card_id'):
            card = session.query(CreditCard).filter(
                CreditCard.id == kwargs['credit_card_id']
            ).first()
            if card:
                if transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA]:
                    card.current_debt += amount  # Borç arttı
                    card.available_limit = card.card_limit - card.current_debt
                elif transaction_type == TransactionType.KREDI_KARTI_ODEME:
                    card.current_debt -= amount  # Ödeme yapıldı
                    card.available_limit = card.card_limit - card.current_debt
    
    @staticmethod
    def get_all_transactions(user_id, start_date=None, end_date=None):
        """Tüm işlemleri getir (filtrelenebilir)"""
        session = SessionLocal()
        try:
            query = session.query(Transaction).filter(Transaction.user_id == user_id)
            
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            transactions = query.order_by(Transaction.transaction_date.desc()).all()
            return transactions
        finally:
            session.close()
    
    @staticmethod
    def get_transaction_by_id(transaction_id):
        """ID'ye göre işlem getir"""
        session = SessionLocal()
        try:
            return session.query(Transaction).filter(Transaction.id == transaction_id).first()
        finally:
            session.close()
    
    @staticmethod
    def update_transaction(transaction_id, **kwargs):
        """İşlem güncelle"""
        session = SessionLocal()
        try:
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            
            if not transaction:
                return False, "İşlem bulunamadı"
            
            # Eski değerleri kaydet (hesap güncellemeleri için)
            old_amount = transaction.amount
            old_payment_method = transaction.payment_method
            old_transaction_type = transaction.transaction_type
            
            # Güncelle
            for key, value in kwargs.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            transaction.updated_at = datetime.now()
            
            # Hesapları güncelle (önce eski işlemi geri al, sonra yeni işlemi uygula)
            # Bu kısım daha karmaşık olabilir, şimdilik basit tutalım
            
            session.commit()
            return True, "Başarılı"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def delete_transaction(transaction_id):
        """İşlem sil ve hesapları geri al"""
        session = SessionLocal()
        try:
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            
            if not transaction:
                return False, "İşlem bulunamadı"
            
            # Hesapları geri al (ters işlem)
            TransactionService._reverse_account_updates(session, transaction)
            
            session.delete(transaction)
            session.commit()
            return True, "İşlem silindi"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def _reverse_account_updates(session, transaction):
        """Hesap güncellemelerini geri al"""
        amount = transaction.amount
        transaction_type = transaction.transaction_type
        payment_method = transaction.payment_method
        
        # Cari hesap geri al
        if transaction.cari_id:
            cari = session.query(Cari).filter(Cari.id == transaction.cari_id).first()
            if cari:
                if transaction_type in [TransactionType.GELIR, TransactionType.KESILEN_FATURA]:
                    cari.balance -= amount  # Alacağı geri al
                elif transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA]:
                    cari.balance += amount  # Borcu geri al
        
        # Banka hesap geri al
        if payment_method == PaymentMethod.BANKA and transaction.bank_account_id:
            bank = session.query(BankAccount).filter(
                BankAccount.id == transaction.bank_account_id
            ).first()
            if bank:
                if transaction_type in [TransactionType.GELIR, TransactionType.KESILEN_FATURA]:
                    bank.balance -= amount  # Para girişini geri al
                elif transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA,
                                         TransactionType.KREDI_KARTI_ODEME, TransactionType.KREDI_ODEME]:
                    bank.balance += amount  # Para çıkışını geri al
        
        # Kredi kartı geri al
        if payment_method == PaymentMethod.KREDI_KARTI and transaction.credit_card_id:
            card = session.query(CreditCard).filter(
                CreditCard.id == transaction.credit_card_id
            ).first()
            if card:
                if transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA]:
                    card.current_debt -= amount  # Borcu geri al
                    card.available_limit = card.card_limit - card.current_debt
                elif transaction_type == TransactionType.KREDI_KARTI_ODEME:
                    card.current_debt += amount  # Ödemeyi geri al
                    card.available_limit = card.card_limit - card.current_debt
    
    @staticmethod
    def get_statistics(user_id):
        """İstatistikler"""
        session = SessionLocal()
        try:
            # Toplam gelir
            total_income = session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type.in_([TransactionType.GELIR, TransactionType.KESILEN_FATURA])
            ).scalar() or 0
            
            # Toplam gider
            total_expense = session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type.in_([TransactionType.GIDER, TransactionType.GELEN_FATURA])
            ).scalar() or 0
            
            # İşlem sayıları
            total_count = session.query(func.count(Transaction.id)).filter(
                Transaction.user_id == user_id
            ).scalar() or 0
            
            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'net': total_income - total_expense,
                'total_count': total_count
            }
        finally:
            session.close()
