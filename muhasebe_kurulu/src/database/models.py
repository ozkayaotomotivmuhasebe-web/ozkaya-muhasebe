from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import json

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default='user')  # 'admin' or 'user'
    can_view_dashboard = Column(Boolean, default=True)
    can_view_invoices = Column(Boolean, default=True)
    can_view_caris = Column(Boolean, default=True)
    can_view_banks = Column(Boolean, default=True)
    can_view_reports = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
    
    invoices = relationship('Invoice', back_populates='user')
    bank_accounts = relationship('BankAccount', back_populates='user')
    caris = relationship('Cari', back_populates='user')
    transactions = relationship('BankTransaction', back_populates='user')
    reports = relationship('Report', back_populates='user')
    credit_cards = relationship('CreditCard', back_populates='user')
    all_transactions = relationship('Transaction', back_populates='user')


class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bank_name = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    iban = Column(String(34), nullable=True)
    branch = Column(String(100), nullable=True)
    balance = Column(Float, default=0.0)
    overdraft_limit = Column(Float, default=0.0)  # Ek hesap limiti
    currency = Column(String(3), default='TRY')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship('User', back_populates='bank_accounts')
    transactions = relationship('BankTransaction', back_populates='bank_account')
    invoices = relationship('Invoice', back_populates='bank_account')
    all_transactions = relationship('Transaction', back_populates='bank_account')


class Cari(Base):
    __tablename__ = 'caris'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(150), nullable=False)
    cari_type = Column(String(20), default='MÜŞTERİ')  # MÜŞTERİ, TEDARİKÇİ, HER İKİSİ
    tax_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship('User', back_populates='caris')
    invoices = relationship('Invoice', back_populates='cari')
    transactions = relationship('Transaction', back_populates='cari')


class InvoiceType(str, enum.Enum):
    GELEN = 'GELEN'
    GIDEN = 'GIDEN'


class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    cari_id = Column(Integer, ForeignKey('caris.id'), nullable=False)
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=True)
    
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    invoice_type = Column(Enum(InvoiceType), nullable=False)
    
    amount = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    description = Column(Text, nullable=True)
    paid_amount = Column(Float, default=0.0)
    status = Column(Enum('DRAFT', 'SENT', 'PARTIALLY_PAID', 'PAID', 'CANCELLED'), default='DRAFT')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship('User', back_populates='invoices')
    cari = relationship('Cari', back_populates='invoices')
    bank_account = relationship('BankAccount', back_populates='invoices')
    line_items = relationship('InvoiceLineItem', back_populates='invoice', cascade='all, delete-orphan')


class InvoiceLineItem(Base):
    __tablename__ = 'invoice_line_items'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    invoice = relationship('Invoice', back_populates='line_items')


class BankTransaction(Base):
    __tablename__ = 'bank_transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=True)
    
    transaction_date = Column(DateTime, default=datetime.now)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum('INCOME', 'EXPENSE'), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    
    user = relationship('User', back_populates='transactions')
    bank_account = relationship('BankAccount', back_populates='transactions')


class Report(Base):
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    report_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    generated_at = Column(DateTime, default=datetime.now)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    data = Column(Text, nullable=True)
    
    user = relationship('User', back_populates='reports')


class CreditCard(Base):
    __tablename__ = 'credit_cards'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    card_name = Column(String(100), nullable=False)  # Örn: "İş Bankası Kredi Kartı"
    card_number_last4 = Column(String(4), nullable=False)  # Son 4 hane
    card_holder = Column(String(100), nullable=False)
    bank_name = Column(String(100), nullable=False)
    card_limit = Column(Float, default=0.0)
    current_debt = Column(Float, default=0.0)
    available_limit = Column(Float, default=0.0)
    closing_day = Column(Integer, default=1)  # Hesap kesim günü
    due_day = Column(Integer, default=15)  # Son ödeme günü
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship('User', back_populates='credit_cards')
    transactions = relationship('Transaction', back_populates='credit_card')


class TransactionType(str, enum.Enum):
    GIDER = 'GIDER'  # Giden
    GELIR = 'GELIR'  # Gelen
    KESILEN_FATURA = 'KESILEN_FATURA'
    GELEN_FATURA = 'GELEN_FATURA'
    KREDI_ODEME = 'KREDI_ODEME'
    KREDI_KARTI_ODEME = 'KREDI_KARTI_ODEME'
    KREDI_CEKIMI = 'KREDI_CEKIMI'
    KREDI_KARTI_ODEME_ALMA = 'KREDI_KARTI_ODEME_ALMA'
    EK_HESAP_FAIZLERI = 'EK_HESAP_FAIZLERI'
    KREDI_DOSYA_MASRAFI = 'KREDI_DOSYA_MASRAFI'
    EKSPERTIZ_UCRETI = 'EKSPERTIZ_UCRETI'


class PaymentMethod(str, enum.Enum):
    NAKIT = 'NAKIT'
    BANKA = 'BANKA'
    KREDI_KARTI = 'KREDI_KARTI'
    CARI = 'CARI'


class Transaction(Base):
    """Tüm işlemleri yöneten ana tablo"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # İşlem detayları
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    # İlişkili hesaplar (hangisi kullanıldıysa)
    cari_id = Column(Integer, ForeignKey('caris.id'), nullable=True)
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=True)
    credit_card_id = Column(Integer, ForeignKey('credit_cards.id'), nullable=True)
    
    # Müşteri/Tedarikçi bilgisi
    customer_name = Column(String(200), nullable=False)  # MÜŞTERİ ÜNVANI
    
    # İşlem açıklaması ve konu
    description = Column(Text, nullable=False)  # AÇIKLAMA
    subject = Column(String(200), nullable=True)  # KONU
    
    # Ödeme şekli
    payment_type = Column(String(100), nullable=True)  # ÖDEME ŞEKLİ
    
    # Tutarlar
    amount = Column(Float, nullable=False)  # TUTAR
    person = Column(String(100), nullable=True)  # ÖDEYEN KİŞİ
    
    # Ek bilgiler
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # İlişkiler
    user = relationship('User', back_populates='all_transactions')
    cari = relationship('Cari', back_populates='transactions')
    bank_account = relationship('BankAccount', back_populates='all_transactions')
    credit_card = relationship('CreditCard', back_populates='transactions')
