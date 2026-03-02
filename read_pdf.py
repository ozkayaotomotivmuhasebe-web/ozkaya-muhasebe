import pdfplumber

pdf_file = r'ocak maaş bordrosu (1).pdf'
with pdfplumber.open(pdf_file) as pdf:
    print(f"=== PDF SAYFA SAYISI: {len(pdf.pages)} ===\n")
    
    for page_num, page in enumerate(pdf.pages):
        print(f"\n{'='*80}")
        print(f"SAYFA {page_num + 1}")
        print(f"{'='*80}\n")
        
        # Metin içeriği
        text = page.extract_text()
        print("METIN İÇERİĞİ:")
        print(text)
        
        # Tablolar
        tables = page.extract_tables()
        if tables:
            print(f"\n\nTABLO SAYISI: {len(tables)}")
            for t_idx, table in enumerate(tables):
                print(f"\n--- TABLO {t_idx + 1} ---")
                for r_idx, row in enumerate(table):
                    print(row)
