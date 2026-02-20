from src.database.db import session_scope
from src.database.models import BankAccount, BankTransaction
from typing import List, Optional, Tuple

class BankService:
    """Banka yönetimi"""
    
    @staticmethod
    def create_account(user_id: int, bank_name: str, account_number: str, 
                       iban: str = None, currency: str = 'TRY', balance: float = 0.0,
                       branch: str = None, overdraft_limit: float = 0.0) -> Tuple[bool, str]:
        """Yeni hesap"""
        try:
            with session_scope() as session:
                account = BankAccount(
                    user_id=user_id, bank_name=bank_name,
                    account_number=account_number, iban=iban, currency=currency,
                    balance=balance, branch=branch, overdraft_limit=overdraft_limit
                )
                session.add(account)
                session.flush()
                return True, "Banka hesabı başarıyla eklendi"
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    @staticmethod
    def get_accounts(user_id: int) -> List[BankAccount]:
        """Tüm hesaplar"""
        with session_scope() as session:
            return session.query(BankAccount).filter_by(user_id=user_id, is_active=True).all()
    
    @staticmethod
    def get_account(account_id: int) -> Optional[BankAccount]:
        """Hesap detayı"""
        with session_scope() as session:
            return session.query(BankAccount).filter_by(id=account_id).first()
    
    @staticmethod
    def add_transaction(user_id: int, bank_account_id: int, amount: float, 
                       transaction_type: str, description: str = None) -> int:
        """İşlem ekle"""
        with session_scope() as session:
            transaction = BankTransaction(
                user_id=user_id, bank_account_id=bank_account_id,
                amount=amount, transaction_type=transaction_type,
                description=description
            )
            session.add(transaction)
            session.flush()
            
            account = session.query(BankAccount).filter_by(id=bank_account_id).first()
            if account:
                if transaction_type == 'INCOME':
                    account.balance += amount
                else:
                    account.balance -= amount
            
            return transaction.id
