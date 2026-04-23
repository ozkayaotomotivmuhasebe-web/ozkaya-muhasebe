import re
import shutil

# ============================================================
# Fix recycle_bin_service.py
# ============================================================
path = r'c:\Users\aryam\OneDrive\Desktop\BURAK\ÖZKAYA\src\services\recycle_bin_service.py'
shutil.copy2(path, path + '.bak')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add format_tr import after the existing imports
old_import = 'from src.database.models import ('
new_import = 'from src.utils.helpers import format_tr\nfrom src.database.models import ('
content = content.replace(old_import, new_import, 1)

# Replace :,.2f ₺ patterns
content = re.sub(r'\{([^{}:]+):,\.2f\} ₺', r'{format_tr(\1)} ₺', content)
content = re.sub(r'\{([^{}:]+):,\.0f\} ₺', r'{format_tr(\1, 0)} ₺', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('recycle_bin_service.py: done')

# ============================================================
# Fix advanced_bank_import_dialog.py
# ============================================================
path2 = r'c:\Users\aryam\OneDrive\Desktop\BURAK\ÖZKAYA\src\ui\dialogs\advanced_bank_import_dialog.py'
shutil.copy2(path2, path2 + '.bak')
with open(path2, 'r', encoding='utf-8') as f:
    content2 = f.read()

# Add format_tr import
old_import2 = 'from src.services.transaction_service import TransactionService'
new_import2 = 'from src.utils.helpers import format_tr\nfrom src.services.transaction_service import TransactionService'
content2 = content2.replace(old_import2, new_import2, 1)

# Replace :,.2f ₺ patterns
content2 = re.sub(r'\{([^{}:]+):,\.2f\} ₺', r'{format_tr(\1)} ₺', content2)
content2 = re.sub(r'\{([^{}:]+):,\.0f\} ₺', r'{format_tr(\1, 0)} ₺', content2)

with open(path2, 'w', encoding='utf-8') as f:
    f.write(content2)
print('advanced_bank_import_dialog.py: done')

# ============================================================
# Fix kira_takip.py - line 278 missing replace
# ============================================================
path3 = r'c:\Users\aryam\OneDrive\Desktop\BURAK\ÖZKAYA\src\ui\kira_takip.py'
shutil.copy2(path3, path3 + '.bak')
with open(path3, 'r', encoding='utf-8') as f:
    content3 = f.read()

# Fix line 278: add .replace(",",".") to first string
old_ozet = (
    '            f"<b>Toplam Ödenen:</b> ₺{toplam_odenen:,.0f}"\n'
    '            f"&nbsp;&nbsp;|&nbsp;&nbsp;<b>Bekleyen/Gecikmiş:</b> ₺{toplam_bekleyen:,.0f}".replace(",",".")'
)
new_ozet = (
    '            f"<b>Toplam Ödenen:</b> ₺{toplam_odenen:,.0f}".replace(",",".")\n'
    '            + f"&nbsp;&nbsp;|&nbsp;&nbsp;<b>Bekleyen/Gecikmiş:</b> ₺{toplam_bekleyen:,.0f}".replace(",",".")'
)
if old_ozet in content3:
    content3 = content3.replace(old_ozet, new_ozet)
    print('kira_takip.py: fixed ozet label')
else:
    print('kira_takip.py: ozet pattern not found - checking...')
    # Try to find it
    idx = content3.find('Toplam Ödenen:</b> ₺{toplam_odenen')
    if idx >= 0:
        print(f'  Found at char {idx}: {repr(content3[idx-10:idx+80])}')

with open(path3, 'w', encoding='utf-8') as f:
    f.write(content3)
print('kira_takip.py: done')
