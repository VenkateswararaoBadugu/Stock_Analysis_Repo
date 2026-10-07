"""
Menu_Bar.py

Left sidebar navigation widget for the application.
Emits a signal whenever a menu item is clicked.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QButtonGroup,
)
from PySide6.QtCore import Qt, Signal


class SideMenuBar(QWidget):
    # Signal emitted when a menu item is clicked (passes the page name)
    menu_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(260)

        # ==================================================
        # Styling
        # ==================================================
        self.setStyleSheet("""
            QWidget#sidebar {
                background-color: #1e293b;
                border-right: 1px solid #334155;
            }

            QLabel#app_brand {
                font-size: 20px;
                font-weight: 800;
                color: #ffffff;
                padding-left: 10px;
            }

            QLabel#menu_header {
                font-size: 11px;
                font-weight: 700;
                color: #64748b;
                padding-left: 12px;
                padding-top: 15px;
                padding-bottom: 5px;
            }

            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                padding-top: 12px;
                padding-bottom: 12px;
                padding-left: 16px;
                text-align: left;
            }

            QPushButton:hover {
                background-color: #334155;
                color: #ffffff;
            }

            QPushButton:checked {
                background-color: #0284c7;
                color: #ffffff;
                font-weight: 700;
            }
        """)

        self.setObjectName("sidebar")

        # ==================================================
        # Layout
        # ==================================================
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(8)

        # App Brand Header
        brand_label = QLabel("📈 MarketHub")
        brand_label.setObjectName("app_brand")

        # Menu Category Section Label
        section_label = QLabel("NAVIGATION")
        section_label.setObjectName("menu_header")

        layout.addWidget(brand_label)
        layout.addSpacing(10)
        layout.addWidget(section_label)

        # Button Group (Ensures only one button is active at a time)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Menu Items configuration
        self.menu_items = [
            ("🔑  Login", "Login"),
            ("📊  Stock Market Analysis", "Stock Market Analysis"),
            ("⚡  Futures & Options (Derivatives)", "Futures & Options (Derivatives)")
        ]

        # Dynamically create navigation buttons
        for idx, (display_name, key_name) in enumerate(self.menu_items):
            btn = QPushButton(display_name)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            # Store screen key in custom dynamic property
            btn.setProperty("page_key", key_name)

            # Default active selection (Stock Market Analysis)
            if key_name == "Stock Market Analysis":
                btn.setChecked(True)

            btn.clicked.connect(self._on_button_clicked)

            self.button_group.addButton(btn, idx)
            layout.addWidget(btn)

        layout.addStretch()

        # Footer Version Label
        footer = QLabel("v1.0.0")
        footer.setStyleSheet("color: #475569; font-size: 12px; padding-left: 12px;")
        layout.addWidget(footer)

    def _on_button_clicked(self):
        button = self.sender()
        page_key = button.property("page_key")
        self.menu_changed.emit(page_key)

    def set_active_page(self, page_name):
        """Programmatically highlight a menu item by page name."""
        for btn in self.button_group.buttons():
            if btn.property("page_key") == page_name:
                btn.setChecked(True)
                break