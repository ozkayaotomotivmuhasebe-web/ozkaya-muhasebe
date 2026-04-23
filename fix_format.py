import re
import shutil

actual_path = r'c:\Users\aryam\OneDrive\Desktop\BURAK\ÖZKAYA\src\ui\main_window.py'

# Backup first
shutil.copy2(actual_path, actual_path + '.bak')

with open(actual_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ============================================================
# STEP 1: Replace display number format patterns
# f"{expr:,.2f} ₺"  ->  f"{format_tr(expr)} ₺"
# f"{expr:,.0f} ₺"  ->  f"{format_tr(expr, 0)} ₺"
# ============================================================
c1 = re.sub(r'\{([^{}:]+):,\.2f\} ₺', r'{format_tr(\1)} ₺', content)
n_22 = len(re.findall(r'\{[^{}:]+:,\.2f\} ₺', content))
c2 = re.sub(r'\{([^{}:]+):,\.0f\} ₺', r'{format_tr(\1, 0)} ₺', c1)
n_00 = len(re.findall(r'\{[^{}:]+:,\.0f\} ₺', content))
print(f'Step 1a: {n_22} x ":,.2f ₺" replaced with format_tr')
print(f'Step 1b: {n_00} x ":,.0f ₺" replaced with format_tr')

# ============================================================
# STEP 2: Fix Excel cell assignments - change string to float
# ws[f'X{row}'] = f"{format_tr(expr)} ₺"  ->  ws[f'X{row}'] = float(expr)
# ============================================================
excel_cell_pat = re.compile(
    r"(ws\[f'[A-Z]\{row\}'\]) = f\"\{format_tr\(([^)]+)\)\} ₺\""
)
matches = excel_cell_pat.findall(c2)
c3 = excel_cell_pat.sub(r'\1 = float(\2)', c2)
print(f'Step 2: {len(matches)} Excel cell string→float replacements')

# ============================================================
# STEP 3: Fix format_currency_tr in Excel cell assignments
# ws[f'X{row}'] = format_currency_tr(expr)  ->  ws[f'X{row}'] = float(expr)
# ============================================================
excel_fct_pat = re.compile(
    r"(ws\[f'[A-Z]\{row\}'\]) = format_currency_tr\(([^)]+)\)"
)
matches3 = excel_fct_pat.findall(c3)
c4 = excel_fct_pat.sub(r'\1 = float(\2)', c3)
print(f'Step 3: {len(matches3)} format_currency_tr→float replacements')

# ============================================================
# STEP 4: Fix bank balance without lira sign in Excel
# ws[f'C{row}'] = f"{bank['balance']:,.2f}"  ->  ws[f'C{row}'] = float(bank['balance'])
# ============================================================
old_bank = """ws[f'C{row}'] = f\"{bank['balance']:,.2f}\""""
new_bank = """ws[f'C{row}'] = float(bank['balance'])"""
c5 = c4.replace(old_bank, new_bank)
n_bank = c4.count(old_bank)
print(f'Step 4: {n_bank} bank balance string→float replacements')

with open(actual_path, 'w', encoding='utf-8') as f:
    f.write(c5)
print(f'Done. Original: {original_len}, New: {len(c5)}')
