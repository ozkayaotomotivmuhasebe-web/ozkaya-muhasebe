"""Yardımcı fonksiyonlar"""

from datetime import datetime, date


def format_tr(value: float, decimals: int = 2) -> str:
    """Türkçe sayı formatı: 1.234.567,89"""
    try:
        val_float = float(value)
    except (ValueError, TypeError):
        return str(value)

    s = f"{val_float:.{decimals}f}"
    integer_part, decimal_part = s.split('.')
    sign = ""
    if integer_part.startswith('-'):
        sign = "-"
        integer_part = integer_part[1:]

    groups = []
    while integer_part:
        groups.append(integer_part[-3:])
        integer_part = integer_part[:-3]
    grouped_integer = '.'.join(reversed(groups)) if groups else "0"

    return f"{sign}{grouped_integer},{decimal_part}"


def format_currency_tr(amount: float, currency: str = "TRY") -> str:
    """Türkçe para formatı: 1.234.567,89 ₺"""
    symbols = {
        "TRY": "₺",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    symbol = symbols.get(currency, currency)
    formatted_number = format_tr(amount)
    return f"{formatted_number} {symbol}".strip()

def format_date(date_obj: date) -> str:
    """Tarihi formatla"""
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    return date_obj.strftime("%d.%m.%Y")

def calculate_tax(amount: float, tax_rate: float) -> float:
    """Vergi hesapla"""
    return amount * (tax_rate / 100)
