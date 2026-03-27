import queue
from Job import Job
from TaskTemplate import TaskTemplate
from scipy import stats
from math import gcd
from functools import reduce

# ---------------- Utilities ----------------

def get_execution_time(best_case_time: float, worst_case_time: float):
    mean = (best_case_time + worst_case_time) / 2
    std_dev = (worst_case_time - best_case_time) / 6
    # return stats.norm.rvs(loc=mean, scale=std_dev)
    return worst_case_time

def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_list(numbers):
    return reduce(lcm, numbers)

# ---------------- Task generation ----------------

def create_task_list(task_templates, hyperperiod):
    """
    Generate tasks to fill the given hyperperiod.
    """
    tasks = []
    for template in task_templates:
        num_instances = hyperperiod // template.time_period
        for i in range(num_instances):
            execution_time = get_execution_time(template.best_case_time, template.worst_case_time)
            arrival_time = i * template.time_period
            tasks.append(Task(
                id=template.id,
                arrival_time=arrival_time,
                execution_time=execution_time,
                deadline=template.deadline + arrival_time,
                time_period=template.time_period
            ))
    return tasks

# ---------------- Task and Job Classes ----------------

class Task:
    def __init__(self, id, arrival_time, execution_time, deadline, time_period):
        self.id = id
        self.arrival_time = arrival_time
        self.remaining_time = execution_time
        self.deadline = deadline
        self.time_period = time_period
    def __lt__(self, other):
        return self.id < other.id
    def __str__(self):
        return f"Task({self.id}, arrival={self.arrival_time}, remaining={self.remaining_time})"

class InternalJob:
    def __init__(self, id, deadline, start_time, end_time, time_period, execution_time):
        self.id = id
        self.deadline = deadline
        self.start_time = start_time
        self.end_time = end_time
        self.time_period = time_period
        self.execution_time = execution_time
        self.name = f"Job-{id}"
    def __str__(self):
        return f"Job({self.name}, start={self.start_time}, end={self.end_time}, deadline={self.deadline})"

# ---------------- Queues ----------------

class SchedulingQueue:
    def __init__(self):
        self.queue = queue.PriorityQueue()
    def put(self, task):
        self.queue.put((task.arrival_time, task))
    def pop(self):
        return self.queue.get()[1]
    def peek(self):
        return self.queue.queue[0][1] if not self.queue.empty() else None
    def empty(self):
        return self.queue.empty()
    def print(self):
        self.queue.queue.sort()
        for item in self.queue.queue:
            print(item[1])

class ReadyQueue:
    def __init__(self):
        self.queue = queue.PriorityQueue()
    def put(self, task):
        self.queue.put((task.time_period, task))
    def pop(self):
        return self.queue.get()[1]
    def peek(self):
        return self.queue.queue[0][1] if not self.queue.empty() else None
    def empty(self):
        return self.queue.empty()

# ---------------- RMScheduler ----------------

class RMScheduler:
    def __init__(self, task_templates=None):
        self.ready_queue = ReadyQueue()
        self.scheduling_queue = SchedulingQueue()
        self.task_templates = task_templates if task_templates else []
        self.current_time = 0
        self.current_job: InternalJob = None
        self.job_log = []

    def run(self):
        while not (self.ready_queue.empty() and self.scheduling_queue.empty()):
            self.update_ready_queue()
            top_ready_task = self.ready_queue.peek()

            if self.current_job is None and top_ready_task:
                self.current_job = self.get_internal_job_from_task(self.ready_queue.pop())
            elif top_ready_task and (self.current_job is None or top_ready_task.time_period < self.current_job.time_period):
                self.log_job(self.current_job)
                self.ready_queue.put(self.get_task_from_internal_job(self.current_job))
                self.current_job = self.get_internal_job_from_task(self.ready_queue.pop())

            if self.current_job:
                self.current_job.execution_time -= 1
                self.log_job_if_finished(self.current_job)

            self.current_time += 1

    def log_job(self, job: InternalJob):
        self.job_log.append(Job(
            id=job.id,
            deadline=job.deadline,
            start_time=job.start_time,
            end_time=job.end_time if job.end_time else self.current_time,
            time_period=job.time_period
        ))

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
            end_time=None,
            time_period=task.time_period,
            execution_time=task.remaining_time
        )

    def get_task_from_internal_job(self, job: InternalJob):
        return Task(
            id=job.id,
            arrival_time=self.current_time,
            execution_time=job.execution_time,
            deadline=job.deadline,
            time_period=job.time_period
        )

    def update_ready_queue(self):
        while not self.scheduling_queue.empty() and self.scheduling_queue.peek().arrival_time <= self.current_time:
            self.ready_queue.put(self.scheduling_queue.pop())

# ---------------- RMSimulation ----------------

class RMSimulation:
    def __init__(self, task_templates, hyperperiod=None):
        if hyperperiod is None:
            # Calculate hyperperiod from templates if not provided
            periods = [t.time_period for t in task_templates]
            hyperperiod = lcm_list(periods)
        self.hyperperiod = hyperperiod
        self.ready_tasks = create_task_list(task_templates, self.hyperperiod)
        self.scheduler = RMScheduler(task_templates)

    def run(self):
        for task in self.ready_tasks:
            self.scheduler.scheduling_queue.put(task)
        self.scheduler.run()
        return self.scheduler.job_log, self.hyperperiod




