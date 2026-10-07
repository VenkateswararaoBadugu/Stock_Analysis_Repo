"""
Visualization.py

Modern Doughnut chart component showing Gain vs Loss distribution.
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

    def set_data(self, gain_percentage, loss_percentage):
        self.gain_percentage = gain_percentage
        self.loss_percentage = loss_percentage
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor("#1e293b"))

        width = self.width()
        height = self.height()

        chart_size = min(width * 0.45, height * 0.65)
        center_x = width * 0.38
        center_y = height * 0.50

        x = center_x - chart_size / 2
        y = center_y - chart_size / 2
        rect = QRectF(x, y, chart_size, chart_size)

        gain = max(0.0, min(100.0, self.gain_percentage))
        loss = max(0.0, min(100.0, self.loss_percentage))
        total = gain + loss

        # Handle No Data state
        if total <= 0:
            pen = QPen(QColor("#334155"), 26)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, 0, 360 * 16)
            self._draw_center_text(painter, center_x, center_y, "No Data")
            painter.end()
            return

        gain_angle = (gain / total) * 360.0
        loss_angle = (loss / total) * 360.0

        # Background track
        bg_pen = QPen(QColor("#0f172a"), 26)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Gain Arc (Green)
        gain_pen = QPen(QColor("#22c55e"), 24)
        gain_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(gain_pen)
        painter.drawArc(rect, 90 * 16, -int(gain_angle * 16))

        # Loss Arc (Red)
        loss_pen = QPen(QColor("#ef4444"), 24)
        loss_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(loss_pen)
        painter.drawArc(rect, int((90 - gain_angle) * 16), -int(loss_angle * 16))

        # Center Label
        self._draw_center_text(painter, center_x, center_y, f"{gain:.0f}% Gain")

        # Legend
        legend_x = width * 0.68
        legend_y = height * 0.38

        self._draw_legend_item(painter, legend_x, legend_y, "#22c55e", "Gain", gain)
        self._draw_legend_item(painter, legend_x, legend_y + 60, "#ef4444", "Loss", loss)

        painter.end()

    def _draw_center_text(self, painter, center_x, center_y, text):
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 15, QFont.Weight.Bold)
        painter.setFont(font)

        text_rect = QRectF(center_x - 70, center_y - 20, 140, 40)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_legend_item(self, painter, x, y, color, label, value):
        # Color indicator
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(x, y, 14, 14), 3, 3)

        # Label
        painter.setPen(QColor("#94a3b8"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(QRectF(x + 24, y - 3, 100, 20), Qt.AlignmentFlag.AlignLeft, label)

        # Value
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        painter.drawText(QRectF(x + 24, y + 18, 100, 22), Qt.AlignmentFlag.AlignLeft, f"{value:.1f}%")