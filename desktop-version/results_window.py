import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gantt_chart import GanttChart


class StatCard(QWidget):
    def __init__(self, label, value, accent, bg):
        super().__init__()
        self.accent = QColor(accent)
        self.bg_color = QColor(bg)
        self.setFixedHeight(84)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(2)
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 9))
        lbl.setStyleSheet("color: #9A8C98; font-weight: 500;")
        val = QLabel(value)
        val.setFont(QFont("Segoe UI", 22, QFont.Bold))
        val.setStyleSheet(f"color: {accent};")
        layout.addWidget(lbl)
        layout.addWidget(val)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        p.setPen(Qt.NoPen)
        p.setBrush(self.bg_color)
        p.drawRoundedRect(rect, 12, 12)
        p.setBrush(self.accent)
        p.drawRoundedRect(0, 10, 5, rect.height() - 20, 3, 3)
        super().paintEvent(event)


class ResultsWindow(QWidget):

    def __init__(self, results, gantt, algo_name=None, show_priority=False):
        super().__init__()
        title_text = f"Results — {algo_name}" if algo_name else "Scheduling Results"
        self.setWindowTitle(f"CPU Scheduling — {title_text}")
        self.setMinimumSize(1000, 680)
        self.setGeometry(320, 110, 1050, 720)
        self.setStyleSheet("background-color: #F8F7FF;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header Banner ─────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #C9B8E8, stop:0.5 #D4C5F0, stop:1 #BFD7F5);
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(30, 0, 30, 0)

        icon_lbl = QLabel("⚙")
        icon_lbl.setFont(QFont("Segoe UI", 22))
        icon_lbl.setStyleSheet("color: #7B6FA0;")

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        t1 = QLabel(title_text)
        t1.setFont(QFont("Segoe UI", 18, QFont.Bold))
        t1.setStyleSheet("color: #4A4E69; letter-spacing: 1px;")

        if algo_name:
            t2 = QLabel(f"Algorithm:  {algo_name}")
            t2.setFont(QFont("Segoe UI", 9))
            t2.setStyleSheet("color: #B07D00;")
        else:
            t2 = QLabel("CPU Process Scheduling Simulator")
            t2.setFont(QFont("Segoe UI", 9))
            t2.setStyleSheet("color: #7B6FA0;")

        title_col.addWidget(t1)
        title_col.addWidget(t2)

        h_lay.addWidget(icon_lbl)
        h_lay.addSpacing(12)
        h_lay.addLayout(title_col)
        h_lay.addStretch()
        root.addWidget(header)

        # ── Scroll area ───────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #F8F7FF; }")

        body_widget = QWidget()
        body_widget.setStyleSheet("background: #F8F7FF;")
        body = QVBoxLayout(body_widget)
        body.setContentsMargins(30, 24, 30, 24)
        body.setSpacing(20)

        def pid_key(p):
            parts = re.split(r'(\d+)', p["pid"])
            return [int(x) if x.isdigit() else x.lower() for x in parts]

        sorted_results = sorted(results, key=pid_key)

        total_wt  = sum(p["waiting"]    for p in sorted_results)
        total_tat = sum(p["turnaround"] for p in sorted_results)
        n = len(sorted_results)
        avg_wt  = total_wt  / n
        avg_tat = total_tat / n

        # ── Stat Cards ────────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)
        for lbl, val, accent, bg in [
            ("Processes",             str(n),                              "#5B8DD9", "#E8F0FD"),
            ("Avg Waiting Time",      f"{avg_wt:.2f}",                    "#D4845A", "#FDF0EA"),
            ("Avg Turnaround Time",   f"{avg_tat:.2f}",                   "#52A775", "#E8F5EE"),
            ("Total Completion Time", str(max(p["completion"] for p in sorted_results)), "#9A6CC8", "#F2EBF9"),
        ]:
            cards_row.addWidget(StatCard(lbl, val, accent, bg))
        body.addLayout(cards_row)

        def section_label(text):
            row = QHBoxLayout()
            dot = QLabel("▌")
            dot.setStyleSheet("color: #9A8CB5; font-size: 18px;")
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl.setStyleSheet("color: #6B6B8A; letter-spacing: 1px;")
            row.addWidget(dot)
            row.addWidget(lbl)
            row.addStretch()
            w = QWidget(); w.setLayout(row)
            return w

        body.addWidget(section_label("PROCESS TABLE"))

        # ── Table ─────────────────────────────────────────────────────────
        table = QTableWidget()
        table.setRowCount(n)

        if show_priority:
            col_count = 7
            headers = [
                "PID", "Arrival Time", "Burst Time", "Priority",
                "Waiting Time", "Turnaround Time", "Completion Time"
            ]
        else:
            col_count = 6
            headers = [
                "PID", "Arrival Time", "Burst Time",
                "Waiting Time", "Turnaround Time", "Completion Time"
            ]

        table.setColumnCount(col_count)
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setFixedHeight(min(n * 42 + 44, 320))

        for row, p in enumerate(sorted_results):
            table.setRowHeight(row, 40)
            if show_priority:
                row_vals = [
                    p["pid"], p["arrival"], p["burst"], p.get("priority", ""),
                    p["waiting"], p["turnaround"], p["completion"]
                ]
            else:
                row_vals = [
                    p["pid"], p["arrival"], p["burst"],
                    p["waiting"], p["turnaround"], p["completion"]
                ]
            for col, val in enumerate(row_vals):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                if col == 0:
                    item.setFont(QFont("Segoe UI", 11, QFont.Bold))
                    item.setForeground(QColor("#5B6FA0"))
                else:
                    item.setFont(QFont("Segoe UI", 10))
                    item.setForeground(QColor("#4A4E69"))
                table.setItem(row, col, item)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F3F0FB;
                gridline-color: transparent;
                color: #4A4E69;
                font-size: 13px;
                border: 1.5px solid #DDD8F0;
                border-radius: 10px;
                outline: none;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #EDE9F8; }
            QTableWidget::item:selected { background-color: #D8D0F0; color: #4A4E69; }
            QHeaderView::section {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #C9B8E8, stop:1 #B8A8DC);
                color: #4A4E69;
                padding: 10px;
                border: none;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
        """)
        body.addWidget(table)

        body.addWidget(section_label("GANTT CHART"))

        gantt_card = QWidget()
        gantt_card.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 12px;
            border: 1.5px solid #DDD8F0;
        """)
        gantt_card_lay = QVBoxLayout(gantt_card)
        gantt_card_lay.setContentsMargins(16, 16, 16, 16)

        gantt_scroll = QScrollArea()
        gantt_scroll.setWidgetResizable(True)
        gantt_scroll.setFixedHeight(160)
        gantt_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:horizontal { height: 8px; background: #EDE9F8; border-radius: 4px; }
            QScrollBar::handle:horizontal { background: #B8A8DC; border-radius: 4px; }
        """)
        gantt_chart = GanttChart(gantt)
        gantt_scroll.setWidget(gantt_chart)
        gantt_card_lay.addWidget(gantt_scroll)
        body.addWidget(gantt_card)

        body.addStretch()
        scroll.setWidget(body_widget)
        root.addWidget(scroll)
