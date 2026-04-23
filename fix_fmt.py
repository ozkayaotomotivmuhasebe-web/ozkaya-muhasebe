path = r'c:\Users\aryam\OneDrive\Desktop\BURAK\ÖZKAYA\src\ui\main_window.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix broken fmt function (two occurrences)
old = '            return f"{format_tr(v)} ₺".replace(",", "X").replace(".", ",").replace("X", ".")'
new = '            return f"{format_tr(v)} ₺"'
count = content.count(old)
content = content.replace(old, new)
print(f'Fixed {count} broken fmt functions')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
