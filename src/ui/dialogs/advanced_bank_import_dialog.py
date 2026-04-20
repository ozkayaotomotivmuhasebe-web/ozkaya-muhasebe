from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QTableWidget, QTableWidgetItem, QComboBox, QMessageBox,
                           QFileDialog, QCheckBox, QTabWidget, QGroupBox, QFormLayout, QHeaderView,
                           QDateEdit, QSpinBox, QLineEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from src.services.transaction_service import TransactionService
from src.services.cari_service import CariService
from src.services.bank_service import BankService
from src.services.credit_card_service import CreditCardService
from src.database.models import TransactionType, PaymentMethod, Loan
from src.database.db import SessionLocal
from src.ui.dialogs.column_mapper_dialog import ColumnMapperDialog
from src.ui.dialogs.quick_rules_dialog import QuickRulesDialog
from src.ui.dialogs.duplicate_transactions_dialog import DuplicateTransactionsDialog
from datetime import datetime
import openpyxl
from difflib import SequenceMatcher
import re


class AdvancedBankImportDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.quick_rules = []  # Hızlı kurallar her zaman tanımlı olsun
        self.bank_accounts = BankService.get_accounts(self.user_id)
        self.credit_cards = CreditCardService.get_active_cards(self.user_id)
        self.loans = self._get_active_loans()
        self.setWindowTitle("Gelişmiş Banka/Kredi Kartı Excel Aktarımı")
        self.setGeometry(200, 100, 1200, 700)
        self.setMinimumSize(1000, 600)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        # Başlık
        title = QLabel("🏦 Banka/Kredi Kartı Ekstresini İthal Et")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)
        # Adım göstergesi
        steps_label = QLabel("Adım 1️⃣ Dosya Seç → Adım 2️⃣ Sütunları Eşleştir → Adım 3️⃣ Hızlı Kurallar → Adım 4️⃣ Önizle & Düzenle → Adım 5️⃣ Kaydet")
        steps_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 9px;")
        layout.addWidget(steps_label)
        layout.addSpacing(10)
        # Adım 1: Dosya seçimi & Ayarlar
        config_group = QGroupBox("Adım 1️⃣ & 2️⃣ - Dosya Seçimi ve Sütun Eşleştirmesi")
        config_layout = QVBoxLayout()
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Dosya seçilmedi...")
        self.file_label.setStyleSheet("color: #666;")
        file_layout.addWidget(self.file_label)
        btn_file = QPushButton("📁 Excel Dosyası Seç")
        btn_file.setMinimumHeight(35)
        btn_file.clicked.connect(self.step1_select_file)
        file_layout.addWidget(btn_file)
        btn_mapper = QPushButton("📋 Sütunları Eşleştir")
        btn_mapper.setMinimumHeight(35)
        btn_mapper.clicked.connect(self.step2_map_columns)
        btn_mapper.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
        """)
        file_layout.addWidget(btn_mapper)
        file_layout.addStretch()
        config_layout.addLayout(file_layout)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        layout.addSpacing(10)
        # Adım 3: Hızlı Kurallar
        rules_group = QGroupBox("Adım 3️⃣ - Hızlı İşlem Kuralları (İsteğe Bağlı)")
        rules_layout = QHBoxLayout()
        rules_info = QLabel("Pattern matching ile müşteri adı, işlem tipi ve ödeme şeklini otomatik atayın")
        rules_info.setStyleSheet("color: #666; font-size: 9px;")
        rules_layout.addWidget(rules_info)
        btn_rules = QPushButton("⚡ Hızlı Kuralları Ayarla")
        btn_rules.setMinimumHeight(35)
        btn_rules.clicked.connect(self.step3_quick_rules)
        btn_rules.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
            }
        """)
        rules_layout.addWidget(btn_rules)
        self.rules_label = QLabel("Kural yok")
        self.rules_label.setStyleSheet("color: #999;")
        rules_layout.addWidget(self.rules_label)
        rules_layout.addStretch()
        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)
        layout.addSpacing(10)
        # Adım 4 & 5: Önizle & Düzenle & Kaydet
        preview_label = QLabel("Adım 4️⃣ - Verileri Önizle ve Düzenle:")
        preview_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(preview_label)
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(9)
        self.preview_table.setHorizontalHeaderLabels([
            "Seç", "Tarih", "İşlem Adı", "Tutar (₺)", "Tür", "Müşteri/Cari", "Ödeme Şekli", "Ödenecek Kredi", "Açıklama"
        ])
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.preview_table.setColumnWidth(0, 50)  # Checkbox
        self.preview_table.setColumnWidth(1, 100)
        self.preview_table.setColumnWidth(2, 200)
        self.preview_table.setColumnWidth(3, 100)
        self.preview_table.setColumnWidth(4, 120)
        self.preview_table.setColumnWidth(5, 180)
        self.preview_table.setColumnWidth(4, 180)
        layout.addWidget(self.preview_table)
        # Seçenekler
        options_layout = QHBoxLayout()
        self.auto_match_check = QCheckBox("✓ Otomatik Müşteri Eşleştir (Fuzzy Matching)")
        self.auto_match_check.setChecked(True)
        options_layout.addWidget(self.auto_match_check)
        # Tarih aralığı filtresi
        self.date_filter_check = QCheckBox("Tarih Aralığı Filtrele")
        self.date_filter_check.setChecked(False)
        self.date_filter_check.toggled.connect(self.toggle_date_filters)
        options_layout.addWidget(self.date_filter_check)
        self.start_date_label = QLabel("Başlangıç:")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setEnabled(False)
        options_layout.addWidget(self.start_date_label)
        options_layout.addWidget(self.start_date_edit)
        self.end_date_label = QLabel("Bitiş:")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setEnabled(False)
        options_layout.addWidget(self.end_date_label)
        options_layout.addWidget(self.end_date_edit)
        self.start_date_label.setVisible(False)
        self.start_date_edit.setVisible(False)
        self.end_date_label.setVisible(False)
        self.end_date_edit.setVisible(False)
        btn_load = QPushButton("📥 Verileri Yükle")
        btn_load.setMinimumHeight(35)
        btn_load.clicked.connect(self.step4_load_data)
        btn_load.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
        """)
        options_layout.addWidget(btn_load)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        layout.addSpacing(10)
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Tümünü Kaydet")
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
        btn_save.clicked.connect(self.step5_save)
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
    def step5_save(self):
        """Adım 5: Tümünü kaydet"""
        if self.preview_table.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek işlem yok!")
            return
        try:
            success_count = 0
            skipped_duplicates = 0
            error_list = []
            duplicate_items = []
            row_payloads = []
            for row_idx in range(self.preview_table.rowCount()):
                checkbox = self.preview_table.cellWidget(row_idx, 0)
                if checkbox is not None and not checkbox.isChecked():
                    continue  # Sadece seçili satırları kaydet
                payload, err = self._collect_preview_row_data(row_idx)
                if err:
                    error_list.append(f"Satır {row_idx + 1}: {err}")
                    continue
                row_payloads.append(payload)

            for payload in row_payloads:
                existing = TransactionService.find_duplicate_transaction(
                    self.user_id,
                    payload['trans_date'],
                    payload['amount'],
                    payload['description'],
                    customer_name=payload['name_text'],
                    person=payload.get('person')
                )
                if existing:
                    payload['is_duplicate'] = True
                    duplicate_items.append({
                        'row_key': payload['row_key'],
                        'row_label': payload.get('row_label', payload['row_key']+1),
                        'date': payload['trans_date'],
                        'customer_name': payload['name_text'],
                        'amount': payload['amount'],
                        'description': payload['description'],
                        'person': payload.get('person')
                    })

            selected_duplicates = set()
            if duplicate_items:
                dialog = DuplicateTransactionsDialog(duplicate_items, self)
                if dialog.exec_() != QDialog.Accepted:
                    return
                selected_duplicates = dialog.get_selected_row_ids()

            for payload in row_payloads:
                if payload.get('is_duplicate') and payload['row_key'] not in selected_duplicates:
                    skipped_duplicates += 1
                    continue

                cari_id = payload['cari_id']
                if not cari_id:
                    cari_id = self._find_or_create_cari_id(payload['name_text'])

                bank_account_id = payload['bank_account_id']
                credit_card_id = payload['credit_card_id']
                payment_method = payload['payment_method']
                payment_text = payload['payment_text']

                if payload['payment_mode'] == "text" and payment_text:
                    normalized_payment = self._normalize_turkish_text(payment_text)
                    if "nakit" not in normalized_payment and "cash" not in normalized_payment:
                        if payment_method == PaymentMethod.KREDI_KARTI and not credit_card_id:
                            credit_card_id = self._find_or_create_credit_card_id(payment_text)
                        elif payment_method == PaymentMethod.BANKA and not bank_account_id:
                            bank_account_id = self._find_or_create_bank_account_id(payment_text)

                transaction, msg = TransactionService.create_transaction(
                    user_id=self.user_id,
                    transaction_date=payload['trans_date'],
                    transaction_type=payload['trans_type'],
                    payment_method=payment_method,
                    customer_name=payload['name_text'],
                    description=payload['description'],
                    amount=payload['amount'],
                    cari_id=cari_id,
                    bank_account_id=bank_account_id,
                    credit_card_id=credit_card_id,
                    subject=payload['subject'],
                    payment_type=payment_text,
                    person=payload.get('person'),
                    notes=payload.get('notes'),
                )
                if transaction:
                    success_count += 1
                else:
                    error_list.append(f"Satır {payload.get('row_label', payload['row_key']+1)}: {msg}")

            result_msg = f"✓ {success_count} işlem başarıyla kaydedildi!"
            if skipped_duplicates:
                result_msg += f"\nMükerrer atlandı: {skipped_duplicates}"
            if error_list:
                result_msg += f"\n\n⚠️ {len(error_list)} hatalar oluştu:\n"
                result_msg += "\n".join(error_list[:5])
            QMessageBox.information(self, "İşlem Tamamlandı", result_msg)
            if success_count > 0:
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kaydetme hatası: {str(e)}")
    
    def step1_select_file(self):
        """Adım 1: Excel dosyasını seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Dosyaları (*.xlsx *.xls)"
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(file_path.split("\\")[-1])
            self.file_label.setStyleSheet("color: #333;")
    
    def step2_map_columns(self):
        """Adım 2: Sütunları eşleştir"""
        if not hasattr(self, 'file_path'):
            QMessageBox.warning(self, "Uyarı", "Lütfen önce Excel dosyası seçin!")
            return
        
        mapper = ColumnMapperDialog(self, self.file_path)
        if mapper.exec_():
            self.column_mapping = mapper.column_mapping
            QMessageBox.information(self, "Başarılı", "Sütun eşleştirmesi kaydedildi!")
    
    def step3_quick_rules(self):
        """Adım 3: Hızlı kuralları ayarla"""
        rules_dialog = QuickRulesDialog(self)
        if rules_dialog.exec_():
            self.quick_rules = rules_dialog.rules
            self.rules_label.setText(f"✓ {len(self.quick_rules)} kural tanımlandı")
            self.rules_label.setStyleSheet("color: #4CAF50;")

    def toggle_date_filters(self, checked):
        """Tarih filtrelerini aç/kapat"""
        self.start_date_label.setVisible(checked)
        self.start_date_edit.setVisible(checked)
        self.end_date_label.setVisible(checked)
        self.end_date_edit.setVisible(checked)
        self.start_date_edit.setEnabled(checked)
        self.end_date_edit.setEnabled(checked)


    def _get_active_loans(self):
        """Aktif ve kalan bakiyesi olan kredileri getir"""
        session = SessionLocal()
        try:
            loans = session.query(Loan).filter(
                Loan.user_id == self.user_id,
                Loan.is_active == True
            ).order_by(Loan.bank_name, Loan.loan_name).all()
            result = []
            for loan in loans:
                total_repayment = max(float(loan.remaining_balance or 0), float(loan.loan_amount or 0))
                remaining_amount = max(0.0, total_repayment - float(loan.total_paid or 0))
                if remaining_amount > 0:
                    result.append(loan)
            return result
        finally:
            session.close()

    def _find_best_loan_match(self, text):
        """Metinden en uygun krediyi bul"""
        if not text:
            return None
        normalized_text = self._normalize_turkish_text(text)
        best_match = None
        best_score = 0.55

        for loan in getattr(self, 'loans', []):
            loan_name = self._normalize_turkish_text(getattr(loan, 'loan_name', '') or '')
            bank_name = self._normalize_turkish_text(getattr(loan, 'bank_name', '') or '')
            combined = f"{bank_name} {loan_name}".strip()

            if loan_name and loan_name in normalized_text:
                return loan
            if bank_name and bank_name in normalized_text and 'kredi' in normalized_text:
                best_match = loan
                best_score = 0.9
                continue

            score = SequenceMatcher(None, normalized_text, combined).ratio()
            if score > best_score:
                best_score = score
                best_match = loan

        return best_match

    def _normalize_turkish_text(self, text):
        """Türkçe karakterleri normalize et (İ→i, ç→c, etc)."""
        if not text:
            return ""
        # Turkish character mapping
        turkish_map = {
            'ç': 'c', 'Ç': 'c',
            'ğ': 'g', 'Ğ': 'g',
            'ı': 'i', 'I': 'i',
            'İ': 'i', 'i': 'i',
            'ö': 'o', 'Ö': 'o',
            'ş': 's', 'Ş': 's',
            'ü': 'u', 'Ü': 'u'
        }
        result = str(text).lower()
        for turkish_char, replacement in turkish_map.items():
            result = result.replace(turkish_char.lower(), replacement)
            result = result.replace(turkish_char.upper(), replacement)
        return result

    def _determine_payment_method(self, payment_text, *fallback_texts):
        """Ödeme metninden ödeme yöntemi belirle (KK/Nakit/Banka)."""
        parts = []
        if payment_text is not None:
            parts.append(str(payment_text))
        for value in fallback_texts:
            if value is not None:
                parts.append(str(value))
        text = self._normalize_turkish_text(" ".join(parts))

        # Önce nakit kontrolü
        if "nakit" in text or "cash" in text:
            return PaymentMethod.NAKIT
        
        # Sonra KK kontrolü - daha geniş kapsam
        # "kk", "k.k", "k k", "kredi kart", "kart", "credit card", "cc"
        kk_keywords = ["kk", "k.k", "k k", "kredi kart", "kart", "credit card", "cc"]
        if any(keyword in text for keyword in kk_keywords):
            return PaymentMethod.KREDI_KARTI
        
        # Hiçbiri değilse banka hesabı
        return PaymentMethod.BANKA

    def _payment_method_to_category(self, payment_method):
        if payment_method == PaymentMethod.NAKIT:
            return "NAKIT"
        if payment_method == PaymentMethod.KREDI_KARTI:
            return "KREDI_KARTI"
        return "BANKA"

    def _category_to_payment_method(self, category_text, fallback_method):
        if category_text == "NAKIT":
            return PaymentMethod.NAKIT
        if category_text == "KREDI_KARTI":
            return PaymentMethod.KREDI_KARTI
        if category_text == "BANKA":
            return PaymentMethod.BANKA
        return fallback_method

    def _find_or_create_cari_id(self, customer_name):
        if not customer_name:
            return None
        name = str(customer_name).strip()
        if not name or name.lower() in ["işlem", "islem", "-- seçiniz --"]:
            return None

        existing = self.find_cari_by_name(name)
        if existing:
            return existing.id

        ok, _ = CariService.create_cari(self.user_id, name, "MÜŞTERİ")
        if not ok:
            return None

        self.caris = CariService.get_caris(self.user_id)
        created = self.find_cari_by_name(name)
        return created.id if created else None

    def _normalize_payment_name(self, value, default_value):
        if value is None:
            return default_value
        text = str(value).strip()
        return text if text else default_value

    def _find_or_create_bank_account_id(self, payment_name):
        bank_name = self._normalize_payment_name(payment_name, "Banka Hesabı")
        accounts = BankService.get_accounts(self.user_id)
        for account in accounts:
            if (account.bank_name or "").strip().lower() == bank_name.lower():
                return account.id

        auto_no = f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S%f')[-10:]}"
        ok, _ = BankService.create_account(
            self.user_id,
            bank_name,
            auto_no,
            currency="TRY",
            balance=0.0,
            branch="OTOMATIK"
        )
        if not ok:
            return None

        accounts = BankService.get_accounts(self.user_id)
        for account in accounts:
            if (account.bank_name or "").strip().lower() == bank_name.lower():
                return account.id
        return None

    def _find_or_create_credit_card_id(self, payment_name):
        card_name = self._normalize_payment_name(payment_name, "KK Otomatik")
        cards = CreditCardService.get_active_cards(self.user_id)
        for card in cards:
            card_name_match = (card.card_name or "").strip().lower() == card_name.lower()
            bank_name_match = (card.bank_name or "").strip().lower() == card_name.lower()
            if card_name_match or bank_name_match:
                return card.id

        card, _ = CreditCardService.create_card(
            self.user_id,
            card_name=card_name,
            card_number_last4="0000",
            card_holder="OTOMATIK",
            bank_name=card_name,
            card_limit=100000.0,
            closing_day=1,
            due_day=15,
        )
        if card:
            return card.id

        cards = CreditCardService.get_active_cards(self.user_id)
        for c in cards:
            if (c.card_name or "").strip().lower() == card_name.lower():
                return c.id
        return None
    
    def step4_load_data(self):
        """Adım 4: Verileri yükle"""
        self.caris = CariService.get_caris(self.user_id)
        self.bank_accounts = BankService.get_accounts(self.user_id)
        self.credit_cards = CreditCardService.get_active_cards(self.user_id)
        if not self.column_mapping:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce sütunları eşleştirin!")
            return
        
        try:
            self.loans = self._get_active_loans()
            file_path = self.column_mapping['file_path']
            
            # .xls ve .xlsx desteği
            if file_path.lower().endswith('.xls'):
                try:
                    import xlrd
                    wb = xlrd.open_workbook(file_path, on_demand=True)
                    ws = wb.sheet_by_index(self.column_mapping['sheet'])
                    is_xlrd = True
                except ImportError:
                    QMessageBox.critical(self, "Hata", "xlrd kitaplığı yüklü değil. .xlsx formatını kullanın.")
                    return
            else:
                wb = openpyxl.load_workbook(file_path, data_only=True)
                ws = wb.worksheets[self.column_mapping['sheet']]
                is_xlrd = False
            
            self.transactions_preview = []
            start_row = self.column_mapping['start_row']
            
            date_col = self.column_mapping.get('date_column', -1)
            name_col = self.column_mapping.get('name_column', -1)
            amount_col = self.column_mapping.get('amount_column', -1)
            type_col = self.column_mapping.get('type_column', -1)
            customer_title_col = self.column_mapping.get('customer_title_column', -1)
            desc_col = self.column_mapping.get('description_column', -1)
            payment_type_col = self.column_mapping.get('payment_type_column', -1)
            subject_col = self.column_mapping.get('subject_column', -1)
            person_col = self.column_mapping.get('person_column', -1)
            reference_col = self.column_mapping.get('reference_column', -1)
            
            # Veri satırlarını oku
            all_rows = []
            if is_xlrd:
                selected_cols = [
                    c for c in [date_col, name_col, amount_col, type_col, customer_title_col,
                                desc_col, payment_type_col, subject_col, person_col, reference_col]
                    if c is not None and c >= 0
                ]
                max_col = max(selected_cols) if selected_cols else max(0, ws.ncols - 1)
                for row_idx in range(start_row - 1, min(start_row - 1 + 5000, ws.nrows)):
                    row_data = []
                    for col_idx in range(max_col + 1):
                        row_data.append(ws.cell_value(row_idx, col_idx))
                    all_rows.append(row_data)
            else:
                for row_idx, row in enumerate(ws.iter_rows(
                    min_row=start_row,
                    values_only=True
                ), start=start_row):
                    if row_idx > start_row + 5000:  # Max 5000 satır
                        break
                    all_rows.append(list(row))
            
            # Her satırı işle
            def parse_date(value):
                if isinstance(value, datetime):
                    return value.date()
                if value in (None, ""):
                    return datetime.now().date()
                if is_xlrd and isinstance(value, (float, int)):
                    try:
                        import xlrd
                        return xlrd.xldate_as_datetime(value, wb.datemode).date()
                    except Exception:
                        return None
                if isinstance(value, str):
                    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d/%m/%Y-%H:%M:%S", "%d.%m.%Y %H:%M:%S"):
                        try:
                            return datetime.strptime(value, fmt).date()
                        except Exception:
                            pass
                return datetime.now().date()

            def parse_amount(value):
                if value in (None, ""):
                    return 0.0
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    v = value.strip().replace(" ", "").replace("₺", "").replace("TL", "")
                    if "," in v and "." in v:
                        v = v.replace(".", "").replace(",", ".")
                    elif "," in v and "." not in v:
                        v = v.replace(",", ".")
                    try:
                        return float(v)
                    except Exception:
                        return 0.0
                return 0.0

            def parse_type(value, amount_value):
                if isinstance(value, str):
                    t = self._normalize_turkish_text(value.strip())

                    if ("kredi" in t and any(k in t for k in ["odeme", "taksit", "loan"])):
                        return "KREDI_ODEME"
                    if (("kredi kart" in t or "kart" in t) and any(k in t for k in ["odeme", "ekstre", "borc"])):
                        return "KREDI_KARTI_ODEME"

                    if any(k in t for k in ["gider", "borc", "cikis", "debit", "odeme", "harcama"]):
                        return "GIDER"
                    if any(k in t for k in ["gelir", "alacak", "giris", "credit", "tahsilat"]):
                        return "GELIR"

                return "GIDER" if amount_value < 0 else "GELIR"

            def get_cell_value(row_data, col_idx):
                if col_idx is None or col_idx < 0:
                    return None
                return row_data[col_idx] if col_idx < len(row_data) else None

            def first_non_empty(values, default_value=None):
                for value in values:
                    if value is None:
                        continue
                    if isinstance(value, str) and not value.strip():
                        continue
                    return value
                return default_value

            for row in all_rows:
                try:
                    date_cell = get_cell_value(row, date_col)
                    trans_date = parse_date(date_cell)
                    
                    # Tarih filtrelemesi
                    if self.date_filter_check.isChecked():
                        filter_start = self.start_date_edit.date().toPyDate()
                        filter_end = self.end_date_edit.date().toPyDate()
                        if trans_date < filter_start or trans_date > filter_end:
                            continue
                    
                    name_cell = first_non_empty([
                        get_cell_value(row, name_col),
                        get_cell_value(row, customer_title_col),
                        get_cell_value(row, subject_col),
                        get_cell_value(row, person_col),
                        get_cell_value(row, desc_col),
                        get_cell_value(row, reference_col),
                    ], "İşlem")
                    amount_cell = get_cell_value(row, amount_col)
                    type_cell = get_cell_value(row, type_col)
                    desc_cell = get_cell_value(row, desc_col)
                    payment_type_cell = get_cell_value(row, payment_type_col)
                    subject_cell = get_cell_value(row, subject_col)
                    person_cell = get_cell_value(row, person_col)
                    reference_cell = get_cell_value(row, reference_col)
                    
                    # Tutar ve tip
                    amount = parse_amount(amount_cell)
                    trans_type = parse_type(type_cell, amount)
                    amount = abs(amount)
                    
                    matched_loan = None

                    # Otomatik müşteri eşleştirmesi
                    matched_cari = None
                    if self.auto_match_check.isChecked():
                        matched_cari = self.find_best_cari_match(str(name_cell))
                    
                    # Hızlı kuralları uygula
                    rule_result = self.apply_quick_rules(str(name_cell), trans_type)
                    
                    if rule_result['customer']:
                        # Kural tarafından belirtilen müşteri
                        matched_cari = self.find_cari_by_name(rule_result['customer'])
                    
                    if rule_result['type']:
                        trans_type = rule_result['type']

                    description_parts = [
                        str(desc_cell).strip() if desc_cell not in (None, "") else None,
                        f"Konu: {str(subject_cell).strip()}" if subject_cell not in (None, "") else None,
                        f"Referans: {str(reference_cell).strip()}" if reference_cell not in (None, "") else None,
                    ]
                    description = " | ".join([part for part in description_parts if part])
                    if not description:
                        description = str(name_cell)

                    if trans_type == "KREDI_ODEME":
                        matched_loan = self._find_best_loan_match(
                            f"{name_cell} {description} {subject_cell or ''} {reference_cell or ''}"
                        )
                    
                    payment_method = self._determine_payment_method(
                        payment_type_cell,
                        type_cell,
                        name_cell,
                        desc_cell,
                        subject_cell,
                        person_cell,
                        reference_cell,
                    )

                    transaction = {
                        'date': trans_date,
                        'name': str(name_cell),
                        'amount': amount,
                        'type': trans_type,
                        'payment_method': payment_method,
                        'payment_type': str(payment_type_cell).strip() if payment_type_cell not in (None, "") else None,
                        'subject': str(subject_cell).strip() if subject_cell not in (None, "") else None,
                        'person': str(person_cell).strip() if person_cell not in (None, "") else None,
                        'cari': matched_cari,
                        'loan': matched_loan,
                        'category': rule_result['category'] or self._payment_method_to_category(payment_method),
                        'description': description,
                    }
                    self.transactions_preview.append(transaction)
                
                except Exception as e:
                    print(f"Satır {row_idx} hatası: {e}")
                    continue
            
            self.populate_preview_table()
            QMessageBox.information(self, "Başarılı",
                f"{len(self.transactions_preview)} işlem yüklendi!")
        
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veri yükleme hatası: {str(e)}")
    
    def find_best_cari_match(self, transaction_name):
        """Fuzzy matching ile en iyi müşteri eşleştirmesini bul"""
        best_match = None
        best_score = 0.6
        
        for cari in self.caris:
            similarity = SequenceMatcher(None,
                transaction_name.lower(),
                cari.name.lower()).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = cari
        
        return best_match
    
    def find_cari_by_name(self, name):
        """Adı ile müşteri bul"""
        for cari in self.caris:
            if cari.name.lower() == name.lower():
                return cari
        return None
    
    def apply_quick_rules(self, transaction_name, default_type):
        """Hızlı kuralları uygula"""
        result = {
            'customer': None,
            'type': default_type,
            'category': None,
        }
        
        for rule in self.quick_rules:
            try:
                if re.search(rule['pattern'], transaction_name, re.IGNORECASE):
                    if rule['customer']:
                        result['customer'] = rule['customer']
                    if rule['type']:
                        result['type'] = rule['type']
                    if rule['category']:
                        result['category'] = rule['category']
                    break
            except:
                pass
        
        return result
    
    def populate_preview_table(self):
        """Önizleme tablosunu doldur"""
        self.preview_table.setRowCount(len(self.transactions_preview))
        for row_idx, trans in enumerate(self.transactions_preview):
            # Seç checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.preview_table.setCellWidget(row_idx, 0, checkbox)

            # Tarih
            self.preview_table.setItem(row_idx, 1, QTableWidgetItem(trans['date'].strftime("%d.%m.%Y")))

            # İşlem Adı
            self.preview_table.setItem(row_idx, 2, QTableWidgetItem(trans['name']))

            # Tutar
            amount_item = QTableWidgetItem(f"{trans['amount']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.preview_table.setItem(row_idx, 3, amount_item)

            # Tür (düzenlenebilir)
            type_combo = QComboBox()
            type_combo.addItems(["GELIR", "GIDER", "KREDI_ODEME", "KREDI_KARTI_ODEME"])
            type_combo.setCurrentText(trans['type'])
            self.preview_table.setCellWidget(row_idx, 4, type_combo)

            # Müşteri (düzenlenebilir, yeşille eşleştiyse)
            cari_combo = QComboBox()
            cari_combo.addItem("-- Seçiniz --", None)
            for cari in self.caris:
                cari_combo.addItem(f"{cari.name} ({cari.cari_type})", cari.id)
            if trans['cari']:
                index = cari_combo.findData(trans['cari'].id)
                if index >= 0:
                    cari_combo.setCurrentIndex(index)
                    cari_combo.setStyleSheet("background-color: #c8e6c9;")
            self.preview_table.setCellWidget(row_idx, 5, cari_combo)

            # Ödeme Şekli (Banka hesabı/Kredi kartı - otomatik eşleştir)
            payment_combo = QComboBox()
            payment_combo.setEditable(True)
            payment_combo.addItem("-- Seçiniz veya Yazın --", None)
            for bank in self.bank_accounts:
                display_name = f"🏦 {bank.bank_name} ({bank.account_number})"
                payment_combo.addItem(display_name, ('bank', bank.id, bank.bank_name))
            for card in self.credit_cards:
                display_name = f"💳 {card.card_name} (***{card.card_number_last4})"
                payment_combo.addItem(display_name, ('card', card.id, card.card_name))
            payment_value = trans.get('payment_type') or trans['category']
            matched = False
            if payment_value:
                payment_str = str(payment_value).strip().lower()
                normalized_payment = self._normalize_turkish_text(payment_str)
                for bank in self.bank_accounts:
                    bank_name_normalized = self._normalize_turkish_text(bank.bank_name.lower())
                    account_normalized = self._normalize_turkish_text(bank.account_number.lower())
                    if (bank_name_normalized in normalized_payment or 
                        normalized_payment in bank_name_normalized or
                        account_normalized in normalized_payment):
                        index = payment_combo.findData(('bank', bank.id, bank.bank_name))
                        if index >= 0:
                            payment_combo.setCurrentIndex(index)
                            payment_combo.setStyleSheet("background-color: #c8e6c9;")
                            matched = True
                            break
                if not matched:
                    for card in self.credit_cards:
                        card_name_normalized = self._normalize_turkish_text(card.card_name.lower())
                        bank_name_normalized = self._normalize_turkish_text(card.bank_name.lower()) if card.bank_name else ""
                        if (card_name_normalized in normalized_payment or 
                            normalized_payment in card_name_normalized or
                            bank_name_normalized in normalized_payment or
                            normalized_payment in bank_name_normalized):
                            index = payment_combo.findData(('card', card.id, card.card_name))
                            if index >= 0:
                                payment_combo.setCurrentIndex(index)
                                payment_combo.setStyleSheet("background-color: #c8e6c9;")
                                matched = True
                                break
                if not matched:
                    payment_combo.setEditText(str(payment_value))
            self.preview_table.setCellWidget(row_idx, 6, payment_combo)

            # Ödenecek Kredi
            loan_combo = QComboBox()
            loan_combo.addItem("-- Kredi Seçiniz --", None)
            for loan in getattr(self, 'loans', []):
                total_repayment = max(float(loan.remaining_balance or 0), float(loan.loan_amount or 0))
                remaining_amount = max(0.0, total_repayment - float(loan.total_paid or 0))
                loan_combo.addItem(
                    f"{loan.bank_name} - {loan.loan_name} (Kalan: {remaining_amount:,.2f} ₺)",
                    loan.id
                )
            if trans.get('loan'):
                index = loan_combo.findData(trans['loan'].id)
                if index >= 0:
                    loan_combo.setCurrentIndex(index)
                    loan_combo.setStyleSheet("background-color: #c8e6c9;")
            self.preview_table.setCellWidget(row_idx, 7, loan_combo)

            # Açıklama
            self.preview_table.setItem(row_idx, 8, QTableWidgetItem(trans['description']))
    def _collect_preview_row_data(self, row_idx):
        error_list = []
        try:
            date_text = self.preview_table.item(row_idx, 1).text()
            name_text = self.preview_table.item(row_idx, 2).text()
            amount_text = self.preview_table.item(row_idx, 3).text()

            type_combo = self.preview_table.cellWidget(row_idx, 4)
            trans_type = TransactionType[type_combo.currentText()]

            cari_combo = self.preview_table.cellWidget(row_idx, 5)
            cari_id = cari_combo.currentData()

            payment_combo = self.preview_table.cellWidget(row_idx, 6)
            payment_data = payment_combo.currentData()
            selected_payment_text = payment_combo.currentText().strip()

            loan_combo = self.preview_table.cellWidget(row_idx, 7)
            loan_id = loan_combo.currentData() if loan_combo else None

            description = self.preview_table.item(row_idx, 8).text()

            # Tarih parse
            try:
                trans_date = datetime.strptime(date_text, "%d.%m.%Y").date()
            except Exception:
                try:
                    trans_date = datetime.strptime(date_text, "%Y-%m-%d").date()
                except Exception:
                    return None, f"Tarih formatı hatalı: {date_text}"

            # Tutar parse
            raw_amount = str(amount_text).strip().replace(" ", "").replace("₺", "").replace("TL", "")
            if "," in raw_amount and "." in raw_amount:
                raw_amount = raw_amount.replace(",", "")
            elif "," in raw_amount and "." not in raw_amount:
                raw_amount = raw_amount.replace(",", ".")
            try:
                amount = float(raw_amount)
            except Exception:
                return None, f"Tutar formatı hatalı: {amount_text}"

            preview_data = self.transactions_preview[row_idx] if row_idx < len(self.transactions_preview) else {}
            subject = preview_data.get('subject')
            person = preview_data.get('person')

            bank_account_id = None
            credit_card_id = None
            payment_method = None
            payment_mode = "text"

            if payment_data and isinstance(payment_data, tuple):
                account_type, account_id, account_name = payment_data
                payment_mode = "existing"
                if account_type == 'bank':
                    bank_account_id = account_id
                    payment_method = PaymentMethod.BANKA
                elif account_type == 'card':
                    credit_card_id = account_id
                    payment_method = PaymentMethod.KREDI_KARTI
            else:
                payment_method = self._determine_payment_method(selected_payment_text)

            # Zorunlu alan validasyonları
            if not name_text or not name_text.strip():
                return None, "İşlem adı boş olamaz."
            if not description or not description.strip():
                return None, "Açıklama boş olamaz."
            if not trans_type:
                return None, "İşlem türü seçilmedi."
            if not payment_method:
                return None, "Ödeme yöntemi belirlenemedi."
            if trans_type == TransactionType.KREDI_ODEME and not loan_id:
                return None, "Kredi ödeme için ödenecek krediyi seçmelisiniz."
            if trans_type == TransactionType.KREDI_ODEME and payment_method == PaymentMethod.BANKA and not bank_account_id and selected_payment_text in ["", "-- Seçiniz veya Yazın --"]:
                return None, "Kredi ödemenin çıkacağı banka hesabını seçmelisiniz."

            return {
                'row_key': row_idx,
                'row_label': row_idx + 1,
                'date_text': date_text,
                'trans_date': trans_date,
                'name_text': name_text,
                'amount_text': amount_text,
                'description': description,
                'amount': amount,
                'trans_type': trans_type,
                'cari_id': cari_id,
                'payment_method': payment_method,
                'payment_text': selected_payment_text,
                'payment_mode': payment_mode,
                'bank_account_id': bank_account_id,
                'credit_card_id': credit_card_id,
                'loan_id': loan_id,
                'notes': f"loan_id:{loan_id}" if loan_id else None,
                'subject': subject,
                'person': person,
            }, None
        except Exception as e:
            return None, str(e)
