class Job:
    def __init__(
        self,
        id,
        deadline,
        start_time,
        end_time,
        time_period,
        release_time=0,
        completed=False,
    ):
        self.id = id
        self.deadline = deadline
        self.start_time = start_time
        self.end_time = end_time
        self.time_period = time_period
        self.release_time = release_time
        self.completed = completed
        self.name = f"Job-{id}"

    def __str__(self):
        return (
            f"Job(name={self.name}, "
            f"release_time={self.release_time}, "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time}, "
            f"deadline={self.deadline}, "
            f"time_period={self.time_period}, "
            f"completed={self.completed}, "
            f"response_time={self.end_time - self.release_time})"
        )