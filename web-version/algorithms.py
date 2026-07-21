def fcfs(processes):
    processes = sorted(processes, key=lambda x: (x["arrival"], x["pid"]))
    time = 0
    result = []
    gantt = []

    for p in processes:
        if time < p["arrival"]:
            time = p["arrival"]
        start = time
        completion = time + p["burst"]
        tat = completion - p["arrival"]
        wt = tat - p["burst"]
        result.append({
            "pid": p["pid"], "arrival": p["arrival"], "burst": p["burst"],
            "completion": completion, "waiting": wt, "turnaround": tat
        })
        gantt.append((p["pid"], start, completion))
        time = completion

    return result, gantt


def sjf(processes):
    processes = processes.copy()
    time = 0
    completed = []
    gantt = []

    while processes:
        available = [p for p in processes if p["arrival"] <= time]
        if not available:
            time += 1
            continue
        p = min(available, key=lambda x: (x["burst"], x["pid"]))
        processes.remove(p)
        start = time
        completion = time + p["burst"]
        tat = completion - p["arrival"]
        wt = tat - p["burst"]
        completed.append({
            "pid": p["pid"], "arrival": p["arrival"], "burst": p["burst"],
            "completion": completion, "waiting": wt, "turnaround": tat
        })
        gantt.append((p["pid"], start, completion))
        time = completion

    return completed, gantt


def srtf(processes):
    processes = processes.copy()
    n = len(processes)
    remaining = {p["pid"]: p["burst"] for p in processes}
    arrival = {p["pid"]: p["arrival"] for p in processes}
    burst = {p["pid"]: p["burst"] for p in processes}

    time = 0
    completed = 0
    gantt = []
    result = {}
    current_pid = None
    start_time = 0

    while completed < n:
        available = [p for p in processes if p["arrival"] <= time and remaining[p["pid"]] > 0]
        if not available:
            time += 1
            continue
        shortest = min(available, key=lambda x: (remaining[x["pid"]], x["pid"]))
        pid = shortest["pid"]

        if current_pid != pid:
            if current_pid is not None:
                gantt.append((current_pid, start_time, time))
            current_pid = pid
            start_time = time

        remaining[pid] -= 1
        time += 1

        if remaining[pid] == 0:
            completion = time
            tat = completion - arrival[pid]
            wt = tat - burst[pid]
            result[pid] = {
                "pid": pid, "arrival": arrival[pid], "burst": burst[pid],
                "completion": completion, "waiting": wt, "turnaround": tat
            }
            completed += 1

    gantt.append((current_pid, start_time, time))
    return list(result.values()), gantt


def priority_scheduling(processes, highest_is_high=False):
    """
    highest_is_high=True  -> larger number = higher priority (scheduled first)
    highest_is_high=False -> smaller number = higher priority (default / classic)
    """
    processes = processes.copy()
    time = 0
    completed = []
    gantt = []

    while processes:
        available = [p for p in processes if p["arrival"] <= time]
        if not available:
            time += 1
            continue

        if highest_is_high:
            # Highest number wins; negate priority for min() to pick largest
            p = max(available, key=lambda x: (x["priority"], -x["arrival"]))
        else:
            # Lowest number wins (classic)
            p = min(available, key=lambda x: (x["priority"], x["arrival"]))

        processes.remove(p)
        start = time
        completion = time + p["burst"]
        tat = completion - p["arrival"]
        wt = tat - p["burst"]

        completed.append({
            "pid": p["pid"], "arrival": p["arrival"], "burst": p["burst"],
            "priority": p["priority"],
            "completion": completion, "waiting": wt, "turnaround": tat
        })
        gantt.append((p["pid"], start, completion))
        time = completion

    return completed, gantt


def round_robin(processes, quantum):
    queue = []
    time = 0
    gantt = []
    result = []

    processes = sorted(processes, key=lambda x: x["arrival"])
    remaining = {p["pid"]: p["burst"] for p in processes}

    while processes or queue:
        while processes and processes[0]["arrival"] <= time:
            queue.append(processes.pop(0))

        if not queue:
            time += 1
            continue

        current = queue.pop(0)
        pid = current["pid"]
        start = time
        exec_time = min(quantum, remaining[pid])
        time += exec_time
        remaining[pid] -= exec_time
        gantt.append((pid, start, time))

        while processes and processes[0]["arrival"] <= time:
            queue.append(processes.pop(0))

        if remaining[pid] > 0:
            queue.append(current)
        else:
            completion = time
            tat = completion - current["arrival"]
            wt = tat - current["burst"]
            result.append({
                "pid": pid, "arrival": current["arrival"], "burst": current["burst"],
                "completion": completion, "waiting": wt, "turnaround": tat
            })

    return result, gantt
