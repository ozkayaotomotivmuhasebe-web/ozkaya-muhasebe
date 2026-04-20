from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, 
                           QLabel, QLineEdit, QDateEdit, QTextEdit, QMessageBox, QComboBox,
                           QDoubleSpinBox, QSpinBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from src.services.loan_service import LoanService
from src.database.db import SessionLocal
from src.database.models import Loan


class LoanDialog(QDialog):
    """Kredi Ekleme/Düzenleme Dialog'u"""
    
    def __init__(self, user_id, parent=None, loan_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.loan_id = loan_id
        self.is_edit_mode = loan_id is not None
        
        if self.is_edit_mode:
            self.setWindowTitle("Kredi Düzenle")
        else:
            self.setWindowTitle("Yeni Kredi Ekle")
        
        self.setGeometry(150, 100, 620, 600)
        self.setMinimumSize(620, 600)
        self.setModal(True)
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_loan()
    
    def init_ui(self):
        """Arayüz elemanlarını oluştur"""
        self.setStyleSheet("""
            QLabel { font-size: 10pt; }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox, QSpinBox {
                min-height: 32px;
                padding: 6px 8px;
                font-size: 10pt;
            }
            QPushButton { min-height: 32px; font-size: 10pt; }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("💰 Kredi Yönetimi")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #333;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Kredi Adı
        self.loan_name_input = QLineEdit()
        self.loan_name_input.setMinimumHeight(35)
        self.loan_name_input.setPlaceholderText("Örn: Ziraat Bankası - İpotekli Kredi")
        form_layout.addRow("📝 Kredi Adı: <span style=\"color:#d32f2f\">*</span>", self.loan_name_input)
        
        # Banka
        self.bank_name_input = QLineEdit()
        self.bank_name_input.setMinimumHeight(35)
        self.bank_name_input.setPlaceholderText("Örn: Ziraat Bankası")
        form_layout.addRow("🏦 Banka: <span style=\"color:#d32f2f\">*</span>", self.bank_name_input)
        
        # Firma
        self.company_name_input = QLineEdit()
        self.company_name_input.setMinimumHeight(35)
        self.company_name_input.setPlaceholderText("Örn: İnşaat A.Ş., Ticaret Ltd.")
        form_layout.addRow("🏢 Firma: <span style=\"color:#d32f2f\">*</span>", self.company_name_input)
        
        # Kredi Türü
        self.loan_type_combo = QComboBox()
        self.loan_type_combo.setMinimumHeight(35)
        self.loan_type_combo.addItems(["İPOTEK", "TAŞIT", "TÜKETICI", "ESNAF", "TARIM", "DİĞER"])
        form_layout.addRow("📋 Kredi Türü: <span style=\"color:#d32f2f\">*</span>", self.loan_type_combo)
        
        # Kredi Tutarı
        self.loan_amount_input = QDoubleSpinBox()
        self.loan_amount_input.setMinimumHeight(35)
        self.loan_amount_input.setMaximum(999999999.99)
        self.loan_amount_input.setDecimals(2)
        self.loan_amount_input.setSuffix(" ₺")
        self.loan_amount_input.valueChanged.connect(self.on_loan_amount_changed)
        form_layout.addRow("💵 Kredi Tutarı: <span style=\"color:#d32f2f\">*</span>", self.loan_amount_input)

        # Geri Ödenecek Kredi Tutarı (remaining_balance)
        self.remaining_balance_input = QDoubleSpinBox()
        self.remaining_balance_input.setMinimumHeight(35)
        self.remaining_balance_input.setMaximum(999999999.99)
        self.remaining_balance_input.setDecimals(2)
        self.remaining_balance_input.setSuffix(" ₺")
        self.remaining_balance_input.valueChanged.connect(self.on_remaining_balance_changed)
        form_layout.addRow("💳 Geri Ödenecek Kredi Tutarı: <span style=\"color:#d32f2f\">*</span>", self.remaining_balance_input)

        self._remaining_balance_manual = False
        self._setting_remaining_balance = False
        
        # Faiz Oranı
        self.interest_rate_input = QDoubleSpinBox()
        self.interest_rate_input.setMinimumHeight(35)
        self.interest_rate_input.setMaximum(100.00)
        self.interest_rate_input.setDecimals(2)
        self.interest_rate_input.setSuffix(" %")
        form_layout.addRow("📊 Faiz Oranı:", self.interest_rate_input)
        
        # Aylık Taksit
        self.monthly_payment_input = QDoubleSpinBox()
        self.monthly_payment_input.setMinimumHeight(35)
        self.monthly_payment_input.setMaximum(999999999.99)
        self.monthly_payment_input.setDecimals(2)
        self.monthly_payment_input.setSuffix(" ₺")
        form_layout.addRow("📌 Aylık Taksit: <span style=\"color:#d32f2f\">*</span>", self.monthly_payment_input)
        
        # Kredi Başlama Tarihi
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setMinimumHeight(35)
        form_layout.addRow("📅 Başlama Tarihi: <span style=\"color:#d32f2f\">*</span>", self.start_date_input)
        
        # Kredi Bitiş Tarihi
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setMinimumHeight(35)
        form_layout.addRow("🏁 Bitiş Tarihi:", self.end_date_input)
        
        # Ödeme Günü
        self.due_day_input = QSpinBox()
        self.due_day_input.setMinimumHeight(35)
        self.due_day_input.setMinimum(1)
        self.due_day_input.setMaximum(31)
        self.due_day_input.setValue(15)
        form_layout.addRow("⏰ Ödeme Günü (Ayın): <span style=\"color:#d32f2f\">*</span>", self.due_day_input)
        
        # Toplam Taksit Sayısı
        self.total_installments_input = QSpinBox()
        self.total_installments_input.setMinimumHeight(35)
        self.total_installments_input.setMinimum(0)
        self.total_installments_input.setMaximum(600)
        form_layout.addRow("🔢 Toplam Taksit Sayısı:", self.total_installments_input)
        
        # Notlar
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("İlgili notlar...")
        form_layout.addRow("📝 Notlar:", self.notes_input)
        
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
        btn_save.clicked.connect(self.save_loan)
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
    
    def load_loan(self):
        """Mevcut krediyi yükle (düzenleme modu için)"""
        try:
            session = SessionLocal()
            loan = session.query(Loan).filter(Loan.id == self.loan_id).first()
            
            if loan:
                self.loan_name_input.setText(loan.loan_name)
                self.bank_name_input.setText(loan.bank_name)
                self.company_name_input.setText(loan.company_name or "")
                self.loan_type_combo.setCurrentText(loan.loan_type)
                self.loan_amount_input.setValue(float(loan.loan_amount))
                self._setting_remaining_balance = True
                self.remaining_balance_input.setValue(float(loan.remaining_balance or 0.0))
                self._setting_remaining_balance = False
                self._remaining_balance_manual = True
                self.interest_rate_input.setValue(float(loan.interest_rate))
                self.monthly_payment_input.setValue(float(loan.monthly_payment))
                self.due_day_input.setValue(loan.due_day)
                self.total_installments_input.setValue(loan.total_installments or 0)
                
                self.start_date_input.setDate(QDate(
                    loan.start_date.year,
                    loan.start_date.month,
                    loan.start_date.day
                ))
                
                if loan.end_date:
                    self.end_date_input.setDate(QDate(
                        loan.end_date.year,
                        loan.end_date.month,
                        loan.end_date.day
                    ))
                
                if loan.notes:
                    self.notes_input.setPlainText(loan.notes)
            
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kredi yüklenemedi: {str(e)}")

    def on_loan_amount_changed(self, value):
        if self._remaining_balance_manual:
            return
        self._setting_remaining_balance = True
        self.remaining_balance_input.setValue(float(value))
        self._setting_remaining_balance = False

    def on_remaining_balance_changed(self, value):
        if self._setting_remaining_balance:
            return
        self._remaining_balance_manual = abs(float(value) - float(self.loan_amount_input.value())) > 0.0001
    
    def save_loan(self):
        """Krediyi kaydet"""
        # Validasyon
        if not self.loan_name_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Kredi adı gerekli!")
            return
        
        if not self.bank_name_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Banka adı gerekli!")
            return
        
        if not self.company_name_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Firma adı gerekli!")
            return
        
        if self.loan_amount_input.value() <= 0:
            QMessageBox.warning(self, "Uyarı", "Kredi tutarı 0'dan büyük olmalı!")
            return

        if self.remaining_balance_input.value() <= 0:
            QMessageBox.warning(self, "Uyarı", "Geri ödenecek kredi tutarı 0'dan büyük olmalı!")
            return
        
        if self.monthly_payment_input.value() <= 0:
            QMessageBox.warning(self, "Uyarı", "Aylık taksit 0'dan büyük olmalı!")
            return
        
        try:
            start_date = self.start_date_input.date().toPyDate()
            end_date = None
            if self.end_date_input.date().toPyDate() > start_date:
                end_date = self.end_date_input.date().toPyDate()
            
            if self.is_edit_mode:
                # Güncelleme
                success, msg = LoanService.update_loan(
                    self.loan_id,
                    loan_name=self.loan_name_input.text().strip(),
                    bank_name=self.bank_name_input.text().strip(),
                    company_name=self.company_name_input.text().strip(),
                    loan_type=self.loan_type_combo.currentText(),
                    loan_amount=self.loan_amount_input.value(),
                    remaining_balance=self.remaining_balance_input.value(),
                    interest_rate=self.interest_rate_input.value(),
                    monthly_payment=self.monthly_payment_input.value(),
                    due_day=self.due_day_input.value(),
                    total_installments=self.total_installments_input.value() or None,
                    start_date=start_date,
                    end_date=end_date,
                    notes=self.notes_input.toPlainText().strip() or None
                )
                
                if success:
                    QMessageBox.information(self, "Başarılı", "Kredi başarıyla güncellendi!")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Hata", f"Kredi güncellenemedi: {msg}")
            else:
                # Oluşturma
                loan, msg = LoanService.create_loan(
                    user_id=self.user_id,
                    loan_name=self.loan_name_input.text().strip(),
                    bank_name=self.bank_name_input.text().strip(),
                    company_name=self.company_name_input.text().strip(),
                    loan_type=self.loan_type_combo.currentText(),
                    loan_amount=self.loan_amount_input.value(),
                    remaining_balance=self.remaining_balance_input.value(),
                    interest_rate=self.interest_rate_input.value(),
                    monthly_payment=self.monthly_payment_input.value(),
                    due_day=self.due_day_input.value(),
                    total_installments=self.total_installments_input.value() or None,
                    start_date=start_date,
                    end_date=end_date,
                    notes=self.notes_input.toPlainText().strip() or None
                )
                
                if loan:
                    QMessageBox.information(self, "Başarılı", "Kredi başarıyla eklendi!")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Hata", f"Kredi eklenemedi: {msg}")
        
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Beklenmeyen hata: {str(e)}")
            print(f"Loan save error: {e}")
