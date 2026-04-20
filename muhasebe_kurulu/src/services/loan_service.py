from src.database.db import SessionLocal
from src.database.models import Loan
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class LoanService:
    """Kredi Yönetim Servisi"""
    
    @staticmethod
    def create_loan(user_id, loan_name, bank_name, company_name=None, loan_type=None, loan_amount=None, 
                   start_date=None, due_day=None, interest_rate=0.0, monthly_payment=0.0,
                   remaining_balance=None,
                   end_date=None, total_installments=None, notes=None):
        """Yeni kredi ekle"""
        session = SessionLocal()
        try:
            initial_remaining_balance = loan_amount if remaining_balance is None else remaining_balance
            loan = Loan(
                user_id=user_id,
                loan_name=loan_name,
                bank_name=bank_name,
                company_name=company_name,
                loan_type=loan_type,
                loan_amount=loan_amount,
                remaining_balance=initial_remaining_balance,
                start_date=start_date,
                due_day=due_day,
                interest_rate=interest_rate,
                monthly_payment=monthly_payment,
                end_date=end_date,
                total_installments=total_installments,
                notes=notes,
                status='AKTIF'
            )
            session.add(loan)
            session.commit()
            return loan, "Kredi başarıyla eklendi"
        except Exception as e:
            session.rollback()
            return None, f"Kredi eklenirken hata: {str(e)}"
        finally:
            session.close()
    
    @staticmethod
    def get_loans(user_id, active_only=False):
        """Kredileri getir"""
        session = SessionLocal()
        try:
            query = session.query(Loan).filter(Loan.user_id == user_id)
            if active_only:
                query = query.filter(Loan.is_active == True, Loan.status == 'AKTIF')
            return query.all()
        except Exception as e:
            print(f"Kredi getirme hatası: {e}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def get_loan(loan_id):
        """Belirli krediyi getir"""
        session = SessionLocal()
        try:
            return session.query(Loan).filter(Loan.id == loan_id).first()
        except Exception as e:
            print(f"Kredi getirme hatası: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def update_loan(loan_id, **kwargs):
        """Kredi güncelle"""
        session = SessionLocal()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                return False, "Kredi bulunamadı"
            
            for key, value in kwargs.items():
                if hasattr(loan, key):
                    setattr(loan, key, value)
            
            loan.updated_at = datetime.now()
            session.commit()
            return True, "Kredi güncellendi"
        except Exception as e:
            session.rollback()
            return False, f"Kredi güncellenirken hata: {str(e)}"
        finally:
            session.close()
    
    @staticmethod
    def delete_loan(loan_id):
        """Kredi sil"""
        session = SessionLocal()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                return False, "Kredi bulunamadı"
            loan.is_active = False
            session.commit()
            return True, "Kredi silindi"
        except Exception as e:
            session.rollback()
            return False, f"Kredi silinirken hata: {str(e)}"
        finally:
            session.close()
    
    @staticmethod
    def make_payment(loan_id, payment_amount, payment_date=None):
        """Kredi ödemesi yap"""
        session = SessionLocal()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                return False, "Kredi bulunamadı"
            
            if payment_date is None:
                payment_date = date.today()
            
            total_repayment = max(float(loan.remaining_balance or 0), float(loan.loan_amount or 0))
            # Kalan bakiyeyi formülle hesapla (geri ödenecek - ödenen)
            current_remaining = max(0.0, total_repayment - float(loan.total_paid or 0))
            if payment_amount > current_remaining:
                return False, f"Ödeme tutarı kalan bakiyeyi ({current_remaining:.2f}) aşamaz"

            loan.total_paid += payment_amount
            loan.remaining_balance = total_repayment
            loan.paid_installments += 1
            loan.updated_at = datetime.now()
            
            # Kredi kapatıldı mı kontrol et
            remaining_after = max(0.0, total_repayment - float(loan.total_paid or 0))
            if remaining_after <= 0:
                loan.status = 'KAPATILDI'
            
            session.commit()
            return True, "Ödeme başarıyla yapıldı"
        except Exception as e:
            session.rollback()
            return False, f"Ödeme yapılırken hata: {str(e)}"
        finally:
            session.close()
    
    @staticmethod
    def get_next_payment_date(loan_id):
        """Sonraki ödeme tarihini hesapla"""
        session = SessionLocal()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                return None
            
            today = date.today()
            next_payment_day = loan.due_day
            
            # Eğer bu aydaki gün geçtiyse, gelecek aya kaydır
            if today.day >= next_payment_day:
                next_date = today + relativedelta(months=1)
            else:
                next_date = today
            
            # Gün ayarla
            try:
                next_date = next_date.replace(day=next_payment_day)
            except ValueError:
                # Ay sonunda gün sayısı daha az ise
                next_date = next_date.replace(day=28)
            
            return next_date
        except Exception as e:
            print(f"Sonraki ödeme tarihi hesaplama hatası: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def get_loans_summary(user_id):
        """Kredi özetini getir"""
        session = SessionLocal()
        try:
            loans = session.query(Loan).filter(
                Loan.user_id == user_id,
                Loan.is_active == True
            ).all()
            
            summary = {
                'toplam_kredi': sum(max(float(l.remaining_balance or 0), float(l.loan_amount or 0)) for l in loans),
                'toplam_odenen': sum(l.total_paid for l in loans),
                'toplam_kalan': sum(max(0.0, max(float(l.remaining_balance or 0), float(l.loan_amount or 0)) - float(l.total_paid or 0)) for l in loans),
                'akif_kredi_sayisi': len([l for l in loans if l.status == 'AKTIF']),
                'kapali_kredi_sayisi': len([l for l in loans if l.status == 'KAPATILDI']),
            }
            return summary
        except Exception as e:
            print(f"Kredi özeti getirme hatası: {e}")
            return None
        finally:
            session.close()
