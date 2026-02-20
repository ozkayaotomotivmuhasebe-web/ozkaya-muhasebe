from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                           QFrame, QHeaderView, QComboBox, QDateEdit, QLineEdit, QTextBrowser,
                           QScrollArea, QSizePolicy, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from src.database.models import User, TransactionType, PaymentMethod
from src.services.invoice_service import InvoiceService
from src.services.cari_service import CariService
from src.services.bank_service import BankService
from src.services.transaction_service import TransactionService
from src.services.credit_card_service import CreditCardService
from src.services.report_service import ReportService
from src.ui.dialogs.user_management_dialog import UserManagementDialog
from src.services.auth_service import AuthService
from src.services.user_settings_service import UserSettingsService
import config


class MainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"{config.APP_NAME} - {user.full_name} ({user.role.upper()})")
        self.setGeometry(0, 0, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #fafafa; }
            QTabWidget::pane { border: 1px solid #ddd; }
            QTabBar::tab { background-color: #e0e0e0; padding: 10px 16px; min-height: 28px; }
            QTabBar::tab:selected { background-color: white; }
            QLabel { font-size: 10pt; }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                padding: 6px 8px;
                font-size: 10pt;
                min-height: 30px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover { background-color: #1976D2; }
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                font-size: 9pt;
            }
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
        self.dashboard_tab = None
        
        # Dashboard (izinli ise)
        if self.user.can_view_dashboard:
            self.dashboard_tab = self.create_dashboard_tab()
            self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # Rol bazlı sekmeler
        if self.user.role == 'admin':
            self.tabs.addTab(self.create_transactions_tab(), "💰 İşlemler")
            if self.user.can_view_invoices:
                self.tabs.addTab(self.create_invoices_tab(), "📄 Faturalar")
            if self.user.can_view_caris:
                self.tabs.addTab(self.create_caris_tab(), "📋 Cari Hesaplar")
                self.tabs.addTab(self.create_cari_extract_tab(), "📑 Cari Ekstre")
            if self.user.can_view_banks:
                self.tabs.addTab(self.create_bank_tab(), "🏦 Banka Hesapları")
            if self.user.can_view_credit_cards:
                self.tabs.addTab(self.create_credit_cards_tab(), "💳 Kredi Kartları")
            if self.user.can_view_reports:
                self.tabs.addTab(self.create_reports_tab(), "📊 Raporlar")
            self.tabs.addTab(self.create_admin_panel_tab(), "👨‍💼 Admin Panel")
        else:
            # Normal kullanıcılar sadece izin verilenleri görebilir
            self.tabs.addTab(self.create_transactions_tab(), "💰 İşlemler")
            if self.user.can_view_invoices:
                self.tabs.addTab(self.create_invoices_tab(), "📄 Faturalar")
            if self.user.can_view_caris:
                self.tabs.addTab(self.create_caris_tab(), "📋 Cari Hesaplar")
                self.tabs.addTab(self.create_cari_extract_tab(), "📑 Cari Ekstre")
            if self.user.can_view_banks:
                self.tabs.addTab(self.create_bank_tab(), "🏦 Banka Hesapları")
            if self.user.can_view_credit_cards:
                self.tabs.addTab(self.create_credit_cards_tab(), "💳 Kredi Kartları")
            if self.user.can_view_reports:
                self.tabs.addTab(self.create_reports_tab(), "📊 Raporlar")
        
        self.tabs.addTab(self.create_settings_tab(), "⚙️ Ayarlar")
        
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        
        self.showMaximized()

    def _resize_table(self, table):
        """Tablo kolon/satırlarını içerige göre ayarla"""
        if table is None:
            return
        table.setWordWrap(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setDefaultSectionSize(28)

    def _get_dashboard_card_defs(self):
        return [
            ("total_invoices", "Toplam Fatura", "#2196F3"),
            ("total_cari", "Toplam Cari", "#4CAF50"),
            ("total_income", "Toplam Gelir", "#009688"),
            ("total_expense", "Toplam Gider", "#f44336"),
            ("bank_total_balance", "Banka Toplam Bakiye", "#3F51B5"),
            ("credit_card_total_debt", "Kredi Kartı Toplam Borç", "#FF9800"),
        ]

    def _get_dashboard_card_keys(self):
        default_keys = [key for key, _, _ in self._get_dashboard_card_defs()]
        keys = UserSettingsService.get_json_setting(self.user.id, "dashboard_cards", None)
        if not keys:
            UserSettingsService.set_json_setting(self.user.id, "dashboard_cards", default_keys)
            return default_keys
        return keys

    def _set_dashboard_card_value(self, key, value):
        if not hasattr(self, "dashboard_cards"):
            return
        card = self.dashboard_cards.get(key)
        if not card:
            return
        labels = card.findChildren(QLabel)
        if len(labels) > 1:
            labels[1].setText(value)
    
    def create_dashboard_tab(self) -> QWidget:
        """Dashboard sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık
        title = QLabel(f"Hoşgeldiniz, {self.user.username}!")
        title.setFont(QFont("SegoeUI", 24, QFont.Bold))
        title.setStyleSheet("color: #333;")
        layout.addWidget(title)
        
        # Dashboard cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.dashboard_cards = {}
        selected_keys = set(self._get_dashboard_card_keys())
        for key, title_text, color in self._get_dashboard_card_defs():
            if key not in selected_keys:
                continue
            card = self.create_stat_card(title_text, "0", color)
            self.dashboard_cards[key] = card
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)
        
        # İki tablo yan yana
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(20)
        
        # Sol: Son Faturalar
        left_layout = QVBoxLayout()
        left_title = QLabel("Son Faturalar (Son 10)")
        left_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left_title.setStyleSheet("color: #333; margin-bottom: 5px;")
        left_layout.addWidget(left_title)
        
        self.table_recent = QTableWidget()
        self.table_recent.setColumnCount(6)
        self.table_recent.setHorizontalHeaderLabels(["Tarih", "Müşteri", "Ürün", "İşlem", "Miktar", "İşlemler"])
        self.table_recent.horizontalHeader().setStretchLastSection(False)
        self.table_recent.setColumnWidth(0, 90)
        self.table_recent.setColumnWidth(1, 180)
        self.table_recent.setColumnWidth(2, 180)
        self.table_recent.setColumnWidth(3, 120)
        self.table_recent.setColumnWidth(4, 100)
        self.table_recent.setColumnWidth(5, 140)
        self.table_recent.setStyleSheet("QTableWidget { border: 1px solid #ddd; border-radius: 4px; }")
        left_layout.addWidget(self.table_recent)
        
        # Sağ: Bekleyen Faturalar
        right_layout = QVBoxLayout()
        right_title = QLabel("Bekleyen Ödemeler")
        right_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        right_title.setStyleSheet("color: #d32f2f; margin-bottom: 5px;")
        right_layout.addWidget(right_title)
        
        self.table_pending = QTableWidget()
        self.table_pending.setColumnCount(6)
        self.table_pending.setHorizontalHeaderLabels(["Müşteri", "Ürün", "İşlem", "Miktar", "Birim", "İşlemler"])
        self.table_pending.horizontalHeader().setStretchLastSection(False)
        self.table_pending.setColumnWidth(0, 180)
        self.table_pending.setColumnWidth(1, 180)
        self.table_pending.setColumnWidth(2, 120)
        self.table_pending.setColumnWidth(3, 100)
        self.table_pending.setColumnWidth(4, 80)
        self.table_pending.setColumnWidth(5, 140)
        self.table_pending.setStyleSheet("QTableWidget { border: 2px solid #ffcdd2; border-radius: 4px; }")
        right_layout.addWidget(self.table_pending)
        
        tables_layout.addLayout(left_layout, 1)
        tables_layout.addLayout(right_layout, 1)
        
        layout.addLayout(tables_layout)
        layout.addStretch()
        widget.setLayout(layout)
        
        self.refresh_dashboard()
        return widget
    
    def create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """İstatistik kartı oluştur"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 0px;
            }}
        """)
        card.setMinimumHeight(120)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 11))
        lbl_title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Segoe UI", 32, QFont.Bold))
        lbl_value.setStyleSheet("color: white;")
        layout.addWidget(lbl_value)
        
        card.setLayout(layout)
        return card
    
    def refresh_dashboard(self):
        """Dashboard verileri yenile"""
        try:
            from src.database.db import SessionLocal
            from src.database.models import Transaction, TransactionType, BankAccount, CreditCard
            from sqlalchemy import func
            
            session = SessionLocal()
            
            # Transaction tablosundan fatura istatistiklerini al
            all_transactions = session.query(Transaction).filter_by(user_id=self.user.id).all()
            
            # Fatura işlemlerini filtrele
            invoice_transactions = [t for t in all_transactions if t.transaction_type in [
                TransactionType.KESILEN_FATURA, 
                TransactionType.GELEN_FATURA
            ]]
            
            # Cari hesapları al
            caris = CariService.get_caris(self.user.id)
            
            # İstatistikleri güncelle
            total_invoices = len(invoice_transactions)
            total_cari = len(caris) if caris else 0

            total_income = sum(
                t.amount for t in all_transactions
                if t.transaction_type in [TransactionType.GELIR, TransactionType.KESILEN_FATURA]
            )
            total_expense = sum(
                t.amount for t in all_transactions
                if t.transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA]
            )

            bank_total_balance = session.query(BankAccount).filter(
                BankAccount.user_id == self.user.id,
                BankAccount.is_active == True
            ).with_entities(func.sum(BankAccount.balance)).scalar() or 0.0

            credit_card_total_debt = session.query(CreditCard).filter(
                CreditCard.user_id == self.user.id,
                CreditCard.is_active == True
            ).with_entities(func.sum(CreditCard.current_debt)).scalar() or 0.0

            self._set_dashboard_card_value("total_invoices", str(total_invoices))
            self._set_dashboard_card_value("total_cari", str(total_cari))
            self._set_dashboard_card_value("total_income", f"{total_income:,.2f} ₺")
            self._set_dashboard_card_value("total_expense", f"{total_expense:,.2f} ₺")
            self._set_dashboard_card_value("bank_total_balance", f"{bank_total_balance:,.2f} ₺")
            self._set_dashboard_card_value("credit_card_total_debt", f"{credit_card_total_debt:,.2f} ₺")
            
            # Son 10 işlemi göster (tüm işlemler)
            recent = sorted(all_transactions, key=lambda x: x.transaction_date, reverse=True)[:10]
            self.table_recent.setRowCount(len(recent))
            
            for i, trans in enumerate(recent):
                # Tarih
                self.table_recent.setItem(i, 0, QTableWidgetItem(str(trans.transaction_date)))
                
                # Müşteri (Cari)
                cari_name = trans.cari.name if trans.cari else "-"
                self.table_recent.setItem(i, 1, QTableWidgetItem(cari_name))
                
                # Ürün (Açıklama)
                product = trans.description[:30] if trans.description else "-"
                self.table_recent.setItem(i, 2, QTableWidgetItem(product))
                
                # İşlem (İşlem Türü)
                islem_tr = {
                    'GELIR': 'Gelir',
                    'GIDER': 'Gider',
                    'KESILEN_FATURA': 'Kesilen Fatura',
                    'GELEN_FATURA': 'Gelen Fatura',
                    'KREDI_ODEME': 'Kredi Ödeme',
                    'KREDI_KARTI_ODEME': 'KK Ödeme'
                }.get(trans.transaction_type.value, trans.transaction_type.value)
                self.table_recent.setItem(i, 3, QTableWidgetItem(islem_tr))
                
                # Miktar
                self.table_recent.setItem(i, 4, QTableWidgetItem(f"{trans.amount:,.2f} ₺"))

                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                action_layout.setSpacing(5)
                action_layout.setAlignment(Qt.AlignCenter)
                action_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                btn_edit = QPushButton("✏️ Düzenle")
                btn_edit.setMinimumHeight(24)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #1976D2; }
                """)
                btn_edit.clicked.connect(lambda checked, tid=trans.id: self.edit_transaction(tid))
                action_layout.addWidget(btn_edit)

                btn_delete = QPushButton("🗑️ Sil")
                btn_delete.setMinimumHeight(24)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #da190b; }
                """)
                btn_delete.clicked.connect(lambda checked, tid=trans.id: self.delete_transaction(tid))
                action_layout.addWidget(btn_delete)

                self.table_recent.setCellWidget(i, 5, action_widget)
            
            # Bekleyen işlemler - son 10 fatura işlemi
            recent_invoices = sorted(invoice_transactions, key=lambda x: x.transaction_date, reverse=True)[:10]
            self.table_pending.setRowCount(len(recent_invoices))
            
            for i, trans in enumerate(recent_invoices):
                # Müşteri
                cari_name = trans.cari.name if trans.cari else "-"
                self.table_pending.setItem(i, 0, QTableWidgetItem(cari_name))
                
                # Ürün (Açıklama)
                product = trans.description[:30] if trans.description else "-"
                self.table_pending.setItem(i, 1, QTableWidgetItem(product))
                
                # İşlem
                islem_type = "Kesilen" if trans.transaction_type == TransactionType.KESILEN_FATURA else "Gelen"
                self.table_pending.setItem(i, 2, QTableWidgetItem(islem_type))
                
                # Miktar
                self.table_pending.setItem(i, 3, QTableWidgetItem(f"{trans.amount:,.2f} ₺"))
                
                # Birim (Ödeme Yöntemi)
                payment = {
                    'NAKIT': 'Nakit',
                    'BANKA': 'Banka',
                    'KREDI_KARTI': 'Kredi Kartı',
                    'CARI': 'Cari'
                }.get(trans.payment_method.value, trans.payment_method.value)
                self.table_pending.setItem(i, 4, QTableWidgetItem(payment))

                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                action_layout.setSpacing(5)
                action_layout.setAlignment(Qt.AlignCenter)
                action_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                btn_edit = QPushButton("✏️ Düzenle")
                btn_edit.setMinimumHeight(24)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #1976D2; }
                """)
                btn_edit.clicked.connect(lambda checked, tid=trans.id: self.edit_transaction(tid))
                action_layout.addWidget(btn_edit)

                btn_delete = QPushButton("🗑️ Sil")
                btn_delete.setMinimumHeight(24)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #da190b; }
                """)
                btn_delete.clicked.connect(lambda checked, tid=trans.id: self.delete_transaction(tid))
                action_layout.addWidget(btn_delete)

                self.table_pending.setCellWidget(i, 5, action_widget)
            
            self._resize_table(self.table_recent)
            self._resize_table(self.table_pending)
            session.close()
        except Exception as e:
            print(f"Dashboard hata: {e}")
            import traceback
            traceback.print_exc()
    
    def create_transactions_tab(self) -> QWidget:
        """İşlemler sekmesi - Excel tarzı"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("💰 Tüm İşlemler")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #333;")
        layout.addWidget(title)
        
        # Filtre ve buton paneli
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Tarih filtreleri
        filter_layout.addWidget(QLabel("Başlangıç:"))
        self.start_date_filter = QDateEdit()
        self.start_date_filter.setCalendarPopup(True)
        self.start_date_filter.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_filter.setMinimumHeight(30)
        filter_layout.addWidget(self.start_date_filter)
        
        filter_layout.addWidget(QLabel("Bitiş:"))
        self.end_date_filter = QDateEdit()
        self.end_date_filter.setCalendarPopup(True)
        self.end_date_filter.setDate(QDate.currentDate())
        self.end_date_filter.setMinimumHeight(30)
        filter_layout.addWidget(self.end_date_filter)
        
        # Filtre uygula butonu
        btn_filter = QPushButton("🔍 Filtrele")
        btn_filter.setMinimumHeight(30)
        btn_filter.clicked.connect(self.apply_transaction_filter)
        filter_layout.addWidget(btn_filter)
        
        filter_layout.addStretch()
        
        # Yeni işlem butonu
        btn_new_transaction = QPushButton("➕ Yeni İşlem")
        btn_new_transaction.setMinimumHeight(35)
        btn_new_transaction.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_new_transaction.clicked.connect(self.show_new_transaction_dialog)
        filter_layout.addWidget(btn_new_transaction)
        
        # Yenile
        btn_refresh_transactions = QPushButton("🔄 Yenile")
        btn_refresh_transactions.setMinimumHeight(35)
        btn_refresh_transactions.clicked.connect(self.refresh_transactions_table)
        filter_layout.addWidget(btn_refresh_transactions)
        
        btn_import_transactions = QPushButton("📥 Excel'den Aktar")
        btn_import_transactions.setMinimumHeight(35)
        btn_import_transactions.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #546E7A; }
        """)
        btn_import_transactions.clicked.connect(self.import_transactions_from_excel)
        filter_layout.addWidget(btn_import_transactions)
        
        layout.addLayout(filter_layout)
        
        # İşlemler tablosu - Excel tarzı
        self.table_transactions = QTableWidget()
        self.table_transactions.setColumnCount(9)
        self.table_transactions.setHorizontalHeaderLabels([
            "TARİH", "TÜR", "MÜŞTERİ ÜNVANI", "AÇIKLAMA", 
            "ÖDEME ŞEKLİ", "KONU", "ÖDEYEN KİŞİ", "TUTAR", "İŞLEMLER"
        ])
        
        # Tablo stilleri
        self.table_transactions.setAlternatingRowColors(True)
        self.table_transactions.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_transactions.setSelectionMode(QTableWidget.SingleSelection)
        self.table_transactions.horizontalHeader().setStretchLastSection(False)
        
        # Kolon genişlikleri - optimize edilmiş
        self.table_transactions.setColumnWidth(0, 90)   # Tarih
        self.table_transactions.setColumnWidth(1, 140)  # Tür
        self.table_transactions.setColumnWidth(2, 180)  # Müşteri
        self.table_transactions.setColumnWidth(3, 220)  # Açıklama
        self.table_transactions.setColumnWidth(4, 100)  # Ödeme Şekli
        self.table_transactions.setColumnWidth(5, 100)  # Konu
        self.table_transactions.setColumnWidth(6, 100)  # Ödeyen
        self.table_transactions.setColumnWidth(7, 110)  # Tutar
        self.table_transactions.setColumnWidth(8, 160)  # İşlemler
        
        self.table_transactions.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #e0e0e0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #2c5f8d;
                color: white;
                padding: 8px;
                border: 1px solid #1e4564;
                font-weight: bold;
            self._resize_table(self.table_recent)
            self._resize_table(self.table_pending)
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #cce5ff;
                color: black;
            }
        """)
        
        layout.addWidget(self.table_transactions)
        
        widget.setLayout(layout)
        self.refresh_transactions_table()
        return widget
    
    def refresh_transactions_table(self):
        """İşlemler tablosunu yenile"""
        try:
            transactions = TransactionService.get_all_transactions(self.user.id)
            self.table_transactions.setRowCount(len(transactions))
            
            for i, trans in enumerate(transactions):
                # Tarih
                date_item = QTableWidgetItem(str(trans.transaction_date))
                self.table_transactions.setItem(i, 0, date_item)
                
                # Tür
                type_text = trans.transaction_type.value if trans.transaction_type else ""
                type_item = QTableWidgetItem(type_text)
                # Renklendirme
                if trans.transaction_type in [TransactionType.GELIR, TransactionType.KESILEN_FATURA]:
                    type_item.setBackground(Qt.green)
                elif trans.transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA]:
                    type_item.setBackground(Qt.red)
                self.table_transactions.setItem(i, 1, type_item)
                
                # Müşteri
                self.table_transactions.setItem(i, 2, QTableWidgetItem(trans.customer_name))
                
                # Açıklama
                self.table_transactions.setItem(i, 3, QTableWidgetItem(trans.description))
                
                # Ödeme Şekli
                payment_text = trans.payment_method.value if trans.payment_method else ""
                self.table_transactions.setItem(i, 4, QTableWidgetItem(payment_text))
                
                # Konu
                self.table_transactions.setItem(i, 5, QTableWidgetItem(trans.subject or ""))
                
                # Ödeyen Kişi
                self.table_transactions.setItem(i, 6, QTableWidgetItem(trans.person or ""))
                
                # Tutar
                amount_item = QTableWidgetItem(f"{trans.amount:,.2f} ₺")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_transactions.setItem(i, 7, amount_item)
                
                # İşlemler butonları - Düzenle ve Sil
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                action_layout.setSpacing(5)
                action_layout.setAlignment(Qt.AlignCenter)
                action_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                
                # Düzenle butonu
                btn_edit = QPushButton("✏️ Düzenle")
                btn_edit.setMinimumHeight(25)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #1976D2; }
                """)
                btn_edit.setProperty('transaction_id', trans.id)
                btn_edit.clicked.connect(lambda checked, tid=trans.id: self.edit_transaction(tid))
                action_layout.addWidget(btn_edit)
                
                # Sil butonu
                btn_delete = QPushButton("🗑️ Sil")
                btn_delete.setMinimumHeight(25)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #da190b; }
                """)
                btn_delete.setProperty('transaction_id', trans.id)
                btn_delete.clicked.connect(lambda checked, tid=trans.id: self.delete_transaction(tid))
                action_layout.addWidget(btn_delete)
                
                self.table_transactions.setCellWidget(i, 8, action_widget)
            
            self._resize_table(self.table_transactions)
                
        except Exception as e:
            print(f"İşlemler yükleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"İşlemler yüklenirken hata: {str(e)}")
    
    def apply_transaction_filter(self):
        """Tarih filtresini uygula"""
        try:
            start_date = self.start_date_filter.date().toPyDate()
            end_date = self.end_date_filter.date().toPyDate()
            
            transactions = TransactionService.get_all_transactions(
                self.user.id, start_date, end_date
            )
            
            # Tabloyu güncelle (aynı kod yukarıdaki gibi)
            self.table_transactions.setRowCount(len(transactions))
            for i, trans in enumerate(transactions):
                self.table_transactions.setItem(i, 0, QTableWidgetItem(str(trans.transaction_date)))
                type_item = QTableWidgetItem(trans.transaction_type.value)
                if trans.transaction_type in [TransactionType.GELIR, TransactionType.KESILEN_FATURA]:
                    type_item.setBackground(Qt.green)
                elif trans.transaction_type in [TransactionType.GIDER, TransactionType.GELEN_FATURA]:
                    type_item.setBackground(Qt.red)
                self.table_transactions.setItem(i, 1, type_item)
                self.table_transactions.setItem(i, 2, QTableWidgetItem(trans.customer_name))
                self.table_transactions.setItem(i, 3, QTableWidgetItem(trans.description))
                self.table_transactions.setItem(i, 4, QTableWidgetItem(trans.payment_method.value))
                self.table_transactions.setItem(i, 5, QTableWidgetItem(trans.subject or ""))
                self.table_transactions.setItem(i, 6, QTableWidgetItem(trans.person or ""))
                amount_item = QTableWidgetItem(f"{trans.amount:,.2f} ₺")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_transactions.setItem(i, 7, amount_item)
                
                # İşlemler butonları
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                action_layout.setSpacing(5)
                action_layout.setAlignment(Qt.AlignCenter)
                action_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                
                btn_edit = QPushButton("✏️ Düzenle")
                btn_edit.setMinimumHeight(25)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #1976D2; }
                """)
                btn_edit.clicked.connect(lambda checked, tid=trans.id: self.edit_transaction(tid))
                action_layout.addWidget(btn_edit)
                
                btn_delete = QPushButton("🗑️ Sil")
                btn_delete.setMinimumHeight(25)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #da190b; }
                """)
                btn_delete.clicked.connect(lambda checked, tid=trans.id: self.delete_transaction(tid))
                action_layout.addWidget(btn_delete)
                
                self.table_transactions.setCellWidget(i, 8, action_widget)
            
            self._resize_table(self.table_transactions)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Filtreleme hatası: {str(e)}")
    
    def show_new_transaction_dialog(self):
        """Yeni işlem ekleme dialog'unu göster"""
        from src.ui.dialogs.transaction_dialog import TransactionDialog
        dialog = TransactionDialog(self.user.id, self)
        if dialog.exec_():
            self.refresh_all_data()
    
    def edit_transaction(self, transaction_id):
        """İşlem düzenle"""
        from src.ui.dialogs.transaction_dialog import TransactionDialog
        dialog = TransactionDialog(self.user.id, self, transaction_id=transaction_id)
        if dialog.exec_():
            self.refresh_all_data()
    
    def delete_transaction(self, transaction_id):
        """İşlem sil"""
        reply = QMessageBox.question(
            self, "Onay", 
            "Bu işlemi silmek istediğinize emin misiniz?\n\nİlgili hesaplar otomatik olarak güncellenecek.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = TransactionService.delete_transaction(transaction_id)
            if success:
                QMessageBox.information(self, "Başarılı", "İşlem silindi ve hesaplar güncellendi")
                self.refresh_all_data()
            else:
                QMessageBox.critical(self, "Hata", f"İşlem silinemedi: {msg}")
    
    def create_invoices_tab(self) -> QWidget:
        """Faturalar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("📄 Fatura Yönetimi")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Fatura")
        btn_new.clicked.connect(self.show_new_invoice_dialog)
        btn_layout.addWidget(btn_new)
        
        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.clicked.connect(self.refresh_invoice_table)
        btn_layout.addWidget(btn_refresh)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table_invoices = QTableWidget()
        self.table_invoices.setColumnCount(5)
        self.table_invoices.setHorizontalHeaderLabels(["Fatura No", "Cari", "Tutar", "Durum", "Tarih"])
        self.table_invoices.horizontalHeader().setStretchLastSection(False)
        self.table_invoices.setColumnWidth(0, 120)
        self.table_invoices.setColumnWidth(1, 250)
        self.table_invoices.setColumnWidth(2, 120)
        self.table_invoices.setColumnWidth(3, 100)
        self.table_invoices.setColumnWidth(4, 100)
        layout.addWidget(self.table_invoices)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.refresh_invoice_table()
        return widget
    
    def refresh_invoice_table(self):
        """Fatura tablosunu yenile - Transaction modelinden fatura işlemlerini göster"""
        try:
            from src.database.db import SessionLocal
            from src.database.models import Transaction, TransactionType, Cari
            
            session = SessionLocal()
            
            # KESILEN_FATURA ve GELEN_FATURA işlemlerini getir
            invoices = session.query(Transaction).filter(
                Transaction.user_id == self.user.id,
                Transaction.transaction_type.in_([TransactionType.KESILEN_FATURA, TransactionType.GELEN_FATURA])
            ).order_by(Transaction.transaction_date.desc()).all()
            
            self.table_invoices.setRowCount(len(invoices))
            
            for i, inv in enumerate(invoices):
                # Fatura numarası (ya da ID)
                invoice_no = inv.invoice_number if hasattr(inv, 'invoice_number') and inv.invoice_number else f"F-{inv.id}"
                self.table_invoices.setItem(i, 0, QTableWidgetItem(invoice_no))
                
                # Cari adı
                cari_name = inv.cari.name if inv.cari else "-"
                self.table_invoices.setItem(i, 1, QTableWidgetItem(cari_name))
                
                # Tutar
                self.table_invoices.setItem(i, 2, QTableWidgetItem(f"{inv.amount:.2f} TL"))
                
                # Durum (Fatura türü)
                status = "Kesilen" if inv.transaction_type == TransactionType.KESILEN_FATURA else "Gelen"
                self.table_invoices.setItem(i, 3, QTableWidgetItem(status))
                
                # Tarih
                self.table_invoices.setItem(i, 4, QTableWidgetItem(str(inv.transaction_date)))
            
            self._resize_table(self.table_invoices)
            session.close()
        except Exception as e:
            print(f"Fatura yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def show_new_invoice_dialog(self):
        """Yeni fatura dialog'u - İşlemler sekmesine yönlendir"""
        # İşlemler sekmesine geç (index 1)
        self.tabs.setCurrentIndex(1)
        
        # Bilgi mesajı göster
        QMessageBox.information(
            self, 
            "Fatura Ekleme", 
            "Fatura eklemek için aşağıdaki 'Yeni İşlem' butonunu kullanarak:\n\n"
            "• Kesilen Fatura (Müşteriye kestiniz)\n"
            "• Gelen Fatura (Tedarikçiden geldi)\n\n"
            "türlerinden birini seçerek fatura ekleyebilirsiniz."
        )
    
    def create_caris_tab(self) -> QWidget:
        """Cari Hesaplar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("📋 Cari Hesap Yönetimi")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Cari")
        btn_new.clicked.connect(self.show_new_cari_dialog)
        btn_layout.addWidget(btn_new)
        
        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.clicked.connect(self.refresh_cari_table)
        btn_layout.addWidget(btn_refresh)
        
        btn_import_caris = QPushButton("📥 Excel'den Aktar")
        btn_import_caris.clicked.connect(self.import_caris_from_excel)
        btn_layout.addWidget(btn_import_caris)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table_caris = QTableWidget()
        self.table_caris.setColumnCount(5)
        self.table_caris.setHorizontalHeaderLabels(["Ad", "Tip", "Bakiye", "Telefon", "İşlemler"])
        self.table_caris.horizontalHeader().setStretchLastSection(False)
        self.table_caris.setColumnWidth(0, 300)
        self.table_caris.setColumnWidth(1, 150)
        self.table_caris.setColumnWidth(2, 130)
        self.table_caris.setColumnWidth(3, 150)
        self.table_caris.setColumnWidth(4, 140)
        layout.addWidget(self.table_caris)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.refresh_cari_table()
        return widget
    
    def refresh_cari_table(self):
        """Cari tablosunu yenile"""
        try:
            caris = CariService.get_caris(self.user.id)
            print(f"Cari sayısı: {len(caris) if caris else 0}")
            self.table_caris.setRowCount(len(caris) if caris else 0)
            
            if caris:
                for i, cari in enumerate(caris):
                    print(f"Cari {i}: {cari.name} - {cari.cari_type}")
                    self.table_caris.setItem(i, 0, QTableWidgetItem(cari.name))
                    self.table_caris.setItem(i, 1, QTableWidgetItem(cari.cari_type))
                    self.table_caris.setItem(i, 2, QTableWidgetItem(f"{cari.balance:.2f}"))
                    self.table_caris.setItem(i, 3, QTableWidgetItem(cari.phone or ""))

                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 2, 5, 2)
                    action_layout.setSpacing(5)
                    action_layout.setAlignment(Qt.AlignCenter)
                    action_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                    btn_edit = QPushButton("✏️ Düzenle")
                    btn_edit.setMinimumHeight(24)
                    btn_edit.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            padding: 4px 8px;
                            font-size: 9pt;
                            font-weight: bold;
                        }
                        QPushButton:hover { background-color: #0b7dda; }
                    """)
                    btn_edit.clicked.connect(lambda checked, cid=cari.id: self.show_edit_cari_dialog(cid))
                    action_layout.addWidget(btn_edit)

                    btn_delete = QPushButton("🗑️ Sil")
                    btn_delete.setMinimumHeight(24)
                    btn_delete.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            padding: 4px 8px;
                            font-size: 9pt;
                            font-weight: bold;
                        }
                        QPushButton:hover { background-color: #da190b; }
                    """)
                    btn_delete.clicked.connect(lambda checked, cid=cari.id: self.delete_cari(cid))
                    action_layout.addWidget(btn_delete)

                    self.table_caris.setCellWidget(i, 4, action_widget)
                print("Cari tablosu başarıyla güncellendi")
            else:
                print("Hiç cari hesap bulunamadı!")
            
            self._resize_table(self.table_caris)
            
            # Cari Ekstre dropdown'ını da güncelle
            if hasattr(self, 'cari_extract_combo'):
                self.cari_extract_combo.clear()
                self.cari_extract_combo.addItem("-- Cari Seçiniz --", None)
                if caris:
                    for cari in caris:
                        self.cari_extract_combo.addItem(f"{cari.name} ({cari.cari_type})", cari.id)
                print("Cari Ekstre dropdown güncellendi")
        except Exception as e:
            print(f"Cari yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def show_new_cari_dialog(self):
        """Yeni cari dialog'u"""
        from src.ui.dialogs.cari_dialog import CariDialog
        dialog = CariDialog(self.user.id, self)
        if dialog.exec_():
            self.refresh_all_data()

    def show_edit_cari_dialog(self, cari_id):
        """Cari düzenleme dialog'u"""
        from src.ui.dialogs.cari_dialog import CariDialog
        dialog = CariDialog(self.user.id, self, cari_id=cari_id)
        if dialog.exec_():
            self.refresh_all_data()

    def delete_cari(self, cari_id):
        """Cari sil (pasif et)"""
        reply = QMessageBox.question(
            self,
            "Onay",
            "Bu cariyi silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = CariService.delete_cari(cari_id)
            if success:
                QMessageBox.information(self, "Başarılı", "Cari silindi")
                self.refresh_all_data()
            else:
                QMessageBox.critical(self, "Hata", msg)
    
    def create_bank_tab(self) -> QWidget:
        """Banka Hesapları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("🏦 Banka Hesapları")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Hesap")
        btn_new.clicked.connect(self.show_new_bank_dialog)
        btn_layout.addWidget(btn_new)
        
        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.clicked.connect(self.refresh_bank_table)
        btn_layout.addWidget(btn_refresh)
        
        btn_import_banks = QPushButton("📥 Excel'den Aktar")
        btn_import_banks.clicked.connect(self.import_banks_from_excel)
        btn_layout.addWidget(btn_import_banks)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table_banks = QTableWidget()
        self.table_banks.setColumnCount(6)
        self.table_banks.setHorizontalHeaderLabels(["Banka", "Hesap No", "Bakiye", "Ek Hesap Limiti", "Para Birimi", "İşlemler"])
        self.table_banks.horizontalHeader().setStretchLastSection(False)
        self.table_banks.setColumnWidth(0, 180)
        self.table_banks.setColumnWidth(1, 220)
        self.table_banks.setColumnWidth(2, 120)
        self.table_banks.setColumnWidth(3, 130)
        self.table_banks.setColumnWidth(4, 100)
        self.table_banks.setColumnWidth(5, 140)
        layout.addWidget(self.table_banks)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        self.refresh_bank_table()
        return widget
    
    def refresh_bank_table(self):
        """Banka tablosunu yenile"""
        try:
            accounts = BankService.get_accounts(self.user.id)
            self.table_banks.setRowCount(len(accounts) if accounts else 0)
            
            if accounts:
                for i, acc in enumerate(accounts):
                    self.table_banks.setItem(i, 0, QTableWidgetItem(acc.bank_name))
                    self.table_banks.setItem(i, 1, QTableWidgetItem(acc.account_number))
                    self.table_banks.setItem(i, 2, QTableWidgetItem(f"{acc.balance:,.2f} ₺"))
                    
                    # Ek hesap limiti
                    overdraft = getattr(acc, 'overdraft_limit', 0.0)
                    self.table_banks.setItem(i, 3, QTableWidgetItem(f"{overdraft:,.2f} ₺"))
                    
                    self.table_banks.setItem(i, 4, QTableWidgetItem(acc.currency))

                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 2, 5, 2)
                    action_layout.setSpacing(5)
                    action_layout.setAlignment(Qt.AlignCenter)
                    action_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                    btn_edit = QPushButton("✏️ Düzenle")
                    btn_edit.setMinimumHeight(24)
                    btn_edit.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            padding: 4px 8px;
                            font-size: 9pt;
                            font-weight: bold;
                        }
                        QPushButton:hover { background-color: #0b7dda; }
                    """)
                    btn_edit.clicked.connect(lambda checked, bid=acc.id: self.show_edit_bank_dialog(bid))
                    action_layout.addWidget(btn_edit)

                    btn_delete = QPushButton("🗑️ Sil")
                    btn_delete.setMinimumHeight(24)
                    btn_delete.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            padding: 4px 8px;
                            font-size: 9pt;
                            font-weight: bold;
                        }
                        QPushButton:hover { background-color: #da190b; }
                    """)
                    btn_delete.clicked.connect(lambda checked, bid=acc.id: self.delete_bank(bid))
                    action_layout.addWidget(btn_delete)

                    self.table_banks.setCellWidget(i, 5, action_widget)
            
            self._resize_table(self.table_banks)
        except Exception as e:
            print(f"Banka yükleme hatası: {e}")
    
    def show_new_bank_dialog(self):
        """Yeni banka hesabı dialog'u"""
        from src.ui.dialogs.bank_dialog import BankDialog
        dialog = BankDialog(self.user.id, self)
        if dialog.exec_():
            self.refresh_all_data()

    def show_edit_bank_dialog(self, account_id):
        """Banka hesabı düzenleme dialog'u"""
        from src.ui.dialogs.bank_dialog import BankDialog
        dialog = BankDialog(self.user.id, self, account_id=account_id)
        if dialog.exec_():
            self.refresh_all_data()

    def delete_bank(self, account_id):
        """Banka hesabı sil (pasif et)"""
        reply = QMessageBox.question(
            self,
            "Onay",
            "Bu banka hesabını silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = BankService.delete_account(account_id)
            if success:
                QMessageBox.information(self, "Başarılı", "Banka hesabı silindi")
                self.refresh_all_data()
            else:
                QMessageBox.critical(self, "Hata", msg)
    
    def create_admin_panel_tab(self) -> QWidget:
        """Admin Panel sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("👨‍💼 Admin Panel")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #333;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━"))
        layout.addSpacing(10)
        
        # Kullanıcı Yönetimi
        user_mgmt_title = QLabel("Kullanıcı Yönetimi")
        user_mgmt_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(user_mgmt_title)
        
        btn_user_mgmt = QPushButton("👥 Kullanıcıları Yönet")
        btn_user_mgmt.setMinimumHeight(40)
        btn_user_mgmt.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
            }
            QPushButton:hover { background-color: #5568d3; }
        """)
        btn_user_mgmt.clicked.connect(self.show_user_management)
        layout.addWidget(btn_user_mgmt)
        
        layout.addSpacing(20)
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━"))
        layout.addSpacing(10)
        
        # Sistem İstatistikleri
        stats_title = QLabel("Sistem İstatistikleri")
        stats_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(stats_title)
        
        try:
            from src.services.admin_service import AdminService
            users = AdminService.get_all_users()
            total_users = len(users) if users else 0
            admin_users = len([u for u in users if u.role == 'admin']) if users else 0
            active_users = len([u for u in users if u.is_active]) if users else 0
            
            stats_info = QLabel(f"""
Toplam Kullanıcı: {total_users}
Admin Sayısı: {admin_users}
Aktif Kullanıcı: {active_users}
Pasif Kullanıcı: {total_users - active_users}
            """.strip())
            stats_info.setFont(QFont("Segoe UI", 11))
            stats_info.setStyleSheet("color: #555; background-color: #f5f5f5; padding: 10px; border-radius: 4px;")
            layout.addWidget(stats_info)
        except Exception as e:
            print(f"Admin stats hata: {e}")
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def show_user_management(self):
        """Kullanıcı yönetimi dialog'unu aç"""
        dialog = UserManagementDialog(self)
        dialog.exec_()
    
    def create_settings_tab(self) -> QWidget:
        """Ayarlar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("⚙️ Ayarlar")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━"))
        
        # Kullanıcı Bilgileri
        info_title = QLabel("👤 Kullanıcı Bilgileri")
        info_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(info_title)
        
        layout.addWidget(QLabel(f"Ad: {self.user.full_name}"))
        layout.addWidget(QLabel(f"Email: {self.user.email}"))
        layout.addWidget(QLabel(f"Kullanıcı Adı: {self.user.username}"))
        
        layout.addSpacing(15)
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━"))
        layout.addSpacing(15)

        # Dashboard Kutucuklari
        dashboard_title = QLabel("📊 Dashboard Kutucuklari")
        dashboard_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(dashboard_title)

        self.dashboard_card_checks = {}
        selected_keys = set(self._get_dashboard_card_keys())
        for key, title_text, _ in self._get_dashboard_card_defs():
            chk = QCheckBox(title_text)
            chk.setChecked(key in selected_keys)
            self.dashboard_card_checks[key] = chk
            layout.addWidget(chk)

        btn_save_dashboard = QPushButton("💾 Dashboard Ayarlarini Kaydet")
        btn_save_dashboard.setMinimumHeight(36)
        btn_save_dashboard.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #546E7A; }
        """)
        btn_save_dashboard.clicked.connect(self.save_dashboard_preferences)
        layout.addWidget(btn_save_dashboard)
        
        # Veri Yedekleme
        backup_title = QLabel("💾 Veri Yedekleme")
        backup_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(backup_title)
        
        btn_db_backup = QPushButton("🗄️ Veritabanını Yedekle")
        btn_db_backup.setMinimumHeight(40)
        btn_db_backup.clicked.connect(self.backup_database)
        layout.addWidget(btn_db_backup)
        
        btn_excel_backup = QPushButton("📥 Tüm Verileri Excel'e Yedekle")
        btn_excel_backup.setMinimumHeight(40)
        btn_excel_backup.clicked.connect(self.export_all_data_to_excel)
        layout.addWidget(btn_excel_backup)
        
        layout.addSpacing(15)
        layout.addWidget(QLabel("━━━━━━━━━━━━━━━━━"))
        layout.addSpacing(15)
        
        # Butonlar
        btn_change_pwd = QPushButton("🔒 Şifre Değiştir")
        btn_change_pwd.setMinimumHeight(40)
        btn_change_pwd.clicked.connect(self.show_change_password_dialog)
        layout.addWidget(btn_change_pwd)
        
        layout.addSpacing(20)
        
        btn_logout = QPushButton("🚪 Çıkış Yap")
        btn_logout.setMinimumHeight(40)
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

    def save_dashboard_preferences(self):
        """Dashboard kutucuk tercihlerini kaydet"""
        if not hasattr(self, "dashboard_card_checks"):
            return

        selected = [
            key for key, chk in self.dashboard_card_checks.items()
            if chk.isChecked()
        ]

        if not selected:
            QMessageBox.warning(self, "Uyari", "En az bir kutucuk secmelisiniz!")
            return

        UserSettingsService.set_json_setting(self.user.id, "dashboard_cards", selected)
        self.rebuild_dashboard_tab()
        QMessageBox.information(self, "Basarili", "Dashboard ayarlari guncellendi")

    def rebuild_dashboard_tab(self):
        """Dashboard sekmesini yeniden olustur"""
        if not self.user.can_view_dashboard:
            return

        index = self.tabs.indexOf(self.dashboard_tab) if self.dashboard_tab else -1
        if index == -1:
            index = 0
        else:
            self.tabs.removeTab(index)

        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.insertTab(index, self.dashboard_tab, "📊 Dashboard")
        self.tabs.setCurrentIndex(index)
    
    def show_change_password_dialog(self):
        """Şifre değiştir dialog'u"""
        QMessageBox.information(self, "Bilgi", "Şifre değiştirme özelliği yakında eklenecek")
    
    def backup_database(self):
        """Veritabanini dosya olarak yedekle"""
        try:
            from pathlib import Path
            from datetime import datetime
            from PyQt5.QtWidgets import QFileDialog
            import shutil
            import config
            
            db_path = Path(config.DATABASE_DIR) / "muhasebe.db"
            if not db_path.exists():
                QMessageBox.warning(self, "Uyarı", "Veritabani dosyasi bulunamadi!")
                return
            
            default_name = f"muhasebe_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Veritabani Yedegi Kaydet",
                default_name,
                "SQLite DB (*.db)"
            )
            
            if not file_path:
                return
            
            shutil.copy2(db_path, file_path)
            copied_extra = []
            for suffix in ["-wal", "-shm"]:
                extra_src = Path(str(db_path) + suffix)
                if extra_src.exists():
                    extra_dst = Path(file_path).with_suffix(Path(file_path).suffix + suffix)
                    shutil.copy2(extra_src, extra_dst)
                    copied_extra.append(extra_dst.name)
            
            msg = f"Yedek olusturuldu:\n{file_path}"
            if copied_extra:
                msg += f"\nEk dosyalar: {', '.join(copied_extra)}"
            QMessageBox.information(self, "Basarili", msg)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veritabani yedeklenirken hata:\n{str(e)}")
    
    def _safe_value(self, value):
        if hasattr(value, "value"):
            return value.value
        return value
    
    def _write_sheet(self, ws, headers, rows):
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        
        header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")
        )
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = header_fill
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        for row_idx, row in enumerate(rows, 2):
            for col_idx, value in enumerate(row, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = border
        
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        ws.column_dimensions["A"].width = 16
    
    def export_all_data_to_excel(self):
        """Tum verileri Excel'e yedekle"""
        try:
            from datetime import datetime, date
            from PyQt5.QtWidgets import QFileDialog
            from openpyxl import Workbook
            from src.database.db import SessionLocal
            from src.database.models import (
                User, BankAccount, Cari, Invoice, InvoiceLineItem,
                BankTransaction, Report, CreditCard, Transaction
            )
            
            default_name = f"tum_veriler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Excel Yedegi Kaydet",
                default_name,
                "Excel Dosyasi (*.xlsx)"
            )
            if not file_path:
                return
            
            wb = Workbook()
            session = SessionLocal()
            
            # Users
            ws = wb.active
            ws.title = "Users"
            users = session.query(User).all()
            rows = []
            for u in users:
                rows.append([
                    u.id, u.username, u.email, u.full_name, u.role,
                    u.can_view_dashboard, u.can_view_invoices, u.can_view_caris,
                    u.can_view_banks, u.can_view_reports, u.is_active,
                    u.created_at, u.last_login
                ])
            self._write_sheet(ws, [
                "id", "username", "email", "full_name", "role",
                "can_view_dashboard", "can_view_invoices", "can_view_caris",
                "can_view_banks", "can_view_reports", "is_active",
                "created_at", "last_login"
            ], rows)
            
            # Bank Accounts
            ws = wb.create_sheet("BankAccounts")
            accounts = session.query(BankAccount).all()
            rows = []
            for a in accounts:
                rows.append([
                    a.id, a.user_id, a.bank_name, a.account_number, a.iban,
                    a.branch, a.balance, a.overdraft_limit, a.currency,
                    a.is_active, a.created_at
                ])
            self._write_sheet(ws, [
                "id", "user_id", "bank_name", "account_number", "iban",
                "branch", "balance", "overdraft_limit", "currency",
                "is_active", "created_at"
            ], rows)
            
            # Caris
            ws = wb.create_sheet("Caris")
            caris = session.query(Cari).all()
            rows = []
            for c in caris:
                rows.append([
                    c.id, c.user_id, c.name, c.cari_type, c.tax_number, c.email,
                    c.phone, c.address, c.city, c.balance, c.is_active, c.created_at
                ])
            self._write_sheet(ws, [
                "id", "user_id", "name", "cari_type", "tax_number", "email",
                "phone", "address", "city", "balance", "is_active", "created_at"
            ], rows)
            
            # Invoices
            ws = wb.create_sheet("Invoices")
            invoices = session.query(Invoice).all()
            rows = []
            for inv in invoices:
                rows.append([
                    inv.id, inv.user_id, inv.cari_id, inv.bank_account_id,
                    inv.invoice_number, inv.invoice_date, inv.due_date,
                    self._safe_value(inv.invoice_type), inv.amount, inv.tax_rate,
                    inv.tax_amount, inv.total_amount, inv.description,
                    inv.paid_amount, inv.status, inv.created_at, inv.updated_at
                ])
            self._write_sheet(ws, [
                "id", "user_id", "cari_id", "bank_account_id",
                "invoice_number", "invoice_date", "due_date", "invoice_type",
                "amount", "tax_rate", "tax_amount", "total_amount",
                "description", "paid_amount", "status", "created_at", "updated_at"
            ], rows)
            
            # Invoice Line Items
            ws = wb.create_sheet("InvoiceItems")
            items = session.query(InvoiceLineItem).all()
            rows = []
            for it in items:
                rows.append([
                    it.id, it.invoice_id, it.description, it.quantity,
                    it.unit_price, it.total
                ])
            self._write_sheet(ws, [
                "id", "invoice_id", "description", "quantity", "unit_price", "total"
            ], rows)
            
            # Bank Transactions
            ws = wb.create_sheet("BankTransactions")
            btx = session.query(BankTransaction).all()
            rows = []
            for bt in btx:
                rows.append([
                    bt.id, bt.user_id, bt.bank_account_id, bt.invoice_id,
                    bt.transaction_date, bt.amount, bt.transaction_type,
                    bt.category, bt.description, bt.reference
                ])
            self._write_sheet(ws, [
                "id", "user_id", "bank_account_id", "invoice_id",
                "transaction_date", "amount", "transaction_type",
                "category", "description", "reference"
            ], rows)
            
            # Reports
            ws = wb.create_sheet("Reports")
            reports = session.query(Report).all()
            rows = []
            for r in reports:
                rows.append([
                    r.id, r.user_id, r.report_type, r.title, r.generated_at,
                    r.start_date, r.end_date, r.data
                ])
            self._write_sheet(ws, [
                "id", "user_id", "report_type", "title", "generated_at",
                "start_date", "end_date", "data"
            ], rows)
            
            # Credit Cards
            ws = wb.create_sheet("CreditCards")
            cards = session.query(CreditCard).all()
            rows = []
            for card in cards:
                rows.append([
                    card.id, card.user_id, card.card_name, card.card_number_last4,
                    card.card_holder, card.bank_name, card.card_limit, card.current_debt,
                    card.available_limit, card.closing_day, card.due_day,
                    card.is_active, card.created_at
                ])
            self._write_sheet(ws, [
                "id", "user_id", "card_name", "card_number_last4",
                "card_holder", "bank_name", "card_limit", "current_debt",
                "available_limit", "closing_day", "due_day", "is_active", "created_at"
            ], rows)
            
            # Transactions
            ws = wb.create_sheet("Transactions")
            transactions = session.query(Transaction).all()
            rows = []
            for t in transactions:
                rows.append([
                    t.id, t.user_id, t.transaction_date,
                    self._safe_value(t.transaction_type), self._safe_value(t.payment_method),
                    t.cari_id, t.bank_account_id, t.credit_card_id,
                    t.customer_name, t.description, t.subject, t.payment_type,
                    t.amount, t.person, t.notes, t.created_at, t.updated_at
                ])
            self._write_sheet(ws, [
                "id", "user_id", "transaction_date", "transaction_type", "payment_method",
                "cari_id", "bank_account_id", "credit_card_id",
                "customer_name", "description", "subject", "payment_type",
                "amount", "person", "notes", "created_at", "updated_at"
            ], rows)
            
            session.close()
            wb.save(file_path)
            QMessageBox.information(self, "Basarili", f"Excel yedegi olusturuldu:\n{file_path}")
        except ImportError:
            QMessageBox.critical(self, "Hata", "openpyxl kutuphanesi bulunamadi. Lutfen 'pip install openpyxl' komutunu calistirin.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel yedegi olusturulurken hata:\n{str(e)}")

    def _normalize_header(self, value):
        if value is None:
            return ""
        text = str(value).strip().lower()
        text = text.replace(" ", "_")
        text = text.replace("-", "_")
        text = text.replace("(", "").replace(")", "")
        return text

    def _read_excel_rows(self, file_path):
        from openpyxl import load_workbook
        wb = load_workbook(file_path, data_only=True)
        ws = wb.active
        headers = []
        rows = []
        for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if i == 1:
                headers = [self._normalize_header(h) for h in row]
                continue
            if not row or all(cell is None for cell in row):
                continue
            row_dict = {}
            for idx, cell in enumerate(row):
                if idx < len(headers) and headers[idx]:
                    row_dict[headers[idx]] = cell
            rows.append(row_dict)
        return rows

    def _get_row_value(self, row, keys, default=None):
        for key in keys:
            if key in row and row[key] is not None:
                return row[key]
        return default

    def _parse_float(self, value, default=0.0):
        if value is None or value == "":
            return default
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip()
        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")
        try:
            return float(text)
        except Exception:
            return default

    def _parse_date(self, value):
        from datetime import datetime, date
        if value is None:
            return None
        if isinstance(value, date):
            return value
        text = str(value).strip()
        for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"]:
            try:
                return datetime.strptime(text, fmt).date()
            except Exception:
                continue
        return None

    def import_transactions_from_excel(self):
        """Excel'den toplu islem aktar"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            from src.database.models import TransactionType, PaymentMethod
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Islemler Excel Dosyasi Sec",
                "",
                "Excel Dosyasi (*.xlsx)"
            )
            if not file_path:
                return
            
            rows = self._read_excel_rows(file_path)
            if not rows:
                QMessageBox.warning(self, "Uyari", "Excel dosyasinda veri bulunamadi")
                return
            
            success = 0
            errors = []
            for idx, row in enumerate(rows, start=2):
                tarih = self._get_row_value(row, ["tarih", "transaction_date", "islem_tarihi"])
                islem_turu = self._get_row_value(row, ["islem_turu", "transaction_type", "tur"])
                odeme = self._get_row_value(row, ["odeme_yontemi", "payment_method", "odeme"])
                musteri = self._get_row_value(row, ["musteri_unvani", "customer_name", "musteri"])
                aciklama = self._get_row_value(row, ["aciklama", "description"]) 
                tutar = self._get_row_value(row, ["tutar", "amount"])
                
                if not (tarih and islem_turu and odeme and musteri and aciklama and tutar is not None):
                    errors.append(f"Satir {idx}: zorunlu alan eksik")
                    continue
                
                date_value = self._parse_date(tarih)
                if not date_value:
                    errors.append(f"Satir {idx}: tarih formati hatali")
                    continue
                
                amount = self._parse_float(tutar, None)
                if amount is None:
                    errors.append(f"Satir {idx}: tutar hatali")
                    continue
                
                ttype_raw = str(islem_turu).strip().upper().replace(" ", "_")
                ptype_raw = str(odeme).strip().upper().replace(" ", "_")
                
                if ttype_raw not in TransactionType.__members__:
                    errors.append(f"Satir {idx}: islem_turu gecersiz")
                    continue
                if ptype_raw not in PaymentMethod.__members__:
                    errors.append(f"Satir {idx}: odeme_yontemi gecersiz")
                    continue
                
                subject = self._get_row_value(row, ["konu", "subject"], None)
                person = self._get_row_value(row, ["odeyen_kisi", "person"], None)
                cari_id = self._get_row_value(row, ["cari_id"], None)
                bank_account_id = self._get_row_value(row, ["bank_account_id"], None)
                credit_card_id = self._get_row_value(row, ["credit_card_id"], None)
                
                kwargs = {
                    "subject": subject,
                    "person": person,
                }
                if cari_id:
                    kwargs["cari_id"] = int(cari_id)
                if bank_account_id:
                    kwargs["bank_account_id"] = int(bank_account_id)
                if credit_card_id:
                    kwargs["credit_card_id"] = int(credit_card_id)
                
                result, msg = TransactionService.create_transaction(
                    self.user.id,
                    date_value,
                    TransactionType[ttype_raw],
                    PaymentMethod[ptype_raw],
                    str(musteri),
                    str(aciklama),
                    amount,
                    **kwargs
                )
                if result:
                    success += 1
                else:
                    errors.append(f"Satir {idx}: {msg}")
            
            self.refresh_all_data()
            msg = f"Aktarim tamamlandi. Basarili: {success}"
            if errors:
                msg += f"\nHata: {len(errors)} (ilk 5)\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "Bilgi", msg)
        except ImportError:
            QMessageBox.critical(self, "Hata", "openpyxl kutuphanesi bulunamadi. Lutfen 'pip install openpyxl' komutunu calistirin.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel aktarim hatasi:\n{str(e)}")

    def import_caris_from_excel(self):
        """Excel'den toplu cari aktar"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Cari Excel Dosyasi Sec",
                "",
                "Excel Dosyasi (*.xlsx)"
            )
            if not file_path:
                return
            
            rows = self._read_excel_rows(file_path)
            if not rows:
                QMessageBox.warning(self, "Uyari", "Excel dosyasinda veri bulunamadi")
                return
            
            success = 0
            errors = []
            for idx, row in enumerate(rows, start=2):
                name = self._get_row_value(row, ["name", "cari_adi", "ad"])
                if not name:
                    errors.append(f"Satir {idx}: cari adi eksik")
                    continue
                cari_type = self._get_row_value(row, ["cari_type", "tip"], "MÜŞTERİ")
                phone = self._get_row_value(row, ["phone", "telefon"], None)
                email = self._get_row_value(row, ["email", "e_posta"], None)
                address = self._get_row_value(row, ["address", "adres"], None)
                balance = self._parse_float(self._get_row_value(row, ["balance", "bakiye"], 0.0), 0.0)
                
                ok, msg = CariService.create_cari(
                    self.user.id,
                    str(name),
                    str(cari_type),
                    email=email,
                    phone=phone,
                    address=address,
                    balance=balance
                )
                if ok:
                    success += 1
                else:
                    errors.append(f"Satir {idx}: {msg}")
            
            self.refresh_all_data()
            msg = f"Aktarim tamamlandi. Basarili: {success}"
            if errors:
                msg += f"\nHata: {len(errors)} (ilk 5)\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "Bilgi", msg)
        except ImportError:
            QMessageBox.critical(self, "Hata", "openpyxl kutuphanesi bulunamadi. Lutfen 'pip install openpyxl' komutunu calistirin.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel aktarim hatasi:\n{str(e)}")

    def import_banks_from_excel(self):
        """Excel'den toplu banka aktar"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Banka Excel Dosyasi Sec",
                "",
                "Excel Dosyasi (*.xlsx)"
            )
            if not file_path:
                return
            
            rows = self._read_excel_rows(file_path)
            if not rows:
                QMessageBox.warning(self, "Uyari", "Excel dosyasinda veri bulunamadi")
                return
            
            success = 0
            errors = []
            for idx, row in enumerate(rows, start=2):
                bank_name = self._get_row_value(row, ["bank_name", "banka_adi", "banka"])
                account_number = self._get_row_value(row, ["account_number", "hesap_no"])
                if not bank_name or not account_number:
                    errors.append(f"Satir {idx}: banka_adi veya hesap_no eksik")
                    continue
                
                iban = self._get_row_value(row, ["iban"], None)
                branch = self._get_row_value(row, ["branch", "sube"], None)
                currency = self._get_row_value(row, ["currency", "para_birimi"], "TRY")
                balance = self._parse_float(self._get_row_value(row, ["balance", "bakiye"], 0.0), 0.0)
                overdraft = self._parse_float(self._get_row_value(row, ["overdraft_limit", "ek_hesap_limiti"], 0.0), 0.0)
                
                ok, msg = BankService.create_account(
                    self.user.id,
                    str(bank_name),
                    str(account_number),
                    iban=iban,
                    currency=str(currency),
                    balance=balance,
                    branch=branch,
                    overdraft_limit=overdraft
                )
                if ok:
                    success += 1
                else:
                    errors.append(f"Satir {idx}: {msg}")
            
            self.refresh_all_data()
            msg = f"Aktarim tamamlandi. Basarili: {success}"
            if errors:
                msg += f"\nHata: {len(errors)} (ilk 5)\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "Bilgi", msg)
        except ImportError:
            QMessageBox.critical(self, "Hata", "openpyxl kutuphanesi bulunamadi. Lutfen 'pip install openpyxl' komutunu calistirin.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel aktarim hatasi:\n{str(e)}")

    def import_credit_cards_from_excel(self):
        """Excel'den toplu kredi karti aktar"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Kredi Karti Excel Dosyasi Sec",
                "",
                "Excel Dosyasi (*.xlsx)"
            )
            if not file_path:
                return
            
            rows = self._read_excel_rows(file_path)
            if not rows:
                QMessageBox.warning(self, "Uyari", "Excel dosyasinda veri bulunamadi")
                return
            
            success = 0
            errors = []
            for idx, row in enumerate(rows, start=2):
                card_name = self._get_row_value(row, ["card_name", "kart_adi", "kart"])
                card_number = self._get_row_value(row, ["card_number_last4", "son4", "card_number"], None)
                card_holder = self._get_row_value(row, ["card_holder", "kart_sahibi"], None)
                bank_name = self._get_row_value(row, ["bank_name", "banka_adi", "banka"], None)
                card_limit = self._parse_float(self._get_row_value(row, ["card_limit", "limit"], None), None)
                
                if not (card_name and card_number and card_holder and bank_name and card_limit is not None):
                    errors.append(f"Satir {idx}: zorunlu alan eksik")
                    continue
                
                card_number_str = str(card_number)
                last4 = card_number_str[-4:]
                closing_day = self._get_row_value(row, ["closing_day", "kesim_gunu"], 1)
                due_day = self._get_row_value(row, ["due_day", "odeme_gunu"], 15)
                
                result, msg = CreditCardService.create_card(
                    self.user.id,
                    str(card_name),
                    str(last4),
                    str(card_holder),
                    str(bank_name),
                    float(card_limit),
                    closing_day=int(closing_day),
                    due_day=int(due_day)
                )
                if result:
                    success += 1
                else:
                    errors.append(f"Satir {idx}: {msg}")
            
            self.refresh_all_data()
            msg = f"Aktarim tamamlandi. Basarili: {success}"
            if errors:
                msg += f"\nHata: {len(errors)} (ilk 5)\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "Bilgi", msg)
        except ImportError:
            QMessageBox.critical(self, "Hata", "openpyxl kutuphanesi bulunamadi. Lutfen 'pip install openpyxl' komutunu calistirin.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel aktarim hatasi:\n{str(e)}")
    
    def refresh_all_data(self):
        """Tüm tabloları ve dashboard'u yenile"""
        try:
            self.refresh_transactions_table()
            self.refresh_dashboard()
            
            # Cari tablosu varsa yenile
            if hasattr(self, 'table_caris'):
                print("Cari tablosu yenileniyor...")
                self.refresh_cari_table()
            else:
                print("UYARI: table_caris henüz oluşturulmamış!")
            
            # Fatura tablosu varsa yenile
            if hasattr(self, 'table_invoices'):
                self.refresh_invoice_table()
            
            # Banka tablosu varsa yenile
            if hasattr(self, 'table_banks'):
                self.refresh_bank_table()
            
            # Kredi kartı tablosu varsa yenile
            if hasattr(self, 'table_credit_cards'):
                self.refresh_credit_cards_table()
        except Exception as e:
            print(f"Veri yenileme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def logout(self):
        """Çıkış yap"""
        reply = QMessageBox.question(self, "Çıkış", "Çıkmak istediğinizden emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
    
    def create_credit_cards_tab(self) -> QWidget:
        """Kredi Kartları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("💳 Kredi Kartı Yönetimi")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        # İstatistikler
        stats_layout = QHBoxLayout()
        try:
            stats = CreditCardService.get_card_statistics(self.user.id)
            
            stats_layout.addWidget(self.create_stat_card("Toplam Kart", str(stats['total_cards']), "#9C27B0"))
            stats_layout.addWidget(self.create_stat_card("Toplam Limit", f"{stats['total_limit']:,.0f} ₺", "#2196F3"))
            stats_layout.addWidget(self.create_stat_card("Toplam Borç", f"{stats['total_debt']:,.0f} ₺", "#f44336"))
            stats_layout.addWidget(self.create_stat_card("Kullanılabilir", f"{stats['total_available']:,.0f} ₺", "#4CAF50"))
        except Exception as e:
            print(f"Kart stats hatası: {e}")
        
        layout.addLayout(stats_layout)
        layout.addSpacing(15)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Kredi Kartı")
        btn_new.setMinimumHeight(35)
        btn_new.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7B1FA2; }
        """)
        btn_new.clicked.connect(self.show_new_credit_card_dialog)
        btn_layout.addWidget(btn_new)
        
        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.setMinimumHeight(35)
        btn_refresh.clicked.connect(self.refresh_credit_cards_table)
        btn_layout.addWidget(btn_refresh)
        
        btn_import_cards = QPushButton("📥 Excel'den Aktar")
        btn_import_cards.setMinimumHeight(35)
        btn_import_cards.clicked.connect(self.import_credit_cards_from_excel)
        btn_layout.addWidget(btn_import_cards)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Tablo
        self.table_credit_cards = QTableWidget()
        self.table_credit_cards.setColumnCount(8)
        self.table_credit_cards.setHorizontalHeaderLabels([
            "Kart Adı", "Banka", "Son 4 Hane", "Limit", "Borç", "Kullanılabilir", "Durum", "İşlemler"
        ])
        self.table_credit_cards.horizontalHeader().setStretchLastSection(False)
        self.table_credit_cards.setColumnWidth(0, 180)
        self.table_credit_cards.setColumnWidth(1, 130)
        self.table_credit_cards.setColumnWidth(2, 90)
        self.table_credit_cards.setColumnWidth(3, 110)
        self.table_credit_cards.setColumnWidth(4, 110)
        self.table_credit_cards.setColumnWidth(5, 110)
        self.table_credit_cards.setColumnWidth(6, 80)
        self.table_credit_cards.setColumnWidth(7, 180)
        layout.addWidget(self.table_credit_cards)
        
        widget.setLayout(layout)
        self.refresh_credit_cards_table()
        return widget
    
    def refresh_credit_cards_table(self):
        """Kredi kartları tablosunu yenile"""
        try:
            cards = CreditCardService.get_all_cards(self.user.id)
            self.table_credit_cards.setRowCount(len(cards))
            
            for i, card in enumerate(cards):
                self.table_credit_cards.setItem(i, 0, QTableWidgetItem(card.card_name))
                self.table_credit_cards.setItem(i, 1, QTableWidgetItem(card.bank_name))
                self.table_credit_cards.setItem(i, 2, QTableWidgetItem(f"****{card.card_number_last4}"))
                self.table_credit_cards.setItem(i, 3, QTableWidgetItem(f"{card.card_limit:,.2f} ₺"))
                self.table_credit_cards.setItem(i, 4, QTableWidgetItem(f"{card.current_debt:,.2f} ₺"))
                self.table_credit_cards.setItem(i, 5, QTableWidgetItem(f"{card.available_limit:,.2f} ₺"))
                
                status = "Aktif" if card.is_active else "Pasif"
                self.table_credit_cards.setItem(i, 6, QTableWidgetItem(status))
                
                # Butonlar
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                action_layout.setSpacing(5)
                action_layout.setAlignment(Qt.AlignCenter)
                action_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                btn_edit = QPushButton("✏️ Düzenle")
                btn_edit.setMinimumHeight(25)
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #0b7dda; }
                """)
                btn_edit.clicked.connect(lambda checked, cid=card.id: self.show_edit_credit_card_dialog(cid))
                action_layout.addWidget(btn_edit)
                
                btn_delete = QPushButton("🗑️ Sil")
                btn_delete.setMinimumHeight(25)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #da190b; }
                """)
                btn_delete.clicked.connect(lambda checked, cid=card.id: self.delete_credit_card(cid))
                action_layout.addWidget(btn_delete)
                
                self.table_credit_cards.setCellWidget(i, 7, action_widget)
            
            self._resize_table(self.table_credit_cards)
        except Exception as e:
            print(f"Kredi kartı yükleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Kredi kartları yüklenirken hata: {str(e)}")
    
    def show_new_credit_card_dialog(self):
        """Yeni kredi kartı dialog"""
        from src.ui.dialogs.credit_card_dialog import CreditCardDialog
        dialog = CreditCardDialog(self.user.id, self)
        if dialog.exec_():
            self.refresh_all_data()

    def show_edit_credit_card_dialog(self, card_id):
        """Kredi kartı düzenleme dialog"""
        from src.ui.dialogs.credit_card_dialog import CreditCardDialog
        dialog = CreditCardDialog(self.user.id, self, card_id=card_id)
        if dialog.exec_():
            self.refresh_all_data()
    
    def delete_credit_card(self, card_id):
        """Kredi kartı sil"""
        reply = QMessageBox.question(self, "Onay", "Bu kredi kartını silmek istediğinize emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = CreditCardService.delete_card(card_id)
            if success:
                QMessageBox.information(self, "Başarılı", "Kredi kartı silindi")
                self.refresh_all_data()
            else:
                QMessageBox.critical(self, "Hata", msg)
    
    def create_cari_extract_tab(self) -> QWidget:
        """Cari Ekstre sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("📑 Cari Hesap Ekstresi")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Cari seçimi
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Cari Hesap:"))
        
        self.cari_extract_combo = QComboBox()
        self.cari_extract_combo.setMinimumHeight(35)
        self.cari_extract_combo.addItem("-- Cari Seçiniz --", None)
        try:
            caris = CariService.get_caris(self.user.id)
            if caris:
                for cari in caris:
                    self.cari_extract_combo.addItem(f"{cari.name} ({cari.cari_type})", cari.id)
        except:
            pass
        filter_layout.addWidget(self.cari_extract_combo)
        
        btn_show_extract = QPushButton("📊 Ekstre Göster")
        btn_show_extract.setMinimumHeight(35)
        btn_show_extract.clicked.connect(self.show_cari_extract)
        filter_layout.addWidget(btn_show_extract)
        
        btn_export_excel = QPushButton("📥 Excel'e Aktar")
        btn_export_excel.setMinimumHeight(35)
        btn_export_excel.setStyleSheet("""
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
        btn_export_excel.clicked.connect(self.export_cari_extract_to_excel)
        filter_layout.addWidget(btn_export_excel)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Ekstre tablosu
        self.table_cari_extract = QTableWidget()
        self.table_cari_extract.setColumnCount(6)
        self.table_cari_extract.setHorizontalHeaderLabels([
            "Tarih", "İşlem Türü", "Açıklama", "Borç", "Alacak", "Bakiye"
        ])
        self.table_cari_extract.horizontalHeader().setStretchLastSection(False)
        self.table_cari_extract.setColumnWidth(0, 100)
        self.table_cari_extract.setColumnWidth(1, 150)
        self.table_cari_extract.setColumnWidth(2, 300)
        self.table_cari_extract.setColumnWidth(3, 120)
        self.table_cari_extract.setColumnWidth(4, 120)
        self.table_cari_extract.setColumnWidth(5, 120)
        layout.addWidget(self.table_cari_extract)
        
        widget.setLayout(layout)
        return widget
    
    def show_cari_extract(self):
        """Cari ekstre göster"""
        cari_id = self.cari_extract_combo.currentData()
        if not cari_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cari hesap seçiniz!")
            return
        
        try:
            from src.database.db import SessionLocal
            from src.database.models import Cari, Transaction
            
            session = SessionLocal()
            cari = session.query(Cari).filter(Cari.id == cari_id).first()
            transactions = session.query(Transaction).filter(
                Transaction.cari_id == cari_id
            ).order_by(Transaction.transaction_date.asc()).all()
            session.close()
            
            self.table_cari_extract.setRowCount(len(transactions))
            running_balance = 0
            
            for i, trans in enumerate(transactions):
                self.table_cari_extract.setItem(i, 0, QTableWidgetItem(str(trans.transaction_date)))
                self.table_cari_extract.setItem(i, 1, QTableWidgetItem(trans.transaction_type.value))
                self.table_cari_extract.setItem(i, 2, QTableWidgetItem(trans.description))
                
                # Borç/Alacak hesaplama
                if trans.transaction_type.value in ['GIDER', 'GELEN_FATURA']:
                    debt = trans.amount
                    credit = 0
                    running_balance -= trans.amount
                else:
                    debt = 0
                    credit = trans.amount
                    running_balance += trans.amount
                
                self.table_cari_extract.setItem(i, 3, QTableWidgetItem(f"{debt:,.2f} ₺" if debt > 0 else "-"))
                self.table_cari_extract.setItem(i, 4, QTableWidgetItem(f"{credit:,.2f} ₺" if credit > 0 else "-"))
                self.table_cari_extract.setItem(i, 5, QTableWidgetItem(f"{running_balance:,.2f} ₺"))
            
            self._resize_table(self.table_cari_extract)
            QMessageBox.information(self, "Bilgi", f"{cari.name} için {len(transactions)} işlem bulundu")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ekstre yüklenirken hata: {str(e)}")
    
    def export_cari_extract_to_excel(self):
        """Cari ekstresini Excel'e aktar"""
        cari_id = self.cari_extract_combo.currentData()
        if not cari_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cari hesap seçiniz!")
            return
        
        # Tabloda veri var mı kontrol et
        if self.table_cari_extract.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Önce 'Ekstre Göster' butonuna basarak verileri yükleyiniz!")
            return
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            from datetime import datetime
            from src.database.db import SessionLocal
            from src.database.models import Cari
            import os
            
            # Cari bilgisini al
            session = SessionLocal()
            cari = session.query(Cari).filter(Cari.id == cari_id).first()
            cari_name = cari.name if cari else "Bilinmeyen"
            session.close()
            
            # Excel dosyası oluştur
            wb = Workbook()
            ws = wb.active
            ws.title = "Cari Ekstre"
            
            # Başlık bilgileri
            ws['A1'] = 'CARİ HESAP EKSTRESİ'
            ws['A1'].font = Font(size=16, bold=True, color='FFFFFF')
            ws['A1'].fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
            ws.merge_cells('A1:F1')
            ws.row_dimensions[1].height = 30
            
            ws['A2'] = f'Cari: {cari_name}'
            ws['A2'].font = Font(size=12, bold=True)
            ws.merge_cells('A2:C2')
            
            ws['D2'] = f'Tarih: {datetime.now().strftime("%d.%m.%Y %H:%M")}'
            ws['D2'].font = Font(size=10)
            ws['D2'].alignment = Alignment(horizontal='right')
            ws.merge_cells('D2:F2')
            
            # Boş satır
            ws.row_dimensions[3].height = 5
            
            # Başlıklar
            headers = ['Tarih', 'İşlem Türü', 'Açıklama', 'Borç', 'Alacak', 'Bakiye']
            header_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=4, column=col_num)
                cell.value = header
                cell.font = Font(bold=True, size=11)
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = border
            
            # Sütun genişlikleri
            ws.column_dimensions['A'].width = 12
            ws.column_dimensions['B'].width = 18
            ws.column_dimensions['C'].width = 35
            ws.column_dimensions['D'].width = 15
            ws.column_dimensions['E'].width = 15
            ws.column_dimensions['F'].width = 15
            
            # Verileri ekle
            for row in range(self.table_cari_extract.rowCount()):
                excel_row = row + 5
                for col in range(6):
                    item = self.table_cari_extract.item(row, col)
                    if item:
                        cell = ws.cell(row=excel_row, column=col+1)
                        value = item.text()
                        
                        # Sayısal değerleri düzenle
                        if col >= 3:  # Borç, Alacak, Bakiye kolonları
                            value = value.replace(' ₺', '').replace('.', '').replace(',', '.')
                            if value != '-':
                                try:
                                    cell.value = float(value)
                                    cell.number_format = '#,##0.00 "₺"'
                                except:
                                    cell.value = value
                            else:
                                cell.value = '-'
                        else:
                            cell.value = value
                        
                        cell.border = border
                        cell.alignment = Alignment(
                            horizontal='right' if col >= 3 else 'left',
                            vertical='center'
                        )
            
            # Dosya kaydetme dialog
            from PyQt5.QtWidgets import QFileDialog
            
            # Varsayılan dosya adı
            default_filename = f"Cari_Ekstre_{cari_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Excel Dosyasını Kaydet",
                default_filename,
                "Excel Dosyası (*.xlsx)"
            )
            
            if file_path:
                wb.save(file_path)
                QMessageBox.information(
                    self, 
                    "Başarılı", 
                    f"Cari ekstre başarıyla Excel'e aktarıldı:\n{file_path}"
                )
                
                # Dosyayı aç
                reply = QMessageBox.question(
                    self,
                    "Dosyayı Aç",
                    "Excel dosyasını şimdi açmak ister misiniz?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    os.startfile(file_path)
        
        except ImportError:
            QMessageBox.critical(self, "Hata", "openpyxl kütüphanesi bulunamadı. Lütfen 'pip install openpyxl' komutunu çalıştırın.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel'e aktarılırken hata oluştu:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def create_reports_tab(self) -> QWidget:
        """Raporlar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("📊 Raporlar ve Analizler")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Rapor türü seçimi
        report_layout = QHBoxLayout()
        report_layout.addWidget(QLabel("Rapor Türü:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.setMinimumHeight(35)
        self.report_type_combo.addItems([
            "Kapsamlı Genel Rapor",
            "Gelir-Gider Raporu",
            "Cari Bakiye Raporu",
            "Banka Özet Raporu",
            "Kredi Kartı Özet Raporu"
        ])
        report_layout.addWidget(self.report_type_combo)
        
        btn_generate = QPushButton("📄 Rapor Oluştur")
        btn_generate.setMinimumHeight(35)
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_generate.clicked.connect(self.generate_report)
        report_layout.addWidget(btn_generate)
        
        btn_export_excel = QPushButton("📥 Excel'e Aktar")
        btn_export_excel.setMinimumHeight(35)
        btn_export_excel.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #F57C00; }
        """)
        btn_export_excel.clicked.connect(self.export_report_to_excel)
        report_layout.addWidget(btn_export_excel)
        
        report_layout.addStretch()
        layout.addLayout(report_layout)
        
        # Rapor görüntüleme alanı
        self.report_display = QTextBrowser()
        self.report_display.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #ddd;
                background-color: white;
                padding: 15px;
                font-family: Consolas, monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.report_display)
        
        widget.setLayout(layout)
        return widget
    
    def generate_report(self):
        """Rapor oluştur"""
        report_type = self.report_type_combo.currentText()
        
        try:
            if report_type == "Kapsamlı Genel Rapor":
                data = ReportService.generate_comprehensive_report(self.user.id)
                html = self._format_comprehensive_report(data)
            elif report_type == "Gelir-Gider Raporu":
                data = ReportService.generate_income_expense_report(self.user.id)
                html = self._format_income_expense_report(data)
            elif report_type == "Cari Bakiye Raporu":
                data = ReportService.generate_cari_balance_report(self.user.id)
                html = self._format_cari_balance_report(data)
            elif report_type == "Banka Özet Raporu":
                data = ReportService.generate_bank_summary_report(self.user.id)
                html = self._format_bank_summary_report(data)
            elif report_type == "Kredi Kartı Özet Raporu":
                data = ReportService.generate_credit_card_summary(self.user.id)
                html = self._format_credit_card_report(data)
            else:
                html = "<h2>Rapor türü seçiniz</h2>"
            
            self.report_display.setHtml(html)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor oluşturulurken hata: {str(e)}")
    
    def _format_comprehensive_report(self, data):
        """Kapsamlı rapor HTML formatı"""
        html = f"""
        <h2 style='color: #2196F3;'>📊 KAPSAMLI GENEL RAPOR</h2>
        <p><strong>Rapor Tarihi:</strong> {data['report_date']}</p>
        <hr>
        
        <h3 style='color: #4CAF50;'>💰 Gelir-Gider Özeti</h3>
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
        <tr><td><strong>Toplam Gelir:</strong></td><td>{data['income_expense']['total_income']:,.2f} ₺</td></tr>
        <tr><td><strong>Toplam Gider:</strong></td><td>{data['income_expense']['total_expense']:,.2f} ₺</td></tr>
        <tr><td><strong>Net Kar/Zarar:</strong></td><td style='color: {"green" if data['income_expense']['net_profit'] >= 0 else "red"};'><strong>{data['income_expense']['net_profit']:,.2f} ₺</strong></td></tr>
        </table>
        
        <h3 style='color: #FF9800;'>📋 Cari Hesaplar</h3>
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
        <tr><td><strong>Toplam Alacak:</strong></td><td>{data['cari_balance']['total_receivable']:,.2f} ₺</td></tr>
        <tr><td><strong>Toplam Borç:</strong></td><td>{data['cari_balance']['total_payable']:,.2f} ₺</td></tr>
        <tr><td><strong>Net Bakiye:</strong></td><td><strong>{data['cari_balance']['net_balance']:,.2f} ₺</strong></td></tr>
        </table>
        
        <h3 style='color: #2196F3;'>🏦 Banka Hesapları</h3>
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
        <tr><td><strong>Toplam Bakiye (TRY):</strong></td><td><strong>{data['bank_summary']['total_balance_try']:,.2f} ₺</strong></td></tr>
        </table>
        
        <h3 style='color: #9C27B0;'>💳 Kredi Kartları</h3>
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
        <tr><td><strong>Toplam Limit:</strong></td><td>{data['credit_card_summary']['total_limit']:,.2f} ₺</td></tr>
        <tr><td><strong>Toplam Borç:</strong></td><td style='color: red;'>{data['credit_card_summary']['total_debt']:,.2f} ₺</td></tr>
        <tr><td><strong>Kullanılabilir Limit:</strong></td><td style='color: green;'>{data['credit_card_summary']['total_available']:,.2f} ₺</td></tr>
        </table>
        
        <h3 style='color: #f44336;'>💼 Genel Finansal Durum</h3>
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
        <tr><td><strong>Likit Varlıklar:</strong></td><td>{data['overall_financial_health']['liquid_assets']:,.2f} ₺</td></tr>
        <tr><td><strong>Alacaklar:</strong></td><td>{data['overall_financial_health']['receivables']:,.2f} ₺</td></tr>
        <tr><td><strong>Borçlar:</strong></td><td>-{data['overall_financial_health']['payables']:,.2f} ₺</td></tr>
        <tr><td><strong>Kredi Kartı Borçları:</strong></td><td>-{data['overall_financial_health']['credit_card_debt']:,.2f} ₺</td></tr>
        <tr style='background-color: #e3f2fd;'><td><strong>NET DEĞER:</strong></td><td style='font-size: 14pt; color: {"green" if data['overall_financial_health']['net_worth'] >= 0 else "red"};'><strong>{data['overall_financial_health']['net_worth']:,.2f} ₺</strong></td></tr>
        </table>
        """
        return html
    
    def _format_income_expense_report(self, data):
        """Gelir-gider raporu HTML"""
        return f"""
        <h2 style='color: #2196F3;'>💰 GELİR-GİDER RAPORU</h2>
        <p><strong>Dönem:</strong> {data['period']['start']} - {data['period']['end']}</p>
        <hr>
        <table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%; font-size: 12pt;'>
        <tr><td><strong>Toplam Gelir:</strong></td><td style='color: green;'><strong>{data['total_income']:,.2f} ₺</strong></td></tr>
        <tr><td><strong>Toplam Gider:</strong></td><td style='color: red;'><strong>{data['total_expense']:,.2f} ₺</strong></td></tr>
        <tr style='background-color: #e3f2fd;'><td><strong>Net Kar/Zarar:</strong></td><td style='font-size: 14pt; color: {"green" if data['net_profit'] >= 0 else "red"};'><strong>{data['net_profit']:,.2f} ₺</strong></td></tr>
        <tr><td><strong>İşlem Sayısı:</strong></td><td>{data['transaction_count']}</td></tr>
        </table>
        """
    
    def _format_cari_balance_report(self, data):
        """Cari bakiye raporu HTML"""
        html = f"""
        <h2 style='color: #FF9800;'>📋 CARİ BAKİYE RAPORU</h2>
        <hr>
        <table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%;'>
        <tr><td><strong>Toplam Cari:</strong></td><td>{data['total_caris']}</td></tr>
        <tr><td><strong>Toplam Alacak:</strong></td><td style='color: green;'>{data['total_receivable']:,.2f} ₺</td></tr>
        <tr><td><strong>Toplam Borç:</strong></td><td style='color: red;'>{data['total_payable']:,.2f} ₺</td></tr>
        <tr style='background-color: #e3f2fd;'><td><strong>Net Bakiye:</strong></td><td><strong>{data['net_balance']:,.2f} ₺</strong></td></tr>
        </table>
        <br>
        <h3>Cari Detayları:</h3>
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
        <tr style='background-color: #f5f5f5;'><th>Cari Adı</th><th>Tip</th><th>Bakiye</th><th>Durum</th></tr>
        """
        for cari in data['caris']:
            color = 'green' if cari['balance'] > 0 else 'red' if cari['balance'] < 0 else 'black'
            html += f"<tr><td>{cari['name']}</td><td>{cari['type']}</td><td style='color: {color};'>{cari['balance']:,.2f} ₺</td><td>{cari['status']}</td></tr>"
        html += "</table>"
        return html
    
    def _format_bank_summary_report(self, data):
        """Banka özet HTML"""
        html = f"""
        <h2 style='color: #2196F3;'>🏦 BANKA ÖZET RAPORU</h2>
        <hr>
        <table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%;'>
        <tr><td><strong>Toplam Hesap:</strong></td><td>{data['total_accounts']}</td></tr>
        <tr style='background-color: #e3f2fd;'><td><strong>Toplam Bakiye (TRY):</strong></td><td style='font-size: 14pt;'><strong>{data['total_balance_try']:,.2f} ₺</strong></td></tr>
        </table>
        <br>
        <h3>Hesap Detayları:</h3>
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
        <tr style='background-color: #f5f5f5;'><th>Banka</th><th>Hesap No</th><th>Bakiye</th><th>Para Birimi</th></tr>
        """
        for bank in data['banks']:
            html += f"<tr><td>{bank['bank_name']}</td><td>{bank['account_number']}</td><td>{bank['balance']:,.2f}</td><td>{bank['currency']}</td></tr>"
        html += "</table>"
        return html
    
    def _format_credit_card_report(self, data):
        """Kredi kartı raporu HTML"""
        html = f"""
        <h2 style='color: #9C27B0;'>💳 KREDİ KARTI ÖZET RAPORU</h2>
        <hr>
        <table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%;'>
        <tr><td><strong>Toplam Kart:</strong></td><td>{data['total_cards']}</td></tr>
        <tr><td><strong>Toplam Limit:</strong></td><td>{data['total_limit']:,.2f} ₺</td></tr>
        <tr><td><strong>Toplam Borç:</strong></td><td style='color: red;'><strong>{data['total_debt']:,.2f} ₺</strong></td></tr>
        <tr><td><strong>Kullanılabilir Limit:</strong></td><td style='color: green;'><strong>{data['total_available']:,.2f} ₺</strong></td></tr>
        <tr><td><strong>Kullanım Oranı:</strong></td><td>{data['overall_usage_rate']:.1f}%</td></tr>
        </table>
        <br>
        <h3>Kart Detayları:</h3>
        <table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
        <tr style='background-color: #f5f5f5;'><th>Kart</th><th>Banka</th><th>Limit</th><th>Borç</th><th>Kullanılabilir</th><th>Kullanım %</th></tr>
        """
        for card in data['cards']:
            html += f"<tr><td>{card['card_name']}</td><td>{card['bank']}</td><td>{card['limit']:,.2f} ₺</td><td style='color: red;'>{card['debt']:,.2f} ₺</td><td style='color: green;'>{card['available']:,.2f} ₺</td><td>{card['usage_rate']:.1f}%</td></tr>"
        html += "</table>"
        return html
    
    def export_report_to_excel(self):
        """Raporu Excel'e aktar"""
        report_type = self.report_type_combo.currentText()
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            from openpyxl.utils import get_column_letter
            from datetime import datetime
            from PyQt5.QtWidgets import QFileDialog
            import os
            
            # Rapor verisini al
            if report_type == "Kapsamlı Genel Rapor":
                data = ReportService.generate_comprehensive_report(self.user.id)
                filename_prefix = "Kapsamli_Genel_Rapor"
            elif report_type == "Gelir-Gider Raporu":
                data = ReportService.generate_income_expense_report(self.user.id)
                filename_prefix = "Gelir_Gider_Raporu"
            elif report_type == "Cari Bakiye Raporu":
                data = ReportService.generate_cari_balance_report(self.user.id)
                filename_prefix = "Cari_Bakiye_Raporu"
            elif report_type == "Banka Özet Raporu":
                data = ReportService.generate_bank_summary_report(self.user.id)
                filename_prefix = "Banka_Ozet_Raporu"
            elif report_type == "Kredi Kartı Özet Raporu":
                data = ReportService.generate_credit_card_summary(self.user.id)
                filename_prefix = "Kredi_Karti_Raporu"
            else:
                QMessageBox.warning(self, "Uyarı", "Önce bir rapor türü seçiniz!")
                return
            
            # Excel oluştur
            wb = Workbook()
            ws = wb.active
            
            # Stil tanımlamaları
            header_font = Font(size=14, bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            title_font = Font(size=12, bold=True)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Rapor türüne göre Excel formatı
            if report_type == "Kapsamlı Genel Rapor":
                self._export_comprehensive_report_excel(ws, data, header_font, header_fill, title_font, border)
            elif report_type == "Gelir-Gider Raporu":
                self._export_income_expense_excel(ws, data, header_font, header_fill, title_font, border)
            elif report_type == "Cari Bakiye Raporu":
                self._export_cari_balance_excel(ws, data, header_font, header_fill, title_font, border)
            elif report_type == "Banka Özet Raporu":
                self._export_bank_summary_excel(ws, data, header_font, header_fill, title_font, border)
            elif report_type == "Kredi Kartı Özet Raporu":
                self._export_credit_card_excel(ws, data, header_font, header_fill, title_font, border)
            
            # Dosya kaydetme dialog
            default_filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Excel Dosyasını Kaydet",
                default_filename,
                "Excel Dosyası (*.xlsx)"
            )
            
            if file_path:
                wb.save(file_path)
                QMessageBox.information(
                    self,
                    "Başarılı",
                    f"Rapor başarıyla Excel'e aktarıldı:\n{file_path}"
                )
                
                # Dosyayı aç
                reply = QMessageBox.question(
                    self,
                    "Dosyayı Aç",
                    "Excel dosyasını şimdi açmak ister misiniz?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    os.startfile(file_path)
        
        except ImportError:
            QMessageBox.critical(self, "Hata", "openpyxl kütüphanesi bulunamadı. Lütfen 'pip install openpyxl' komutunu çalıştırın.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel'e aktarılırken hata oluştu:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def _export_comprehensive_report_excel(self, ws, data, header_font, header_fill, title_font, border):
        """Kapsamlı rapor Excel export"""
        ws.title = "Kapsamlı Rapor"
        
        # Başlık
        ws['A1'] = 'KAPSAMLI GENEL RAPOR'
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.merge_cells('A1:D1')
        ws.row_dimensions[1].height = 30
        
        ws['A2'] = f'Rapor Tarihi: {data["report_date"][:19]}'
        ws['A2'].font = Font(size=10)
        ws.merge_cells('A2:D2')
        
        row = 4
        
        # Genel Mali Durum
        ws[f'A{row}'] = 'GENEL MALİ DURUM'
        ws[f'A{row}'].font = title_font
        ws[f'A{row}'].fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        ws.merge_cells(f'A{row}:D{row}')
        row += 1
        
        health = data['overall_financial_health']
        items = [
            ('Likid Varlıklar (Banka)', health['liquid_assets']),
            ('Alacaklar', health['receivables']),
            ('Borçlar', health['payables']),
            ('Kredi Kartı Borcu', health['credit_card_debt']),
            ('NET DEĞER', health['net_worth'])
        ]
        
        for label, value in items:
            ws[f'A{row}'] = label
            ws[f'B{row}'] = f"{value:,.2f} ₺"
            ws[f'A{row}'].border = border
            ws[f'B{row}'].border = border
            if label == 'NET DEĞER':
                ws[f'A{row}'].font = Font(bold=True)
                ws[f'B{row}'].font = Font(bold=True, size=12)
                ws[f'B{row}'].fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
            row += 1
        
        row += 1
        
        # Gelir-Gider
        ws[f'A{row}'] = 'GELİR-GİDER ÖZETİ'
        ws[f'A{row}'].font = title_font
        ws[f'A{row}'].fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        ws.merge_cells(f'A{row}:D{row}')
        row += 1
        
        ie = data['income_expense']
        ws[f'A{row}'] = 'Toplam Gelir'
        ws[f'B{row}'] = f"{ie['total_income']:,.2f} ₺"
        ws[f'A{row}'].border = border
        ws[f'B{row}'].border = border
        row += 1
        
        ws[f'A{row}'] = 'Toplam Gider'
        ws[f'B{row}'] = f"{ie['total_expense']:,.2f} ₺"
        ws[f'A{row}'].border = border
        ws[f'B{row}'].border = border
        row += 1
        
        ws[f'A{row}'] = 'Net Kar/Zarar'
        ws[f'B{row}'] = f"{ie['net_profit']:,.2f} ₺"
        ws[f'A{row}'].font = Font(bold=True)
        ws[f'B{row}'].font = Font(bold=True)
        ws[f'A{row}'].border = border
        ws[f'B{row}'].border = border
        
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 20
    
    def _export_income_expense_excel(self, ws, data, header_font, header_fill, title_font, border):
        """Gelir-Gider raporu Excel export"""
        ws.title = "Gelir-Gider"
        
        ws['A1'] = 'GELİR-GİDER RAPORU'
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.merge_cells('A1:C1')
        ws.row_dimensions[1].height = 30
        
        ws['A2'] = f'Dönem: {data["period"]["start"]} - {data["period"]["end"]}'
        ws.merge_cells('A2:C2')
        
        row = 4
        headers = [('Toplam Gelir', data['total_income']),
                   ('Toplam Gider', data['total_expense']),
                   ('Net Kar/Zarar', data['net_profit']),
                   ('İşlem Sayısı', data['transaction_count'])]
        
        for label, value in headers:
            ws[f'A{row}'] = label
            if isinstance(value, (int, float)) and label != 'İşlem Sayısı':
                ws[f'B{row}'] = f"{value:,.2f} ₺"
            else:
                ws[f'B{row}'] = value
            ws[f'A{row}'].border = border
            ws[f'B{row}'].border = border
            if label == 'Net Kar/Zarar':
                ws[f'A{row}'].font = Font(bold=True, size=12)
                ws[f'B{row}'].font = Font(bold=True, s=12)
            row += 1
        
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
    
    def _export_cari_balance_excel(self, ws, data, header_font, header_fill, title_font, border):
        """Cari bakiye raporu Excel export"""
        ws.title = "Cari Bakiye"
        
        ws['A1'] = 'CARİ BAKİYE RAPORU'
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.merge_cells('A1:D1')
        ws.row_dimensions[1].height = 30
        
        row = 3
        ws[f'A{row}'] = 'Toplam Cari Sayısı'
        ws[f'B{row}'] = data['total_caris']
        row += 1
        ws[f'A{row}'] = 'Toplam Alacak'
        ws[f'B{row}'] = f"{data['total_receivable']:,.2f} ₺"
        ws[f'B{row}'].fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        row += 1
        ws[f'A{row}'] = 'Toplam Borç'
        ws[f'B{row}'] = f"{data['total_payable']:,.2f} ₺"
        ws[f'B{row}'].fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
        row += 1
        ws[f'A{row}'] = 'Net Bakiye'
        ws[f'B{row}'] = f"{data['net_balance']:,.2f} ₺"
        ws[f'A{row}'].font = Font(bold=True)
        ws[f'B{row}'].font = Font(bold=True, size=12)
        
        row += 2
        ws[f'A{row}'] = 'CARİ DETAYLARI'
        ws[f'A{row}'].font = title_font
        ws[f'A{row}'].fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        ws.merge_cells(f'A{row}:D{row}')
        row += 1
        
        # Başlıklar
        headers = ['Cari Adı', 'Tür', 'Bakiye', 'Durum']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
            cell.border = border
        row += 1
        
        # Veriler
        for cari in data['caris']:
            ws[f'A{row}'] = cari['name']
            ws[f'B{row}'] = cari['type']
            ws[f'C{row}'] = f"{cari['balance']:,.2f} ₺"
            ws[f'D{row}'] = cari['status']
            
            for col in range(1, 5):
                ws.cell(row=row, column=col).border = border
            
            if cari['balance'] > 0:
                ws[f'C{row}'].font = Font(color='006100')
            elif cari['balance'] < 0:
                ws[f'C{row}'].font = Font(color='9C0006')
            row += 1
        
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 15
    
    def _export_bank_summary_excel(self, ws, data, header_font, header_fill, title_font, border):
        """Banka özet raporu Excel export"""
        ws.title = "Banka Özeti"
        
        ws['A1'] = 'BANKA ÖZET RAPORU'
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.merge_cells('A1:D1')
        ws.row_dimensions[1].height = 30
        
        row = 3
        ws[f'A{row}'] = 'Toplam Hesap Sayısı'
        ws[f'B{row}'] = data['total_accounts']
        row += 1
        ws[f'A{row}'] = 'Toplam Bakiye (TRY)'
        ws[f'B{row}'] = f"{data['total_balance_try']:,.2f} ₺"
        ws[f'A{row}'].font = Font(bold=True)
        ws[f'B{row}'].font = Font(bold=True, size=12)
        ws[f'B{row}'].fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        
        row += 2
        ws[f'A{row}'] = 'HESAP DETAYLARI'
        ws[f'A{row}'].font = title_font
        ws[f'A{row}'].fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        ws.merge_cells(f'A{row}:D{row}')
        row += 1
        
        headers = ['Banka Adı', 'Hesap No', 'Bakiye', 'Para Birimi']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
            cell.border = border
        row += 1
        
        for bank in data['banks']:
            ws[f'A{row}'] = bank['bank_name']
            ws[f'B{row}'] = bank['account_number']
            ws[f'C{row}'] = f"{bank['balance']:,.2f}"
            ws[f'D{row}'] = bank['currency']
            
            for col in range(1, 5):
                ws.cell(row=row, column=col).border = border
            row += 1
        
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 12
    
    def _export_credit_card_excel(self, ws, data, header_font, header_fill, title_font, border):
        """Kredi kartı raporu Excel export"""
        ws.title = "Kredi Kartları"
        
        ws['A1'] = 'KREDİ KARTI ÖZET RAPORU'
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.merge_cells('A1:F1')
        ws.row_dimensions[1].height = 30
        
        row = 3
        summary = [
            ('Toplam Kart Sayısı', data['total_cards'], None),
            ('Toplam Limit', f"{data['total_limit']:,.2f} ₺", None),
            ('Toplam Borç', f"{data['total_debt']:,.2f} ₺", 'FFC7CE'),
            ('Kullanılabilir Limit', f"{data['total_available']:,.2f} ₺", 'C6EFCE'),
            ('Genel Kullanım Oranı', f"{data['overall_usage_rate']:.1f}%", None)
        ]
        
        for label, value, fill in summary:
            ws[f'A{row}'] = label
            ws[f'B{row}'] = value
            ws[f'A{row}'].border = border
            ws[f'B{row}'].border = border
            if fill:
                ws[f'B{row}'].fill = PatternFill(start_color=fill, end_color=fill, fill_type='solid')
            if 'Toplam Borç' in label or 'Kullanılabilir' in label:
                ws[f'A{row}'].font = Font(bold=True)
                ws[f'B{row}'].font = Font(bold=True)
            row += 1
        
        row += 1
        ws[f'A{row}'] = 'KART DETAYLARI'
        ws[f'A{row}'].font = title_font
        ws[f'A{row}'].fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        ws.merge_cells(f'A{row}:F{row}')
        row += 1
        
        headers = ['Kart Adı', 'Banka', 'Limit', 'Borç', 'Kullanılabilir', 'Kullanım %']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
            cell.border = border
        row += 1
        
        for card in data['cards']:
            ws[f'A{row}'] = card['card_name']
            ws[f'B{row}'] = card['bank']
            ws[f'C{row}'] = f"{card['limit']:,.2f} ₺"
            ws[f'D{row}'] = f"{card['debt']:,.2f} ₺"
            ws[f'E{row}'] = f"{card['available']:,.2f} ₺"
            ws[f'F{row}'] = f"{card['usage_rate']:.1f}%"
            
            for col in range(1, 7):
                ws.cell(row=row, column=col).border = border
            
            # Kullanım oranına göre renklendirme
            if card['usage_rate'] > 80:
                ws[f'F{row}'].fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
            elif card['usage_rate'] > 50:
                ws[f'F{row}'].fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
            
            row += 1
        
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 18
        ws.column_dimensions['F'].width = 12

