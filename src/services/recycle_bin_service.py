import json
from datetime import datetime
from src.database.db import SessionLocal
from src.database.models import (
    DeletedItem, Transaction, Cari, BankAccount, Loan, CreditCard, Employee,
    TransactionType, PaymentMethod
)


class RecycleBinService:
    """Çöp kutusu servisi - silinen kayıtları saklar ve geri alır"""

    # ---------- Ekleme ----------

    @staticmethod
    def save_transaction(transaction) -> None:
        """Transaction silinmeden önce çöp kutusuna kaydet"""
        data = {
            'user_id': transaction.user_id,
            'transaction_date': str(transaction.transaction_date),
            'transaction_type': transaction.transaction_type.value if transaction.transaction_type else None,
            'payment_method': transaction.payment_method.value if transaction.payment_method else None,
            'cari_id': transaction.cari_id,
            'bank_account_id': transaction.bank_account_id,
            'destination_bank_account_id': transaction.destination_bank_account_id,
            'credit_card_id': transaction.credit_card_id,
            'customer_name': transaction.customer_name,
            'description': transaction.description,
            'subject': transaction.subject,
            'payment_type': transaction.payment_type,
            'amount': transaction.amount,
            'person': transaction.person,
            'notes': transaction.notes,
            'due_date': str(transaction.due_date) if transaction.due_date else None,
            'is_paid': transaction.is_paid,
            'paid_date': str(transaction.paid_date) if transaction.paid_date else None,
            'paid_amount': transaction.paid_amount,
        }
        label = (
            f"{transaction.transaction_date} | "
            f"{transaction.transaction_type.value if transaction.transaction_type else '?'} | "
            f"{transaction.customer_name} | "
            f"{transaction.amount:,.2f} ₺"
        )
        RecycleBinService._add(transaction.user_id, 'transaction', None, label, data)

    @staticmethod
    def save_cari(cari) -> None:
        data = {
            'user_id': cari.user_id,
            'name': cari.name,
            'cari_type': cari.cari_type,
            'tax_number': cari.tax_number,
            'email': cari.email,
            'phone': cari.phone,
            'address': cari.address,
            'city': cari.city,
            'balance': cari.balance,
        }
        label = f"Cari: {cari.name} | Bakiye: {cari.balance:,.2f} ₺"
        RecycleBinService._add(cari.user_id, 'cari', cari.id, label, data)

    @staticmethod
    def save_bank(bank) -> None:
        data = {
            'user_id': bank.user_id,
            'bank_name': bank.bank_name,
            'account_number': bank.account_number,
            'iban': bank.iban,
            'branch': bank.branch,
            'balance': bank.balance,
            'overdraft_limit': bank.overdraft_limit,
            'currency': bank.currency,
        }
        label = f"Banka: {bank.bank_name} | Hesap: {bank.account_number} | Bakiye: {bank.balance:,.2f} ₺"
        RecycleBinService._add(bank.user_id, 'banka', bank.id, label, data)

    @staticmethod
    def save_loan(loan) -> None:
        data = {
            'user_id': loan.user_id,
            'loan_name': loan.loan_name,
            'bank_name': loan.bank_name,
            'company_name': loan.company_name,
            'loan_type': loan.loan_type,
            'loan_amount': loan.loan_amount,
            'remaining_balance': loan.remaining_balance,
            'monthly_payment': loan.monthly_payment,
            'interest_rate': loan.interest_rate,
            'start_date': str(loan.start_date) if loan.start_date else None,
            'end_date': str(loan.end_date) if loan.end_date else None,
            'due_day': loan.due_day,
            'total_paid': loan.total_paid,
            'paid_installments': loan.paid_installments,
            'total_installments': loan.total_installments,
            'status': loan.status,
            'notes': loan.notes,
        }
        label = f"Kredi: {loan.loan_name} | {loan.bank_name} | Kalan: {loan.remaining_balance:,.2f} ₺"
        RecycleBinService._add(loan.user_id, 'kredi', loan.id, label, data)

    @staticmethod
    def save_credit_card(card) -> None:
        data = {
            'user_id': card.user_id,
            'card_name': card.card_name,
            'card_number_last4': card.card_number_last4,
            'card_holder': card.card_holder,
            'bank_name': card.bank_name,
            'card_limit': card.card_limit,
            'current_debt': card.current_debt,
            'closing_day': card.closing_day,
            'due_day': card.due_day,
            'parent_card_id': card.parent_card_id,
        }
        label = f"KK: {card.card_name} | {card.bank_name} | Borç: {card.current_debt:,.2f} ₺"
        RecycleBinService._add(card.user_id, 'kredi_karti', card.id, label, data)

    @staticmethod
    def save_employee(employee, user_id: int) -> None:
        data = {
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'email': employee.email,
            'phone': employee.phone,
            'start_date': str(employee.start_date) if employee.start_date else None,
            'gross_salary': employee.gross_salary,
            'overtime_rate': employee.overtime_rate,
            'sgk_rate': employee.sgk_rate,
            'unemployment_rate': employee.unemployment_rate,
            'income_tax_rate': employee.income_tax_rate,
            'stamp_tax_rate': employee.stamp_tax_rate,
            'child_count': employee.child_count,
        }
        label = f"Çalışan: {employee.first_name} {employee.last_name} | Maaş: {employee.gross_salary:,.2f} ₺"
        RecycleBinService._add(user_id, 'calisan', employee.id, label, data)

    @staticmethod
    def _add(user_id: int, item_type: str, item_id, label: str, data: dict) -> None:
        session = SessionLocal()
        try:
            item = DeletedItem(
                user_id=user_id,
                item_type=item_type,
                item_id=item_id,
                item_label=label,
                item_data=json.dumps(data, ensure_ascii=False, default=str),
                deleted_at=datetime.now(),
            )
            session.add(item)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"RecycleBin kayıt hatası: {e}")
        finally:
            session.close()

    # ---------- Listeleme ----------

    @staticmethod
    def get_items(user_id: int) -> list:
        """Kullanıcının çöp kutusundaki tüm öğeleri döndür (en yeni önce)"""
        session = SessionLocal()
        try:
            items = session.query(DeletedItem).filter(
                DeletedItem.user_id == user_id
            ).order_by(DeletedItem.deleted_at.desc()).all()
            return items
        finally:
            session.close()

    # ---------- Geri Alma ----------

    @staticmethod
    def restore_item(deleted_item_id: int) -> tuple:
        """Öğeyi geri al. (success: bool, message: str)"""
        session = SessionLocal()
        try:
            item = session.query(DeletedItem).filter(DeletedItem.id == deleted_item_id).first()
            if not item:
                return False, "Kayıt bulunamadı"

            data = json.loads(item.item_data)

            if item.item_type == 'transaction':
                return RecycleBinService._restore_transaction(session, item, data)
            elif item.item_type == 'cari':
                return RecycleBinService._restore_soft(session, item, Cari)
            elif item.item_type == 'banka':
                return RecycleBinService._restore_soft(session, item, BankAccount)
            elif item.item_type == 'kredi':
                return RecycleBinService._restore_soft(session, item, Loan)
            elif item.item_type == 'kredi_karti':
                return RecycleBinService._restore_soft(session, item, CreditCard)
            elif item.item_type == 'calisan':
                return RecycleBinService._restore_soft(session, item, Employee)
            elif item.item_type == 'kira_takip_sekme':
                return RecycleBinService._restore_kira_tab(session, item, data)
            elif item.item_type == 'kira_kiraci':
                return RecycleBinService._restore_kira_kiraci(session, item, data)
            else:
                return False, f"Bilinmeyen kayıt türü: {item.item_type}"
        except Exception as e:
            session.rollback()
            import traceback; traceback.print_exc()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def _restore_transaction(session, deleted_item, data: dict) -> tuple:
        """Transaction'ı yeniden oluştur"""
        try:
            t_date = data.get('transaction_date')
            if t_date:
                from datetime import date as _date
                t_date = _date.fromisoformat(str(t_date))

            tx = Transaction(
                user_id=data['user_id'],
                transaction_date=t_date,
                transaction_type=TransactionType(data['transaction_type']) if data.get('transaction_type') else None,
                payment_method=PaymentMethod(data['payment_method']) if data.get('payment_method') else None,
                cari_id=data.get('cari_id'),
                bank_account_id=data.get('bank_account_id'),
                destination_bank_account_id=data.get('destination_bank_account_id'),
                credit_card_id=data.get('credit_card_id'),
                customer_name=data.get('customer_name', ''),
                description=data.get('description', ''),
                subject=data.get('subject'),
                payment_type=data.get('payment_type'),
                amount=data.get('amount', 0),
                person=data.get('person'),
                notes=data.get('notes'),
                is_paid=data.get('is_paid', False),
                paid_amount=data.get('paid_amount', 0.0),
            )
            if data.get('due_date'):
                from datetime import date as _date
                try:
                    tx.due_date = _date.fromisoformat(str(data['due_date']))
                except Exception:
                    pass
            if data.get('paid_date'):
                from datetime import date as _date
                try:
                    tx.paid_date = _date.fromisoformat(str(data['paid_date']))
                except Exception:
                    pass

            session.add(tx)
            session.delete(deleted_item)
            session.commit()
            return True, "İşlem geri alındı"
        except Exception as e:
            session.rollback()
            return False, str(e)

    @staticmethod
    def _restore_soft(session, deleted_item, model_class) -> tuple:
        """Soft-delete kaydını geri al (is_active=True yap)"""
        try:
            if deleted_item.item_id:
                obj = session.query(model_class).filter(model_class.id == deleted_item.item_id).first()
                if obj:
                    obj.is_active = True
                    if hasattr(obj, 'status') and model_class.__name__ == 'Loan':
                        obj.status = 'AKTIF'
                    session.delete(deleted_item)
                    session.commit()
                    return True, "Kayıt geri alındı"
            return False, "Orijinal kayıt bulunamadı (kalıcı silinmiş olabilir)"
        except Exception as e:
            session.rollback()
            return False, str(e)

    @staticmethod
    def _restore_kira_tab(session, deleted_item, data: dict) -> tuple:
        """Kira takip sekmesini JSON dosyasına geri ekle"""
        try:
            from pathlib import Path as _Path
            user_id = deleted_item.user_id
            data_file = _Path("data") / f"kira_takip_data_{user_id}.json"
            existing = {"tabs": [], "tab_widths": {}}
            if data_file.exists():
                try:
                    existing = json.loads(data_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            existing.setdefault("tabs", [])
            existing["tabs"].append(data)
            data_file.parent.mkdir(exist_ok=True)
            data_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            session.delete(deleted_item)
            session.commit()
            return True, "Kira takip sekmesi geri alındı. Sayfayı yenileyin."
        except Exception as e:
            session.rollback()
            return False, str(e)

    @staticmethod
    def _restore_kira_kiraci(session, deleted_item, data: dict) -> tuple:
        """Kiracıyı kira takip JSON dosyasındaki ilgili sekmeye geri ekle"""
        try:
            from pathlib import Path as _Path
            user_id = deleted_item.user_id
            data_file = _Path("data") / f"kira_takip_data_{user_id}.json"
            existing = {"tabs": [], "tab_widths": {}}
            if data_file.exists():
                try:
                    existing = json.loads(data_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            existing.setdefault("tabs", [])

            tab_name   = data.get("tab_name", "")
            contract   = data.get("contract", {})
            payments   = data.get("payments", {})
            odeme_detay = data.get("odeme_detay", {})
            yil_nots   = data.get("yil_nots", {})

            # İlgili sekmeyi bul
            target_tab = None
            for tab in existing["tabs"]:
                if tab.get("tab_name") == tab_name:
                    target_tab = tab
                    break
            if target_tab is None:
                if existing["tabs"]:
                    target_tab = existing["tabs"][0]
                else:
                    return False, f"'{tab_name}' sekmesi bulunamadı"

            # ID çakışmasını önle
            existing_ids = {c["id"] for c in target_tab.get("contracts", [])}
            old_cid = contract.get("id", 0)
            new_cid = old_cid
            if new_cid in existing_ids:
                new_cid = max(existing_ids, default=0) + 1
                contract = {**contract, "id": new_cid}

            target_tab.setdefault("contracts", []).append(contract)

            # Ödeme verilerini birleştir
            old_key = str(old_cid); new_key = str(new_cid)
            if old_key in payments:
                target_tab.setdefault("payments", {})[new_key] = payments[old_key]
            if old_key in odeme_detay:
                target_tab.setdefault("odeme_detay", {})[new_key] = odeme_detay[old_key]
            if old_key in yil_nots:
                target_tab.setdefault("yil_nots", {})[new_key] = yil_nots[old_key]

            data_file.parent.mkdir(exist_ok=True)
            data_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            session.delete(deleted_item)
            session.commit()
            return True, f"Kiracı '{contract.get('kiraci', '')}' geri alındı."
        except Exception as e:
            session.rollback()
            return False, str(e)

    # ---------- Kalıcı Silme ----------

    @staticmethod
    def permanent_delete(deleted_item_id: int) -> tuple:
        """Çöp kutusundan kalıcı olarak sil"""
        session = SessionLocal()
        try:
            item = session.query(DeletedItem).filter(DeletedItem.id == deleted_item_id).first()
            if not item:
                return False, "Kayıt bulunamadı"
            session.delete(item)
            session.commit()
            return True, "Kalıcı olarak silindi"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def empty_bin(user_id: int) -> tuple:
        """Çöp kutusunu tamamen boşalt"""
        session = SessionLocal()
        try:
            count = session.query(DeletedItem).filter(DeletedItem.user_id == user_id).delete()
            session.commit()
            return True, f"{count} kayıt kalıcı olarak silindi"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
