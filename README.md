# CPU Scheduling Simulator

A tool for simulating and visualizing classic CPU scheduling algorithms. Enter a set of processes, pick an algorithm, and see the resulting Gantt chart along with waiting time, turnaround time, and completion time for each process.

This repo contains two versions of the simulator:

## 🖥️ `desktop-app/` — PyQt5 Desktop Application

A desktop GUI application built with PyQt5.

**Run locally:**
```bash
cd desktop-app
pip install -r requirements.txt
python main.py
```

## 🌐 `web-app/` — Streamlit Web Application

A browser-based version of the same simulator, built with Streamlit.

**Run locally:**
```bash
cd web-app
pip install -r requirements.txt
streamlit run app.py
```

**Live demo:** *https://cpu-scheduler-application.streamlit.app/*

## Features

- Supports classic CPU scheduling algorithms (FCFS, SJF, Round Robin, Priority Scheduling, etc.)
- Interactive Gantt chart visualization
- Per-process waiting time, turnaround time, and completion time
- Algorithm comparison view

## Project Structure

```
cpu-scheduling-simulator/
├── desktop-app/       # PyQt5 desktop version
│   ├── main.py
│   ├── algorithms.py
│   ├── results_window.py
│   ├── compare_window.py
│   └── gantt_chart.py
└── web-app/           # Streamlit web version
    ├── app.py
    ├── algorithms.py
    └── requirements.txt
```
