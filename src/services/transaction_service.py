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
                    if transaction_type in [TransactionType.GELIR, TransactionType.GELEN_FATURA]:
                        cari.balance += amount  # Alacak arttı (ödeme/gelen fatura)
                    elif transaction_type in [TransactionType.GIDER, TransactionType.KESILEN_FATURA]:
                        cari.balance -= amount  # Borç arttı (gider/kesilen fatura)
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
    def get_all_transactions(user_id, start_date=None, end_date=None, offset=0, limit=None):
        """Tüm işlemleri getir (filtrelenebilir ve offset/limit destekli)
        
        Args:
            user_id: Kullanıcı ID
            start_date: Başlangıç tarihi (opsiyonel)
            end_date: Bitiş tarihi (opsiyonel)
            offset: Kaç kayıt atla (default: 0)
            limit: Kaç kayıt getir (None = tümü)
        
        Returns: {
            'transactions': Transaction listesi,
            'total': toplam kayıt sayısı,
            'offset': kullanılan offset,
            'limit': kullanılan limit
        }
        """
        session = SessionLocal()
        try:
            query = session.query(Transaction).filter(Transaction.user_id == user_id)
            
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            # Toplam sayısını al
            total = query.count()
            
            # Sorguyu sırala
            query = query.order_by(Transaction.transaction_date.desc())
            
            # Offset ve limit uygula
            if offset > 0:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            transactions = query.all()
            
            return {
                'transactions': transactions,
                'total': total,
                'offset': offset,
                'limit': limit
            }
        finally:
            session.close()
    
    @staticmethod
    def search_transactions(user_id, search_text, start_date=None, end_date=None, offset=0, limit=None):
        """Veritabanında işlem ara (offset/limit destekli)
        
        Arama şu sütunlarda yapılır:
        - Müşteri adı (customer_name)
        - Açıklama (description)
        - Konu (subject)
        - Kişi (person)
        - Tutar (amount)
        
        Args:
            user_id: Kullanıcı ID
            search_text: Aranacak metin
            start_date: Başlangıç tarihi (opsiyonel)
            end_date: Bitiş tarihi (opsiyonel)
            offset: Kaç kayıt atla
            limit: Kaç kayıt getir (None = tümü)
        
        Returns: {transactions, total, offset, limit}
        """
        from sqlalchemy import or_
        session = SessionLocal()
        try:
            # Arama metnini prepare et
            search_pattern = f"%{search_text}%"
            
            query = session.query(Transaction).filter(
                Transaction.user_id == user_id,
                or_(
                    Transaction.customer_name.ilike(search_pattern),
                    Transaction.description.ilike(search_pattern),
                    Transaction.subject.ilike(search_pattern),
                    Transaction.person.ilike(search_pattern),
                    Transaction.amount == float(search_text) if search_text.replace('.', '').replace(',', '').isdigit() else False
                )
            )
            
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            # Toplam sayısını al
            total = query.count()
            
            # Sorguyu sırala
            query = query.order_by(Transaction.transaction_date.desc())
            
            # Offset ve limit uygula
            if offset > 0:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            transactions = query.all()
            
            return {
                'transactions': transactions,
                'total': total,
                'offset': offset,
                'limit': limit
            }
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
        """İşlem güncelle ve bağlı hesapları yeniden hesapla"""
        session = SessionLocal()
        try:
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            
            if not transaction:
                return False, "İşlem bulunamadı"

            # Önce mevcut işlemin etkilerini geri al
            TransactionService._reverse_account_updates(session, transaction)

            # Yeni alanları uygula
            for key, value in kwargs.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            transaction.updated_at = datetime.now()
            session.flush()

            # Güncel işlem değerleri ile etkileri tekrar uygula
            update_kwargs = {
                'cari_id': transaction.cari_id,
                'bank_account_id': transaction.bank_account_id,
                'destination_bank_account_id': transaction.destination_bank_account_id,
                'credit_card_id': transaction.credit_card_id,
                'subject': transaction.subject,
                'payment_type': transaction.payment_type,
                'person': transaction.person,
                'notes': transaction.notes,
                'due_date': transaction.due_date,
            }
            TransactionService._update_related_accounts(
                session,
                transaction,
                transaction.transaction_type,
                transaction.payment_method,
                transaction.amount,
                update_kwargs
            )
            
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
                if transaction_type in [TransactionType.GELIR, TransactionType.GELEN_FATURA]:
                    cari.balance -= amount  # Alacağı geri al
                elif transaction_type in [TransactionType.GIDER, TransactionType.KESILEN_FATURA]:
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
    def set_payment_with_overflow(transaction_id, paid_amount, paid_date=None):
        """Ödeme girişi — fazla ödeme varsa aynı carinin sonraki ödenmemiş faturasına uygular.

        Fazla ödeme (paid_amount > fatura tutarı) durumunda:
          1. Mevcut fatura tam ödendi olarak işaretlenir.
          2. Fazla tutar, aynı carinin tarih/id sıralamasına göre ilk ödenmemiş
             KESILEN_FATURA kaydına aktarılır.
          3. Uygulanacak başka fatura yoksa fazla tutar bilgi mesajında gösterilir.

        Returns: (success: bool, message: str, overflow_info: dict)
          overflow_info anahtarları:
            'overflow'        – toplam fazla tutar (float)
            'applied'         – sonraki faturaya uygulanan tutar (float)
            'next_invoice_id' – uygulanan faturanın id'si (int | None)
            'next_invoice_no' – uygulanan faturanın numarası (str | None)
        """
        from datetime import date as date_type
        session = SessionLocal()
        try:
            t = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not t:
                return False, "İşlem bulunamadı.", {}

            paid_amount = max(0.0, float(paid_amount))

            # ── Fazla ödeme yok → mevcut kısmi/tam ödeme mantığı ──────────────
            if paid_amount <= t.amount:
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
                return True, "Ödeme güncellendi.", {}

            # ── Fazla ödeme var ───────────────────────────────────────────────
            overflow = round(paid_amount - t.amount, 2)
            t.paid_amount = t.amount   # Bu fatura TAMAMEN ödendi
            t.is_paid = True
            t.paid_date = paid_date or date_type.today()

            overflow_info = {
                'overflow': overflow,
                'applied': 0.0,
                'next_invoice_id': None,
                'next_invoice_no': None,
            }

            # Aynı carinin sonraki ödenmemiş / kısmi ödenmiş KESILEN_FATURA'larını bul
            if t.cari_id or t.customer_name:
                query = session.query(Transaction).filter(
                    Transaction.user_id == t.user_id,
                    Transaction.id != transaction_id,
                    Transaction.transaction_type == TransactionType.KESILEN_FATURA,
                    Transaction.is_paid == False,
                )
                if t.cari_id:
                    query = query.filter(Transaction.cari_id == t.cari_id)
                else:
                    query = query.filter(Transaction.customer_name == t.customer_name)

                next_invoices = query.order_by(
                    Transaction.transaction_date.asc(), Transaction.id.asc()
                ).all()

                for next_inv in next_invoices:
                    current_paid = getattr(next_inv, 'paid_amount', 0.0) or 0.0
                    remaining = next_inv.amount - current_paid
                    if remaining <= 0:
                        continue
                    apply_amount = min(overflow, remaining)
                    next_inv.paid_amount = round(current_paid + apply_amount, 2)
                    if next_inv.paid_amount >= next_inv.amount:
                        next_inv.is_paid = True
                        next_inv.paid_date = paid_date or date_type.today()
                    inv_no = getattr(next_inv, 'invoice_number', None) or f"F-{next_inv.id}"
                    overflow_info['next_invoice_id'] = next_inv.id
                    overflow_info['next_invoice_no'] = inv_no
                    overflow_info['applied'] = apply_amount
                    break  # Sadece ilk uygun faturaya uygula

            session.commit()

            from src.utils.helpers import format_tr as _fmt
            if overflow_info['applied'] > 0:
                msg = (
                    f"Fatura tam ödendi. {_fmt(overflow_info['overflow'])} TL fazla ödemenin "
                    f"{_fmt(overflow_info['applied'])} TL'si "
                    f"'{overflow_info['next_invoice_no']}' numaralı faturaya uygulandı."
                )
            else:
                msg = (
                    f"Fatura tam ödendi. {_fmt(overflow)} TL fazla ödeme vardı "
                    f"ancak uygulanacak başka ödenmemiş fatura bulunamadı."
                )
            return True, msg, overflow_info

        except Exception as e:
            session.rollback()
            return False, str(e), {}
        finally:
            session.close()

    @staticmethod
    def apply_cari_payment(reference_transaction_id, payment_amount, paid_date=None):
        """Ödemeyi carinin faturalarına FATURA TARİHİNE göre sırayla uygula (eskiden yeniye).

        Hangi faturaya sağ tıklanmış olursa olsun, o carinin en eski ödenmemiş
        KESILEN_FATURA'sından başlayarak ödemeyi dağıtır.

        Returns: (success: bool, message: str, applied_list: list[dict])
          applied_list her eleman:
            {
              'invoice_id'  : int,
              'invoice_no'  : str,
              'applied'     : float,   # bu faturaya uygulanan tutar
              'new_paid'    : float,   # faturedaki toplam ödenen tutar
              'fully_paid'  : bool,
            }
        """
        from datetime import date as date_type
        from src.utils.helpers import format_tr as _fmt
        session = SessionLocal()
        try:
            ref = session.query(Transaction).filter(Transaction.id == reference_transaction_id).first()
            if not ref:
                return False, "İşlem bulunamadı.", []

            payment_amount = max(0.0, float(payment_amount))
            today = paid_date or date_type.today()

            # Aynı carinin tüm ödenmemiş (veya kısmi ödenmiş) KESILEN_FATURA'larını
            # fatura tarihine göre eskiden yeniye sırala
            query = session.query(Transaction).filter(
                Transaction.user_id == ref.user_id,
                Transaction.transaction_type == TransactionType.KESILEN_FATURA,
                Transaction.is_paid == False,
            )
            if ref.cari_id:
                query = query.filter(Transaction.cari_id == ref.cari_id)
            else:
                query = query.filter(Transaction.customer_name == ref.customer_name)

            invoices = query.order_by(
                Transaction.transaction_date.asc(), Transaction.id.asc()
            ).all()

            if not invoices:
                return False, "Bu cari için ödenmemiş fatura bulunamadı.", []

            remaining = payment_amount
            applied_list = []

            for inv in invoices:
                if remaining <= 0:
                    break
                current_paid = getattr(inv, 'paid_amount', 0.0) or 0.0
                balance = inv.amount - current_paid
                if balance <= 0:
                    continue
                apply = min(remaining, balance)
                inv.paid_amount = round(current_paid + apply, 2)
                fully = inv.paid_amount >= inv.amount
                if fully:
                    inv.is_paid = True
                    inv.paid_date = today
                else:
                    inv.paid_date = today
                inv_no = getattr(inv, 'invoice_number', None) or f"F-{inv.id}"
                applied_list.append({
                    'invoice_id': inv.id,
                    'invoice_no': inv_no,
                    'applied': apply,
                    'new_paid': inv.paid_amount,
                    'fully_paid': fully,
                })
                remaining = round(remaining - apply, 2)

            session.commit()

            lines = []
            for a in applied_list:
                durum = "tam ödendi" if a['fully_paid'] else f"kısmi ({_fmt(a['new_paid'])} TL ödendi)"
                lines.append(f"  • {a['invoice_no']}: {_fmt(a['applied'])} TL uygulandı → {durum}")

            if remaining > 0:
                lines.append(f"  ⚠️ {_fmt(remaining)} TL fazla ödeme kaldı, uygulanacak başka fatura yok.")

            msg = "Ödeme fatura tarih sırasıyla uygulandı:\n" + "\n".join(lines)
            return True, msg, applied_list

        except Exception as e:
            session.rollback()
            return False, str(e), []
        finally:
            session.close()

    @staticmethod
    def auto_detect_paid_invoices(user_id):
        """GELIR işlemlerine göre fatura ödeme durumunu senkronize et.

        Eşleşme mantığı (iki aşamalı):
          1. TAM EŞLEŞME: aynı cari + tutar ±1 TL + 'fatura' keyword → fatura tamamen ödendi.
          2. DAĞITIM: Tam eşleşmeye girmeyen GELIR'ler, aynı carinin faturalarına
             FATURA TARİHİNE GÖRE (en eski önce) dağıtılır.
             Örnek: 21.000 TL GELIR + [F-181:15.000, F-182:250.000] →
               F-181 tamamen kapanır (15.000), F-182'ye 6.000 kısmi uygulanır.
        """
        session = SessionLocal()
        changed = 0
        try:
            from src.database.models import Cari
            from collections import defaultdict

            # Fatura tarihi sırasına göre eskiden yeniye sırala
            all_invoices = session.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.KESILEN_FATURA,
            ).order_by(Transaction.transaction_date.asc(), Transaction.id.asc()).all()

            gelir_txs = session.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.GELIR,
            ).all()

            cari_map = {}
            for c in session.query(Cari).filter_by(user_id=user_id).all():
                cari_map[c.id] = c.name.strip().lower() if c.name else ""

            def _cari_name(tx):
                if tx.cari_id and tx.cari_id in cari_map:
                    return cari_map[tx.cari_id]
                return (tx.customer_name or "").strip().lower()

            def _same_cari(tx1, tx2):
                if tx1.cari_id and tx2.cari_id:
                    return tx1.cari_id == tx2.cari_id
                n1 = _cari_name(tx1)
                n2 = _cari_name(tx2)
                return bool(n1) and n1 == n2

            def _has_fatura_keyword(pay):
                combined = ((pay.description or "") + " " + (getattr(pay, "subject", "") or "")).lower()
                return "fatura" in combined

            def _bucket(tx):
                """Gruplama anahtarı: cari_id öncelikli, yoksa normalize isim."""
                if tx.cari_id:
                    return tx.cari_id
                n = _cari_name(tx)
                return n if n else None

            # ── 1. TAM EŞLEŞME ────────────────────────────────────────────────────
            used_pay_ids = set()   # Tam eşleşmede kullanılan GELIR id'leri
            exact_inv_ids = set()  # Tam eşleşmesi olan fatura id'leri

            for inv in all_invoices:
                for pay in gelir_txs:
                    if pay.id in used_pay_ids:
                        continue
                    if abs(pay.amount - inv.amount) > 1.0:
                        continue
                    if not _has_fatura_keyword(pay):
                        continue
                    if not _same_cari(inv, pay):
                        continue
                    # Eşleşti
                    used_pay_ids.add(pay.id)
                    exact_inv_ids.add(inv.id)
                    cur = getattr(inv, "paid_amount", 0.0) or 0.0
                    if not inv.is_paid and cur == 0.0:
                        inv.is_paid = True
                        inv.paid_amount = inv.amount
                        inv.paid_date = pay.transaction_date
                        changed += 1
                    elif inv.is_paid and cur < inv.amount:
                        inv.paid_amount = inv.amount
                        if not inv.paid_date:
                            inv.paid_date = pay.transaction_date
                        changed += 1
                    break  # Bu fatura için ilk eşleşen GELIR yeterli

            # ── 2. DAĞITIM: kalan GELIR'leri cari bazlı, tarih sırasıyla dağıt ──
            # Kullanılmamış GELIR'leri cari bucket'ına göre grupla
            cari_gelirs = defaultdict(list)
            for pay in gelir_txs:
                if pay.id in used_pay_ids:
                    continue
                if not _has_fatura_keyword(pay):
                    continue
                b = _bucket(pay)
                if b is not None:
                    cari_gelirs[b].append(pay)

            # Tam eşleşmesi olmayan faturalar, bucket'a göre grupla (zaten tarih sıralı)
            cari_invs = defaultdict(list)
            for inv in all_invoices:
                if inv.id in exact_inv_ids:
                    continue
                b = _bucket(inv)
                if b is not None:
                    cari_invs[b].append(inv)

            all_buckets = set(list(cari_gelirs.keys()) + list(cari_invs.keys()))
            for bucket in all_buckets:
                pays = cari_gelirs.get(bucket, [])
                invs = cari_invs.get(bucket, [])
                if not invs:
                    continue

                total_gelir = sum(p.amount for p in pays)
                latest_date = max(
                    (p.transaction_date for p in pays if p.transaction_date), default=None
                )

                if total_gelir <= 0:
                    # Bu cari için dağıtılacak GELIR yok → önceki auto-kısmi ödemeleri temizle
                    for inv in invs:
                        cur = getattr(inv, "paid_amount", 0.0) or 0.0
                        if cur > 0 and not inv.is_paid and inv.paid_date is None:
                            # paid_date yoksa auto-set → sıfırla
                            inv.paid_amount = 0.0
                            changed += 1
                        elif inv.is_paid and abs(cur - inv.amount) < 1.0:
                            inv.is_paid = False
                            inv.paid_amount = 0.0
                            inv.paid_date = None
                            changed += 1
                    continue

                # Fatura tarihine göre eskiden yeniye dağıt
                remaining = total_gelir
                for inv in invs:
                    cur = getattr(inv, "paid_amount", 0.0) or 0.0

                    if remaining <= 0:
                        # Para bitti; bu faturada önceden auto-set 0-date varsa sıfırla
                        if cur > 0 and not inv.is_paid and inv.paid_date is None:
                            inv.paid_amount = 0.0
                            changed += 1
                        continue

                    apply = min(remaining, inv.amount)
                    new_paid = round(apply, 2)

                    # Önemli fark yoksa dokunma (floating point sessizliği)
                    if abs(new_paid - cur) < 0.5 and inv.is_paid == (new_paid >= inv.amount):
                        remaining = round(remaining - apply, 2)
                        continue

                    if new_paid >= inv.amount:
                        inv.is_paid = True
                        inv.paid_amount = inv.amount
                        inv.paid_date = latest_date
                    else:
                        inv.is_paid = False
                        inv.paid_amount = new_paid
                        inv.paid_date = latest_date
                    changed += 1
                    remaining = round(remaining - apply, 2)

            if changed > 0:
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"auto_detect_paid_invoices hatası: {e}")
        finally:
            session.close()
        return changed
