import math

def dm_rta_test(tasks):

    # Task sorting based on their priority
    tasks = sorted(tasks, key=lambda t: t["D"])

    response_times = []

    for i in range(len(tasks)):
        # Task[i] paramethers
        Ci = tasks[i]["C"]
        Di = tasks[i]["D"]
        Ri = Ci
        while True:
            Rold = Ri
            interference = 0
            for h in range(i):
                Ch = tasks[h]["C"]
                Th = tasks[h]["T"]
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

# Testing (Both ok)
tasks = [
    {"C":1,"T":4,"D":4},
    {"C":2,"T":5,"D":5}
]
result = dm_rta_test(tasks)
print(result)

tasks = [
    {"C": 1, "T": 4, "D": 4},   # τ1
    {"C": 2, "T": 5, "D": 5},   # τ2
    {"C": 1, "T": 10, "D": 10}  # τ3
]
result = dm_rta_test(tasks)
print(result)