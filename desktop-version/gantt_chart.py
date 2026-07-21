from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient, QPen, QFontMetrics
from PyQt5.QtCore import Qt, QRect, QRectF


# Soft pastel palette for Gantt bars
PALETTE = [
    ("#A8C5E8", "#C5DBEE"),   # soft blue
    ("#A8D5B5", "#C5E5CE"),   # soft green
    ("#E8B4A8", "#F0CAC5"),   # soft coral
    ("#C5A8E8", "#DAC5F0"),   # soft violet
    ("#E8D5A8", "#F0E5C5"),   # soft peach
    ("#A8D8E8", "#C5E8F0"),   # soft cyan
    ("#E8A8C5", "#F0C5DA"),   # soft pink
    ("#B5C8A8", "#CCDAC5"),   # soft sage
    ("#D5A8E8", "#E5C5F0"),   # soft lavender
    ("#E8C8A8", "#F0DAC5"),   # soft amber
]


class GanttChart(QWidget):

    BAR_Y       = 45
    BAR_H       = 48
    SCALE       = 38
    LEFT_PAD    = 20
    RIGHT_PAD   = 40
    TICK_H      = 8
    LABEL_Y_OFF = 20

    def __init__(self, gantt):
        super().__init__()
        self.gantt = gantt
        self._assign_colors()

        if gantt:
            total_time = gantt[-1][2]
        else:
            total_time = 0
        w = self.LEFT_PAD + int(total_time * self.SCALE) + self.RIGHT_PAD
        self.setMinimumWidth(max(w, 600))
        self.setMinimumHeight(130)

    def _assign_colors(self):
        seen = {}
        idx = 0
        for pid, _, _ in self.gantt:
            if pid not in seen:
                seen[pid] = PALETTE[idx % len(PALETTE)]
                idx += 1
        self.color_map = seen

    def paintEvent(self, event):
        if not self.gantt:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        painter.fillRect(self.rect(), QColor("#FFFFFF"))

        x = self.LEFT_PAD
        y = self.BAR_Y
        h = self.BAR_H

        pid_font  = QFont("Segoe UI", 10, QFont.Bold)
        time_font = QFont("Segoe UI", 8)
        painter.setFont(pid_font)

        for seg_idx, (pid, start, end) in enumerate(self.gantt):
            width = int((end - start) * self.SCALE)
            base_color, light_color = self.color_map[pid]

            grad = QLinearGradient(x, y, x, y + h)
            grad.setColorAt(0.0, QColor(light_color))
            grad.setColorAt(1.0, QColor(base_color))
            painter.setBrush(grad)

            pen = QPen(QColor(base_color).darker(115))
            pen.setWidth(1)
            painter.setPen(pen)

            rect = QRectF(x, y, width, h)
            painter.drawRoundedRect(rect, 6, 6)

            # PID label
            painter.setPen(QPen(QColor("#4A4E69")))
            painter.setFont(pid_font)
            fm = QFontMetrics(pid_font)
            tw = fm.horizontalAdvance(pid)
            if tw + 6 <= width:
                painter.drawText(
                    int(x + (width - tw) / 2),
                    int(y + h / 2 + fm.ascent() / 2 - 2),
                    pid
                )

            # Time ticks
            painter.setFont(time_font)
            fm2 = QFontMetrics(time_font)
            painter.setPen(QPen(QColor("#9A8C98")))

            tick_x = x
            painter.drawLine(tick_x, y + h, tick_x, y + h + self.TICK_H)

            t_str = str(start)
            tw2 = fm2.horizontalAdvance(t_str)
            painter.drawText(
                int(tick_x - tw2 / 2),
                int(y + h + self.TICK_H + fm2.ascent() + 2),
                t_str
            )

            x += width

        # Final end time
        painter.setFont(time_font)
        fm2 = QFontMetrics(time_font)
        painter.setPen(QPen(QColor("#9A8C98")))
        painter.drawLine(x, y + h, x, y + h + self.TICK_H)
        t_str = str(self.gantt[-1][2])
        tw2 = fm2.horizontalAdvance(t_str)
        painter.drawText(
            int(x - tw2 / 2),
            int(y + h + self.TICK_H + fm2.ascent() + 2),
            t_str
        )

        # Timeline baseline
        painter.setPen(QPen(QColor("#C5BBDE"), 2))
        painter.drawLine(self.LEFT_PAD, y + h, x, y + h)

        painter.end()
