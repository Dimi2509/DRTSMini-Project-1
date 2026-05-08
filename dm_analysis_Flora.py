import math


def compute_dm_wcrts(task_templates):
    """
    Compute analytical Worst-Case Response Times under Deadline Monotonic.
    Returns one WCRT per task.
    """

    # Deadline Monotonic: smaller relative deadline = higher priority
    sorted_tasks = sorted(task_templates, key=lambda t: t.deadline)

    response_times = {}
    priority_order = [task.id for task in sorted_tasks]

    utilization = sum(
        task.worst_case_time / task.time_period
        for task in task_templates
    )

    for i, task in enumerate(sorted_tasks):
        Ci = task.worst_case_time
        Di = task.deadline

        Ri = Ci

        while True:
            R_old = Ri

            interference = 0
            for h in range(i):
                hp_task = sorted_tasks[h]
                Ch = hp_task.worst_case_time
                Th = hp_task.time_period

                interference += math.ceil(R_old / Th) * Ch

            Ri = Ci + interference

            # Save also the value that caused the failure
            response_times[task.id] = Ri

            if Ri > Di:
                return {
                    "schedulable": False,
                    "response_times": response_times,
                    "failed_task_id": task.id,
                    "priority_order": priority_order,
                    "utilization": utilization,
                }

            if Ri == R_old:
                break

    return {
        "schedulable": True,
        "response_times": response_times,
        "failed_task_id": None,
        "priority_order": priority_order,
        "utilization": utilization,
    }

