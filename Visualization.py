
"""
Visualization.py

Contains charts used by the Stock Market Analysis application.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
)
from PySide6.QtCore import Qt, QRectF


class DoughnutChart(QWidget):
    """
    Doughnut chart showing Gain vs Loss contribution.

    Example:

        Gain: 65%
        Loss: 35%
    """

    def __init__(
        self,
        gain_percentage=0.0,
        loss_percentage=0.0,
        title="Gain / Loss"
    ):
        super().__init__()

        self.gain_percentage = gain_percentage
        self.loss_percentage = loss_percentage
        self.title = title

        self.setMinimumHeight(330)
        self.setMinimumWidth(400)

    def set_data(
        self,
        gain_percentage,
        loss_percentage
    ):
        self.gain_percentage = gain_percentage
        self.loss_percentage = loss_percentage

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        # --------------------------------------------------
        # Background
        # --------------------------------------------------

        painter.fillRect(
            self.rect(),
            QColor("#101827")
        )

        width = self.width()
        height = self.height()

        # --------------------------------------------------
        # Chart dimensions
        # --------------------------------------------------

        chart_size = min(
            width * 0.48,
            height * 0.70
        )

        center_x = width * 0.38
        center_y = height * 0.48

        x = center_x - chart_size / 2
        y = center_y - chart_size / 2

        rect = QRectF(
            x,
            y,
            chart_size,
            chart_size
        )

        # --------------------------------------------------
        # Values
        # --------------------------------------------------

        gain = max(
            0.0,
            min(100.0, self.gain_percentage)
        )

        loss = max(
            0.0,
            min(100.0, self.loss_percentage)
        )

        total = gain + loss

        # --------------------------------------------------
        # If no data
        # --------------------------------------------------

        if total <= 0:

            painter.setPen(
                QPen(
                    QColor("#34425a"),
                    30
                )
            )

            painter.drawArc(
                rect,
                0,
                360 * 16
            )

            self._draw_center_text(
                painter,
                center_x,
                center_y,
                "No Data"
            )

            painter.end()

            return

        # Normalize to 100%
        gain_angle = (
            gain / total
        ) * 360.0

        loss_angle = (
            loss / total
        ) * 360.0

        # --------------------------------------------------
        # Background ring
        # --------------------------------------------------

        painter.setPen(
            QPen(
                QColor("#263247"),
                30
            )
        )

        painter.drawArc(
            rect,
            0,
            360 * 16
        )

        # --------------------------------------------------
        # Gain
        # --------------------------------------------------

        painter.setPen(
            QPen(
                QColor("#35c759"),
                30
            )
        )

        painter.drawArc(
            rect,
            90 * 16,
            -int(gain_angle * 16)
        )

        # --------------------------------------------------
        # Loss
        # --------------------------------------------------

        painter.setPen(
            QPen(
                QColor("#ff4d5e"),
                30
            )
        )

        painter.drawArc(
            rect,
            int(
                (90 - gain_angle) * 16
            ),
            -int(loss_angle * 16)
        )

        # --------------------------------------------------
        # Center text
        # --------------------------------------------------

        self._draw_center_text(
            painter,
            center_x,
            center_y,
            "100%"
        )

        # --------------------------------------------------
        # Legend
        # --------------------------------------------------

        legend_x = width * 0.67
        legend_y = height * 0.35

        self._draw_legend_item(
            painter,
            legend_x,
            legend_y,
            "#35c759",
            "Gain",
            gain
        )

        self._draw_legend_item(
            painter,
            legend_x,
            legend_y + 65,
            "#ff4d5e",
            "Loss",
            loss
        )

        painter.end()

    # ======================================================
    # Center text
    # ======================================================

    def _draw_center_text(
        self,
        painter,
        center_x,
        center_y,
        text
    ):

        painter.setPen(
            QColor("white")
        )

        font = QFont(
            "Arial",
            20,
            QFont.Weight.Bold
        )

        painter.setFont(font)

        text_rect = QRectF(
            center_x - 70,
            center_y - 20,
            140,
            40
        )

        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter,
            text
        )

    # ======================================================
    # Legend
    # ======================================================

    def _draw_legend_item(
        self,
        painter,
        x,
        y,
        color,
        label,
        value
    ):

        # Color box
        painter.setBrush(
            QBrush(QColor(color))
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.drawRoundedRect(
            QRectF(
                x,
                y,
                16,
                16
            ),
            4,
            4
        )

        # Label
        painter.setPen(
            QColor("white")
        )

        font = QFont(
            "Arial",
            12
        )

        painter.setFont(font)

        painter.drawText(
            QRectF(
                x + 28,
                y - 3,
                100,
                24
            ),
            Qt.AlignmentFlag.AlignLeft,
            label
        )

        # Percentage
        font = QFont(
            "Arial",
            13,
            QFont.Weight.Bold
        )

        painter.setFont(font)

        painter.drawText(
            QRectF(
                x + 28,
                y + 20,
                100,
                24
            ),
            Qt.AlignmentFlag.AlignLeft,
            f"{value:.1f}%"
        )
