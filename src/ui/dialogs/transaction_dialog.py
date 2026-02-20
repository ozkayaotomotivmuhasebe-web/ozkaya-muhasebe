from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, 
                           QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit, QMessageBox,
                           QDoubleSpinBox, QRadioButton, QButtonGroup, QGroupBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from src.database.models import TransactionType, PaymentMethod
from src.services.transaction_service import TransactionService
from src.services.cari_service import CariService
from src.services.bank_service import BankService
from src.database.db import SessionLocal
from src.database.models import CreditCard
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
        
        self.setGeometry(150, 100, 760, 680)
        self.setMinimumSize(760, 680)
        self.setModal(True)
        self.init_ui()
        
        # Düzenleme modundaysa işlem verilerini yükle
        if self.is_edit_mode:
            self.load_transaction()
    
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
        
        # Ödeme Yöntemi
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setMinimumHeight(35)
        self.payment_method_combo.addItems(["NAKIT", "BANKA", "KREDI_KARTI", "CARI", "TRANSFER"])
        self.payment_method_combo.currentTextChanged.connect(self.on_payment_method_changed)
        form_layout.addRow("💳 Ödeme Yöntemi: <span style=\"color:#d32f2f\">*</span>", self.payment_method_combo)
        
        # Müşteri/Tedarikçi
        self.customer_input = QLineEdit()
        self.customer_input.setMinimumHeight(35)
        self.customer_input.setPlaceholderText("Müşteri/Tedarikçi adı")
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
        self.load_bank_accounts()
        self.account_layout.addWidget(QLabel("🏦 Banka Hesabı:"))
        self.account_layout.addWidget(self.bank_combo)
        self.bank_combo.setVisible(False)
        self.account_layout.itemAt(self.account_layout.count() - 2).widget().setVisible(False)
        
        # Banka Hesabı Seçimi (Hedef - Transfer için)
        self.destination_bank_combo = QComboBox()
        self.destination_bank_combo.setMinimumHeight(35)
        self.destination_bank_combo.addItem("-- Hedef Hesabı Seçiniz --", None)
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
        
        self.account_group.setLayout(self.account_layout)
        form_layout.addRow(self.account_group)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
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
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())
    
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
            if banks:
                for bank in banks:
                    self.bank_combo.addItem(
                        f"{bank.bank_name} - {bank.account_number} ({bank.balance:.2f} {bank.currency})", 
                        bank.id
                    )
        except Exception as e:
            print(f"Banka yükleme hatası: {e}")
    
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
    
    def on_type_changed(self, transaction_type):
        """İşlem türü değiştiğinde"""
        # TRANSFER işlemlerinde banka hesaplarını göster
        if transaction_type == "TRANSFER":
            self.payment_method_combo.setCurrentText("TRANSFER")
            # Müşteri ünvanını otomatik yap
            self.customer_input.setText("Banka Transferi")
            self.customer_input.setReadOnly(True)
        else:
            self.customer_input.setReadOnly(False)
            
        # Fatura işlemlerinde önce cari görünmeli
        if transaction_type in ["KESILEN_FATURA", "GELEN_FATURA"]:
            # Fatura işlemlerinde cariyi göster
            self.account_layout.itemAt(0).widget().setVisible(True)  # Cari Label
            self.account_layout.itemAt(1).widget().setVisible(True)  # Cari Combo
            # Ödeme yöntemi varsayılan olarak CARI olsun
            self.payment_method_combo.setCurrentText("CARI")
        # Gelir işlemlerinde banka
        elif transaction_type == "GELIR":
            self.payment_method_combo.setCurrentText("BANKA")
    
    def on_payment_method_changed(self, payment_method):
        """Ödeme yöntemi değiştiğinde ilgili hesap alanlarını göster/gizle"""
        transaction_type = self.type_combo.currentText()
        
        # Tüm hesap alanlarını gizle
        for i in range(self.account_layout.count()):
            widget = self.account_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(False)
        
        # TRANSFER ödeme yöntemi - 2 banka hesabı göster
        if payment_method == "TRANSFER":
            self.account_layout.itemAt(2).widget().setVisible(True)  # Banka Label
            self.account_layout.itemAt(3).widget().setVisible(True)  # Banka Combo (Kaynak)
            self.account_layout.itemAt(4).widget().setVisible(True)  # Hedef Banka Label
            self.account_layout.itemAt(5).widget().setVisible(True)  # Hedef Banka Combo
        # FATURA işlemlerinde DAIMA cari göster
        elif transaction_type in ["KESILEN_FATURA", "GELEN_FATURA"]:
            self.account_layout.itemAt(0).widget().setVisible(True)  # Cari Label
            self.account_layout.itemAt(1).widget().setVisible(True)  # Cari Combo
            
            # Eğer ödeme yöntemi BANKA ise hem cari hem banka göster
            if payment_method == "BANKA":
                self.account_layout.itemAt(2).widget().setVisible(True)  # Banka Label
                self.account_layout.itemAt(3).widget().setVisible(True)  # Banka Combo
        else:
            # Diğer işlemler için seçili ödeme yöntemine göre göster
            if payment_method == "CARI":
                self.account_layout.itemAt(0).widget().setVisible(True)  # Label
                self.account_layout.itemAt(1).widget().setVisible(True)  # Combo
            elif payment_method == "NAKIT":
                # NAKIT ödeme: cari göster (yazdığında) veya seç
                self.account_layout.itemAt(0).widget().setVisible(True)  # Cari Label
                self.account_layout.itemAt(1).widget().setVisible(True)  # Cari Combo
            elif payment_method == "KREDI_KARTI":
                # KREDI_KARTI: cari ve kredi kartı göster
                self.account_layout.itemAt(0).widget().setVisible(True)  # Cari Label
                self.account_layout.itemAt(1).widget().setVisible(True)  # Cari Combo
                self.account_layout.itemAt(6).widget().setVisible(True)  # Kredi Kartı Label
                self.account_layout.itemAt(7).widget().setVisible(True)  # Kredi Kartı Combo
            elif payment_method == "BANKA":
                self.account_layout.itemAt(2).widget().setVisible(True)  # Label
                self.account_layout.itemAt(3).widget().setVisible(True)  # Combo
    
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
                
                # Ödeme yöntemi
                self.payment_method_combo.setCurrentText(transaction.payment_method.name)
                
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
            
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem yüklenemedi: {str(e)}")
    
    def save_transaction(self):
        """İşlemi kaydet"""
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
            transaction_type = TransactionType[self.type_combo.currentText()]
            payment_method = PaymentMethod[self.payment_method_combo.currentText()]
            
            kwargs = {
                'subject': self.subject_input.text().strip() or None,
                'person': self.person_input.text().strip() or None,
                'payment_type': payment_method.value
            }
            
            # FATURA işlemlerinde hem cari hem ödeme yöntemi hesabı eklenebilir
            if transaction_type in [TransactionType.KESILEN_FATURA, TransactionType.GELEN_FATURA]:
                # Cari mutlaka olmalı
                if self.cari_combo.currentData():
                    kwargs['cari_id'] = self.cari_combo.currentData()
                else:
                    QMessageBox.warning(self, "Uyarı", "Fatura işlemleri için cari hesap seçmelisiniz!")
                    return
                
                # Eğer ödeme yöntemi BANKA ise banka da ekle
                if payment_method == PaymentMethod.BANKA and self.bank_combo.currentData():
                    kwargs['bank_account_id'] = self.bank_combo.currentData()
            # TRANSFER işlemlerinde 2 banka hesabı gerekli
            elif transaction_type == TransactionType.TRANSFER:
                if not self.bank_combo.currentData():
                    QMessageBox.warning(self, "Uyarı", "Kaynak banka hesabı seçmelisiniz!")
                    return
                if not self.destination_bank_combo.currentData():
                    QMessageBox.warning(self, "Uyarı", "Hedef banka hesabı seçmelisiniz!")
                    return
                if self.bank_combo.currentData() == self.destination_bank_combo.currentData():
                    QMessageBox.warning(self, "Uyarı", "Kaynak ve hedef hesaplar farklı olmalıdır!")
                    return
                
                kwargs['bank_account_id'] = self.bank_combo.currentData()
                kwargs['destination_bank_account_id'] = self.destination_bank_combo.currentData()
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
                elif payment_method == PaymentMethod.BANKA and self.bank_combo.currentData():
                    kwargs['bank_account_id'] = self.bank_combo.currentData()
            
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
                # Oluşturma modu
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
