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
    can_view_transactions = Column(Boolean, default=False)
    can_view_invoices = Column(Boolean, default=True)
    can_view_caris = Column(Boolean, default=True)
    can_view_cari_extract = Column(Boolean, default=False)
    can_view_banks = Column(Boolean, default=True)
    can_view_credit_cards = Column(Boolean, default=True)
    can_view_loans = Column(Boolean, default=True)
    can_view_reports = Column(Boolean, default=False)
    can_view_payroll = Column(Boolean, default=True)
    can_view_employees = Column(Boolean, default=True)
    can_view_bulk_payroll = Column(Boolean, default=True)
    can_view_payroll_records = Column(Boolean, default=True)
    can_view_settings = Column(Boolean, default=True)
    can_view_admin_panel = Column(Boolean, default=False)
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
    loans = relationship('Loan', back_populates='user')


class UserSetting(Base):
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship('User')


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
    all_transactions = relationship('Transaction', back_populates='bank_account', foreign_keys='Transaction.bank_account_id')
    destination_transactions = relationship('Transaction', back_populates='destination_bank_account', foreign_keys='Transaction.destination_bank_account_id')


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
    # Ortak limit: Bu kart başka bir kartın limitini paylaşıyorsa parent kartın id'si
    parent_card_id = Column(Integer, ForeignKey('credit_cards.id'), nullable=True)
    
    user = relationship('User', back_populates='credit_cards')
    transactions = relationship('Transaction', back_populates='credit_card')
    # Ek kartlar (aynı limiti paylaşan)
    child_cards = relationship('CreditCard', foreign_keys='CreditCard.parent_card_id',
                               backref='parent_card', lazy='dynamic')


class Loan(Base):
    """Kredi Yönetim Tablosu"""
    __tablename__ = 'loans'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    loan_name = Column(String(100), nullable=False)  # Örn: "Banka X - İpotekli Kredi"
    bank_name = Column(String(100), nullable=False)  # Kredi veren banka
    loan_type = Column(String(50), nullable=False)  # Örn: "İPOTEK", "TAŞIT", "TÜKETICI"
    loan_amount = Column(Float, nullable=False)  # Alınan toplam kredi
    remaining_balance = Column(Float, nullable=False)  # Kalan bakiye
    monthly_payment = Column(Float, default=0.0)  # Aylık taksit tutarı
    interest_rate = Column(Float, default=0.0)  # Faiz oranı (%)
    start_date = Column(Date, nullable=False)  # Kredi başlama tarihi
    end_date = Column(Date, nullable=True)  # Kredi bitiş (vadesini doluş tarihi)
    due_day = Column(Integer, default=15)  # Ödeme günü (ayın kaçıncı günü)
    total_paid = Column(Float, default=0.0)  # Toplam ödenen
    paid_installments = Column(Integer, default=0)  # Ödenen taksit sayısı
    total_installments = Column(Integer, nullable=True)  # Toplam taksit sayısı
    status = Column(String(20), default='AKTIF')  # AKTIF, KAPATILDI, IPTAL
    notes = Column(Text, nullable=True)  # Not/açıklama
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship('User', back_populates='loans')


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
    TRANSFER = 'TRANSFER'  # Banka hesapları arası transfer
    NAKIT_CEKIMI = 'NAKIT_CEKIMI'  # Bankadan nakit çekim
    NAKIT_YATIRIMI = 'NAKIT_YATIRIMI'  # Bankaya nakit yatırım


class PaymentMethod(str, enum.Enum):
    NAKIT = 'NAKIT'
    BANKA = 'BANKA'
    KREDI_KARTI = 'KREDI_KARTI'
    CARI = 'CARI'
    TRANSFER = 'TRANSFER'  # Hesaptan hesaba transfer


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
    destination_bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=True)  # Transfer için hedef
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
    bank_account = relationship('BankAccount', back_populates='all_transactions', foreign_keys='Transaction.bank_account_id')
    destination_bank_account = relationship('BankAccount', back_populates='destination_transactions', foreign_keys='Transaction.destination_bank_account_id')
    credit_card = relationship('CreditCard', back_populates='transactions')


class Employee(Base):
    """Çalışan bilgileri"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    start_date = Column(Date, nullable=True)
    
    # Varsayılan bordro değerleri
    gross_salary = Column(Float, default=0.0)
    overtime_rate = Column(Float, default=150.0)  # %150 mesai
    sgk_rate = Column(Float, default=14.0)
    unemployment_rate = Column(Float, default=1.0)
    income_tax_rate = Column(Float, default=15.0)
    stamp_tax_rate = Column(Float, default=0.759)
    child_count = Column(Integer, default=0)  # Bakmakla yükümlü çocuk sayısı
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
