import math
from parser import parse_csv_files, dataframe_to_jobs

dataset = parse_csv_files(dataset_name="automotive", utilization="0.50")

# Following pseudo-code book 
def dm_rta_jobs(jobs):

    # Task sorting based on their priority
    jobs = sorted(jobs, key=lambda j: j.deadline) 

    response_times = []

    for i in range(len(jobs)):
        # Job paramethers
        Ci = jobs[i].end_time - jobs[i].start_time
        Di = jobs[i].deadline
        Ri = Ci
        while True:
            Rold = Ri
            interference = 0
            for h in range(i):
                Ch = jobs[h].end_time - jobs[h].start_time
                Th = jobs[h].time_period
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
    jobs = dataframe_to_jobs(df)
    result = dm_rta_jobs(jobs)

    if not result["schedulable"]:
        print("Unschedulable taskset found")
        break
result = dm_rta_jobs(jobs)

if result["schedulable"]:
    print("System is SCHEDULABLE\n")

    for i, job in enumerate(sorted(jobs, key=lambda j: j.deadline)):
        print(
            f"Job {job.id}: "
            f"C={job.end_time - job.start_time}, "
            f"T={job.time_period}, "
            f"D={job.deadline}, "
            f"R={result['response_times'][i]}"
        )
else:
    print("System is UNSCHEDULABLE")