from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                           QTableWidget, QTableWidgetItem, QComboBox, QMessageBox,
                           QFileDialog, QSpinBox, QCheckBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from src.services.transaction_service import TransactionService
from src.services.cari_service import CariService
from src.database.models import TransactionType, PaymentMethod
from datetime import datetime
import openpyxl
from difflib import SequenceMatcher
import re


class BankStatementImportDialog(QDialog):
    """Banka Ekstresini İthal Et - Otomatik Müşteri Eşleşmesi ile"""
    
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.transactions_preview = []
        self.caris = CariService.get_caris(user_id)
        
        self.setWindowTitle("Banka Ekstresini İthal Et")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(1200, 700)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Arayüz elemanlarını oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("📊 Banka Ekstresini İthal Et")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Dosya seçimi
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Dosya seçilmedi...")
        self.file_label.setStyleSheet("color: #666;")
        file_layout.addWidget(self.file_label)
        
        btn_browse = QPushButton("📁 Excel Dosyası Seç")
        btn_browse.setMinimumHeight(35)
        btn_browse.clicked.connect(self.select_file)
        file_layout.addWidget(btn_browse)
        file_layout.addStretch()
        layout.addLayout(file_layout)
        layout.addSpacing(10)
        
        # Seçenekler
        options_group = QGroupBox("İthal Seçenekleri")
        options_layout = QFormLayout()
        
        self.sheet_name_input = QSpinBox()
        self.sheet_name_input.setMinimum(1)
        self.sheet_name_input.setValue(1)
        options_layout.addRow("Excel Sayfası Numarası:", self.sheet_name_input)
        
        self.start_row_input = QSpinBox()
        self.start_row_input.setMinimum(1)
        self.start_row_input.setValue(2)  # Varsayılan başlık var
        options_layout.addRow("Başlangıç Satırı (başlık atla):", self.start_row_input)
        
        self.auto_match_check = QCheckBox("Müşteri Adlarını Otomatik Eşleştir")
        self.auto_match_check.setChecked(True)
        options_layout.addRow("Seçenekler:", self.auto_match_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        layout.addSpacing(10)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Tarih", "İşlem Adı", "Tutar (₺)", "Tür", "Müşteri/Cari", "Kategori", "Açıklama"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 180)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 200)
        layout.addWidget(self.table)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        btn_import = QPushButton("📥 İthal Et ve Önizle")
        btn_import.setMinimumHeight(40)
        btn_import.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        btn_import.clicked.connect(self.import_excel)
        btn_layout.addWidget(btn_import)
        
        btn_save = QPushButton("💾 Tümünü İşlem Olarak Kaydet")
        btn_save.setMinimumHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_save.clicked.connect(self.save_all_transactions)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ İptal")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def select_file(self):
        """Excel dosyası seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Dosyaları (*.xlsx *.xls)"
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(file_path.split("\\")[-1])
            self.file_label.setStyleSheet("color: #333;")
    
    def _normalize_turkish_text(self, text):
        if not text:
            return ""
        mapping = {
            'ç': 'c', 'Ç': 'c', 'ğ': 'g', 'Ğ': 'g', 'ı': 'i', 'I': 'i',
            'İ': 'i', 'ö': 'o', 'Ö': 'o', 'ş': 's', 'Ş': 's', 'ü': 'u', 'Ü': 'u'
        }
        result = str(text).strip().lower()
        for old_char, new_char in mapping.items():
            result = result.replace(old_char, new_char)
        result = re.sub(r'[^a-z0-9\s]', ' ', result)
        result = re.sub(r'\s+', ' ', result).strip()
        return result

    def _extract_meaningful_tokens(self, text):
        stop_words = {
            'bank', 'banka', 'hesap', 'hesabi', 'sube', 'subesi', 'odeme', 'odemesi',
            'kredi', 'kart', 'karti', 'havale', 'eft', 'swift', 'islem', 'masraf',
            'komisyon', 'faiz', 'taksit', 'nakit', 'virman', 'para', 'gonderim',
            'ltd', 'limited', 'sti', 'sirketi', 'anonim', 'as', 'tic', 'ticaret', 'san', 'sanayi'
        }
        normalized = self._normalize_turkish_text(text)
        return [token for token in normalized.split() if len(token) >= 2 and token not in stop_words]

    def find_best_cari_match(self, transaction_name):
        """Sadece yüksek güvenli müşteri eşleşmelerini otomatik seç."""
        normalized_transaction = self._normalize_turkish_text(transaction_name)
        transaction_tokens = set(self._extract_meaningful_tokens(transaction_name))

        if not normalized_transaction or not transaction_tokens:
            return None

        best_match = None
        best_score = 0.0
        second_best_score = 0.0

        for cari in self.caris:
            cari_name = (getattr(cari, 'name', '') or '').strip()
            if not cari_name:
                continue

            normalized_cari = self._normalize_turkish_text(cari_name)
            cari_tokens = set(self._extract_meaningful_tokens(cari_name))
            if not cari_tokens:
                continue

            if normalized_transaction == normalized_cari:
                return cari

            if len(cari_tokens) == 1:
                continue

            common_tokens = transaction_tokens & cari_tokens
            if common_tokens == cari_tokens:
                return cari
            if len(common_tokens) < 2:
                continue

            token_score = len(common_tokens) / len(cari_tokens)
            similarity = SequenceMatcher(None, normalized_transaction, normalized_cari).ratio()
            combined_score = (token_score * 0.75) + (similarity * 0.25)

            if combined_score > best_score:
                second_best_score = best_score
                best_score = combined_score
                best_match = cari
            elif combined_score > second_best_score:
                second_best_score = combined_score

        if best_score >= 0.75 and (best_score - second_best_score) >= 0.10:
            return best_match

        return None
    
    def import_excel(self):
        """Excel dosyasını oku ve işlem önizlemesi oluştur"""
        if not hasattr(self, 'file_path'):
            QMessageBox.warning(self, "Uyarı", "Lütfen önce Excel dosyası seçin!")
            return
        
        try:
            wb = openpyxl.load_workbook(self.file_path)
            ws = wb.worksheets[self.sheet_name_input.value() - 1]
            
            self.transactions_preview = []
            start_row = self.start_row_input.value()
            
            for row_idx, row in enumerate(ws.iter_rows(
                min_row=start_row, 
                values_only=False
            ), start=start_row):
                if row_idx > start_row + 1000:  # Max 1000 satır
                    break
                
                try:
                    # Excel'deki hücreleri oku
                    date_cell = row[0].value if len(row) > 0 else None
                    name_cell = row[1].value if len(row) > 1 else None
                    amount_cell = row[2].value if len(row) > 2 else None
                    
                    if not all([date_cell, name_cell, amount_cell]):
                        continue
                    
                    # Tarih formatlama
                    if isinstance(date_cell, str):
                        trans_date = datetime.strptime(date_cell, "%d.%m.%Y").date()
                    else:
                        trans_date = date_cell
                    
                    # Tutar negatifse gider, pozitifse gelir
                    amount = float(amount_cell)
                    trans_type = "GIDER" if amount < 0 else "GELIR"
                    amount = abs(amount)
                    
                    # Otomatik müşteri eşleştirmesi
                    matched_cari = None
                    if self.auto_match_check.isChecked():
                        matched_cari = self.find_best_cari_match(str(name_cell))
                    
                    transaction = {
                        'date': trans_date,
                        'name': str(name_cell),
                        'amount': amount,
                        'type': trans_type,
                        'cari': matched_cari,
                        'category': 'NAKIT',
                    }
                    self.transactions_preview.append(transaction)
                
                except Exception as e:
                    print(f"Satır {row_idx} hatası: {e}")
                    continue
            
            # Tabloyu güncelle
            self.populate_table()
            QMessageBox.information(self, "Başarılı", 
                f"{len(self.transactions_preview)} işlem yüklendi!\n"
                f"Lütfen müşteri eşleştirmelerini kontrol edin.")
        
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel okuma hatası: {str(e)}")
    
    def populate_table(self):
        """Tabloyu işlem verileriyle doldur"""
        self.table.setRowCount(len(self.transactions_preview))
        for row_idx, trans in enumerate(self.transactions_preview):
            # Tarih
            self.table.setItem(row_idx, 0, QTableWidgetItem(trans['date'].strftime("%d.%m.%Y")))

            # İşlem Adı
            self.table.setItem(row_idx, 1, QTableWidgetItem(trans['name']))

            # Tutar
            amount_item = QTableWidgetItem(f"{trans['amount']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 2, amount_item)

            # Tür (Gelir/Gider)
            type_combo = QComboBox()
            type_combo.addItems(["GELIR", "GIDER"])
            type_combo.setCurrentText(trans['type'])
            self.table.setCellWidget(row_idx, 3, type_combo)

            # Müşteri/Cari Seçimi
            cari_combo = QComboBox()
            cari_combo.addItem("-- Seçiniz --", None)
            for cari in self.caris:
                cari_combo.addItem(f"{cari.name} ({cari.cari_type})", cari.id)

            if trans['cari']:
                index = cari_combo.findData(trans['cari'].id)
                if index >= 0:
                    cari_combo.setCurrentIndex(index)
                    # Başarılı eşleştirmeyi yeşille
                    cari_combo.setStyleSheet("background-color: #c8e6c9;")

            self.table.setCellWidget(row_idx, 4, cari_combo)

            # Kategori
            cat_combo = QComboBox()
            cat_combo.addItems(["NAKIT", "BANKA", "KREDI_KARTI"])
            cat_combo.setCurrentText(trans['category'])
            self.table.setCellWidget(row_idx, 5, cat_combo)

            # Açıklama
            self.table.setItem(row_idx, 6, QTableWidgetItem(trans['name']))
    
    def save_all_transactions(self):
        """Tüm işlemleri kaydet"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek işlem yok!")
            return

        try:
            success_count = 0
            error_list = []

            for row_idx in range(self.table.rowCount()):
                try:
                    # Tablodan verileri oku
                    date_text = self.table.item(row_idx, 0).text()
                    name_text = self.table.item(row_idx, 1).text()
                    amount_text = self.table.item(row_idx, 2).text()

                    type_combo = self.table.cellWidget(row_idx, 3)
                    trans_type = TransactionType[type_combo.currentText()]

                    cari_combo = self.table.cellWidget(row_idx, 4)
                    cari_id = cari_combo.currentData()

                    # Tarih parse et
                    trans_date = datetime.strptime(date_text, "%d.%m.%Y").date()

                    # Tutar
                    amount = float(amount_text.replace(",", "").replace(".", ""))

                    # İşlem oluştur
                    transaction, msg = TransactionService.create_transaction(
                        user_id=self.user_id,
                        transaction_date=trans_date,
                        transaction_type=trans_type,
                        payment_method=PaymentMethod.BANKA,
                        customer_name=name_text,
                        description=f"Banka ekstresinden ithal: {name_text}",
                        amount=amount,
                        cari_id=cari_id,
                        bank_account_id=None,
                    )

                    if transaction:
                        success_count += 1
                    else:
                        error_list.append(f"Satır {row_idx + 1}: {msg}")

                except Exception as e:
                    error_list.append(f"Satır {row_idx + 1}: {str(e)}")

            # Sonuç mesajı
            result_msg = f"✓ {success_count} işlem başarıyla kaydedildi!"

            if error_list:
                result_msg += f"\n\n⚠️ {len(error_list)} hatalar oluştu:\n"
                result_msg += "\n".join(error_list[:5])  # İlk 5 hatayı göster

            QMessageBox.information(self, "İşlem Tamamlandı", result_msg)

            if success_count > 0:
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kaydetme hatası: {str(e)}")
