
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


# ==========================================================
# Company Search Worker
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


# ==========================================================
# Main Window
# ==========================================================

class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Stock Market Analysis"
        )

        self.resize(
            1100,
            800
        )

        # Selected ticker
        self.selected_symbol = None

        # Search worker
        self.search_worker = None

        # Search timer
        self.search_timer = QTimer()

        self.search_timer.setSingleShot(
            True
        )

        self.search_timer.setInterval(
            400
        )

        self.search_timer.timeout.connect(
            self.perform_company_search
        )

        # ==================================================
        # Main Styling
        # ==================================================

        self.setStyleSheet("""

            QWidget {
                background-color: #101827;
                color: white;
            }

            QLabel#title {
                font-size: 30px;
                font-weight: bold;
                color: white;
            }

            QLabel#subtitle {
                font-size: 15px;
                color: #9ca8ba;
            }

            QLabel#result {
                font-size: 17px;
                font-weight: bold;
                color: white;
                padding: 10px;
            }

            QLabel#section_title {
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding-top: 10px;
                padding-bottom: 5px;
            }

            QLineEdit {
                background-color: #182235;
                border: 1px solid #34425a;
                border-radius: 26px;
                padding-left: 20px;
                padding-right: 20px;
                color: white;
                font-size: 16px;
            }

            QLineEdit:focus {
                border: 2px solid #4f8cff;
            }

            QPushButton {
                background-color: #4f8cff;
                border: none;
                border-radius: 26px;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding-left: 25px;
                padding-right: 25px;
            }

            QPushButton:hover {
                background-color: #6b9cff;
            }

            QPushButton:pressed {
                background-color: #3b73d1;
            }

            QListWidget {
                background-color: #182235;
                border: 1px solid #34425a;
                border-radius: 10px;
                color: white;
                font-size: 15px;
                padding: 5px;
            }

            QListWidget::item {
                padding: 12px;
                border-radius: 6px;
            }

            QListWidget::item:hover {
                background-color: #263652;
            }

            QListWidget::item:selected {
                background-color: #315fa8;
            }

            QScrollArea {
                border: none;
                background-color: #101827;
            }

            QFrame#analysis_card {
                background-color: #141f32;
                border: 1px solid #263650;
                border-radius: 15px;
            }
        """)

        # ==================================================
        # ROOT LAYOUT
        # ==================================================

        root_layout = QVBoxLayout()

        root_layout.setContentsMargins(
            60,
            35,
            60,
            25
        )

        root_layout.setSpacing(0)

        # ==================================================
        # TOP SECTION
        # This section stays at the top.
        # ==================================================

        top_section = QWidget()

        top_layout = QVBoxLayout(
            top_section
        )

        top_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        top_layout.setSpacing(10)

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        title = QLabel(
            "Stock Market Analysis"
        )

        title.setObjectName(
            "title"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # --------------------------------------------------
        # Subtitle
        # --------------------------------------------------

        subtitle = QLabel(
            "Search for a company name or stock symbol"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # --------------------------------------------------
        # Search bar
        # --------------------------------------------------

        search_layout = QHBoxLayout()

        search_layout.setSpacing(
            12
        )

        self.search_bar = QLineEdit()

        self.search_bar.setPlaceholderText(
            "Search company or stock symbol..."
        )

        self.search_bar.setMinimumHeight(
            54
        )

        self.search_bar.textChanged.connect(
            self.on_search_text_changed
        )

        self.search_bar.returnPressed.connect(
            self.search_company
        )

        search_button = QPushButton(
            "Search"
        )

        search_button.setMinimumHeight(
            54
        )

        search_button.setMinimumWidth(
            130
        )

        search_button.clicked.connect(
            self.search_company
        )

        search_layout.addWidget(
            self.search_bar,
            1
        )

        search_layout.addWidget(
            search_button,
            0
        )

        # --------------------------------------------------
        # Suggestions
        # --------------------------------------------------

        self.suggestions = QListWidget()

        self.suggestions.setMaximumHeight(
            210
        )

        self.suggestions.hide()

        self.suggestions.itemClicked.connect(
            self.company_selected
        )

        # --------------------------------------------------
        # Add top section
        # --------------------------------------------------

        top_layout.addWidget(
            title
        )

        top_layout.addWidget(
            subtitle
        )

        top_layout.addSpacing(
            28
        )

        top_layout.addLayout(
            search_layout
        )

        top_layout.addWidget(
            self.suggestions
        )

        root_layout.addWidget(
            top_section
        )

        # ==================================================
        # SPACE AFTER SEARCH
        # ==================================================

        root_layout.addSpacing(
            25
        )

        # ==================================================
        # ANALYSIS AREA
        # ==================================================

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # --------------------------------------------------
        # Analysis container
        # --------------------------------------------------

        analysis_container = QWidget()

        analysis_layout = QVBoxLayout(
            analysis_container
        )

        analysis_layout.setContentsMargins(
            10,
            10,
            10,
            20
        )

        analysis_layout.setSpacing(
            15
        )

        # --------------------------------------------------
        # Analysis card
        # --------------------------------------------------

        self.analysis_card = QFrame()

        self.analysis_card.setObjectName(
            "analysis_card"
        )

        card_layout = QVBoxLayout(
            self.analysis_card
        )

        card_layout.setContentsMargins(
            25,
            20,
            25,
            20
        )

        card_layout.setSpacing(
            10
        )

        # Section title
        section_title = QLabel(
            "Company Analysis"
        )

        section_title.setObjectName(
            "section_title"
        )

        section_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # Result
        self.result_label = QLabel(
            "Search for a company to see analysis"
        )

        self.result_label.setObjectName(
            "result"
        )

        self.result_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.result_label.setWordWrap(
            True
        )

        card_layout.addWidget(
            section_title
        )

        card_layout.addWidget(
            self.result_label
        )

        # --------------------------------------------------
        # Doughnut chart
        # --------------------------------------------------

        self.chart = DoughnutChart(
            0,
            0,
            "1-Year Gain / Loss"
        )

        self.chart.setMinimumHeight(
            330
        )

        self.chart.hide()

        card_layout.addWidget(
            self.chart
        )

        # --------------------------------------------------
        # Add card
        # --------------------------------------------------

        analysis_layout.addWidget(
            self.analysis_card
        )

        analysis_layout.addStretch()

        self.scroll_area.setWidget(
            analysis_container
        )

        root_layout.addWidget(
            self.scroll_area,
            1
        )

        self.setLayout(
            root_layout
        )

    # ======================================================
    # Search Text Changed
    # ======================================================

    def on_search_text_changed(
        self,
        text
    ):

        self.selected_symbol = None

        text = text.strip()

        self.suggestions.clear()

        if len(text) < 2:

            self.suggestions.hide()

            return

        self.search_timer.start()

    # ======================================================
    # Perform Company Search
    # ======================================================

    def perform_company_search(
        self
    ):

        query = (
            self.search_bar
            .text()
            .strip()
        )

        if len(query) < 2:
            return

        self.search_worker = SearchWorker(
            query
        )

        self.search_worker.results_ready.connect(
            self.display_suggestions
        )

        self.search_worker.start()

    # ======================================================
    # Display Suggestions
    # ======================================================

    def display_suggestions(
        self,
        companies
    ):

        self.suggestions.clear()

        if not companies:

            self.suggestions.hide()

            return

        for company in companies:

            name = company.get(
                "name",
                "Unknown Company"
            )

            symbol = company.get(
                "symbol",
                ""
            )

            exchange = company.get(
                "exchange",
                ""
            )

            # Requested format:
            #
            # Company Name (CODE)

            display_text = (
                f"{name} ({symbol})"
            )

            if exchange:

                display_text += (
                    f"  •  {exchange}"
                )

            item = QListWidgetItem(
                display_text
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                company
            )

            self.suggestions.addItem(
                item
            )

        self.suggestions.show()

    # ======================================================
    # Company Selected
    # ======================================================

    def company_selected(
        self,
        item
    ):

        company = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not company:
            return

        name = company.get(
            "name",
            ""
        )

        symbol = company.get(
            "symbol",
            ""
        )

        self.selected_symbol = symbol

        self.search_bar.setText(
            f"{name} ({symbol})"
        )

        self.suggestions.hide()

        self.search_bar.setCursorPosition(
            len(
                self.search_bar.text()
            )
        )

    # ======================================================
    # Search Company
    # ======================================================

    def search_company(
        self
    ):

        text = (
            self.search_bar
            .text()
            .strip()
        )

        if not text:

            self.result_label.setText(
                "Please enter a company name "
                "or stock symbol."
            )

            self.chart.hide()

            return

        self.suggestions.hide()

        # --------------------------------------------------
        # Determine ticker symbol
        # --------------------------------------------------

        if self.selected_symbol:

            search_value = (
                self.selected_symbol
            )

        else:

            match = re.search(
                r"\(([A-Za-z0-9.\-^=]+)\)",
                text
            )

            if match:

                search_value = (
                    match.group(1)
                )

            else:

                search_value = text

        # --------------------------------------------------
        # Loading
        # --------------------------------------------------

        self.result_label.setText(
            "Loading company data..."
        )

        self.chart.hide()

        QApplication.processEvents()

        # --------------------------------------------------
        # Get company data
        # --------------------------------------------------

        result = get_company_data(
            search_value
        )

        if not result["success"]:

            self.result_label.setText(
                result["message"]
            )

            return

        # --------------------------------------------------
        # Data
        # --------------------------------------------------

        data = result["data"]

        company = data[
            "company_name"
        ]

        symbol = data[
            "symbol"
        ]

        price = data[
            "current_price"
        ]

        change = data[
            "price_change_percentage"
        ]

        currency = data[
            "currency"
        ]

        sector = data[
            "sector"
        ]

        industry = data[
            "industry"
        ]

        gain = data[
            "gain_percentage"
        ]

        loss = data[
            "loss_percentage"
        ]

        # --------------------------------------------------
        # Display company information
        # --------------------------------------------------

        self.result_label.setText(

            f"{company}\n\n"

            f"Symbol: {symbol}\n"

            f"Current Price: "
            f"{price:.2f} {currency}\n"

            f"1-Year Change: "
            f"{change:+.2f}%\n\n"

            f"Sector: {sector}\n"

            f"Industry: {industry}"
        )

        # --------------------------------------------------
        # Update chart
        # --------------------------------------------------

        self.chart.set_data(
            gain,
            loss
        )

        self.chart.show()


# ==========================================================
# Application Entry Point
# ==========================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()
