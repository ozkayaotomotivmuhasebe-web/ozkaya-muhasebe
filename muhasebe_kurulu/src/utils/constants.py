"""Utils modülü"""
from datetime import date

# TURKISH FIXED HOLIDAYS (sabit tatiller)
# Format: (month, day)
TURKISH_FIXED_HOLIDAYS = [
    (1, 1),      # Yılbaşı / New Year
    (4, 23),     # Ulusal Egemenlik ve Çocuk Bayramı / National Sovereignty Day
    (5, 1),      # Emek ve Dayanışma Günü / Labor Day
    (5, 19),     # Gençlik ve Spor Bayramı / Youth and Sports Day
    (7, 15),     # Demokrasi ve Milli Birlik Günü / Democracy and National Unity Day
    (8, 30),     # Zafer Bayramı / Victory Day
    (10, 29),    # Cumhuriyet Bayramı / Republic Day
]

# Variable holidays (değişken tatiller) - These are approximate and should be updated yearly
# For 2024-2026, add specific dates here
TURKISH_VARIABLE_HOLIDAYS_2024_2026 = [
    # Ramazan Bayramı 2024
    date(2024, 4, 10),
    date(2024, 4, 11),
    date(2024, 4, 12),
    # Kurban Bayramı 2024
    date(2024, 6, 15),
    date(2024, 6, 16),
    date(2024, 6, 17),
    date(2024, 6, 18),
    
    # Ramazan Bayramı 2025
    date(2025, 3, 30),
    date(2025, 3, 31),
    date(2025, 4, 1),
    # Kurban Bayramı 2025
    date(2025, 6, 4),
    date(2025, 6, 5),
    date(2025, 6, 6),
    date(2025, 6, 7),
    
    # Ramazan Bayramı 2026
    date(2026, 3, 20),
    date(2026, 3, 21),
    date(2026, 3, 22),
    # Kurban Bayramı 2026
    date(2026, 5, 24),
    date(2026, 5, 25),
    date(2026, 5, 26),
    date(2026, 5, 27),
]
