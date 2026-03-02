from src.database.db import SessionLocal
from src.database.models import Transaction, Cari, BankAccount, CreditCard, Loan, TransactionType, PaymentMethod
from datetime import datetime, date
from sqlalchemy import func


class TransactionService:
    """İşlem yönetimi servisi - Tüm işlemleri buradan yönetiriz"""

    @staticmethod
    def find_duplicate_transaction(user_id, transaction_date, amount, description, customer_name=None, person=None):
        """Mükerrer işlem kontrolü (tarih + tutar + açıklama + kişi/müşteri)"""
        session = SessionLocal()
        try:
            def _norm(value):
                return str(value).strip().casefold() if value is not None else ""

            desc_norm = _norm(description)
            cust_norm = _norm(customer_name)
            person_norm = _norm(person)

            if not cust_norm and not person_norm:
                return None

            candidates = session.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date == transaction_date,
                Transaction.amount == amount
            ).all()

            for trans in candidates:
                if _norm(trans.description) != desc_norm:
                    continue
                if cust_norm and _norm(trans.customer_name) != cust_norm:
                    continue
                if person_norm and _norm(trans.person) != person_norm:
                    continue
                return trans

            return None
        finally:
            session.close()
    
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
                destination_bank_account_id=kwargs.get('destination_bank_account_id'),
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
        
        # TRANSFER İŞLEMLERİ - Kaynak hesaptan düş, hedef hesaba ekle
        if transaction_type == TransactionType.TRANSFER and payment_method == PaymentMethod.TRANSFER:
            # Kaynak hesap
            source_bank = session.query(BankAccount).filter(
                BankAccount.id == kwargs.get('bank_account_id')
            ).first()
            if source_bank:
                source_bank.balance -= amount
            
            # Hedef hesap
            dest_bank = session.query(BankAccount).filter(
                BankAccount.id == kwargs.get('destination_bank_account_id')
            ).first()
            if dest_bank:
                dest_bank.balance += amount
            
            return  # Transfer işleminde başka güncelleme yok
        
        # NAKİT ÇEKİM - Bankadan nakit çek (banka bakiyesi azalır)
        if transaction_type == TransactionType.NAKIT_CEKIMI:
            bank = session.query(BankAccount).filter(
                BankAccount.id == kwargs.get('bank_account_id')
            ).first()
            if bank:
                bank.balance -= amount
            return
        
        # NAKİT YATIRIM - Bankaya nakit yatır (banka bakiyesi artar)
        if transaction_type == TransactionType.NAKIT_YATIRIMI:
            bank = session.query(BankAccount).filter(
                BankAccount.id == kwargs.get('bank_account_id')
            ).first()
            if bank:
                bank.balance += amount
            return
        
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
                    elif payment_method == PaymentMethod.NAKIT:
                        # NAKIT ödeme seçilmiş cari ile işlem
                        cari.balance -= amount if transaction_type == TransactionType.GIDER else amount
        
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

        # KREDİ GÜNCELLEMESİ (KREDI_ODEME)
        if transaction_type == TransactionType.KREDI_ODEME:
            loan_id = kwargs.get('loan_id') or TransactionService._extract_loan_id(kwargs.get('notes'))
            if loan_id:
                loan = session.query(Loan).filter(Loan.id == loan_id, Loan.user_id == transaction.user_id).first()
                if loan:
                    total_repayment = max(float(loan.remaining_balance or 0), float(loan.loan_amount or 0))
                    current_remaining = max(0.0, total_repayment - float(loan.total_paid or 0))
                    if amount > current_remaining:
                        raise ValueError(f"Ödeme tutarı kalan kredi bakiyesini ({current_remaining:.2f}) aşamaz")
                    loan.total_paid += amount
                    loan.remaining_balance = total_repayment
                    loan.paid_installments += 1
                    remaining_after = max(0.0, total_repayment - float(loan.total_paid or 0))
                    if remaining_after <= 0:
                        loan.status = 'KAPATILDI'
    
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
        
        # Nakit çekim geri al (banka bakiyesi artar)
        if transaction_type == TransactionType.NAKIT_CEKIMI and transaction.bank_account_id:
            bank = session.query(BankAccount).filter(
                BankAccount.id == transaction.bank_account_id
            ).first()
            if bank:
                bank.balance += amount
            return
        
        # Nakit yatırım geri al (banka bakiyesi azalır)
        if transaction_type == TransactionType.NAKIT_YATIRIMI and transaction.bank_account_id:
            bank = session.query(BankAccount).filter(
                BankAccount.id == transaction.bank_account_id
            ).first()
            if bank:
                bank.balance -= amount
            return
        
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

        # Kredi geri al
        if transaction_type == TransactionType.KREDI_ODEME:
            loan_id = TransactionService._extract_loan_id(transaction.notes)
            if loan_id:
                loan = session.query(Loan).filter(Loan.id == loan_id, Loan.user_id == transaction.user_id).first()
                if loan:
                    total_repayment = max(float(loan.remaining_balance or 0), float(loan.loan_amount or 0))
                    loan.total_paid = max((loan.total_paid or 0) - amount, 0.0)
                    loan.remaining_balance = total_repayment
                    loan.paid_installments = max((loan.paid_installments or 0) - 1, 0)
                    remaining_after = max(0.0, total_repayment - float(loan.total_paid or 0))
                    if remaining_after > 0 and loan.status == 'KAPATILDI':
                        loan.status = 'AKTIF'

    @staticmethod
    def _extract_loan_id(notes):
        if not notes:
            return None
        text = str(notes).strip()
        if not text.startswith('loan_id:'):
            return None
        raw_id = text.split(':', 1)[1].strip()
        if raw_id.isdigit():
            return int(raw_id)
        return None
    
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
