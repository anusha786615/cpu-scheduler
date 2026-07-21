import re
import pandas as pd
import plotly.express as px
import streamlit as st

from algorithms import fcfs, sjf, srtf, priority_scheduling, round_robin

st.set_page_config(page_title="CPU Scheduling Simulator", page_icon="⚙️", layout="wide")

# ── Session state ─────────────────────────────────────────────────────────
if "processes" not in st.session_state:
    st.session_state.processes = []

PASTEL = {
    "bg": "#F8F7FF",
    "accent": "#9A8CB5",
    "text": "#4A4E69",
}

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {PASTEL['bg']}; }}
    h1, h2, h3 {{ color: {PASTEL['text']}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚙️ CPU Scheduling Simulator")
st.caption("Configure and run CPU scheduling algorithms — right in your browser")

# ── Sidebar: algorithm + process entry ────────────────────────────────────
with st.sidebar:
    st.header("Configuration")
    algo = st.selectbox(
        "Algorithm",
        ["Select Algorithm", "FCFS", "SJF", "SRTF", "Round Robin", "Priority"],
    )

    st.subheader("Add a process")
    pid = st.text_input("PID", placeholder="e.g. P1")
    arrival = st.number_input("Arrival Time", min_value=0, step=1, value=0)
    burst = st.number_input("Burst Time", min_value=1, step=1, value=1)

    priority_val = None
    if algo == "Priority":
        priority_val = st.number_input("Priority", step=1, value=0)
        priority_order = st.radio(
            "Priority Order",
            ["Lowest Number = High Priority", "Highest Number = High Priority"],
        )

    quantum = None
    if algo == "Round Robin":
        quantum = st.number_input("Quantum", min_value=1, step=1, value=2)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➕ Add Process", use_container_width=True):
            if not pid.strip():
                st.warning("PID cannot be empty.")
            elif any(p["pid"] == pid for p in st.session_state.processes):
                st.warning(f"Process '{pid}' already exists. Use a unique PID.")
            else:
                proc = {"pid": pid.strip(), "arrival": int(arrival), "burst": int(burst)}
                if algo == "Priority":
                    proc["priority"] = int(priority_val)
                st.session_state.processes.append(proc)
                st.success(f"Process '{pid}' added.")

    with col_b:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.processes = []
            st.rerun()

    st.caption(f"Processes added: {len(st.session_state.processes)}")

# ── Process table preview ─────────────────────────────────────────────────
if st.session_state.processes:
    st.subheader("Current Processes")
    st.dataframe(pd.DataFrame(st.session_state.processes), use_container_width=True, hide_index=True)
else:
    st.info("Add processes from the sidebar to get started.")


def pid_sort_key(p):
    parts = re.split(r"(\d+)", p["pid"])
    return [int(x) if x.isdigit() else x.lower() for x in parts]


def render_results(result, gantt, algo_name, show_priority=False):
    sorted_results = sorted(result, key=pid_sort_key)
    n = len(sorted_results)
    total_wt = sum(p["waiting"] for p in sorted_results)
    total_tat = sum(p["turnaround"] for p in sorted_results)
    avg_wt = total_wt / n
    avg_tat = total_tat / n

    st.markdown(f"### Results — {algo_name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Processes", n)
    c2.metric("Avg Waiting Time", f"{avg_wt:.2f}")
    c3.metric("Avg Turnaround Time", f"{avg_tat:.2f}")
    c4.metric("Total Completion Time", max(p["completion"] for p in sorted_results))

    st.markdown("**Process Table**")
    cols = ["pid", "arrival", "burst"]
    if show_priority:
        cols.append("priority")
    cols += ["waiting", "turnaround", "completion"]
    df = pd.DataFrame(sorted_results)[cols]
    df.columns = [c.replace("_", " ").title() for c in cols]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("**Gantt Chart**")
    gantt_df = pd.DataFrame(gantt, columns=["pid", "start", "end"])
    gantt_df["duration"] = gantt_df["end"] - gantt_df["start"]
    fig = px.bar(
        gantt_df,
        base="start",
        x="duration",
        y=["Timeline"] * len(gantt_df),
        color="pid",
        orientation="h",
        text="pid",
        title=None,
    )
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="",
        showlegend=True,
        height=200,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_traces(textposition="inside")
    st.plotly_chart(fig, use_container_width=True)


def run_all_algorithms(processes, quantum=2, priority_order="lowest"):
    algos = []

    def avg(results, key):
        return sum(r[key] for r in results) / len(results)

    r, g = fcfs(processes)
    algos.append({"name": "FCFS", "awt": avg(r, "waiting"), "atat": avg(r, "turnaround"), "result": r, "gantt": g})

    r, g = sjf(processes)
    algos.append({"name": "SJF", "awt": avg(r, "waiting"), "atat": avg(r, "turnaround"), "result": r, "gantt": g})

    r, g = srtf(processes)
    algos.append({"name": "SRTF", "awt": avg(r, "waiting"), "atat": avg(r, "turnaround"), "result": r, "gantt": g})

    r, g = round_robin(processes, quantum)
    algos.append({
        "name": f"Round Robin (q={quantum})",
        "awt": avg(r, "waiting"), "atat": avg(r, "turnaround"), "result": r, "gantt": g,
    })

    if all("priority" in p for p in processes):
        highest_is_high = priority_order == "highest"
        r, g = priority_scheduling(processes, highest_is_high=highest_is_high)
        algos.append({"name": "Priority", "awt": avg(r, "waiting"), "atat": avg(r, "turnaround"), "result": r, "gantt": g})

    return algos


def build_insight(name):
    insights = {
        "FCFS": "FCFS won because the processes arrived in an order that minimized waiting. It works best when burst times are similar. Simple and starvation-free.",
        "SJF": "SJF won because it always picks the shortest available process next, minimizing average waiting time. Optimal for batch systems with known burst times.",
        "SRTF": "SRTF won because it preempts running processes whenever a shorter one arrives, giving the globally minimum average waiting time among all algorithms.",
        "Priority": "Priority Scheduling won because high-priority processes also had short burst times here, keeping overall waiting low. Best when process importance varies.",
    }
    for key in insights:
        if key in name:
            return insights[key]
    return "Round Robin won because the quantum matched burst times well, distributing CPU time fairly. Prevents any process from monopolizing the CPU — best for interactive systems."


# ── Action buttons ─────────────────────────────────────────────────────────
st.divider()
run_col, best_col = st.columns(2)

with run_col:
    if st.button("▶ Run Scheduler", type="primary", use_container_width=True):
        if not st.session_state.processes:
            st.warning("No processes added.")
        elif algo == "Select Algorithm":
            st.warning("Please select a scheduling algorithm.")
        else:
            processes = st.session_state.processes
            if algo == "FCFS":
                result, gantt = fcfs(processes)
            elif algo == "SJF":
                result, gantt = sjf(processes)
            elif algo == "SRTF":
                result, gantt = srtf(processes)
            elif algo == "Priority":
                highest_is_high = priority_order == "Highest Number = High Priority"
                result, gantt = priority_scheduling(processes, highest_is_high)
            elif algo == "Round Robin":
                result, gantt = round_robin(processes, int(quantum))
            render_results(result, gantt, algo, show_priority=(algo == "Priority"))

with best_col:
    if st.button("🏆 Find Best Algorithm", use_container_width=True):
        if not st.session_state.processes:
            st.warning("Please add processes first.")
        else:
            processes = st.session_state.processes
            has_priorities = all("priority" in p for p in processes)
            p_order = "lowest"
            rr_quantum = 2

            with st.expander("Comparison settings", expanded=not has_priorities):
                rr_quantum = st.number_input("Round Robin Quantum for comparison", min_value=1, value=2, key="cmp_q")
                if not has_priorities:
                    st.caption("Priorities aren't set for all processes — Priority Scheduling will be skipped in the comparison unless you add priorities to every process from the sidebar.")
                else:
                    p_order_choice = st.radio(
                        "Priority Order for comparison",
                        ["Lowest Number = High Priority", "Highest Number = High Priority"],
                        key="cmp_order",
                    )
                    p_order = "highest" if p_order_choice == "Highest Number = High Priority" else "lowest"

            all_results = run_all_algorithms(processes, quantum=int(rr_quantum), priority_order=p_order)
            all_results.sort(key=lambda x: (x["awt"], x["atat"]))
            best = all_results[0]

            st.success(f"🏆 Best Algorithm: **{best['name']}**  |  Avg Waiting Time: {best['awt']:.2f}  |  Avg Turnaround Time: {best['atat']:.2f}")

            st.markdown("**Comparison Table** (sorted by Average Waiting Time)")
            comp_df = pd.DataFrame([
                {"Rank": i + 1, "Algorithm": r["name"], "Avg Waiting Time": round(r["awt"], 2), "Avg Turnaround Time": round(r["atat"], 2)}
                for i, r in enumerate(all_results)
            ])
            st.dataframe(comp_df, use_container_width=True, hide_index=True)

            st.info(f"💡 **Why is this the best?**\n\n{build_insight(best['name'])}")

            st.markdown("**View full details for any algorithm:**")
            tabs = st.tabs([r["name"] for r in all_results])
            for tab, r in zip(tabs, all_results):
                with tab:
                    render_results(r["result"], r["gantt"], r["name"], show_priority=(r["name"] == "Priority"))
