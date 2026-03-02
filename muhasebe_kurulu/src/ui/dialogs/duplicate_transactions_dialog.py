from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QCheckBox, QLabel, QHeaderView
)
from PyQt5.QtCore import Qt
from datetime import date, datetime


class DuplicateTransactionsDialog(QDialog):
    """Mükerrer işlem seçim dialogu"""

    def __init__(self, duplicates, parent=None):
        super().__init__(parent)
        self.duplicates = duplicates or []
        self.selected_row_keys = set()

        self.setWindowTitle("Mükerrer İşlemler")
        self.setMinimumSize(820, 460)
        self.setModal(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        info = QLabel("Aynı gün/kişi/tutar/açıklama ile mükerrer işlemler bulundu. Eklemek istediklerinizi seçin.")
        info.setWordWrap(True)
        layout.addWidget(info)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Seç", "Satır", "Tarih", "Kişi/Müşteri", "Tutar", "Açıklama"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 180)
        self.table.setColumnWidth(4, 120)

        self.table.setRowCount(len(self.duplicates))
        for row_idx, item in enumerate(self.duplicates):
            row_key = item.get("row_key", item.get("row_idx", row_idx))
            row_label = item.get("row_label", str(row_key + 1))

            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox.setProperty("row_key", row_key)
            self.table.setCellWidget(row_idx, 0, checkbox)

            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_label)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(self._format_date(item.get("date"))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(item.get("customer_name") or ""))
            self.table.setItem(row_idx, 4, QTableWidgetItem(self._format_amount(item.get("amount"))))
            self.table.setItem(row_idx, 5, QTableWidgetItem(item.get("description") or ""))

        layout.addWidget(self.table)

        buttons_layout = QHBoxLayout()

        btn_select_all = QPushButton("Tümünü Seç")
        btn_select_all.clicked.connect(lambda: self._set_all(True))
        buttons_layout.addWidget(btn_select_all)

        btn_clear_all = QPushButton("Seçimi Kaldır")
        btn_clear_all.clicked.connect(lambda: self._set_all(False))
        buttons_layout.addWidget(btn_clear_all)

        buttons_layout.addStretch()

        btn_accept = QPushButton("Seçilenleri Ekle")
        btn_accept.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_accept)

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def _format_date(self, value):
        if isinstance(value, (datetime, date)):
            return value.strftime("%d.%m.%Y")
        return str(value or "")

    def _format_amount(self, value):
        try:
            return f"{float(value):,.2f}"
        except Exception:
            return str(value or "")

    def _set_all(self, checked):
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox):
                widget.setChecked(checked)

    def get_selected_row_ids(self):
        selected = set()
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                row_key = widget.property("row_key")
                selected.add(row_key)
        return selected
