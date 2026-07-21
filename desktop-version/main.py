import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from algorithms import *
from results_window import ResultsWindow
from compare_window import CompareWindow


class SchedulerApp(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduling Simulator")
        self.setGeometry(400, 200, 640, 580)
        self.processes = []

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("CPU Scheduling Simulator")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #4A4E69; margin-bottom: 4px;")
        layout.addWidget(title)

        subtitle = QLabel("Configure and run CPU scheduling algorithms")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet("color: #9A8C98; margin-bottom: 8px;")
        layout.addWidget(subtitle)

        self.algorithm = QComboBox()
        self.algorithm.addItems([
            "Select Algorithm", "FCFS", "SJF", "SRTF", "Round Robin", "Priority"
        ])
        layout.addWidget(self.algorithm)

        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.form.setLabelAlignment(Qt.AlignRight)

        self.pid     = QLineEdit()
        self.arrival = QLineEdit()
        self.burst   = QLineEdit()
        self.priority_field = QLineEdit()
        self.quantum = QLineEdit()

        for field in [self.pid, self.arrival, self.burst, self.priority_field, self.quantum]:
            field.setPlaceholderText("Enter value…")

        self.form.addRow("PID",          self.pid)
        self.form.addRow("Arrival Time", self.arrival)
        self.form.addRow("Burst Time",   self.burst)

        self.priority_label = QLabel("Priority")
        self.quantum_label  = QLabel("Quantum")
        self.form.addRow(self.priority_label,  self.priority_field)
        self.form.addRow(self.quantum_label,   self.quantum)

        self.priority_order_label = QLabel("Priority Order")
        self.priority_order_combo = QComboBox()
        self.priority_order_combo.addItems([
            "Highest Number = High Priority",
            "Lowest Number = High Priority"
        ])
        self.form.addRow(self.priority_order_label, self.priority_order_combo)

        layout.addLayout(self.form)

        self.priority_label.hide()
        self.priority_field.hide()
        self.quantum_label.hide()
        self.quantum.hide()
        self.priority_order_label.hide()
        self.priority_order_combo.hide()

        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(10)
        self.add_btn = QPushButton("➕  Add Process")
        self.run_btn = QPushButton("▶  Run Scheduler")
        btn_row1.addWidget(self.add_btn)
        btn_row1.addWidget(self.run_btn)
        layout.addLayout(btn_row1)

        self.best_btn = QPushButton("🏆  Find Best Algorithm")
        self.best_btn.setStyleSheet("""
            QPushButton {
                background-color: #C9ADA7;
                border: none;
                padding: 11px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
            }
            QPushButton:hover { background-color: #B5938C; }
            QPushButton:pressed { background-color: #9A7B74; }
        """)
        layout.addWidget(self.best_btn)

        self.process_count_label = QLabel("Processes added: 0")
        self.process_count_label.setAlignment(Qt.AlignCenter)
        self.process_count_label.setStyleSheet("color: #9A8C98; font-size: 12px; margin-top: 2px;")
        layout.addWidget(self.process_count_label)

        self.setLayout(layout)

        self.algorithm.currentTextChanged.connect(self.update_form)
        self.add_btn.clicked.connect(self.add_process)
        self.run_btn.clicked.connect(self.run_scheduler)
        self.best_btn.clicked.connect(self.find_best)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #F8F7FF;
            color: #4A4E69;
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
        }
        QLineEdit {
            background-color: #FFFFFF;
            border: 1.5px solid #D6D2E8;
            padding: 7px 10px;
            border-radius: 8px;
            color: #4A4E69;
        }
        QLineEdit:focus { border: 1.5px solid #9A8CB5; }
        QComboBox {
            background-color: #FFFFFF;
            border: 1.5px solid #D6D2E8;
            padding: 7px 10px;
            border-radius: 8px;
            color: #4A4E69;
        }
        QComboBox:focus { border: 1.5px solid #9A8CB5; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            border: 1px solid #D6D2E8;
            selection-background-color: #E8E4F5;
            color: #4A4E69;
        }
        QPushButton {
            background-color: #9A8CB5;
            border: none;
            padding: 10px;
            border-radius: 10px;
            font-weight: bold;
            color: #FFFFFF;
        }
        QPushButton:hover { background-color: #7C6FA0; }
        QPushButton:pressed { background-color: #6B5F8E; }
        QLabel { font-weight: 500; color: #4A4E69; }
        QFormLayout QLabel { color: #6B6B8A; }
        """)

    def update_form(self, algo):
        self.priority_label.hide(); self.priority_field.hide()
        self.quantum_label.hide();  self.quantum.hide()
        self.priority_order_label.hide(); self.priority_order_combo.hide()
        if algo == "Priority":
            self.priority_label.show(); self.priority_field.show()
            self.priority_order_label.show(); self.priority_order_combo.show()
        elif algo == "Round Robin":
            self.quantum_label.show(); self.quantum.show()

    def add_process(self):
        pid = self.pid.text().strip()
        if not pid:
            QMessageBox.warning(self, "Error", "PID cannot be empty."); return

        if any(p["pid"] == pid for p in self.processes):
            QMessageBox.warning(self, "Duplicate PID",
                f"Process '{pid}' already exists. Use a unique PID."); return

        try:
            arrival = int(self.arrival.text())
            burst   = int(self.burst.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Arrival and Burst must be integers."); return

        if arrival < 0 or burst <= 0:
            QMessageBox.warning(self, "Error", "Arrival >= 0 and Burst > 0 required."); return

        process = {"pid": pid, "arrival": arrival, "burst": burst}

        if self.algorithm.currentText() == "Priority":
            try:
                process["priority"] = int(self.priority_field.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "Priority must be an integer."); return

        self.processes.append(process)
        self.process_count_label.setText(f"Processes added: {len(self.processes)}")
        QMessageBox.information(self, "Process Added", f"Process '{pid}' added successfully.")
        self.pid.clear(); self.arrival.clear(); self.burst.clear(); self.priority_field.clear()

    def run_scheduler(self):
        if not self.processes:
            QMessageBox.warning(self, "Error", "No processes added."); return

        algo = self.algorithm.currentText()

        if algo == "FCFS":
            result, gantt = fcfs(self.processes)
        elif algo == "SJF":
            result, gantt = sjf(self.processes)
        elif algo == "SRTF":
            result, gantt = srtf(self.processes)
        elif algo == "Priority":
            highest_is_high = (self.priority_order_combo.currentText() == "Highest Number = High Priority")
            result, gantt = priority_scheduling(self.processes, highest_is_high)
        elif algo == "Round Robin":
            try:
                q = int(self.quantum.text())
                if q <= 0: raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantum must be a positive integer."); return
            result, gantt = round_robin(self.processes, q)
        else:
            QMessageBox.warning(self, "Error", "Please select a scheduling algorithm."); return

        self.results = ResultsWindow(result, gantt, algo_name=algo, show_priority=(algo == "Priority"))
        self.results.show()

    def find_best(self):
        if not self.processes:
            QMessageBox.warning(self, "Error", "Please add processes first."); return

        # Check if any process is missing a priority value
        has_priorities = all("priority" in p for p in self.processes)

        priority_order = "lowest"  # default

        if not has_priorities:
            # Build a dialog that asks for priority for each process
            dialog = QDialog(self)
            dialog.setWindowTitle("Set Priorities for Comparison")
            dialog.setMinimumWidth(420)
            dialog.setStyleSheet("""
                QDialog { background-color: #F8F7FF; }
                QLabel { color: #4A4E69; font-size: 13px; }
                QLineEdit {
                    background-color: #FFFFFF;
                    border: 1.5px solid #D6D2E8;
                    padding: 6px 10px;
                    border-radius: 8px;
                    color: #4A4E69;
                    font-size: 13px;
                }
                QLineEdit:focus { border: 1.5px solid #9A8CB5; }
                QComboBox {
                    background-color: #FFFFFF;
                    border: 1.5px solid #D6D2E8;
                    padding: 6px 10px;
                    border-radius: 8px;
                    color: #4A4E69;
                    font-size: 13px;
                }
                QPushButton {
                    background-color: #9A8CB5;
                    border: none;
                    padding: 9px 18px;
                    border-radius: 10px;
                    font-weight: bold;
                    color: #FFFFFF;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #7C6FA0; }
            """)

            dlg_layout = QVBoxLayout(dialog)
            dlg_layout.setContentsMargins(24, 20, 24, 20)
            dlg_layout.setSpacing(10)

            info = QLabel(
                "Priorities are not set for all processes.\n"
                "Enter a priority for each process so Priority Scheduling\n"
                "can be included in the comparison:"
            )
            info.setWordWrap(True)
            info.setStyleSheet("color: #6B6B8A; font-size: 12px; margin-bottom: 4px;")
            dlg_layout.addWidget(info)

            priority_fields = {}
            for p in self.processes:
                row = QHBoxLayout()
                lbl = QLabel(f"{p['pid']}  (Arr:{p['arrival']}  Burst:{p['burst']})")
                lbl.setFixedWidth(200)
                field = QLineEdit()
                field.setPlaceholderText("Priority (integer)")
                priority_fields[p["pid"]] = field
                row.addWidget(lbl)
                row.addWidget(field)
                dlg_layout.addLayout(row)

            # Priority order combo
            order_row = QHBoxLayout()
            order_lbl = QLabel("Priority Order:")
            order_lbl.setFixedWidth(120)
            order_combo = QComboBox()
            order_combo.addItems([
                "Lowest Number = High Priority",
                "Highest Number = High Priority"
            ])
            order_row.addWidget(order_lbl)
            order_row.addWidget(order_combo)
            dlg_layout.addLayout(order_row)

            # Quantum field inside the same dialog
            q_row = QHBoxLayout()
            q_lbl = QLabel("Round Robin Quantum:")
            q_lbl.setFixedWidth(160)
            q_field = QLineEdit()
            q_field.setPlaceholderText("e.g. 2")
            q_field.setText("2")
            q_row.addWidget(q_lbl)
            q_row.addWidget(q_field)
            dlg_layout.addLayout(q_row)

            dlg_layout.addSpacing(6)
            confirm_btn = QPushButton("Confirm & Compare")
            confirm_btn.clicked.connect(dialog.accept)
            dlg_layout.addWidget(confirm_btn)

            if dialog.exec_() != QDialog.Accepted:
                return

            # Validate priorities
            updated_processes = []
            for p in self.processes:
                text = priority_fields[p["pid"]].text().strip()
                try:
                    pri = int(text)
                except ValueError:
                    QMessageBox.warning(
                        self, "Invalid Priority",
                        f"Priority for '{p['pid']}' must be an integer."
                    )
                    return
                updated_processes.append({**p, "priority": pri})

            # Validate quantum
            try:
                q = int(q_field.text())
                if q <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantum must be a positive integer.")
                return

            priority_order = (
                "highest"
                if order_combo.currentText() == "Highest Number = High Priority"
                else "lowest"
            )

            # Persist priorities back to main process list
            self.processes = updated_processes

        else:
            # Priorities already set — just ask for quantum
            q, ok = QInputDialog.getInt(
                self,
                "Round Robin Quantum",
                "Enter the quantum time for Round Robin\n(used when comparing all algorithms):",
                value=2, min=1, max=1000, step=1
            )
            if not ok:
                return

            # Determine the priority order from the current combo selection
            priority_order = (
                "highest"
                if self.priority_order_combo.currentText() == "Highest Number = High Priority"
                else "lowest"
            )

        self.compare_win = CompareWindow(
            self.processes, quantum=q, priority_order=priority_order
        )
        self.compare_win.show()


app = QApplication(sys.argv)
window = SchedulerApp()
window.show()
sys.exit(app.exec_())
