import sys
import re

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QFrame,
    QGridLayout,
    QStackedWidget,
    QTextEdit,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QThread,
    Signal,
)

from Get_the_Data import (
    search_companies,
    get_company_data,
)
from Visualization import DoughnutChart
from Menu_Bar import SideMenuBar


# ==========================================================
# Background Workers
# ==========================================================

class SearchWorker(QThread):
    results_ready = Signal(list)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            results = search_companies(self.query)
            self.results_ready.emit(results)
        except Exception:
            self.results_ready.emit([])


class DataFetchWorker(QThread):
    data_ready = Signal(dict)

    def __init__(self, search_value):
        super().__init__()
        self.search_value = search_value

    def run(self):
        try:
            result = get_company_data(self.search_value)
            self.data_ready.emit(result)
        except Exception as e:
            self.data_ready.emit({
                "success": False,
                "message": f"An unexpected error occurred: {e}"
            })


# ==========================================================
# Page 1: Stock Market Analysis Page
# ==========================================================

class StockAnalysisPage(QWidget):

    def __init__(self):
        super().__init__()

        self.selected_symbol = None
        self.search_worker = None
        self.data_worker = None

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(400)
        self.search_timer.timeout.connect(self.perform_company_search)

        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QLabel#title {
                font-size: 30px;
                font-weight: 800;
                color: #ffffff;
            }

            QLabel#subtitle {
                font-size: 14px;
                color: #94a3b8;
            }

            QLabel#company_header {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#company_symbol {
                font-size: 15px;
                color: #38bdf8;
                font-weight: 600;
            }

            QLabel#metric_title {
                font-size: 12px;
                color: #94a3b8;
                font-weight: 600;
                text-transform: uppercase;
            }

            QLabel#metric_value {
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#section_heading {
                font-size: 16px;
                font-weight: bold;
                color: #38bdf8;
                padding-bottom: 4px;
            }

            QLabel#status_msg {
                font-size: 16px;
                color: #94a3b8;
                padding: 20px;
            }

            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 27px;
                padding-left: 20px;
                padding-right: 20px;
                color: white;
                font-size: 16px;
            }

            QLineEdit:focus {
                border: 2px solid #38bdf8;
            }

            QPushButton {
                background-color: #0284c7;
                border: none;
                border-radius: 27px;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding-left: 28px;
                padding-right: 28px;
            }

            QPushButton:hover {
                background-color: #0369a1;
            }

            QListWidget {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                color: white;
                font-size: 15px;
                padding: 6px;
            }

            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
            }

            QListWidget::item:hover {
                background-color: #334155;
            }

            QListWidget::item:selected {
                background-color: #0284c7;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QFrame#analysis_card {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 16px;
            }

            QFrame#metric_box {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 12px;
            }

            QFrame#info_box {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(50, 35, 50, 25)
        root_layout.setSpacing(0)

        # --------------------------------------------------
        # Top Search Bar Section
        # --------------------------------------------------
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        title = QLabel("Stock Market Analysis")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Search for a company name or stock symbol")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search company or stock symbol...")
        self.search_bar.setMinimumHeight(54)
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        self.search_bar.returnPressed.connect(self.search_company)

        search_button = QPushButton("Search")
        search_button.setMinimumHeight(54)
        search_button.setMinimumWidth(130)
        search_button.clicked.connect(self.search_company)

        search_layout.addWidget(self.search_bar, 1)
        search_layout.addWidget(search_button, 0)

        self.suggestions = QListWidget()
        self.suggestions.setMaximumHeight(210)
        self.suggestions.hide()
        self.suggestions.itemClicked.connect(self.company_selected)

        top_layout.addWidget(title)
        top_layout.addWidget(subtitle)
        top_layout.addSpacing(18)
        top_layout.addLayout(search_layout)
        top_layout.addWidget(self.suggestions)

        root_layout.addWidget(top_section)
        root_layout.addSpacing(25)

        # --------------------------------------------------
        # Analysis Container
        # --------------------------------------------------
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        analysis_container = QWidget()
        analysis_layout = QVBoxLayout(analysis_container)
        analysis_layout.setContentsMargins(0, 0, 0, 0)
        analysis_layout.setSpacing(15)

        self.analysis_card = QFrame()
        self.analysis_card.setObjectName("analysis_card")

        card_layout = QVBoxLayout(self.analysis_card)
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setSpacing(20)

        # Status Label
        self.status_label = QLabel("Search for a company to view analysis.")
        self.status_label.setObjectName("status_msg")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Company Header Details
        self.header_widget = QWidget()
        header_layout = QVBoxLayout(self.header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.company_name_lbl = QLabel()
        self.company_name_lbl.setObjectName("company_header")
        self.company_name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.company_symbol_lbl = QLabel()
        self.company_symbol_lbl.setObjectName("company_symbol")
        self.company_symbol_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(self.company_name_lbl)
        header_layout.addWidget(self.company_symbol_lbl)
        self.header_widget.hide()

        # Buy / Sell Verdict Banner (Check Box Banner)
        self.verdict_card = QFrame()
        self.verdict_card.setObjectName("info_box")
        verdict_layout = QVBoxLayout(self.verdict_card)
        verdict_layout.setContentsMargins(20, 15, 20, 15)

        self.verdict_title = QLabel()
        self.verdict_title.setStyleSheet("font-size: 20px; font-weight: 800;")
        self.verdict_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verdict_reason = QLabel()
        self.verdict_reason.setStyleSheet("font-size: 14px; color: #e2e8f0; padding-top: 4px;")
        self.verdict_reason.setAlignment(Qt.AlignmentFlag.AlignCenter)

        verdict_layout.addWidget(self.verdict_title)
        verdict_layout.addWidget(self.verdict_reason)
        self.verdict_card.hide()

        # Metrics Grid
        self.metrics_widget = QWidget()
        grid = QGridLayout(self.metrics_widget)
        grid.setSpacing(12)

        self.card_price = self._create_metric_card("Current Price", grid, 0, 0)
        self.card_change = self._create_metric_card("1-Year Change", grid, 0, 1)
        self.card_sector = self._create_metric_card("Sector", grid, 1, 0)
        self.card_industry = self._create_metric_card("Industry", grid, 1, 1)
        self.metrics_widget.hide()

        # Company Detailed Info Card (Main Area, Leadership, Subsidiaries)
        self.info_card = QFrame()
        self.info_card.setObjectName("info_box")
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setSpacing(14)

        # Main Area
        main_area_heading = QLabel("🏢 Main Area / Business Summary")
        main_area_heading.setObjectName("section_heading")
        self.lbl_main_area = QLabel()
        self.lbl_main_area.setWordWrap(True)
        self.lbl_main_area.setStyleSheet("color: #cbd5e1; font-size: 14px; line-height: 1.4;")

        # Business Leadership
        owner_heading = QLabel("👤 Business Leadership & Key Executives")
        owner_heading.setObjectName("section_heading")
        self.lbl_owner = QLabel()
        self.lbl_owner.setWordWrap(True)
        self.lbl_owner.setStyleSheet("color: #cbd5e1; font-size: 14px;")

        # Subsidiaries
        sub_heading = QLabel("🏢 Subsidiaries & Operating Units")
        sub_heading.setObjectName("section_heading")
        self.lbl_subsidiary = QLabel()
        self.lbl_subsidiary.setWordWrap(True)
        self.lbl_subsidiary.setStyleSheet("color: #cbd5e1; font-size: 14px;")

        info_layout.addWidget(main_area_heading)
        info_layout.addWidget(self.lbl_main_area)
        info_layout.addSpacing(8)
        info_layout.addWidget(owner_heading)
        info_layout.addWidget(self.lbl_owner)
        info_layout.addSpacing(8)
        info_layout.addWidget(sub_heading)
        info_layout.addWidget(self.lbl_subsidiary)

        self.info_card.hide()

        # Chart
        self.chart = DoughnutChart(0, 0, "1-Year Performance")
        self.chart.setMinimumHeight(330)
        self.chart.hide()

        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.header_widget)
        card_layout.addWidget(self.verdict_card)
        card_layout.addWidget(self.metrics_widget)
        card_layout.addWidget(self.info_card)
        card_layout.addWidget(self.chart)

        analysis_layout.addWidget(self.analysis_card)
        analysis_layout.addStretch()

        self.scroll_area.setWidget(analysis_container)
        root_layout.addWidget(self.scroll_area, 1)

    def _create_metric_card(self, title, grid_layout, row, col):
        frame = QFrame()
        frame.setObjectName("metric_box")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(15, 12, 15, 12)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("metric_title")

        lbl_val = QLabel("-")
        lbl_val.setObjectName("metric_value")
        lbl_val.setWordWrap(True)

        lay.addWidget(lbl_title)
        lay.addWidget(lbl_val)
        grid_layout.addWidget(frame, row, col)

        return lbl_val

    def on_search_text_changed(self, text):
        self.selected_symbol = None
        text = text.strip()
        self.suggestions.clear()

        if len(text) < 2:
            self.suggestions.hide()
            return

        self.search_timer.start()

    def perform_company_search(self):
        query = self.search_bar.text().strip()
        if len(query) < 2:
            return

        self.search_worker = SearchWorker(query)
        self.search_worker.results_ready.connect(self.display_suggestions)
        self.search_worker.start()

    def display_suggestions(self, companies):
        self.suggestions.clear()
        if not companies:
            self.suggestions.hide()
            return

        for company in companies:
            name = company.get("name", "Unknown Company")
            symbol = company.get("symbol", "")
            exchange = company.get("exchange", "")

            display_text = f"{name} ({symbol})"
            if exchange:
                display_text += f"  •  {exchange}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, company)
            self.suggestions.addItem(item)

        self.suggestions.show()

    def company_selected(self, item):
        company = item.data(Qt.ItemDataRole.UserRole)
        if not company:
            return

        name = company.get("name", "")
        symbol = company.get("symbol", "")

        self.selected_symbol = symbol
        self.search_bar.setText(f"{name} ({symbol})")
        self.suggestions.hide()
        self.search_bar.setCursorPosition(len(self.search_bar.text()))

    def search_company(self):
        text = self.search_bar.text().strip()
        if not text:
            self.status_label.setText("Please enter a company name or stock symbol.")
            self.status_label.show()
            self.header_widget.hide()
            self.verdict_card.hide()
            self.metrics_widget.hide()
            self.info_card.hide()
            self.chart.hide()
            return

        self.suggestions.hide()

        if self.selected_symbol:
            search_value = self.selected_symbol
        else:
            match = re.search(r"\(([A-Za-z0-9.\-^=]+)\)", text)
            search_value = match.group(1) if match else text

        self.status_label.setText("Loading market and company data...")
        self.status_label.show()
        self.header_widget.hide()
        self.verdict_card.hide()
        self.metrics_widget.hide()
        self.info_card.hide()
        self.chart.hide()

        self.data_worker = DataFetchWorker(search_value)
        self.data_worker.data_ready.connect(self.on_data_retrieved)
        self.data_worker.start()

    def on_data_retrieved(self, result):
        if not result["success"]:
            self.status_label.setText(result["message"])
            return

        data = result["data"]

        # Company Header
        self.company_name_lbl.setText(data["company_name"])
        self.company_symbol_lbl.setText(f"{data['symbol']}  •  {data['exchange']}")

        # Worthy Check Box Banner
        is_worthy = data["is_worthy"]
        if is_worthy:
            self.verdict_card.setStyleSheet("""
                QFrame#info_box {
                    background-color: #064e3b;
                    border: 2px solid #10b981;
                    border-radius: 12px;
                }
            """)
            self.verdict_title.setText("☑ WORTHY TO BUY")
            self.verdict_title.setStyleSheet("color: #34d399; font-size: 20px; font-weight: 800;")
        else:
            self.verdict_card.setStyleSheet("""
                QFrame#info_box {
                    background-color: #7f1d1d;
                    border: 2px solid #ef4444;
                    border-radius: 12px;
                }
            """)
            self.verdict_title.setText("☒ NOT RECOMMENDED / CAUTION")
            self.verdict_title.setStyleSheet("color: #fca5a5; font-size: 20px; font-weight: 800;")

        self.verdict_reason.setText(data["recommendation_reason"])

        # Metrics
        price = data["current_price"]
        curr = data["currency"]
        change = data["price_change_percentage"]

        self.card_price.setText(f"{price:.2f} {curr}")
        color_hex = "#22c55e" if change >= 0 else "#ef4444"
        self.card_change.setText(f"{change:+.2f}%")
        self.card_change.setStyleSheet(f"color: {color_hex};")

        self.card_sector.setText(data["sector"])
        self.card_industry.setText(data["industry"])

        # Company Information
        summary_text = data["summary"]
        if len(summary_text) > 400:
            summary_text = summary_text[:400] + "..."

        self.lbl_main_area.setText(summary_text)
        self.lbl_owner.setText(data["leadership"])

        # Subsidiary information
        self.lbl_subsidiary.setText(
            f"Operates core business in {data['sector']} / {data['industry']} across key global markets."
        )

        # Chart
        self.chart.set_data(data["gain_percentage"], data["loss_percentage"])

        # Display All
        self.status_label.hide()
        self.header_widget.show()
        self.verdict_card.show()
        self.metrics_widget.show()
        self.info_card.show()
        self.chart.show()


# ==========================================================
# Page 2: Login Page Placeholder
# ==========================================================

class LoginPage(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedSize(380, 420)
        card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 16px;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
                color: white;
            }
            QPushButton {
                background-color: #0284c7;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        title = QLabel("Account Login")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        username = QLineEdit()
        username.setPlaceholderText("Username / Email")

        password = QLineEdit()
        password.setPlaceholderText("Password")
        password.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton("Sign In")

        card_layout.addWidget(title)
        card_layout.addSpacing(10)
        card_layout.addWidget(username)
        card_layout.addWidget(password)
        card_layout.addSpacing(10)
        card_layout.addWidget(login_btn)
        card_layout.addStretch()

        layout.addWidget(card)


# ==========================================================
# Page 3: Futures & Options Placeholder
# ==========================================================

class FuturesOptionsPage(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("⚡ Futures & Options (Derivatives)\n\nModule coming soon...")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 20px; color: #94a3b8; font-weight: 600;")

        layout.addWidget(lbl)


# ==========================================================
# Main Window Container
# ==========================================================

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stock Market & Derivatives Analysis Platform")
        self.resize(1350, 850)
        self.setStyleSheet("background-color: #0f172a;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar Navigation
        self.sidebar = SideMenuBar()
        main_layout.addWidget(self.sidebar)

        # 2. Right Stacked Widget
        self.stacked_widget = QStackedWidget()

        self.login_page = LoginPage()
        self.stock_page = StockAnalysisPage()
        self.fno_page = FuturesOptionsPage()

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.stock_page)
        self.stacked_widget.addWidget(self.fno_page)

        self.stacked_widget.setCurrentWidget(self.stock_page)

        main_layout.addWidget(self.stacked_widget, 1)

        self.sidebar.menu_changed.connect(self.switch_page)

    def switch_page(self, page_name):
        if page_name == "Login":
            self.stacked_widget.setCurrentWidget(self.login_page)
        elif page_name == "Stock Market Analysis":
            self.stacked_widget.setCurrentWidget(self.stock_page)
        elif page_name == "Futures & Options (Derivatives)":
            self.stacked_widget.setCurrentWidget(self.fno_page)


# ==========================================================
# Application Entry Point
# ==========================================================

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()