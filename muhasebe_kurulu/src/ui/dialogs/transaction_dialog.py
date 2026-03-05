from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, 
                           QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit, QMessageBox,
                           QDoubleSpinBox, QRadioButton, QButtonGroup, QGroupBox,
                           QWidget, QApplication)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont
from src.database.models import TransactionType, PaymentMethod, Transaction
from src.services.transaction_service import TransactionService
from src.services.cari_service import CariService
from src.services.bank_service import BankService
from src.database.db import SessionLocal
from src.database.models import CreditCard, Loan
from datetime import date


class TransactionDialog(QDialog):
    """Yeni İşlem Eklema/Düzenleme Dialog'u - Otomatik hesap güncellemeli"""
    
    def __init__(self, user_id, parent=None, transaction_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.transaction_id = transaction_id
        self.is_edit_mode = transaction_id is not None
        
        if self.is_edit_mode:
            self.setWindowTitle("İşlem Düzenle")
        else:
            self.setWindowTitle("Yeni İşlem Ekle")
        
        self.setMinimumWidth(780)
        self.setModal(True)
        self.init_ui()
        self._auto_resize()
        
        # Düzenleme modundaysa işlem verilerini yükle
        if self.is_edit_mode:
            self.load_transaction()
            self._auto_resize()
    
    def _auto_resize(self):
        """Dialog'u içeriğe göre boyutlandır, ekranın %90'dan fazlasını kaplamaz"""
        screen = QApplication.primaryScreen().availableGeometry()
        max_w = int(screen.width()  * 0.90)
        max_h = int(screen.height() * 0.90)
        self.adjustSize()
        hint = self.sizeHint()
        w = min(max(hint.width(),  780), max_w)
        h = min(max(hint.height(), 400), max_h)
        self.resize(w, h)
        # Ekrana göre ortala
        self.move(
            screen.x() + (screen.width()  - w) // 2,
            screen.y() + (screen.height() - h) // 2
        )

    def init_ui(self):
        """Arayüz elemanlarını oluştur"""
        self.setStyleSheet("""
            QLabel { font-size: 10pt; }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
                min-height: 32px;
                padding: 6px 8px;
                font-size: 10pt;
            }
            QPushButton { min-height: 32px; font-size: 10pt; }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 10)
        
        # Başlık
        if self.is_edit_mode:
            title = QLabel("✏️ İşlem Düzenle")
        else:
            title = QLabel("💰 Yeni İşlem Ekle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #333;")
        layout.addWidget(title)
        
        # Form alanları
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Tarih
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumHeight(35)
        form_layout.addRow("📅 Tarih: <span style=\"color:#d32f2f\">*</span>", self.date_input)
        
        # İşlem Türü
        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(35)
        self.type_combo.addItems([
            "GIDER", "GELIR", "KESILEN_FATURA", "GELEN_FATURA",
            "KREDI_ODEME", "KREDI_KARTI_ODEME", "KREDI_CEKIMI",
            "EK_HESAP_FAIZLERI", "KREDI_DOSYA_MASRAFI", "EKSPERTIZ_UCRETI", "TRANSFER"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form_layout.addRow("📋 İşlem Türü: <span style=\"color:#d32f2f\">*</span>", self.type_combo)

        # Vade Tarihi (sadece Kesilen Fatura için görünür)
        self.due_date_label = QLabel("📅 Vade Tarihi (30 gün):")
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate().addDays(30))
        self.due_date_input.setMinimumHeight(35)
        self.due_date_input.setStyleSheet("background-color: #FFF9C4;")
        self.due_date_label.setVisible(False)
        self.due_date_input.setVisible(False)
        form_layout.addRow(self.due_date_label, self.due_date_input)

        # Tarih değişince vade tarihini otomatik güncelle
        self.date_input.dateChanged.connect(self._update_due_date_from_invoice_date)
        
        # Ödeme Yöntemi
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setMinimumHeight(35)
        self.payment_method_combo.addItem("Nakit", "NAKIT")
        self.payment_method_combo.addItem("Banka Hesabı", "BANKA")
        self.payment_method_combo.addItem("Kredi Kartları", "KREDI_KARTI")
        self.payment_method_combo.addItem("Cari Hesap", "CARI")
        self.payment_method_combo.addItem("Transfer", "TRANSFER")
        self.payment_method_combo.currentIndexChanged.connect(self.on_payment_method_changed)
        form_layout.addRow("💳 Ödeme Yöntemi: <span style=\"color:#d32f2f\">*</span>", self.payment_method_combo)
        
        # Müşteri/Tedarikçi
        self.customer_input = QLineEdit()
        self.customer_input.setMinimumHeight(35)
        self.customer_input.setPlaceholderText("Müşteri/Tedarikçi adı")
        self.customer_input.editingFinished.connect(self.on_customer_name_changed)
        form_layout.addRow("👤 Müşteri Ünvanı: <span style=\"color:#d32f2f\">*</span>", self.customer_input)
        
        # Açıklama
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("İşlem açıklaması")
        form_layout.addRow("📝 Açıklama: <span style=\"color:#d32f2f\">*</span>", self.description_input)
        
        # Konu (Opsiyonel)
        self.subject_input = QLineEdit()
        self.subject_input.setMinimumHeight(35)
        self.subject_input.setPlaceholderText("Konu")
        form_layout.addRow("📌 Konu:", self.subject_input)
        
        # Tutar
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMinimumHeight(35)
        self.amount_input.setMaximum(999999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" ₺")
        form_layout.addRow("💵 Tutar: <span style=\"color:#d32f2f\">*</span>", self.amount_input)
        
        # Ödeyen Kişi (Opsiyonel)
        self.person_input = QLineEdit()
        self.person_input.setMinimumHeight(35)
        self.person_input.setPlaceholderText("Ödeyen kişi")
        form_layout.addRow("🧑 Ödeyen Kişi:", self.person_input)
        
        # --- Hesap Seçimi Grubu (Dinamik) ---
        self.account_group = QGroupBox("Hesap Seçimi")
        self.account_layout = QVBoxLayout()
        
        # Cari Hesap Seçimi
        self.cari_combo = QComboBox()
        self.cari_combo.setMinimumHeight(35)
        self.cari_combo.addItem("-- Cari Seçiniz --", None)
        self.load_cari_accounts()
        self.account_layout.addWidget(QLabel("📋 Cari Hesap:"))
        self.account_layout.addWidget(self.cari_combo)
        
        # Banka Hesabı Seçimi (Kaynak)
        self.bank_combo = QComboBox()
        self.bank_combo.setMinimumHeight(35)
        self.bank_combo.addItem("-- Banka Hesabı Seçiniz --", None)
        self.bank_combo.currentIndexChanged.connect(self.on_source_bank_changed)
        self.account_layout.addWidget(QLabel("🏦 Banka Hesabı:"))
        self.account_layout.addWidget(self.bank_combo)
        self.bank_combo.setVisible(False)
        self.account_layout.itemAt(self.account_layout.count() - 2).widget().setVisible(False)
        
        # Banka Hesabı Seçimi (Hedef - Transfer için)
        self.destination_bank_combo = QComboBox()
        self.destination_bank_combo.setMinimumHeight(35)
        self.destination_bank_combo.addItem("-- Hedef Hesabı Seçiniz --", None)
        self.destination_bank_combo.currentIndexChanged.connect(self._update_transfer_customer_name)
        self.load_bank_accounts()
        self.account_layout.addWidget(QLabel("🏦 Hedef Hesabı (Transfer):"))
        self.account_layout.addWidget(self.destination_bank_combo)
        self.destination_bank_combo.setVisible(False)
        self.account_layout.itemAt(self.account_layout.count() - 2).widget().setVisible(False)
        
        # Kredi Kartı Seçimi
        self.card_combo = QComboBox()
        self.card_combo.setMinimumHeight(35)
        self.card_combo.addItem("-- Kredi Kartı Seçiniz --", None)
        self.load_credit_cards()
        self.account_layout.addWidget(QLabel("💳 Kredi Kartı:"))
        self.account_layout.addWidget(self.card_combo)
        self.card_combo.setVisible(False)
        self.account_layout.itemAt(self.account_layout.count() - 2).widget().setVisible(False)
        
        # Kredi Kartı Ödeme Seçimi (Ödeme yapılacak kartı seçmek için)
        self.credit_card_payment_combo = QComboBox()
        self.credit_card_payment_combo.setMinimumHeight(35)
        self.credit_card_payment_combo.addItem("-- Ödeme Yapılacak Kart Seçiniz --", None)
        self.load_credit_cards_for_payment()
        self.account_layout.addWidget(QLabel("💳 Ödeme Yapılacak Kredi Kartı:"))
        self.account_layout.addWidget(self.credit_card_payment_combo)
        self.credit_card_payment_combo.setVisible(False)
        self.account_layout.itemAt(self.account_layout.count() - 2).widget().setVisible(False)

        # Kredi Ödeme Seçimi (KREDI_ODEME için)
        self.loan_payment_combo = QComboBox()
        self.loan_payment_combo.setMinimumHeight(35)
        self.loan_payment_combo.addItem("-- Ödeme Yapılacak Kredi Seçiniz --", None)
        self.load_loans_for_payment()
        self.loan_payment_combo.currentIndexChanged.connect(self.on_loan_payment_changed)
        self.account_layout.addWidget(QLabel("🏦 Ödeme Yapılacak Kredi:"))
        self.account_layout.addWidget(self.loan_payment_combo)
        self.loan_payment_combo.setVisible(False)
        self.account_layout.itemAt(self.account_layout.count() - 2).widget().setVisible(False)
        
        self.account_group.setLayout(self.account_layout)
        form_layout.addRow(self.account_group)
        
        layout.addLayout(form_layout)

        # Butonlar
        btn_container = QWidget()
        btn_container.setStyleSheet("background: #f5f5f5; border-top: 1px solid #ddd;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(14, 10, 14, 10)
        
        btn_save = QPushButton("✅ Kaydet")
        btn_save.setMinimumHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_save.clicked.connect(self.save_transaction)
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
                font-size: 12pt;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addWidget(btn_container)
        self.setLayout(layout)
        self.on_payment_method_changed()
    
    def load_cari_accounts(self):
        """Cari hesapları yükle"""
        try:
            caris = CariService.get_caris(self.user_id)
            if caris:
                for cari in caris:
                    self.cari_combo.addItem(f"{cari.name} ({cari.cari_type})", cari.id)
        except Exception as e:
            print(f"Cari yükleme hatası: {e}")
    
    def load_bank_accounts(self):
        """Banka hesaplarını yükle"""
        try:
            banks = BankService.get_accounts(self.user_id)
            self._bank_accounts = banks or []

            previous_source = self.bank_combo.currentData()
            self.bank_combo.clear()
            self.bank_combo.addItem("-- Banka Hesabı Seçiniz --", None)
            self.bank_combo.addItem("💵 Nakit Kasası", "NAKIT")

            if self._bank_accounts:
                for bank in self._bank_accounts:
                    self.bank_combo.addItem(
                        f"{bank.bank_name} - {bank.account_number} ({bank.balance:.2f} {bank.currency})",
                        bank.id
                    )

            if previous_source:
                index = self.bank_combo.findData(previous_source)
                if index >= 0:
                    self.bank_combo.setCurrentIndex(index)

            self.refresh_destination_bank_accounts()
        except Exception as e:
            print(f"Banka yükleme hatası: {e}")

    def refresh_destination_bank_accounts(self):
        """Transfer hedef hesap listesini kaynak hesaba göre güncelle"""
        previous_destination = self.destination_bank_combo.currentData()
        source_bank_id = self.bank_combo.currentData()

        self.destination_bank_combo.clear()
        self.destination_bank_combo.addItem("-- Hedef Hesabı Seçiniz --", None)

        # Kaynak banka değilse Nakit seçeneği ekle
        if source_bank_id != "NAKIT":
            self.destination_bank_combo.addItem("💵 Nakit Kasası", "NAKIT")

        banks = getattr(self, '_bank_accounts', [])
        for bank in banks:
            if source_bank_id and bank.id == source_bank_id:
                continue
            self.destination_bank_combo.addItem(
                f"{bank.bank_name} - {bank.account_number} ({bank.balance:.2f} {bank.currency})",
                bank.id
            )

        if previous_destination and previous_destination != source_bank_id:
            index = self.destination_bank_combo.findData(previous_destination)
            if index >= 0:
                self.destination_bank_combo.setCurrentIndex(index)

        # Müşteri adını otomatik güncelle
        self._update_transfer_customer_name()

    def on_source_bank_changed(self, index=None):
        """Kaynak banka değiştiğinde hedef hesap listesini yenile"""
        self.refresh_destination_bank_accounts()

    def _update_transfer_customer_name(self):
        """Transfer türüne göre müşteri adını otomatik ayarla"""
        if self.type_combo.currentText() != "TRANSFER":
            return
        src = self.bank_combo.currentData()
        dst = self.destination_bank_combo.currentData()
        if src == "NAKIT" and dst and dst != "NAKIT":
            self.customer_input.setText("Nakit Yatırım")
        elif src and src != "NAKIT" and dst == "NAKIT":
            self.customer_input.setText("Nakit Çekim")
        else:
            self.customer_input.setText("Banka Transferi")
    
    def load_credit_cards(self):
        """Kredi kartlarını yükle"""
        session = SessionLocal()
        try:
            cards = session.query(CreditCard).filter(
                CreditCard.user_id == self.user_id,
                CreditCard.is_active == True
            ).all()
            for card in cards:
                self.card_combo.addItem(
                    f"{card.card_name} - ****{card.card_number_last4} (Limit: {card.available_limit:.2f})",
                    card.id
                )
        except Exception as e:
            print(f"Kredi kartı yükleme hatası: {e}")
        finally:
            session.close()
    
    def load_credit_cards_for_payment(self):
        """Kredi kartlarını ödeme için yükle (borçlu olanları göster)"""
        session = SessionLocal()
        try:
            cards = session.query(CreditCard).filter(
                CreditCard.user_id == self.user_id,
                CreditCard.is_active == True,
                CreditCard.current_debt > 0  # Sadece borçlu kartları göster
            ).all()
            for card in cards:
                self.credit_card_payment_combo.addItem(
                    f"{card.card_name} - ****{card.card_number_last4} (Borç: {card.current_debt:.2f})",
                    card.id
                )
        except Exception as e:
            print(f"Kredi kartı ödeme yükleme hatası: {e}")
        finally:
            session.close()

    def load_loans_for_payment(self):
        """Kredileri ödeme için yükle (kalan bakiyesi olanları göster)"""
        session = SessionLocal()
        try:
            loans = session.query(Loan).filter(
                Loan.user_id == self.user_id,
                Loan.is_active == True
            ).all()
            for loan in loans:
                total_repayment = max(float(loan.remaining_balance or 0), float(loan.loan_amount or 0))
                remaining_amount = max(0.0, total_repayment - float(loan.total_paid or 0))
                if remaining_amount <= 0:
                    continue
                self.loan_payment_combo.addItem(
                    f"{loan.loan_name} - {loan.bank_name} (Kalan: {remaining_amount:.2f})",
                    loan.id
                )
        except Exception as e:
            print(f"Kredi ödeme yükleme hatası: {e}")
        finally:
            session.close()

    def on_loan_payment_changed(self, index=None):
        """KREDI_ODEME için müşteri alanını seçilen krediye göre otomatik eşleştir"""
        if self.type_combo.currentText() != "KREDI_ODEME":
            return
        loan_id = self.loan_payment_combo.currentData()
        if not loan_id:
            return
        session = SessionLocal()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id, Loan.user_id == self.user_id).first()
            if loan:
                self.customer_input.setText(loan.loan_name)
        finally:
            session.close()

    def _normalize_name(self, value):
        return " ".join((value or "").strip().lower().split())

    def _extract_cari_name_from_item(self, item_text):
        if not item_text:
            return ""
        if " (" in item_text:
            return item_text.split(" (", 1)[0].strip()
        return item_text.strip()

    def _find_cari_index_by_name(self, customer_name):
        target = self._normalize_name(customer_name)
        if not target:
            return -1

        partial_index = -1
        for index in range(1, self.cari_combo.count()):
            item_name = self._extract_cari_name_from_item(self.cari_combo.itemText(index))
            normalized_item = self._normalize_name(item_name)
            if normalized_item == target:
                return index
            if partial_index < 0 and (target in normalized_item or normalized_item in target):
                partial_index = index

        return partial_index

    def _reload_cari_accounts(self):
        self.cari_combo.clear()
        self.cari_combo.addItem("-- Cari Seçiniz --", None)
        self.load_cari_accounts()

    def _sync_customer_to_cari(self, auto_create=False):
        """Müşteri ünvanını cari ile eşleştir; gerekirse cari oluştur"""
        transaction_type = self.type_combo.currentText()
        if transaction_type in ["TRANSFER", "KREDI_ODEME", "KREDI_KARTI_ODEME"]:
            return

        customer_name = self.customer_input.text().strip()
        if not customer_name:
            return

        existing_index = self._find_cari_index_by_name(customer_name)
        if existing_index >= 0:
            self.cari_combo.setCurrentIndex(existing_index)
            return

        if not auto_create:
            return

        success, message = CariService.create_cari(
            user_id=self.user_id,
            name=customer_name,
            cari_type='MÜŞTERİ'
        )
        if not success:
            QMessageBox.warning(self, "Uyarı", f"Cari otomatik oluşturulamadı: {message}")
            return

        self._reload_cari_accounts()
        created_index = self._find_cari_index_by_name(customer_name)
        if created_index >= 0:
            self.cari_combo.setCurrentIndex(created_index)

    def on_customer_name_changed(self):
        """Müşteri ünvanı değiştiğinde cari hesabı otomatik eşleştir"""
        self._sync_customer_to_cari(auto_create=False)

    def _parse_loan_id_from_notes(self, notes):
        if not notes:
            return None
        text = str(notes).strip()
        if not text.startswith("loan_id:"):
            return None
        raw_id = text.split(":", 1)[1].strip()
        if raw_id.isdigit():
            return int(raw_id)
        return None

    def _get_loan_name(self, loan_id):
        session = SessionLocal()
        try:
            loan = session.query(Loan).filter(Loan.id == loan_id, Loan.user_id == self.user_id).first()
            return loan.loan_name if loan else ""
        finally:
            session.close()
    
    def _update_due_date_from_invoice_date(self):
        """Fatura tarihi değişince vade tarihini otomatik güncelle (sadece KESILEN_FATURA için)"""
        if self.type_combo.currentText() == "KESILEN_FATURA":
            self.due_date_input.setDate(self.date_input.date().addDays(30))

    def on_type_changed(self, transaction_type):
        """İşlem türü değiştiğinde"""
        # Vade tarihi alanını göster/gizle
        is_kesilen = transaction_type == "KESILEN_FATURA"
        self.due_date_label.setVisible(is_kesilen)
        self.due_date_input.setVisible(is_kesilen)
        if is_kesilen:
            # Otomatik 30 gün vade ata
            self.due_date_input.setDate(self.date_input.date().addDays(30))
        # Varsayılan müşteri alanı durumu
        self.customer_input.setReadOnly(False)

        # TRANSFER işlemlerinde ödeme yöntemi zorunlu TRANSFER
        if transaction_type == "TRANSFER":
            idx = self.payment_method_combo.findData("TRANSFER")
            if idx >= 0:
                self.payment_method_combo.setCurrentIndex(idx)
            self._update_transfer_customer_name()
            self.customer_input.setReadOnly(True)
        elif transaction_type in ["KESILEN_FATURA", "GELEN_FATURA"]:
            # Fatura işlemlerinde varsayılan CARI
            idx = self.payment_method_combo.findData("CARI")
            if idx >= 0:
                self.payment_method_combo.setCurrentIndex(idx)
        elif transaction_type == "GELIR":
            # Gelir için varsayılan BANKA
            idx = self.payment_method_combo.findData("BANKA")
            if idx >= 0:
                self.payment_method_combo.setCurrentIndex(idx)
        elif transaction_type == "KREDI_KARTI_ODEME":
            # Kredi kartı ödemede kaynak BANKA
            idx = self.payment_method_combo.findData("BANKA")
            if idx >= 0:
                self.payment_method_combo.setCurrentIndex(idx)
        elif transaction_type == "KREDI_ODEME":
            # Kredi ödemede seçilen ödeme yöntemi korunur, kredi seçimi zorunludur
            self.customer_input.setReadOnly(True)
            self.on_loan_payment_changed()

        self.on_payment_method_changed()
    
    def on_payment_method_changed(self, index=None):
        """Ödeme yöntemi değiştiğinde ilgili hesap alanlarını göster/gizle"""
        payment_method = self.payment_method_combo.currentData()
        if not payment_method:
            return
        
        transaction_type = self.type_combo.currentText()
        
        # Tüm hesap alanlarını gizle
        for i in range(self.account_layout.count()):
            widget = self.account_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(False)
        
        # TRANSFER: kaynak + hedef banka (nakit seçeneği dahil)
        if transaction_type == "TRANSFER" or payment_method == "TRANSFER":
            self.account_layout.itemAt(2).widget().setVisible(True)  # Banka Label
            self.account_layout.itemAt(3).widget().setVisible(True)  # Banka Combo (Kaynak)
            self.account_layout.itemAt(4).widget().setVisible(True)  # Hedef Banka Label
            self.account_layout.itemAt(5).widget().setVisible(True)  # Hedef Banka Combo
        # KREDI_KARTI_ODEME: sadece ödeme yöntemi hesabı + ödeme yapılacak kart
        elif transaction_type == "KREDI_KARTI_ODEME":
            if payment_method == "BANKA":
                self.account_layout.itemAt(2).widget().setVisible(True)  # Banka Label
                self.account_layout.itemAt(3).widget().setVisible(True)  # Banka Combo
            elif payment_method == "KREDI_KARTI":
                self.account_layout.itemAt(6).widget().setVisible(True)  # Kart Label
                self.account_layout.itemAt(7).widget().setVisible(True)  # Kart Combo
            self.account_layout.itemAt(8).widget().setVisible(True)  # Ödeme Yapılacak Kart Label
            self.account_layout.itemAt(9).widget().setVisible(True)  # Ödeme Yapılacak Kart Combo
        # KREDI_ODEME: sadece ödeme yöntemi hesabı + ödeme yapılacak kredi
        elif transaction_type == "KREDI_ODEME":
            if payment_method == "BANKA":
                self.account_layout.itemAt(2).widget().setVisible(True)  # Banka Label
                self.account_layout.itemAt(3).widget().setVisible(True)  # Banka Combo
            elif payment_method == "KREDI_KARTI":
                self.account_layout.itemAt(6).widget().setVisible(True)  # Kart Label
                self.account_layout.itemAt(7).widget().setVisible(True)  # Kart Combo
            self.account_layout.itemAt(10).widget().setVisible(True)  # Kredi Label
            self.account_layout.itemAt(11).widget().setVisible(True)  # Kredi Combo
        else:
            # Diğer işlemlerde TRANSFER hariç her zaman cari görünür
            self.account_layout.itemAt(0).widget().setVisible(True)  # Cari Label
            self.account_layout.itemAt(1).widget().setVisible(True)  # Cari Combo

            # 2. hesap seçimi ödeme yöntemine göre
            if payment_method == "BANKA":
                self.account_layout.itemAt(2).widget().setVisible(True)  # Banka Label
                self.account_layout.itemAt(3).widget().setVisible(True)  # Banka Combo
            elif payment_method == "KREDI_KARTI":
                self.account_layout.itemAt(6).widget().setVisible(True)  # Kart Label
                self.account_layout.itemAt(7).widget().setVisible(True)  # Kart Combo

        # Görünürlük değişince boyutu güncelle
        self._auto_resize()
    
    def load_transaction(self):
        """Mevcut işlem verilerini yükle (düzenleme modu için)"""
        try:
            from src.database.models import Transaction
            session = SessionLocal()
            transaction = session.query(Transaction).filter(
                Transaction.id == self.transaction_id
            ).first()
            
            if transaction:
                # Tarih
                self.date_input.setDate(QDate(transaction.transaction_date.year,
                                              transaction.transaction_date.month,
                                              transaction.transaction_date.day))
                
                # İşlem türü
                self.type_combo.setCurrentText(transaction.transaction_type.name)

                # Vade tarihi (Kesilen Fatura için)
                if transaction.transaction_type.name == "KESILEN_FATURA":
                    if hasattr(transaction, 'due_date') and transaction.due_date:
                        self.due_date_input.setDate(QDate(transaction.due_date.year,
                                                          transaction.due_date.month,
                                                          transaction.due_date.day))
                    else:
                        self.due_date_input.setDate(QDate(transaction.transaction_date.year,
                                                          transaction.transaction_date.month,
                                                          transaction.transaction_date.day).addDays(30))
                
                # Ödeme yöntemi
                payment_method_index = self.payment_method_combo.findData(transaction.payment_method.name)
                if payment_method_index >= 0:
                    self.payment_method_combo.setCurrentIndex(payment_method_index)
                
                # Müşteri
                self.customer_input.setText(transaction.customer_name or "")
                
                # Açıklama
                self.description_input.setPlainText(transaction.description or "")
                
                # Konu
                if transaction.subject:
                    self.subject_input.setText(transaction.subject)
                
                # Tutar
                self.amount_input.setValue(float(transaction.amount))
                
                # Ödeyen kişi
                if transaction.person:
                    self.person_input.setText(transaction.person)
                
                # Hesap seçimleri
                if transaction.cari_id:
                    index = self.cari_combo.findData(transaction.cari_id)
                    if index >= 0:
                        self.cari_combo.setCurrentIndex(index)
                
                if transaction.bank_account_id:
                    index = self.bank_combo.findData(transaction.bank_account_id)
                    if index >= 0:
                        self.bank_combo.setCurrentIndex(index)
                
                if transaction.destination_bank_account_id:
                    index = self.destination_bank_combo.findData(transaction.destination_bank_account_id)
                    if index >= 0:
                        self.destination_bank_combo.setCurrentIndex(index)
                
                if transaction.credit_card_id:
                    index = self.card_combo.findData(transaction.credit_card_id)
                    if index >= 0:
                        self.card_combo.setCurrentIndex(index)
                
                # Kredi kartı ödeme kombosu (KREDI_ODEME ve KREDI_KARTI_ODEME için)
                if transaction.credit_card_id and transaction.transaction_type in [
                    TransactionType.KREDI_KARTI_ODEME
                ]:
                    index = self.credit_card_payment_combo.findData(transaction.credit_card_id)
                    if index >= 0:
                        self.credit_card_payment_combo.setCurrentIndex(index)

                if transaction.transaction_type == TransactionType.KREDI_ODEME:
                    loan_id = self._parse_loan_id_from_notes(transaction.notes)
                    if loan_id:
                        index = self.loan_payment_combo.findData(loan_id)
                        if index >= 0:
                            self.loan_payment_combo.setCurrentIndex(index)
                    elif transaction.customer_name:
                        for i in range(self.loan_payment_combo.count()):
                            item_text = self.loan_payment_combo.itemText(i)
                            if item_text.startswith(transaction.customer_name):
                                self.loan_payment_combo.setCurrentIndex(i)
                                break
            
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem yüklenemedi: {str(e)}")
    
    def save_transaction(self):
        """İşlemi kaydet"""
        transaction_type = TransactionType[self.type_combo.currentText()]

        if transaction_type not in [TransactionType.TRANSFER, TransactionType.KREDI_ODEME, TransactionType.KREDI_KARTI_ODEME]:
            self._sync_customer_to_cari(auto_create=True)

        if transaction_type == TransactionType.KREDI_ODEME and self.loan_payment_combo.currentData():
            loan_name = self._get_loan_name(self.loan_payment_combo.currentData())
            if loan_name:
                self.customer_input.setText(loan_name)

        # Validasyon
        if not self.customer_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Müşteri ünvanı gerekli!")
            return
        
        if not self.description_input.toPlainText().strip():
            QMessageBox.warning(self, "Uyarı", "Açıklama gerekli!")
            return
        
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "Uyarı", "Tutar 0'dan büyük olmalı!")
            return
        
        # İşlem oluştur veya güncelle
        try:
            transaction_date = self.date_input.date().toPyDate()
            payment_method = PaymentMethod[self.payment_method_combo.currentData()]
            
            kwargs = {
                'subject': self.subject_input.text().strip() or None,
                'person': self.person_input.text().strip() or None,
                'payment_type': payment_method.value
            }

            if transaction_type not in [TransactionType.TRANSFER, TransactionType.KREDI_ODEME, TransactionType.KREDI_KARTI_ODEME] and self.cari_combo.currentData():
                kwargs['cari_id'] = self.cari_combo.currentData()
            
            # FATURA işlemlerinde hem cari hem ödeme yöntemi hesabı eklenebilir
            if transaction_type in [TransactionType.KESILEN_FATURA, TransactionType.GELEN_FATURA]:
                # Cari mutlaka olmalı
                if self.cari_combo.currentData():
                    kwargs['cari_id'] = self.cari_combo.currentData()
                else:
                    QMessageBox.warning(self, "Uyarı", "Fatura işlemleri için cari hesap seçmelisiniz!")
                    return

                # Kesilen fatura için vade tarihi ekle (otomatik 30 gün)
                if transaction_type == TransactionType.KESILEN_FATURA:
                    kwargs['due_date'] = self.due_date_input.date().toPyDate()

                # Eğer ödeme yöntemi BANKA ise banka da ekle (Nakit değilse)
                if payment_method == PaymentMethod.BANKA and self.bank_combo.currentData() and self.bank_combo.currentData() != "NAKIT":
                    kwargs['bank_account_id'] = self.bank_combo.currentData()
            # TRANSFER işlemlerinde kaynak + hedef (banka veya nakit kasası)
            elif transaction_type == TransactionType.TRANSFER:
                src = self.bank_combo.currentData()
                dst = self.destination_bank_combo.currentData()

                if not src:
                    QMessageBox.warning(self, "Uyarı", "Kaynak hesabı seçmelisiniz!")
                    return
                if not dst:
                    QMessageBox.warning(self, "Uyarı", "Hedef hesabı seçmelisiniz!")
                    return
                if src == dst:
                    QMessageBox.warning(self, "Uyarı", "Kaynak ve hedef farklı olmalıdır!")
                    return
                if src == "NAKIT" and dst == "NAKIT":
                    QMessageBox.warning(self, "Uyarı", "Nakit'ten Nakit'e transfer yapılamaz!")
                    return

                # Bankadan nakit çekim
                if dst == "NAKIT":
                    transaction_type = TransactionType.NAKIT_CEKIMI
                    kwargs['bank_account_id'] = src
                # Nakitten bankaya yatırım
                elif src == "NAKIT":
                    transaction_type = TransactionType.NAKIT_YATIRIMI
                    kwargs['bank_account_id'] = dst
                # Normal banka transferi
                else:
                    kwargs['bank_account_id'] = src
                    kwargs['destination_bank_account_id'] = dst
            # Kredi Kartı Ödeme
            elif transaction_type == TransactionType.KREDI_KARTI_ODEME:
                if not self.credit_card_payment_combo.currentData():
                    QMessageBox.warning(self, "Uyarı", "Ödeme yapılacak kredi kartı seçmelisiniz!")
                    return

                if payment_method == PaymentMethod.BANKA:
                    bank_id = self.bank_combo.currentData()
                    if not bank_id or bank_id == "NAKIT":
                        QMessageBox.warning(self, "Uyardı", "Hangi banka hesabından ödeyeceğinizi seçmelisiniz!")
                        return
                    kwargs['bank_account_id'] = bank_id
                elif payment_method == PaymentMethod.KREDI_KARTI:
                    if not self.card_combo.currentData():
                        QMessageBox.warning(self, "Uyarı", "Kredi kartından ödeme için kart seçmelisiniz!")
                        return
                    kwargs['credit_card_id'] = self.card_combo.currentData()
                kwargs['credit_card_id'] = self.credit_card_payment_combo.currentData()
            # Kredi Ödeme
            elif transaction_type == TransactionType.KREDI_ODEME:
                if not self.loan_payment_combo.currentData():
                    QMessageBox.warning(self, "Uyarı", "Ödeme yapılacak kredi seçmelisiniz!")
                    return

                if payment_method == PaymentMethod.BANKA:
                    bank_id = self.bank_combo.currentData()
                    if not bank_id or bank_id == "NAKIT":
                        QMessageBox.warning(self, "Uyardı", "Hangi banka hesabından ödeyeceğinizi seçmelisiniz!")
                        return
                    kwargs['bank_account_id'] = bank_id
                elif payment_method == PaymentMethod.CARI:
                    if not self.cari_combo.currentData():
                        QMessageBox.warning(self, "Uyarı", "Cari hesaptan ödeme için cari seçmelisiniz!")
                        return
                    kwargs['cari_id'] = self.cari_combo.currentData()
                elif payment_method == PaymentMethod.KREDI_KARTI:
                    if not self.card_combo.currentData():
                        QMessageBox.warning(self, "Uyarı", "Kredi kartı ile ödeme için kart seçmelisiniz!")
                        return
                    kwargs['credit_card_id'] = self.card_combo.currentData()
                kwargs['notes'] = f"loan_id:{self.loan_payment_combo.currentData()}"
            else:
                # Diğer işlemler için NAKIT/KREDI_KARTI seçildiğinde cari göster
                if payment_method == PaymentMethod.CARI and self.cari_combo.currentData():
                    kwargs['cari_id'] = self.cari_combo.currentData()
                elif payment_method == PaymentMethod.NAKIT and self.cari_combo.currentData():
                    # NAKIT ödeme: cari hesap seçiliyse ekle
                    kwargs['cari_id'] = self.cari_combo.currentData()
                elif payment_method == PaymentMethod.KREDI_KARTI:
                    # KREDI_KARTI: cari ve kredi kartı
                    if self.cari_combo.currentData():
                        kwargs['cari_id'] = self.cari_combo.currentData()
                    if self.card_combo.currentData():
                        kwargs['credit_card_id'] = self.card_combo.currentData()
                elif payment_method == PaymentMethod.BANKA:
                    bank_id = self.bank_combo.currentData()
                    if not bank_id or bank_id == "NAKIT":
                        QMessageBox.warning(self, "Uyarı", "Banka hesabı seçmelisiniz!")
                        return
                    kwargs['bank_account_id'] = bank_id
            
            if self.is_edit_mode:
                # Güncelleme modu
                kwargs.update({
                    'transaction_date': transaction_date,
                    'transaction_type': transaction_type,
                    'payment_method': payment_method,
                    'customer_name': self.customer_input.text().strip(),
                    'description': self.description_input.toPlainText().strip(),
                    'amount': self.amount_input.value()
                })
                
                success, msg = TransactionService.update_transaction(
                    self.transaction_id,
                    **kwargs
                )
                
                if success:
                    QMessageBox.information(self, "Başarılı", "İşlem başarıyla güncellendi!")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Hata", f"İşlem güncellenemedi: {msg}")
            else:
                # Oluşturma modu - Önce mükerrer kontrol yap
                # Aynı gün, aynı tutar, aynı cari kontrolü
                cari_id = kwargs.get('cari_id')
                duplicate_found = False
                
                db = SessionLocal()
                try:
                    query = db.query(Transaction).filter(
                        Transaction.user_id == self.user_id,
                        Transaction.transaction_date == transaction_date,
                        Transaction.amount == self.amount_input.value()
                    )
                    
                    # Eğer cari_id varsa onu da kontrol et
                    if cari_id:
                        query = query.filter(Transaction.cari_id == cari_id)
                    
                    duplicate = query.first()
                    if duplicate:
                        duplicate_found = True
                        # Mükerrer işlem bulundu, kullanıcıya sor
                        reply = QMessageBox.question(
                            self,
                            "Mükerrer İşlem Uyarısı",
                            f"⚠️ Aynı tarih ({transaction_date.strftime('%d.%m.%Y')}), "
                            f"aynı tutar ({self.amount_input.value():.2f} ₺) "
                            f"ve aynı müşteri ile işlem mevcut!\n\n"
                            f"Mevcut işlem:\n"
                            f"• Müşteri: {duplicate.customer_name}\n"
                            f"• Açıklama: {duplicate.description[:50]}...\n"
                            f"• Tür: {duplicate.transaction_type.value}\n\n"
                            f"Yine de bu işlemi eklemek istiyor musunuz?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        
                        if reply == QMessageBox.No:
                            db.close()
                            return  # İşlemi iptal et
                finally:
                    db.close()
                
                # Mükerrer değilse veya kullanıcı onayladıysa devam et
                transaction, msg = TransactionService.create_transaction(
                    user_id=self.user_id,
                    transaction_date=transaction_date,
                    transaction_type=transaction_type,
                    payment_method=payment_method,
                    customer_name=self.customer_input.text().strip(),
                    description=self.description_input.toPlainText().strip(),
                    amount=self.amount_input.value(),
                    **kwargs
                )
                
                if transaction:
                    QMessageBox.information(self, "Başarılı", 
                        "İşlem başarıyla oluşturuldu!\n\n"
                        "İlgili hesaplar otomatik olarak güncellendi.")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Hata", f"İşlem oluşturulamadı: {msg}")
        
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Beklenmeyen hata: {str(e)}")
            print(f"Transaction save error: {e}")
