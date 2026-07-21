import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from algorithms import fcfs, sjf, srtf, priority_scheduling, round_robin
from results_window import ResultsWindow


class CompareWindow(QWidget):

    def __init__(self, processes, quantum=2, priority_order="lowest"):
        super().__init__()
        self.setWindowTitle("Best Algorithm Finder")
        self.setMinimumSize(860, 640)
        self.setGeometry(280, 100, 900, 680)
        self.setStyleSheet("background-color: #F8F7FF;")

        self._detail_windows = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #C9B8E8, stop:0.5 #D4C5F0, stop:1 #BFD7F5);
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(28, 0, 28, 0)

        icon = QLabel("🏆")
        icon.setFont(QFont("Segoe UI", 22))

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        t1 = QLabel("Best Algorithm Finder")
        t1.setFont(QFont("Segoe UI", 17, QFont.Bold))
        t1.setStyleSheet("color: #4A4E69;")
        t2 = QLabel("Click  'View Details'  to see full results, Gantt chart and process table for any algorithm")
        t2.setFont(QFont("Segoe UI", 9))
        t2.setStyleSheet("color: #7B6FA0;")
        title_col.addWidget(t1)
        title_col.addWidget(t2)

        h_lay.addWidget(icon)
        h_lay.addSpacing(12)
        h_lay.addLayout(title_col)
        h_lay.addStretch()
        root.addWidget(header)

        # ── Scroll body ───────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #F8F7FF; }")

        body_w = QWidget()
        body_w.setStyleSheet("background: #F8F7FF;")
        body = QVBoxLayout(body_w)
        body.setContentsMargins(28, 22, 28, 28)
        body.setSpacing(16)

        self.all_results = self._run_all(processes, quantum, priority_order)
        self.all_results.sort(key=lambda x: (x["awt"], x["atat"]))
        best = self.all_results[0]

        # ── Winner Banner ─────────────────────────────────────────────────
        winner_card = QWidget()
        winner_card.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #D4EDDA, stop:1 #C3E6CB);
            border-radius: 14px;
            border: 2px solid #A8D5B5;
        """)
        winner_card.setFixedHeight(90)
        wc_lay = QHBoxLayout(winner_card)
        wc_lay.setContentsMargins(24, 0, 24, 0)

        trophy = QLabel("🏆")
        trophy.setFont(QFont("Segoe UI", 30))

        w_text = QVBoxLayout()
        w_text.setSpacing(2)
        w1 = QLabel(f"Best Algorithm:  {best['name']}")
        w1.setFont(QFont("Segoe UI", 16, QFont.Bold))
        w1.setStyleSheet("color: #2D6A4F;")
        w2 = QLabel(
            f"Avg Waiting Time: {best['awt']:.2f}   |   "
            f"Avg Turnaround Time: {best['atat']:.2f}"
        )
        w2.setFont(QFont("Segoe UI", 10))
        w2.setStyleSheet("color: #52796F;")
        w_text.addWidget(w1)
        w_text.addWidget(w2)

        view_best_btn = QPushButton("📊 View Details")
        view_best_btn.setFixedSize(130, 38)
        view_best_btn.setStyleSheet("""
            QPushButton {
                background-color: #52B788;
                color: white;
                border: none;
                border-radius: 9px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #40916C; }
        """)
        view_best_btn.clicked.connect(
            lambda checked, r=best: self._open_details(r)
        )

        wc_lay.addWidget(trophy)
        wc_lay.addSpacing(14)
        wc_lay.addLayout(w_text)
        wc_lay.addStretch()
        wc_lay.addWidget(view_best_btn)
        body.addWidget(winner_card)

        body.addWidget(self._section_label(
            "COMPARISON TABLE  —  sorted by Average Waiting Time  |  Click 'View Details' for full results"
        ))

        # ── Rank styles: (bg, text_color, border, verdict) ───────────────
        RANK_STYLES = {
            0: ("#D4EDDA", "#2D6A4F", "#A8D5B5", "🥇 Best"),
            1: ("#D6E8FB", "#1A4F8A", "#A9CAED", "🥈 2nd"),
            2: ("#EDE0F5", "#6A3093", "#CBAEE0", "🥉 3rd"),
        }
        DEFAULT_STYLE = ("#FFFFFF", "#6B6B8A", "#DDD8F0", "")

        for rank, r in enumerate(self.all_results):
            bg, fg, border, verdict = RANK_STYLES.get(rank, DEFAULT_STYLE)
            card = self._make_algo_card(r, rank, bg, fg, border, verdict)
            body.addWidget(card)

        # ── Insight Box ───────────────────────────────────────────────────
        insight_card = QWidget()
        insight_card.setStyleSheet("""
            background-color: #FFF8E7;
            border-radius: 12px;
            border: 1px solid #FFE0A0;
        """)
        ic_lay = QVBoxLayout(insight_card)
        ic_lay.setContentsMargins(20, 16, 20, 16)

        ic_title = QLabel("💡  Why is this the best?")
        ic_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        ic_title.setStyleSheet("color: #B07D00;")

        ic_text = QLabel(self._build_insight(best["name"]))
        ic_text.setFont(QFont("Segoe UI", 10))
        ic_text.setStyleSheet("color: #7A6030;")
        ic_text.setWordWrap(True)

        ic_lay.addWidget(ic_title)
        ic_lay.addSpacing(6)
        ic_lay.addWidget(ic_text)
        body.addWidget(insight_card)

        body.addStretch()
        scroll.setWidget(body_w)
        root.addWidget(scroll)

    def _make_algo_card(self, r, rank, bg, fg, border, verdict):
        card = QWidget()
        card.setFixedHeight(72)
        card.setStyleSheet(f"""
            background-color: {bg};
            border-radius: 10px;
            border: 1.5px solid {border};
        """)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(12)

        rank_lbl = QLabel(f"#{rank + 1}")
        rank_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        rank_lbl.setStyleSheet(f"color: {fg}; border: none; background: transparent;")
        rank_lbl.setFixedWidth(36)

        name_lbl = QLabel(r["name"])
        name_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold if rank == 0 else QFont.Normal))
        name_lbl.setStyleSheet(f"color: {fg}; border: none; background: transparent;")
        name_lbl.setMinimumWidth(180)

        awt_col = QVBoxLayout()
        awt_col.setSpacing(1)
        awt_title = QLabel("Avg Waiting Time")
        awt_title.setFont(QFont("Segoe UI", 8))
        awt_title.setStyleSheet("color: #9A8C98; border: none; background: transparent;")
        awt_val = QLabel(f"{r['awt']:.2f}")
        awt_val.setFont(QFont("Segoe UI", 13, QFont.Bold))
        awt_val.setStyleSheet(f"color: {fg}; border: none; background: transparent;")
        awt_col.addWidget(awt_title)
        awt_col.addWidget(awt_val)

        atat_col = QVBoxLayout()
        atat_col.setSpacing(1)
        atat_title = QLabel("Avg Turnaround Time")
        atat_title.setFont(QFont("Segoe UI", 8))
        atat_title.setStyleSheet("color: #9A8C98; border: none; background: transparent;")
        atat_val = QLabel(f"{r['atat']:.2f}")
        atat_val.setFont(QFont("Segoe UI", 13, QFont.Bold))
        atat_val.setStyleSheet(f"color: {fg}; border: none; background: transparent;")
        atat_col.addWidget(atat_title)
        atat_col.addWidget(atat_val)

        verdict_lbl = QLabel(verdict)
        verdict_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        verdict_lbl.setStyleSheet(f"color: {fg}; border: none; background: transparent;")
        verdict_lbl.setFixedWidth(70)
        verdict_lbl.setAlignment(Qt.AlignCenter)

        detail_btn = QPushButton("📊 View Details")
        detail_btn.setFixedSize(130, 36)
        detail_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {fg};
                border: 1.5px solid {border};
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: rgba(0,0,0,0.06);
            }}
        """)
        detail_btn.clicked.connect(lambda checked, res=r: self._open_details(res))

        lay.addWidget(rank_lbl)
        lay.addWidget(name_lbl)
        lay.addStretch()
        lay.addLayout(awt_col)
        lay.addSpacing(30)
        lay.addLayout(atat_col)
        lay.addSpacing(20)
        lay.addWidget(verdict_lbl)
        lay.addSpacing(10)
        lay.addWidget(detail_btn)

        return card

    def _open_details(self, r):
        win = ResultsWindow(r["result"], r["gantt"], algo_name=r["name"], show_priority=(r["name"] == "Priority"))
        win.show()
        self._detail_windows.append(win)

    def _section_label(self, text):
        row = QHBoxLayout()
        row.setSpacing(10)
        dot = QLabel("▌")
        dot.setStyleSheet("color: #9A8CB5; font-size: 18px;")
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet("color: #6B6B8A; letter-spacing: 0.8px;")
        row.addWidget(dot)
        row.addWidget(lbl)
        row.addStretch()
        w = QWidget()
        w.setLayout(row)
        return w

    def _run_all(self, processes, quantum, priority_order="lowest"):
        algos = []

        def avg(results, key):
            return sum(r[key] for r in results) / len(results)

        r, g = fcfs(processes)
        algos.append({"name": "FCFS", "awt": avg(r, "waiting"),
                      "atat": avg(r, "turnaround"), "result": r, "gantt": g})

        r, g = sjf(processes)
        algos.append({"name": "SJF", "awt": avg(r, "waiting"),
                      "atat": avg(r, "turnaround"), "result": r, "gantt": g})

        r, g = srtf(processes)
        algos.append({"name": "SRTF", "awt": avg(r, "waiting"),
                      "atat": avg(r, "turnaround"), "result": r, "gantt": g})

        r, g = round_robin(processes, quantum)
        algos.append({"name": f"Round Robin (q={quantum})", "awt": avg(r, "waiting"),
                      "atat": avg(r, "turnaround"), "result": r, "gantt": g})

        if all("priority" in p for p in processes):
            highest_is_high = (priority_order == "highest")
            r, g = priority_scheduling(processes, highest_is_high=highest_is_high)
            algos.append({"name": "Priority", "awt": avg(r, "waiting"),
                          "atat": avg(r, "turnaround"), "result": r, "gantt": g})

        return algos

    def _build_insight(self, name):
        insights = {
            "FCFS":     ("FCFS won because the processes arrived in an order that minimized waiting. "
                         "It works best when burst times are similar. Simple and starvation-free."),
            "SJF":      ("SJF won because it always picks the shortest available process next, "
                         "minimizing average waiting time. Optimal for batch systems with known burst times."),
            "SRTF":     ("SRTF won because it preempts running processes whenever a shorter one arrives, "
                         "giving the globally minimum average waiting time among all algorithms."),
            "Priority": ("Priority Scheduling won because high-priority processes also had short burst times "
                         "here, keeping overall waiting low. Best when process importance varies."),
        }
        for key in insights:
            if key in name:
                return insights[key]
        return ("Round Robin won because the quantum matched burst times well, distributing CPU time "
                "fairly. Prevents any process from monopolizing the CPU — best for interactive systems.")
