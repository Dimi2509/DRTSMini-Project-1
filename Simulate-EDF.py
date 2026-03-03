import queue
from Job import Job
from scipy import stats
from math import ceil


def get_execution_time(best_case_time: float, worst_case_time: float):
    mean = (best_case_time + worst_case_time) / 2
    std_dev = (worst_case_time - best_case_time) / 6  # Assuming 99.7% of values
    return stats.norm.rvs(
        loc=mean, scale=std_dev
    )  # Return a random execution time based on normal distribution


def create_task_list(task_templates: list, num_tasks):
    tasks = []
    for i in range(num_tasks):
        for template in task_templates:
            execution_time = ceil(
                get_execution_time(template.best_case_time, template.worst_case_time)
            )
            arrival_time = i * template.time_period
            tasks.append(
                Task(
                    id=template.id,
                    arrival_time=arrival_time,
                    execution_time=execution_time,
                    deadline=template.deadline + arrival_time,
                    time_period=template.time_period,
                )
            )
    return tasks


class TaskTemplate:
    def __init__(self, id, best_case_time, worst_case_time, time_period, deadline):
        self.id = id
        self.best_case_time = best_case_time
        self.worst_case_time = worst_case_time
        self.time_period = time_period
        self.deadline = deadline


class Task:
    def __init__(self, id, arrival_time, execution_time, deadline, time_period):
        self.id = id
        self.arrival_time = arrival_time
        self.remaining_time = execution_time
        self.deadline = deadline
        self.time_period = time_period

    def __lt__(self, other):
        return self.deadline < other.deadline
    
    def __gt__(self, other):
        return self.deadline > other.deadline

    def __eq__(self, value):
        return self.deadline == value.deadline

    def __str__(self):
        return f"Task(id={self.id}, arrival_time={self.arrival_time}, remaining_time={self.remaining_time}, deadline={self.deadline}, time_period={self.time_period})"

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
        return f"Job(name={self.name}, start_time={self.start_time}, end_time={self.end_time}, deadline={self.deadline}, time_period={self.time_period}, execution_time={self.execution_time})"


class EDFScheduler:
    def __init__(self, task_templates=None):
        self.ready_queue = queue.PriorityQueue()
        self.task_templates = task_templates if task_templates is not None else []
        self.current_time = 0
        self.job_log = []
        self.current_job: InternalJob = None

    def add_task(self, task):
        self.ready_queue.put(task)

    def run(self):
        self.ready_queue.queue.sort()  # Ensure the ready queue is sorted by deadline
        # for task in self.ready_queue.queue:
        #     print(task)
        while not self.ready_queue.empty():
            top_ready_task = (
                self.ready_queue.queue[0] if not self.ready_queue.empty() else None
            )
            # If processor is idle and there is a ready task, start executing the top ready task
            if (
                self.current_job is None
                and top_ready_task is not None
                and top_ready_task.arrival_time <= self.current_time
            ):
                self.current_job = self.get_internal_job_from_task(top_ready_task)
                self.ready_queue.queue.pop(0)
            # Context change condition: if the top ready task has an earlier deadline than the second ready job,
            # preempt the current job
            elif (
                top_ready_task is not None
                and top_ready_task.arrival_time <= self.current_time
                and (self.current_job is None or top_ready_task.deadline < self.current_job.deadline)
            ):
                if self.current_job is not None:
                    self.current_job.end_time = self.current_time
                    self.job_log.append(self.current_job)
                    task_to_requeue = self.get_task_from_internal_job(self.current_job)
                    self.ready_queue.put(task_to_requeue)
                self.current_job = self.get_internal_job_from_task(top_ready_task)
                self.ready_queue.queue.pop(0)

            # If there is a current job, execute it for one time unit
            if self.current_job is not None:
                self.current_job.execution_time -= 1 
                if self.current_job.execution_time <= 0:
                    self.current_job.end_time = self.current_time + 1
                    self.log_job(self.current_job)
                    self.current_job = None
            self.current_time += 1
    
    def log_job(self, job: InternalJob):
        self.job_log.append(Job(
            id=job.id,
            deadline=job.deadline,
            start_time=job.start_time,
            end_time=job.end_time,
            time_period=job.time_period
        ))
    
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


class EDFSimulation:
    def __init__(self, tasks, num_tasks):
        self.ready_tasks = create_task_list(tasks, num_tasks)
        self.scheduler = EDFScheduler(tasks)

    def run(self):
        for task in self.ready_tasks:
            self.scheduler.add_task(task)
        self.scheduler.run()
        return self.scheduler.job_log


task1 = TaskTemplate(1, 2, 10, 12, 12)
task2 = TaskTemplate(2, 1, 5, 5, 5)
simulation = EDFSimulation([task1, task2], 10).run()
for job in simulation:
    print(job)
