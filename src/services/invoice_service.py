from src.database.db import session_scope
from src.database.models import Invoice, InvoiceLineItem, Cari
from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy import and_

class InvoiceService:
    """Fatura yönetimi"""
    
    @staticmethod
    def create_invoice(
        user_id: int,
        cari_id: int,
        invoice_number: str,
        invoice_date: date,
        invoice_type: str,
        items: List[Dict],
        tax_rate: float = 0.0,
        description: str = "",
        due_date: date = None
    ) -> int:
        """Yeni fatura oluştur"""
        with session_scope() as session:
            subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            
            invoice = Invoice(
                user_id=user_id,
                cari_id=cari_id,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                due_date=due_date or invoice_date,
                invoice_type=invoice_type,
                amount=subtotal,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                total_amount=total_amount,
                description=description,
                status='DRAFT'
            )
            session.add(invoice)
            session.flush()
            
            for item in items:
                line_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    description=item.get('description', ''),
                    quantity=item.get('quantity', 1),
                    unit_price=item.get('unit_price', 0),
                    total=item.get('quantity', 1) * item.get('unit_price', 0)
                )
                session.add(line_item)
            
            return invoice.id
    
    @staticmethod
    def get_user_invoices(user_id: int) -> List[Invoice]:
        """Kullanıcının tüm faturaları"""
        with session_scope() as session:
            return session.query(Invoice).filter_by(user_id=user_id).order_by(Invoice.created_at.desc()).all()
    
    @staticmethod
    def get_invoice(invoice_id: int) -> Optional[Invoice]:
        """Fatura detayını al"""
        with session_scope() as session:
            return session.query(Invoice).filter_by(id=invoice_id).first()
    
    @staticmethod
    def update_invoice_status(invoice_id: int, status: str) -> bool:
        """Fatura statüsü güncelle"""
        with session_scope() as session:
            invoice = session.query(Invoice).filter_by(id=invoice_id).first()
            if invoice:
                invoice.status = status
                invoice.updated_at = datetime.now()
                return True
            return False
    
    @staticmethod
    def get_invoice_statistics(user_id: int) -> Dict:
        """İstatistikleri getir"""
        with session_scope() as session:
            total = session.query(Invoice).filter_by(user_id=user_id).count()
            paid = session.query(Invoice).filter_by(user_id=user_id, status='PAID').count()
            unpaid = session.query(Invoice).filter_by(user_id=user_id).filter(
                Invoice.status.in_(['DRAFT', 'SENT', 'PARTIALLY_PAID'])
            ).count()
            
            return {
                'total_invoices': total,
                'paid': paid,
                'unpaid': unpaid
            }
