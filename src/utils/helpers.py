"""Yardımcı fonksiyonlar"""

from datetime import datetime, date, timedelta
from src.utils.constants import TURKISH_FIXED_HOLIDAYS, TURKISH_VARIABLE_HOLIDAYS_2024_2026


def format_tr(value: float, decimals: int = 2) -> str:
    """Türkçe sayı formatı: 1.234.567,89"""
    try:
        val_float = float(value)
    except (ValueError, TypeError):
        return str(value)

    s = f"{val_float:.{decimals}f}"
    parts = s.split('.')
    if len(parts) == 2:
        integer_part, decimal_part = parts
    else:
        integer_part, decimal_part = parts[0], ''
    sign = ""
    if integer_part.startswith('-'):
        sign = "-"
        integer_part = integer_part[1:]

    groups = []
    while integer_part:
        groups.append(integer_part[-3:])
        integer_part = integer_part[:-3]
    grouped_integer = '.'.join(reversed(groups)) if groups else "0"

    if decimal_part:
        return f"{sign}{grouped_integer},{decimal_part}"
    return f"{sign}{grouped_integer}"


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


def is_turkish_holiday(check_date: date) -> bool:
    """
    Türkiye'nin resmi tatil günü mü kontrol et
    Hem sabit tatilleri (Yılbaşı, Kurban Bayramı vb.) hem de değişken tatilleri kontrol eder
    """
    if not isinstance(check_date, date):
        if isinstance(check_date, datetime):
            check_date = check_date.date()
        else:
            return False
    
    # Check fixed holidays
    for month, day in TURKISH_FIXED_HOLIDAYS:
        if check_date.month == month and check_date.day == day:
            return True
    
    # Check variable holidays
    if check_date in TURKISH_VARIABLE_HOLIDAYS_2024_2026:
        return True
    
    return False


def is_business_day(check_date: date) -> bool:
    """
    İş günü mü kontrol et (hafta sonu ve tatillerden hariç)
    0=Monday, 1=Tuesday, ..., 5=Saturday, 6=Sunday
    """
    if not isinstance(check_date, date):
        if isinstance(check_date, datetime):
            check_date = check_date.date()
        else:
            return False
    
    # Check weekends (Saturday=5, Sunday=6)
    if check_date.weekday() >= 5:
        return False
    
    # Check holidays
    if is_turkish_holiday(check_date):
        return False
    
    return True


def adjust_to_business_day(target_date: date, forward: bool = True) -> date:
    """
    Tarihi iş gününe ayarla
    Eğer hafta sonu veya tatil günü ise, sonraki/önceki iş gününe kaydır
    
    Args:
        target_date: Ayarlanacak tarih
        forward: True ise ileri, False ise geriye kaydır
    
    Returns:
        Ayarlanmış iş günü
    """
    if not isinstance(target_date, date):
        if isinstance(target_date, datetime):
            target_date = target_date.date()
        else:
            return target_date
    
    current_date = target_date
    
    if forward:
        # İleri kaydırma - sonraki iş gününü bul
        while not is_business_day(current_date):
            current_date += timedelta(days=1)
    else:
        # Geriye kaydırma - önceki iş gününü bul
        while not is_business_day(current_date):
            current_date -= timedelta(days=1)
    
    return current_date
