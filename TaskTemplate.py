class TaskTemplate:
    def __init__(self, id, best_case_time, worst_case_time, time_period, deadline, jitter=None, pe=None):
        self.id = id
        self.best_case_time = best_case_time
        self.worst_case_time = worst_case_time
        self.time_period = time_period
        self.deadline = deadline
        self.jitter = jitter if jitter is not None else 0
        self.pe = pe if pe is not None else 0