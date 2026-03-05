from src.database.db import SessionLocal
from src.database.models import Transaction, Cari, BankAccount, CreditCard, Loan, TransactionType, PaymentMethod
from datetime import datetime, date
from sqlalchemy import func


class TransactionService:
    """İşlem yönetimi servisi - Tüm işlemleri buradan yönetiriz"""

    @staticmethod
    def find_duplicate_transaction(user_id, transaction_date, amount, description, customer_name=None, person=None, session=None):
        """Mükerrer işlem kontrolü (tarih + tutar + açıklama + kişi/müşteri)
        
        session parametresi verilirse o session kullanılır ve kapatılmaz.
        Verilmezse yeni bir session açılır ve finally'de kapatılır.
        """
        external_session = session is not None
        if not external_session:
            session = SessionLocal()
        try:
            def _norm(value):
                return str(value).strip().casefold() if value is not None else ""

            desc_norm = _norm(description)
            cust_norm = _norm(customer_name)
            person_norm = _norm(person)

            if not cust_norm and not person_norm:
                return None

            # Flush yaparak session içindeki pending nesneleri de sorgulaya ekle
            if external_session:
                session.flush()

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
            if not external_session:
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
                notes=kwargs.get('notes'),
                due_date=kwargs.get('due_date')
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
                elif transaction_type == TransactionType.KREDI_KARTI_ODEME:
                    card.current_debt -= amount  # Ödeme yapıldı
                # Ortak limit grubundaki tüm kartların available_limit'ini yeniden hesapla
                TransactionService._recalc_card_group(session, card)

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
                elif transaction_type == TransactionType.KREDI_KARTI_ODEME:
                    card.current_debt += amount  # Ödemeyi geri al
                # Ortak limit grubundaki tüm kartların available_limit'ini yeniden hesapla
                TransactionService._recalc_card_group(session, card)

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
    def _recalc_card_group(session, card):
        """Ortak limitli gruptaki tüm kartların available_limit değerini güncelle."""
        parent = (session.query(CreditCard).filter(CreditCard.id == card.parent_card_id).first()
                  if card.parent_card_id else card)
        if not parent:
            return
        children = session.query(CreditCard).filter(CreditCard.parent_card_id == parent.id).all()
        total_debt = parent.current_debt + sum(c.current_debt for c in children)
        shared_available = parent.card_limit - total_debt
        parent.available_limit = shared_available
        for child in children:
            child.available_limit = shared_available

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

    @staticmethod
    def mark_invoice_as_paid(transaction_id, paid=True, paid_date=None):
        """Faturayı tam ödendi / ödenmedi olarak işaretle."""
        from datetime import date as date_type
        session = SessionLocal()
        try:
            t = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not t:
                return False, "İşlem bulunamadı."
            t.is_paid = paid
            t.paid_date = (paid_date or date_type.today()) if paid else None
            t.paid_amount = t.amount if paid else 0.0
            session.commit()
            return True, "Fatura ödeme durumu güncellendi."
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def set_partial_payment(transaction_id, paid_amount, paid_date=None):
        """Kısmi ödeme tutarını güncelle.

        paid_amount >= fatura tutarı ise tam ödenmiş sayılır.
        paid_amount == 0 ise ödeme sıfırlanır.
        Returns: (success, message)
        """
        from datetime import date as date_type
        session = SessionLocal()
        try:
            t = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not t:
                return False, "İşlem bulunamadı."
            paid_amount = max(0.0, float(paid_amount))
            t.paid_amount = paid_amount
            if paid_amount >= t.amount:
                t.is_paid = True
                t.paid_date = paid_date or date_type.today()
            elif paid_amount == 0.0:
                t.is_paid = False
                t.paid_date = None
            else:
                t.is_paid = False
                t.paid_date = paid_date or date_type.today()
            session.commit()
            return True, "Kısmi ödeme güncellendi."
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def auto_detect_paid_invoices(user_id):
        """GELIR işlemlerine göre fatura ödeme durumunu senkronize et.

        Eşleşme kriterleri (HEPSİ gerekmez, biri yeterliyse):
          - Aynı cari_id  VEYA  aynı customer_name  VEYA  cari ismi ile customer_name eşleşmesi
          - Tutar ±1 TL
          - Açıklama, konu veya description içinde "fatura" geçiyor  (VEYA transaction_type KESILEN/GELEN_FATURA)
        """
        session = SessionLocal()
        changed = 0
        try:
            from src.database.models import Cari

            all_invoices = session.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.KESILEN_FATURA,
            ).all()

            gelir_txs = session.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.GELIR,
            ).all()

            # Cari id → name eşlemesi (hızlı lookup)
            cari_map = {}
            for c in session.query(Cari).filter_by(user_id=user_id).all():
                cari_map[c.id] = c.name.strip().lower() if c.name else ""

            def _name(tx):
                """Bir transaction'ın cari ismini döndür (her iki kaynaktan)."""
                if tx.cari_id and tx.cari_id in cari_map:
                    return cari_map[tx.cari_id]
                if tx.customer_name:
                    return tx.customer_name.strip().lower()
                return ""

            def _has_fatura_keyword(pay):
                combined = " ".join([
                    (pay.description or ""),
                    (getattr(pay, 'subject', '') or ""),
                ]).lower()
                return "fatura" in combined

            def _cari_match(inv, pay):
                """İki işlem arasında cari eşleşmesi kontrol et."""
                inv_name = _name(inv)
                pay_name = _name(pay)
                return (
                    (inv.cari_id and pay.cari_id and inv.cari_id == pay.cari_id)
                    or (inv_name and pay_name and inv_name == pay_name)
                )

            def find_match(inv):
                """Tam eşleşme: tutar ±1 TL + fatura keyword + aynı cari."""
                for pay in gelir_txs:
                    if abs(pay.amount - inv.amount) > 1.0:
                        continue
                    if not _has_fatura_keyword(pay):
                        continue
                    if _cari_match(inv, pay):
                        return pay
                return None

            def find_partial_matches(inv):
                """Kısmi eşleşme: aynı cariden fatura keyword'lü GELIR'lerin toplamı.

                Tam eşleşmesi (±1 TL) olmayan faturalar için kullanılır.
                Returns: (toplam_odenen, en_son_tarih) veya (0.0, None)
                """
                matched_pays = []
                for pay in gelir_txs:
                    if not _has_fatura_keyword(pay):
                        continue
                    if not _cari_match(inv, pay):
                        continue
                    if pay.amount <= 0 or pay.amount > inv.amount + 1.0:
                        continue
                    matched_pays.append(pay)
                if not matched_pays:
                    return 0.0, None
                total = sum(p.amount for p in matched_pays)
                latest_date = max(p.transaction_date for p in matched_pays if p.transaction_date)
                return total, latest_date

            for inv in all_invoices:
                current_paid = getattr(inv, 'paid_amount', 0.0) or 0.0
                match = find_match(inv)

                if match:
                    # Tam eşleşme var
                    if not inv.is_paid and current_paid == 0.0:
                        # Henüz işaretlenmemiş → tam ödendi yap
                        inv.is_paid = True
                        inv.paid_amount = inv.amount
                        inv.paid_date = match.transaction_date
                        changed += 1
                    elif inv.is_paid and current_paid < inv.amount:
                        # is_paid=True ama paid_amount eksik (eski veri) → tutarı düzelt
                        inv.paid_amount = inv.amount
                        if not inv.paid_date:
                            inv.paid_date = match.transaction_date
                        changed += 1
                    # is_paid=True ve paid_amount tam → dokunma (zaten doğru)
                else:
                    # Tam eşleşme yok — kısmi eşleşme kontrol et
                    partial_total, partial_date = find_partial_matches(inv)

                    if partial_total > 0 and partial_total < inv.amount:
                        # Kısmi ödeme var
                        if abs(current_paid - partial_total) > 1.0 or inv.is_paid:
                            # DB'de farklı değer var veya yanlışlıkla is_paid=True → güncelle
                            inv.paid_amount = partial_total
                            inv.is_paid = False
                            inv.paid_date = partial_date
                            changed += 1
                    elif partial_total >= inv.amount:
                        # Kısmi ödemelerin toplamı fatura tutarını karşılıyor → tam ödendi
                        if not inv.is_paid or abs(current_paid - inv.amount) > 1.0:
                            inv.is_paid = True
                            inv.paid_amount = inv.amount
                            inv.paid_date = partial_date
                            changed += 1
                    elif inv.is_paid and (abs(current_paid - inv.amount) < 1.0 or current_paid == 0.0):
                        # Auto-tam-ödeme vardı ama GELIR silindi → geri al
                        inv.is_paid = False
                        inv.paid_amount = 0.0
                        inv.paid_date = None
                        changed += 1
                    elif current_paid > 0 and not inv.is_paid and partial_total == 0.0:
                        # Eşleşen GELIR yok (silindi) → kısmi ödemeyi sıfırla
                        inv.paid_amount = 0.0
                        inv.paid_date = None
                        changed += 1
                # Manuel kısmi (0 < paid_amount < amount, is_paid=False, eşleşme yok) → dokunma

            if changed > 0:
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"auto_detect_paid_invoices hatası: {e}")
        finally:
            session.close()
        return changed
