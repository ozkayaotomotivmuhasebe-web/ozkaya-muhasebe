"""Yardımcı fonksiyonlar"""

from datetime import datetime, date

def format_currency(amount: float, currency: str = "TRY") -> str:
    """Para birimini formatla"""
    symbols = {
        "TRY": "₺",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    symbol = symbols.get(currency, currency)
    return f"{amount:,.2f} {symbol}"

def format_date(date_obj: date) -> str:
    """Tarihi formatla"""
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    return date_obj.strftime("%d.%m.%Y")

def calculate_tax(amount: float, tax_rate: float) -> float:
    """Vergi hesapla"""
    return amount * (tax_rate / 100)
