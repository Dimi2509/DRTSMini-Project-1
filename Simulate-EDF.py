import queue
import Job
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

    def __str__(self):
        return f"Task(id={self.id}, arrival_time={self.arrival_time}, remaining_time={self.remaining_time}, deadline={self.deadline}, time_period={self.time_period})"


class EDFScheduler:
    def __init__(self):
        self.ready_queue = queue.PriorityQueue()
        self.current_time = 0
        self.job_log = []
        self.current_job = None

    def add_task(self, task):
        self.ready_queue.put(task)

    def run(self):
        for task in self.ready_queue.queue:
            print(task)
        while not self.ready_queue.empty():
            top_ready_task = (
                self.ready_queue.queue[0] if not self.ready_queue.empty() else None
            )
            second_ready_task = (self.ready_queue.queue[1] if not len(self.ready_queue.queue) == 1 else None)
            # If processor is idle and there is a ready task, start executing the top ready task
            if (
                self.current_job is None
                and top_ready_task is not None
                and top_ready_task.arrival_time <= self.current_time
            ):
                self.current_job = Job.Job(
                    top_ready_task.id,
                    top_ready_task.deadline,
                    self.current_time,
                    None,
                    top_ready_task.time_period,
                )
            # Context change condition: if the top ready task has an earlier deadline than the second ready job,
            # preempt the current job
            elif (
                second_ready_task
                and second_ready_task.arrival_time <= self.current_time
                and (self.current_job is None or second_ready_task.id != self.current_job.id)
                and (self.current_job is None or self.current_job.deadline > second_ready_task.deadline)
            ):
                if self.current_job is not None:
                    self.current_job.end_time = self.current_time
                    self.job_log.append(self.current_job)
                self.current_job = Job.Job(
                    top_ready_task.id,
                    top_ready_task.deadline,
                    self.current_time,
                    None,
                    top_ready_task.time_period,
                )
            # If there is a current job, execute it for one time unit
            if self.current_job is not None:
                self.ready_queue.queue[0].remaining_time -= 1
                # If the current job has finished executing, log it and set current job to None
                if self.ready_queue.queue[0].remaining_time <= 0:
                    self.current_job.end_time = self.current_time + 1
                    self.job_log.append(self.current_job)
                    self.ready_queue.queue.pop(
                        0
                    )  # Remove the completed job from the ready queue
                    self.current_job = None
            self.current_time += 1


class EDFSimulation:
    def __init__(self, tasks, num_tasks):
        self.ready_tasks = create_task_list(tasks, num_tasks)
        self.scheduler = EDFScheduler()

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
