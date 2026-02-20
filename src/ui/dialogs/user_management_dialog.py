from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                           QTableWidgetItem, QMessageBox, QLabel, QLineEdit, QComboBox,
                           QFormLayout, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.services.admin_service import AdminService
from src.database.db import SessionLocal
from src.database.models import User


class UserManagementDialog(QDialog):
    """Kullanıcı yönetimi dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kullanıcı Yönetimi")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(900, 600)
        self.setModal(True)
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("KULLANICI YÖNETİMİ")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Buton paneli
        btn_layout = QHBoxLayout()
        
        self.btn_new = QPushButton("Yeni Kullanıcı")
        self.btn_new.setMinimumHeight(35)
        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.btn_new.clicked.connect(self.show_new_user_dialog)
        btn_layout.addWidget(self.btn_new)
        
        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.setMinimumHeight(35)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b7dda; }
        """)
        self.btn_edit.clicked.connect(self.show_edit_user_dialog)
        btn_layout.addWidget(self.btn_edit)
        
        self.btn_role = QPushButton("Rol Değiştir")
        self.btn_role.setMinimumHeight(35)
        self.btn_role.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e68a00; }
        """)
        self.btn_role.clicked.connect(self.change_user_role)
        btn_layout.addWidget(self.btn_role)

        self.btn_permissions = QPushButton("Yetkiler")
        self.btn_permissions.setMinimumHeight(35)
        self.btn_permissions.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #546E7A; }
        """)
        self.btn_permissions.clicked.connect(self.show_permissions_dialog)
        btn_layout.addWidget(self.btn_permissions)
        
        self.btn_delete = QPushButton("Sil")
        self.btn_delete.setMinimumHeight(35)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        self.btn_delete.clicked.connect(self.delete_user)
        btn_layout.addWidget(self.btn_delete)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Kullanıcı Tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Kullanıcı Adı", "Ad Soyadı", "E-posta", "Rol", "Durum"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 220)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #eee;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
        """)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_users(self):
        """Kullanıcıları yükle"""
        try:
            users = AdminService.get_all_users()
            self.table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
                self.table.setItem(row, 1, QTableWidgetItem(user.username))
                self.table.setItem(row, 2, QTableWidgetItem(user.full_name))
                self.table.setItem(row, 3, QTableWidgetItem(user.email))
                
                role_text = "Admin" if user.role == 'admin' else "Kullanıcı"
                self.table.setItem(row, 4, QTableWidgetItem(role_text))
                
                status_text = "Aktif" if user.is_active else "Pasif"
                self.table.setItem(row, 5, QTableWidgetItem(status_text))
            
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kullanıcılar yüklenirken hata: {str(e)}")
    
    def get_selected_user(self):
        """Seçili kullanıcıyı al"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Bir kullanıcı seçiniz!")
            return None
        
        row = selected_rows[0].row()
        user_id = int(self.table.item(row, 0).text())
        return user_id, row
    
    def show_new_user_dialog(self):
        """Yeni kullanıcı oluştur dialog"""
        dialog = NewUserDialog(self)
        if dialog.exec_():
            self.load_users()
    
    def show_edit_user_dialog(self):
        """Kullanıcı düzenleme dialog"""
        result = self.get_selected_user()
        if not result:
            return
        
        user_id, row = result
        dialog = EditUserDialog(user_id, self)
        if dialog.exec_():
            self.load_users()
    
    def change_user_role(self):
        """Kullanıcının rolünü değiştir"""
        result = self.get_selected_user()
        if not result:
            return
        
        user_id, row = result
        
        dialog = RoleChangeDialog(user_id, self)
        if dialog.exec_():
            self.load_users()
    
    def delete_user(self):
        """Kullanıcı sil"""
        result = self.get_selected_user()
        if not result:
            return
        
        user_id, row = result
        
        username = self.table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "Onay", 
            f"'{username}' kullanıcısını silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = AdminService.delete_user(user_id)
            if success:
                QMessageBox.information(self, "Başarı", "Kullanıcı silindi")
                self.load_users()
            else:
                QMessageBox.critical(self, "Hata", msg)

    def show_permissions_dialog(self):
        """Kullanıcı yetkilerini düzenle"""
        result = self.get_selected_user()
        if not result:
            return

        user_id, _ = result
        dialog = PermissionsDialog(user_id, self)
        if dialog.exec_():
            self.load_users()


class NewUserDialog(QDialog):
    """Yeni kullanıcı oluştur dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Kullanıcı Oluştur")
        self.setGeometry(150, 150, 400, 300)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        layout = QFormLayout()
        layout.setSpacing(10)
        
        self.input_username = QLineEdit()
        self.input_username.setMinimumHeight(35)
        layout.addRow("Kullanıcı Adı: <span style=\"color:#d32f2f\">*</span>", self.input_username)
        
        self.input_email = QLineEdit()
        self.input_email.setMinimumHeight(35)
        layout.addRow("E-posta: <span style=\"color:#d32f2f\">*</span>", self.input_email)
        
        self.input_fullname = QLineEdit()
        self.input_fullname.setMinimumHeight(35)
        layout.addRow("Ad Soyadı: <span style=\"color:#d32f2f\">*</span>", self.input_fullname)
        
        self.input_password = QLineEdit()
        self.input_password.setMinimumHeight(35)
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addRow("Şifre: <span style=\"color:#d32f2f\">*</span>", self.input_password)
        
        self.combo_role = QComboBox()
        self.combo_role.setMinimumHeight(35)
        self.combo_role.addItems(["Kullanıcı", "Admin"])
        layout.addRow("Rol:", self.combo_role)
        
        btn_layout = QHBoxLayout()
        
        btn_create = QPushButton("Oluştur")
        btn_create.setMinimumHeight(35)
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_create.clicked.connect(self.create_user)
        btn_layout.addWidget(btn_create)
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.setMinimumHeight(35)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addRow("", btn_layout)
        self.setLayout(layout)
    
    def create_user(self):
        """Kullanıcı oluştur"""
        username = self.input_username.text().strip()
        email = self.input_email.text().strip()
        fullname = self.input_fullname.text().strip()
        password = self.input_password.text()
        role = "admin" if self.combo_role.currentText() == "Admin" else "user"
        
        if not all([username, email, fullname, password]):
            QMessageBox.warning(self, "Uyarı", "Tüm alanlar gerekli!")
            return
        
        user, msg = AdminService.create_user(username, email, password, fullname, role)
        if user:
            QMessageBox.information(self, "Başarı", "Kullanıcı oluşturuldu")
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)


class EditUserDialog(QDialog):
    """Kullanıcı düzenleme dialog"""
    
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Kullanıcıyı Düzenle")
        self.setGeometry(150, 150, 400, 200)
        self.setModal(True)
        self.init_ui()
        self.load_user_data()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        layout = QFormLayout()
        layout.setSpacing(10)
        
        self.input_fullname = QLineEdit()
        self.input_fullname.setMinimumHeight(35)
        layout.addRow("Ad Soyadı: <span style=\"color:#d32f2f\">*</span>", self.input_fullname)
        
        self.input_email = QLineEdit()
        self.input_email.setMinimumHeight(35)
        layout.addRow("E-posta: <span style=\"color:#d32f2f\">*</span>", self.input_email)
        
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("Kaydet")
        btn_save.setMinimumHeight(35)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0b7dda; }
        """)
        btn_save.clicked.connect(self.save_user)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.setMinimumHeight(35)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addRow("", btn_layout)
        self.setLayout(layout)
    
    def load_user_data(self):
        """Kullanıcı verilerini yükle ve input'a doldur"""
        from src.database.db import SessionLocal
        from src.database.models import User
        
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == self.user_id).first()
            if user:
                self.input_fullname.setText(user.full_name)
                self.input_email.setText(user.email)
        finally:
            session.close()
    
    def save_user(self):
        """Kullanıcı verilerini kaydet"""
        fullname = self.input_fullname.text().strip()
        email = self.input_email.text().strip()
        
        if not all([fullname, email]):
            QMessageBox.warning(self, "Uyarı", "Tüm alanlar gerekli!")
            return
        
        success, msg = AdminService.update_user(
            self.user_id, 
            full_name=fullname, 
            email=email
        )
        
        if success:
            QMessageBox.information(self, "Başarı", "Kullanıcı güncellendi")
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)


class RoleChangeDialog(QDialog):
    """Rol değiştir dialog"""
    
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Rol Değiştir")
        self.setGeometry(150, 150, 350, 150)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        layout = QFormLayout()
        layout.setSpacing(10)
        
        self.combo_role = QComboBox()
        self.combo_role.setMinimumHeight(35)
        self.combo_role.addItems(["Kullanıcı", "Admin"])
        layout.addRow("Yeni Rol:", self.combo_role)
        
        btn_layout = QHBoxLayout()
        
        btn_change = QPushButton("Değiştir")
        btn_change.setMinimumHeight(35)
        btn_change.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e68a00; }
        """)
        btn_change.clicked.connect(self.change_role)
        btn_layout.addWidget(btn_change)
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.setMinimumHeight(35)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addRow("", btn_layout)
        self.setLayout(layout)
    
    def change_role(self):
        """Rolü değiştir"""
        role = "admin" if self.combo_role.currentText() == "Admin" else "user"
        success, msg = AdminService.set_user_role(self.user_id, role)
        
        if success:
            QMessageBox.information(self, "Başarı", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)


class PermissionsDialog(QDialog):
    """Kullanıcı yetkileri dialog"""

    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Kullanıcı Yetkileri")
        self.setGeometry(200, 200, 360, 300)
        self.setModal(True)
        self.init_ui()
        self.load_permissions()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("Sayfa Yetkileri")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title)

        self.chk_dashboard = QCheckBox("Dashboard")
        self.chk_invoices = QCheckBox("Faturalar")
        self.chk_caris = QCheckBox("Cari Hesaplar")
        self.chk_banks = QCheckBox("Banka Hesapları")
        self.chk_credit_cards = QCheckBox("Kredi Kartları")
        self.chk_reports = QCheckBox("Raporlar")

        layout.addWidget(self.chk_dashboard)
        layout.addWidget(self.chk_invoices)
        layout.addWidget(self.chk_caris)
        layout.addWidget(self.chk_banks)
        layout.addWidget(self.chk_credit_cards)
        layout.addWidget(self.chk_reports)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Kaydet")
        btn_save.setMinimumHeight(32)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_save.clicked.connect(self.save_permissions)
        btn_layout.addWidget(btn_save)

        btn_cancel = QPushButton("İptal")
        btn_cancel.setMinimumHeight(32)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_permissions(self):
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == self.user_id).first()
            if not user:
                QMessageBox.critical(self, "Hata", "Kullanıcı bulunamadı")
                self.reject()
                return

            self.chk_dashboard.setChecked(bool(user.can_view_dashboard))
            self.chk_invoices.setChecked(bool(user.can_view_invoices))
            self.chk_caris.setChecked(bool(user.can_view_caris))
            self.chk_banks.setChecked(bool(user.can_view_banks))
            self.chk_credit_cards.setChecked(bool(user.can_view_credit_cards))
            self.chk_reports.setChecked(bool(user.can_view_reports))
        finally:
            session.close()

    def save_permissions(self):
        success, msg = AdminService.update_user(
            self.user_id,
            can_view_dashboard=self.chk_dashboard.isChecked(),
            can_view_invoices=self.chk_invoices.isChecked(),
            can_view_caris=self.chk_caris.isChecked(),
            can_view_banks=self.chk_banks.isChecked(),
            can_view_credit_cards=self.chk_credit_cards.isChecked(),
            can_view_reports=self.chk_reports.isChecked()
        )

        if success:
            QMessageBox.information(self, "Başarı", "Yetkiler güncellendi")
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)
