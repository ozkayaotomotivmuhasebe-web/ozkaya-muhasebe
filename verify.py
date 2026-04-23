import re

path = r'c:\Users\aryam\OneDrive\Desktop\BURAK\ÖZKAYA\src\ui\main_window.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Count remaining English format patterns
eng_fmt = re.findall(r':,\.\d+f\}.*?\u20ba', content)
print(f'Remaining English format patterns in src/: {len(eng_fmt)}')
for m in eng_fmt[:5]:
    print(' ', m)

# Count broken fmt replace chains
broken_fmt = re.findall(r'format_tr.*replace.*replace', content)
print(f'Broken fmt replace chains: {len(broken_fmt)}')

print('Verification done.')
