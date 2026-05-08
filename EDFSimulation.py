import queue
from Job import Job
from TaskTemplate import TaskTemplate
from scipy import stats
from math import ceil, gcd


def get_execution_time(
    best_case_time: float, worst_case_time: float, use_worst_case=False
):
    mean = (best_case_time + worst_case_time) / 2
    std_dev = (worst_case_time - best_case_time) / 6

    if use_worst_case:
        return worst_case_time

    return ceil(stats.norm.rvs(loc=mean, scale=std_dev))


def get_hyperperiod(task_templates):
    periods = [template.time_period for template in task_templates]
    lcm = periods[0]

    for period in periods[1:]:
        lcm = lcm * period // gcd(lcm, period)

    return lcm


def get_highest_start_time(task_templates, num_tasks, use_hyperperiod=False):
    if use_hyperperiod:
        hyperperiod = get_hyperperiod(task_templates)
        return hyperperiod - 1

    max_time = 0
    for template in task_templates:
        max_time = max(max_time, template.time_period * num_tasks)

    return max_time - 1


def create_task_list(
    task_templates: list,
    num_tasks=5,
    use_worst_case=False,
    use_hyperperiod=False,
):
    tasks = []
    max_time = get_highest_start_time(
        task_templates,
        num_tasks,
        use_hyperperiod,
    )

    for template in task_templates:
        arrival_time = 0

        while arrival_time <= max_time:
            tasks.append(
                Task(
                    id=template.id,
                    arrival_time=arrival_time,
                    release_time=arrival_time,
                    execution_time=get_execution_time(
                        template.best_case_time,
                        template.worst_case_time,
                        use_worst_case,
                    ),
                    deadline=template.deadline + arrival_time,
                    time_period=template.time_period,
                )
            )

            arrival_time += template.time_period

    return tasks


class Task:
    def __init__(
        self,
        id,
        arrival_time,
        execution_time,
        deadline,
        time_period,
        release_time=None,
    ):
        self.id = id
        self.arrival_time = arrival_time
        self.release_time = arrival_time if release_time is None else release_time
        self.remaining_time = execution_time
        self.deadline = deadline
        self.time_period = time_period

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self):
        return (
            f"Task(id={self.id}, "
            f"arrival_time={self.arrival_time}, "
            f"release_time={self.release_time}, "
            f"remaining_time={self.remaining_time}, "
            f"deadline={self.deadline}, "
            f"time_period={self.time_period})"
        )


class InternalJob:
    def __init__(
        self,
        id,
        deadline,
        start_time,
        end_time,
        time_period,
        execution_time,
        release_time,
    ):
        self.id = id
        self.deadline = deadline
        self.start_time = start_time
        self.end_time = end_time
        self.time_period = time_period
        self.execution_time = execution_time
        self.release_time = release_time
        self.name = f"Job-{id}"

    def __str__(self):
        return (
            f"Job(name={self.name}, "
            f"release_time={self.release_time}, "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time}, "
            f"deadline={self.deadline}, "
            f"time_period={self.time_period}, "
            f"execution_time={self.execution_time})"
        )


class SchedulingQueue:
    def __init__(self):
        self.queue = queue.PriorityQueue()

    def put(self, task):
        self.queue.put((task.arrival_time, task.id, task))

    def pop(self):
        return self.queue.get()[2]

    def peek(self):
        if not self.queue.empty():
            return self.queue.queue[0][2]
        return None

    def empty(self):
        return self.queue.empty()

    def print(self):
        self.queue.queue.sort()
        for item in self.queue.queue:
            print(item[2])


class ReadyQueue:
    def __init__(self):
        self.queue = queue.PriorityQueue()

    def put(self, task):
        self.queue.put((task.deadline, task.id, task))

    def pop(self):
        return self.queue.get()[2]

    def peek(self):
        if not self.queue.empty():
            return self.queue.queue[0][2]
        return None

    def empty(self):
        return self.queue.empty()


class EDFScheduler:
    def __init__(self, task_templates=None):
        self.ready_queue = ReadyQueue()
        self.scheduling_queue = SchedulingQueue()
        self.task_templates = task_templates if task_templates is not None else []
        self.current_time = 0
        self.job_log = []
        self.wcrts = {}
        self.current_job: InternalJob = None

    def run(self) -> list:
        while not (
            self.ready_queue.empty()
            and self.scheduling_queue.empty()
            and self.current_job is None
        ):
            self.update_ready_queue()
            top_ready_task = self.ready_queue.peek()

            if self.current_job is None and top_ready_task is not None:
                self.current_job = self.get_internal_job_from_task(
                    self.ready_queue.pop()
                )

            elif (
                top_ready_task is not None
                and top_ready_task.deadline < self.current_job.deadline
            ):
                self.log_job(self.current_job)
                self.ready_queue.put(
                    self.get_task_from_internal_job(self.current_job)
                )
                self.current_job = self.get_internal_job_from_task(
                    self.ready_queue.pop()
                )

            if self.current_job is not None:
                self.current_job.execution_time -= 1
                self.log_job_if_finished(self.current_job)

            self.current_time += 1

        return self.job_log

    def log_job(self, job: InternalJob):
        completed = job.execution_time <= 0

        executed_job = Job(
            id=job.id,
            deadline=job.deadline,
            start_time=job.start_time,
            end_time=(
                job.end_time
                if job.end_time is not None
                else self.current_time
            ),
            time_period=job.time_period,
            release_time=job.release_time,
            completed=completed,
        )

        if completed:
            response_time = executed_job.end_time - executed_job.release_time
            self.wcrts[executed_job.id] = max(
                response_time,
                self.wcrts.get(executed_job.id, 0),
            )

        self.job_log.append(executed_job)

    def log_job_if_finished(self, job: InternalJob):
        if job.execution_time <= 0:
            job.end_time = self.current_time + 1
            self.log_job(job)
            self.current_job = None

    def get_internal_job_from_task(self, task: Task):
        return InternalJob(
            id=task.id,
            deadline=task.deadline,
            start_time=self.current_time, 
            # Start time indicates when task is taken from the queue not when it actually is released, so when it's 
            # released it waits and then it starts
            # released_time<=start_time<=end_time
            end_time=None,
            time_period=task.time_period,
            execution_time=task.remaining_time,
            release_time=task.release_time,
        )

    def get_task_from_internal_job(self, job: InternalJob):
        return Task(
            id=job.id,
            arrival_time=self.current_time,
            release_time=job.release_time,
            execution_time=job.execution_time,
            deadline=job.deadline,
            time_period=job.time_period,
        )

    def update_ready_queue(self):
        while (
            not self.scheduling_queue.empty()
            and self.scheduling_queue.peek().arrival_time <= self.current_time
        ):
            self.ready_queue.put(self.scheduling_queue.pop())

    def get_wcrts(self):
        return self.wcrts


class EDFSimulation:
    def __init__(
        self,
        tasks,
        num_tasks,
        use_worst_case=False,
        use_hyperperiod=False,
    ):
        self.ready_tasks = create_task_list(
            tasks,
            num_tasks,
            use_worst_case,
            use_hyperperiod,
        )
        self.scheduler = EDFScheduler(tasks)

    def run(self) -> list[Job]:
        for task in self.ready_tasks:
            self.scheduler.scheduling_queue.put(task)

        return self.scheduler.run()

    def get_wcrts(self):
        return self.scheduler.get_wcrts()


if __name__ == "__main__":
    task_templates = [
        TaskTemplate(
            id=1,
            best_case_time=1,
            worst_case_time=12,
            time_period=6,
            deadline=4,
            jitter=0,
        ),
        TaskTemplate(
            id=2,
            best_case_time=1,
            worst_case_time=12,
            time_period=8,
            deadline=5,
            jitter=0,
        ),
        TaskTemplate(
            id=3,
            best_case_time=1,
            worst_case_time=13,
            time_period=9,
            deadline=7,
            jitter=0,
        ),
    ]

    simulation = EDFSimulation(
        task_templates,
        num_tasks=5,
        use_worst_case=False,
        use_hyperperiod=False,
    )

    job_log = simulation.run()
    wcrts = simulation.get_wcrts()

    print(wcrts)