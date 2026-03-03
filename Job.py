class Job:
    def __init__(self, id, deadline, start_time, end_time, time_period):
        self.id = id
        self.deadline = deadline
        self.start_time = start_time
        self.end_time = end_time
        self.time_period = time_period
        self.name = f"Job-{id}"

    def __str__(self):
        return f"Job(name={self.name}, start_time={self.start_time}, end_time={self.end_time}, deadline={self.deadline}, time_period={self.time_period}, execution_time={self.end_time-self.start_time}"
