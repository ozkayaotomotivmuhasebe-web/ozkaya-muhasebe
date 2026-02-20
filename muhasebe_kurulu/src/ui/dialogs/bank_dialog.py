from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from src.services.bank_service import BankService


class BankDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        """UI başlat"""
        self.setWindowTitle("Yeni Banka Hesabı Ekle")
        self.setMinimumSize(560, 620)
        self.resize(600, 640)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 10pt;
                color: #333;
                padding-bottom: 2px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 10pt;
                min-height: 28px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Başlık
        title = QLabel("🏦 Yeni Banka Hesabı")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Banka Adı
        layout.addWidget(QLabel("Banka Adı *"))
        self.txt_bank_name = QLineEdit()
        self.txt_bank_name.setPlaceholderText("Ziraat Bankası")
        layout.addWidget(self.txt_bank_name)
        
        # Şube
        layout.addWidget(QLabel("Şube"))
        self.txt_branch = QLineEdit()
        self.txt_branch.setPlaceholderText("Ankara Şubesi")
        layout.addWidget(self.txt_branch)
        
        # Hesap Numarası
        layout.addWidget(QLabel("Hesap Numarası *"))
        self.txt_account_number = QLineEdit()
        self.txt_account_number.setPlaceholderText("TR0000000000000000")
        layout.addWidget(self.txt_account_number)
        
        # Para Birimi
        layout.addWidget(QLabel("Para Birimi *"))
        self.combo_currency = QComboBox()
        self.combo_currency.addItems(["TRY", "USD", "EUR", "GBP"])
        layout.addWidget(self.combo_currency)
        
        # Başlangıç Bakiyesi
        layout.addWidget(QLabel("Başlangıç Bakiye *"))
        self.txt_balance = QLineEdit()
        self.txt_balance.setText("0.00")
        self.txt_balance.setPlaceholderText("0.00")
        validator = QDoubleValidator(0.0, 999999999.99, 2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.txt_balance.setValidator(validator)
        layout.addWidget(self.txt_balance)
        
        # Ek Hesap Limiti
        layout.addWidget(QLabel("Ek Hesap Limiti"))
        self.txt_overdraft_limit = QLineEdit()
        self.txt_overdraft_limit.setText("0.00")
        self.txt_overdraft_limit.setPlaceholderText("0.00")
        validator_overdraft = QDoubleValidator(0.0, 999999999.99, 2)
        validator_overdraft.setNotation(QDoubleValidator.StandardNotation)
        self.txt_overdraft_limit.setValidator(validator_overdraft)
        layout.addWidget(self.txt_overdraft_limit)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Kaydet")
        btn_save.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_save.clicked.connect(self.save_bank)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ İptal")
        btn_cancel.setStyleSheet("background-color: #f44336; color: white;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def save_bank(self):
        """Banka hesabı kaydet"""
        # Validasyon
        bank_name = self.txt_bank_name.text().strip()
        branch = self.txt_branch.text().strip()
        account_number = self.txt_account_number.text().strip()
        currency = self.combo_currency.currentText()
        balance_text = self.txt_balance.text().strip()
        overdraft_text = self.txt_overdraft_limit.text().strip()
        
        if not bank_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen banka adı giriniz!")
            return
        
        if not account_number:
            QMessageBox.warning(self, "Uyarı", "Lütfen hesap numarası giriniz!")
            return
        
        try:
            balance = float(balance_text.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçersiz bakiye formatı!")
            return
        
        try:
            overdraft_limit = float(overdraft_text.replace(',', '.')) if overdraft_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçersiz ek hesap limiti formatı!")
            return
        
        if balance < 0:
            QMessageBox.warning(self, "Uyarı", "Bakiye sıfırdan küçük olamaz!")
            return
        
        if overdraft_limit < 0:
            QMessageBox.warning(self, "Uyarı", "Ek hesap limiti sıfırdan küçük olamaz!")
            return
        
        # Kaydet
        try:
            success, msg = BankService.create_account(
                user_id=self.user_id,
                bank_name=bank_name,
                branch=branch or None,
                account_number=account_number,
                balance=balance,
                currency=currency,
                overdraft_limit=overdraft_limit
            )
            
            if success:
                QMessageBox.information(self, "Başarılı", "Banka hesabı eklendi!")
                self.accept()
            else:
                QMessageBox.critical(self, "Hata", msg)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hesap eklenirken hata: {str(e)}")
