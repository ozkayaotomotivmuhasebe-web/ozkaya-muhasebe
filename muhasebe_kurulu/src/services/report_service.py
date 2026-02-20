from src.database.db import SessionLocal
from src.database.models import Transaction, Cari, BankAccount, CreditCard, Report
from datetime import datetime, date
from sqlalchemy import func
import json


class ReportService:
    """Rapor servisi"""
    
    @staticmethod
    def generate_income_expense_report(user_id, start_date=None, end_date=None):
        """Gelir-Gider raporu"""
        session = SessionLocal()
        try:
            query = session.query(Transaction).filter(Transaction.user_id == user_id)
            
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            transactions = query.all()
            
            income = sum(t.amount for t in transactions if t.transaction_type.value in ['GELIR', 'KESILEN_FATURA'])
            expense = sum(t.amount for t in transactions if t.transaction_type.value in ['GIDER', 'GELEN_FATURA'])
            
            return {
                'total_income': income,
                'total_expense': expense,
                'net_profit': income - expense,
                'transaction_count': len(transactions),
                'period': {
                    'start': str(start_date) if start_date else 'Başlangıç',
                    'end': str(end_date) if end_date else 'Günümüz'
                }
            }
        finally:
            session.close()
    
    @staticmethod
    def generate_cari_balance_report(user_id):
        """Cari bakiye raporu"""
        session = SessionLocal()
        try:
            caris = session.query(Cari).filter(
                Cari.user_id == user_id,
                Cari.is_active == True
            ).all()
            
            total_receivable = sum(c.balance for c in caris if c.balance > 0)
            total_payable = sum(abs(c.balance) for c in caris if c.balance < 0)
            
            cari_data = [
                {
                    'name': c.name,
                    'type': c.cari_type,
                    'balance': c.balance,
                    'status': 'Alacak' if c.balance > 0 else 'Borç' if c.balance < 0 else 'Sıfır'
                }
                for c in caris
            ]
            
            return {
                'total_caris': len(caris),
                'total_receivable': total_receivable,
                'total_payable': total_payable,
                'net_balance': total_receivable - total_payable,
                'caris': cari_data
            }
        finally:
            session.close()
    
    @staticmethod
    def generate_bank_summary_report(user_id):
        """Banka özet raporu"""
        session = SessionLocal()
        try:
            banks = session.query(BankAccount).filter(
                BankAccount.user_id == user_id,
                BankAccount.is_active == True
            ).all()
            
            total_balance_try = sum(b.balance for b in banks if b.currency == 'TRY')
            
            bank_data = [
                {
                    'bank_name': b.bank_name,
                    'account_number': b.account_number,
                    'balance': b.balance,
                    'currency': b.currency
                }
                for b in banks
            ]
            
            return {
                'total_accounts': len(banks),
                'total_balance_try': total_balance_try,
                'banks': bank_data
            }
        finally:
            session.close()
    
    @staticmethod
    def generate_credit_card_summary(user_id):
        """Kredi kartı özet raporu"""
        session = SessionLocal()
        try:
            cards = session.query(CreditCard).filter(
                CreditCard.user_id == user_id,
                CreditCard.is_active == True
            ).all()
            
            total_limit = sum(c.card_limit for c in cards)
            total_debt = sum(c.current_debt for c in cards)
            total_available = sum(c.available_limit for c in cards)
            
            card_data = [
                {
                    'card_name': c.card_name,
                    'bank': c.bank_name,
                    'limit': c.card_limit,
                    'debt': c.current_debt,
                    'available': c.available_limit,
                    'usage_rate': (c.current_debt / c.card_limit * 100) if c.card_limit > 0 else 0
                }
                for c in cards
            ]
            
            return {
                'total_cards': len(cards),
                'total_limit': total_limit,
                'total_debt': total_debt,
                'total_available': total_available,
                'overall_usage_rate': (total_debt / total_limit * 100) if total_limit > 0 else 0,
                'cards': card_data
            }
        finally:
            session.close()
    
    @staticmethod
    def generate_comprehensive_report(user_id, start_date=None, end_date=None):
        """Kapsamlı genel rapor"""
        income_expense = ReportService.generate_income_expense_report(user_id, start_date, end_date)
        cari_balance = ReportService.generate_cari_balance_report(user_id)
        bank_summary = ReportService.generate_bank_summary_report(user_id)
        card_summary = ReportService.generate_credit_card_summary(user_id)
        
        return {
            'report_date': str(datetime.now()),
            'income_expense': income_expense,
            'cari_balance': cari_balance,
            'bank_summary': bank_summary,
            'credit_card_summary': card_summary,
            'overall_financial_health': {
                'liquid_assets': bank_summary['total_balance_try'],
                'receivables': cari_balance['total_receivable'],
                'payables': cari_balance['total_payable'],
                'credit_card_debt': card_summary['total_debt'],
                'net_worth': (
                    bank_summary['total_balance_try'] + 
                    cari_balance['total_receivable'] - 
                    cari_balance['total_payable'] - 
                    card_summary['total_debt']
                )
            }
        }
    
    @staticmethod
    def save_report(user_id, report_type, title, data, start_date=None, end_date=None):
        """Raporu veritabanına kaydet"""
        session = SessionLocal()
        try:
            report = Report(
                user_id=user_id,
                report_type=report_type,
                title=title,
                start_date=start_date,
                end_date=end_date,
                data=json.dumps(data, ensure_ascii=False)
            )
            session.add(report)
            session.commit()
            return report, "Başarılı"
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()
    
    @staticmethod
    def get_saved_reports(user_id):
        """Kaydedilmiş raporları getir"""
        session = SessionLocal()
        try:
            reports = session.query(Report).filter(
                Report.user_id == user_id
            ).order_by(Report.generated_at.desc()).all()
            return reports
        finally:
            session.close()
