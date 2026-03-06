import math
from parser import parse_csv_files, dataframe_to_task_templates

dataset = parse_csv_files(dataset_name="automotive", utilization="0.50")

# Following pseudo-code book 
def dm_rta_tasks(task_templates):

    # Task sorting based on their priority
    task_templates = sorted(task_templates, key=lambda t: t.deadline) 

    response_times = []

    for i in range(len(task_templates)):
        # Job paramethers
        Ci = task_templates[i].worst_case_time
        Di = task_templates[i].deadline
        Ri = Ci
        while True:
            Rold = Ri
            interference = 0
            for h in range(i):
                Ch = task_templates[h].worst_case_time
                Th = task_templates[h].time_period
                interference += math.ceil(Rold / Th) * Ch
            Ri = Ci + interference
            if Ri > Di:
                return {
                    "schedulable": False,
                    "response_times": None
                }
            if Ri == Rold:
                break
        response_times.append(Ri)
    return {
        "schedulable": True,
        "response_times": response_times
    }

for df in dataset:
    task_templates = dataframe_to_task_templates(df)
    result = dm_rta_tasks(task_templates)

    if not result["schedulable"]:
        print("Unschedulable taskset found")
        break
result = dm_rta_tasks(task_templates)

if result["schedulable"]:
    print("System is SCHEDULABLE\n")

    for i, task_templates in enumerate(sorted(task_templates, key=lambda t: t.deadline)):
        print(
            f"Task {task_templates.id}: "
            f"C={task_templates.worst_case_time}, "
            f"T={task_templates.time_period}, "
            f"D={task_templates.deadline}, "
            f"R={result['response_times'][i]}"
        )
else:
    print("System is UNSCHEDULABLE")