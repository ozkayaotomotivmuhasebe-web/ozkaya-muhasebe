from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                           QDialog, QSpinBox, QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit,
                           QLineEdit, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import QHeaderView
from src.database.models import User, InvoiceType
from src.services.invoice_service import InvoiceService
from src.services.cari_service import CariService
from src.services.bank_service import BankService
from src.services.auth_service import AuthService
from src.utils.app_icon import get_app_icon
import config
from datetime import datetime, date, timedelta


class MainWindow(QMainWindow):
    """Ana uygulama penceresi - Optimize edilmiş"""
    
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self.setWindowTitle(f"{config.APP_NAME} - {user.full_name}")
        self.setGeometry(0, 0, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #fafafa; }
            QTabWidget::pane { border: 1px solid #ddd; }
            QTabBar::tab { background-color: #e0e0e0; padding: 8px 15px; }
            QTabBar::tab:selected { background-color: white; }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
            QTableWidget { border: 1px solid #ddd; }
            QHeaderView::section { background-color: #f5f5f5; padding: 5px; }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Sekmeler - Yetkilere göre ekle
        if self.user.can_view_dashboard:
            self.tabs.addTab(self.create_dashboard_tab(), "📊 Dashboard")
        
        if self.user.can_view_invoices:
            self.tabs.addTab(self.create_invoices_tab(), "📄 Faturalar")
        
        if self.user.can_view_caris:
            self.tabs.addTab(self.create_caris_tab(), "📋 Cari Hesaplar")
        
        if self.user.can_view_banks:
            self.tabs.addTab(self.create_bank_tab(), "🏦 Banka Hesapları")
        
        if self.user.can_view_credit_cards:
            self.tabs.addTab(self.create_credit_cards_tab(), "💳 Kredi Kartları")
        
        if self.user.can_view_reports:
            self.tabs.addTab(self.create_reports_tab(), "📊 Raporlar")
        
        # Admin ise kullanıcı yönetimi sekmesi ekle
        if self.user.role == 'admin':
            self.tabs.addTab(self.create_user_management_tab(), "👥 Kullanıcı Yönetimi")
        
        # Ayarlar her zaman görünsün
        self.tabs.addTab(self.create_settings_tab(), "⚙️ Ayarlar")
        
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
            @staticmethod
            def format_tr(val):
                """Türkçe sayı formatı: 7.521,00"""
                try:
                    val_float = float(val)
                except (ValueError, TypeError):
                    return str(val)
                s = f"{val_float:.2f}"
                parts = s.split('.')
                integer_part = parts[0]
                decimal_part = parts[1] if len(parts) > 1 else "00"
                result = ""
                for i, digit in enumerate(reversed(integer_part)):
                    if i > 0 and i % 3 == 0:
                        result = "." + result
                    result = digit + result
                return f"{result},{decimal_part}"
        
        self.showMaximized()
    
    def create_dashboard_tab(self) -> QWidget:
        """Dashboard sekmesi"""
        widget = QWidget()
                    self.lbl_paid_invoices.findChild(QLabel).setText(f"{self.format_tr(stats['paid'])} Ödendi")
                    self.lbl_pending.findChild(QLabel).setText(f"{self.format_tr(stats['unpaid'])} Beklemede")
        # Başlık
        title = QLabel("📊 Kontrol Paneli")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Dashboard cards
        cards_layout = QHBoxLayout()
        
                        self.table_recent.setItem(i, 2, QTableWidgetItem(self.format_tr(inv.total_amount)))
        self.lbl_total_invoices = self.create_dashboard_card("Toplam Faturalar", "0")
        cards_layout.addWidget(self.lbl_total_invoices)
        
        # Ödenen Faturalar
        self.lbl_paid_invoices = self.create_dashboard_card("Ödenen", "0 TRY", "#4CAF50")
        cards_layout.addWidget(self.lbl_paid_invoices)
        
        # Beklemede
        self.lbl_pending = self.create_dashboard_card("Beklemede", "0 TRY", "#FF9800")
        cards_layout.addWidget(self.lbl_pending)
        
        layout.addLayout(cards_layout)
        layout.addSpacing(20)
                    self.table_invoices.setItem(i, 2, QTableWidgetItem(self.format_tr(inv.amount)))
                    self.table_invoices.setItem(i, 3, QTableWidgetItem(self.format_tr(inv.tax_amount)))
        layout.addWidget(QLabel("📋 Son Faturalar"))
        self.table_recent = QTableWidget()
        self.table_recent.setColumnCount(5)
        self.table_recent.setHorizontalHeaderLabels(["Fatura No", "Cari", "Tutar", "Durum", "Tarih"])
        self.table_recent.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_recent.setMaximumHeight(300)
        layout.addWidget(self.table_recent)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Verileri al
        self.refresh_dashboard()
                    self.table_caris.setItem(i, 2, QTableWidgetItem(self.format_tr(cari.balance)))
        return widget
    
    def create_dashboard_card(self, title: str, value: str, color: str = "#2196F3") -> QFrame:
        """Dashboard kartı oluştur"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 4px;
                padding: 15px;
            }}
        """)
                    self.table_banks.setItem(i, 2, QTableWidgetItem(f"{self.format_tr(acc.balance)} {acc.currency}"))
        layout = QVBoxLayout()
        
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Arial", 10, QFont.Bold))
        lbl_title.setStyleSheet("color: #666;")
        layout.addWidget(lbl_title)
        
        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(lbl_value)
        
        card.setLayout(layout)
        return card
    
    def refresh_dashboard(self):
        """Dashboard verileri yenile"""
        try:
            stats = InvoiceService.get_invoice_statistics(self.user.id)
            self.lbl_total_invoices.findChild(QLabel).setText(str(stats['total_invoices']))
            self.lbl_paid_invoices.findChild(QLabel).setText(f"{stats['paid']} Ödendi")
            self.lbl_pending.findChild(QLabel).setText(f"{stats['unpaid']} Beklemede")
            
            # Son faturaları göster
            invoices = InvoiceService.get_user_invoices(self.user.id)[:5]
            self.table_recent.setRowCount(len(invoices))
            
            for i, inv in enumerate(invoices):
                self.table_recent.setItem(i, 0, QTableWidgetItem(inv.invoice_number))
                self.table_recent.setItem(i, 1, QTableWidgetItem(inv.cari.name if inv.cari else ""))
                self.table_recent.setItem(i, 2, QTableWidgetItem(f"{inv.total_amount:.2f}"))
                self.table_recent.setItem(i, 3, QTableWidgetItem(inv.status))
                self.table_recent.setItem(i, 4, QTableWidgetItem(str(inv.created_at.date())))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veri yükleme hatası: {e}")
    
    def create_invoices_tab(self) -> QWidget:
        """Faturalar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("📄 Fatura Yönetimi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Fatura")
        btn_new.clicked.connect(self.show_new_invoice_dialog)
        btn_layout.addWidget(btn_new)
        
        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.clicked.connect(self.refresh_dashboard)
        btn_layout.addWidget(btn_refresh)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Fatura tablosu
        self.table_invoices = QTableWidget()
        self.table_invoices.setColumnCount(6)
        self.table_invoices.setHorizontalHeaderLabels(["Fatura No", "Cari", "Tutar", "Vergisi", "Durum", "İşlem"])
        self.table_invoices.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_invoices.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table_invoices)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.refresh_invoice_table()
        return widget
    
    def refresh_invoice_table(self):
        """Fatura tablosunu yenile"""
        invoices = InvoiceService.get_user_invoices(self.user.id)
        self.table_invoices.setRowCount(len(invoices))
        
        for i, inv in enumerate(invoices):
            self.table_invoices.setItem(i, 0, QTableWidgetItem(inv.invoice_number))
            self.table_invoices.setItem(i, 1, QTableWidgetItem(inv.cari.name if inv.cari else ""))
            self.table_invoices.setItem(i, 2, QTableWidgetItem(f"{inv.amount:.2f}"))
            self.table_invoices.setItem(i, 3, QTableWidgetItem(f"{inv.tax_amount:.2f}"))
            self.table_invoices.setItem(i, 4, QTableWidgetItem(inv.status))
            
            btn_edit = QPushButton("Düzenle")
            self.table_invoices.setCellWidget(i, 5, btn_edit)
    
    def show_new_invoice_dialog(self):
        """Yeni fatura dialog'u"""
        QMessageBox.information(self, "Bilgi", "Yeni fatura oluşturma özelliği yakında eklenecek")
    
    def create_caris_tab(self) -> QWidget:
        """Cari Hesaplar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("📋 Cari Hesap Yönetimi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Cari")
        btn_new.clicked.connect(self.show_new_cari_dialog)
        btn_layout.addWidget(btn_new)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Cari tablosu
        self.table_caris = QTableWidget()
        self.table_caris.setColumnCount(5)
        self.table_caris.setHorizontalHeaderLabels(["Ad", "Tip", "Bakiye", "Telefon", "İşlem"])
        self.table_caris.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_caris)
        
        widget.setLayout(layout)
        self.refresh_cari_table()
        return widget
    
    def refresh_cari_table(self):
        """Cari tablosunu yenile"""
        caris = CariService.get_caris(self.user.id)
        self.table_caris.setRowCount(len(caris))
        
        for i, cari in enumerate(caris):
            self.table_caris.setItem(i, 0, QTableWidgetItem(cari.name))
            self.table_caris.setItem(i, 1, QTableWidgetItem(cari.cari_type))
            self.table_caris.setItem(i, 2, QTableWidgetItem(f"{cari.balance:.2f}"))
            self.table_caris.setItem(i, 3, QTableWidgetItem(cari.phone or ""))
            
            btn_edit = QPushButton("Düzenle")
            self.table_caris.setCellWidget(i, 4, btn_edit)
    
    def show_new_cari_dialog(self):
        """Yeni cari dialog'u"""
        QMessageBox.information(self, "Bilgi", "Yeni cari oluşturma özelliği yakında eklenecek")
    
    def create_bank_tab(self) -> QWidget:
        """Banka Hesapları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("🏦 Banka Hesapları")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Hesap")
        btn_layout.addWidget(btn_new)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Banka tablosu
        self.table_banks = QTableWidget()
        self.table_banks.setColumnCount(4)
        self.table_banks.setHorizontalHeaderLabels(["Banka", "Hesap No", "Bakiye", "İşlem"])
        self.table_banks.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_banks)
        
        widget.setLayout(layout)
        self.refresh_bank_table()
        return widget
    
    def refresh_bank_table(self):
        """Banka tablosunu yenile"""
        accounts = BankService.get_accounts(self.user.id)
        self.table_banks.setRowCount(len(accounts))
        
        for i, acc in enumerate(accounts):
            self.table_banks.setItem(i, 0, QTableWidgetItem(acc.bank_name))
            self.table_banks.setItem(i, 1, QTableWidgetItem(acc.account_number))
            self.table_banks.setItem(i, 2, QTableWidgetItem(f"{acc.balance:.2f} {acc.currency}"))
            
            btn_view = QPushButton("Göster")
            self.table_banks.setCellWidget(i, 3, btn_view)
    
    def create_settings_tab(self) -> QWidget:
        """Ayarlar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("⚙️ Ayarlar")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Kullanıcı bilgileri
        layout.addWidget(QLabel("Kullanıcı Bilgileri:"))
        layout.addWidget(QLabel(f"👤 Ad: {self.user.full_name}"))
        layout.addWidget(QLabel(f"📧 Email: {self.user.email}"))
        layout.addWidget(QLabel(f"👤 Kullanıcı Adı: {self.user.username}"))
        
        layout.addSpacing(20)
        
        # Şifre değiştir butonu
        btn_change_pwd = QPushButton("🔒 Şifre Değiştir")
        btn_change_pwd.clicked.connect(self.show_change_password_dialog)
        layout.addWidget(btn_change_pwd)
        
        layout.addSpacing(20)
        
        # Çıkış butonu
        btn_logout = QPushButton("🚪 Çıkış Yap")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def show_change_password_dialog(self):
        """Şifre değiştir dialog'u"""
        QMessageBox.information(self, "Bilgi", "Şifre değiştirme özelliği yakında eklenecek")
    
    def create_credit_cards_tab(self) -> QWidget:
        """Kredi Kartları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("💳 Kredi Kartları")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Kart")
        btn_layout.addWidget(btn_new)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Kredi kartı tablosu
        self.table_cards = QTableWidget()
        self.table_cards.setColumnCount(5)
        self.table_cards.setHorizontalHeaderLabels(["Kart Adı", "Banka", "Son 4 Hane", "Limit", "Kullanım"])
        self.table_cards.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_cards)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_reports_tab(self) -> QWidget:
        """Raporlar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("📊 Raporlar ve Analizler")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Rapor butonları
        btn_layout = QVBoxLayout()
        
        btn_income = QPushButton("📈 Gelir-Gider Raporu")
        btn_income.setMinimumHeight(40)
        btn_layout.addWidget(btn_income)
        
        btn_cari = QPushButton("📋 Cari Hesap Raporu")
        btn_cari.setMinimumHeight(40)
        btn_layout.addWidget(btn_cari)
        
        btn_bank = QPushButton("🏦 Banka Raporu")
        btn_bank.setMinimumHeight(40)
        btn_layout.addWidget(btn_bank)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_user_management_tab(self) -> QWidget:
        """Kullanıcı Yönetimi sekmesi - Sadece Admin için"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("👥 Kullanıcı Yönetimi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Açıklama
        info = QLabel("Kullanıcıları yönetmek ve yetkilerini düzenlemek için butona tıklayın:")
        info.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(info)
        
        # Kullanıcı yönetimi butonu
        btn_manage = QPushButton("👥 Kullanıcı Yönetimi Panelini Aç")
        btn_manage.setMinimumHeight(50)
        btn_manage.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5568d3; }
        """)
        btn_manage.clicked.connect(self.show_user_management_dialog)
        layout.addWidget(btn_manage)
        
        # Yetkiler hakkında bilgi
        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border-left: 4px solid #2196F3;
                border-radius: 4px;
                padding: 15px;
                margin-top: 20px;
            }
        """)
        info_layout = QVBoxLayout()
        
        info_title = QLabel("ℹ️ Yetki Sistemi Hakkında")
        info_title.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(info_title)
        
        info_text = QLabel(
            "• Her kullanıcı için ayrı ayrı sayfa yetkileri belirleyebilirsiniz\n"
            "• Dashboard, Faturalar, Cari Hesaplar, Banka Hesapları, Kredi Kartları ve Raporlar\n"
            "• Kullanıcı sadece yetkisi olan sayfaları görebilir\n"
            "• Admin rolündeki kullanıcılar varsayılan olarak tüm yetkilere sahiptir"
        )
        info_text.setStyleSheet("color: #333; line-height: 1.5;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        info_box.setLayout(info_layout)
        layout.addWidget(info_box)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def show_user_management_dialog(self):
        """Kullanıcı yönetimi dialogunu göster"""
        from src.ui.dialogs.user_management_dialog import UserManagementDialog
        dialog = UserManagementDialog(self)
        dialog.exec_()
    
    def logout(self):
        """Çıkış yap"""
        reply = QMessageBox.question(self, "Çıkış", "Çıkmak istediğinizden emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
