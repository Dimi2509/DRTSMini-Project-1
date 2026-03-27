import matplotlib.pyplot as plt
import numpy as np
import copy
from math import gcd

class AnalyzerEDF:
    def __init__(self, tasks):
        self.tasks = tasks
        self.is_schedulable = None
    
    def add_task(self, task):
        self.tasks.append(task)
        self.analyze_aperiodic()

    def analyze_aperiodic(self, current_time=0):
        self.tasks = self._sort(self.tasks)

        prev_f_time = current_time
        for task in self.tasks:
            remain_exec_time = task.worst_case_time - current_time # Remaining execution time of task
            finish_time = prev_f_time + remain_exec_time
            prev_f_time = finish_time
            if finish_time > task.deadline:
                self.is_schedulable = False
                return False
        
        self.is_schedulable = True
        return True
    
    def analyze_periodic(self):
        H = self.get_hyperperiod(self.tasks)
        D_max = self.get_d_max()
        L_star, U = self.get_l_star_and_demand()
        if round(U, 12) > 1: # Round to avoid terrible floating point inaccuracies
            print(f"Overloaded processor core. Utilization: {U}")
            self.is_schedulable = False
            return False
        
        if self.is_deadline_eq_period():
            print(f"All deadlines equal to periods with undersaturated utilization")
            self.is_schedulable = True
            return True

        sorted_tasks = copy.deepcopy(self.tasks)

        limit = min(H, max(D_max, L_star))

        t = 0
        while t <= limit:
            self._sort(sorted_tasks)
            t = sorted_tasks[0].deadline
            sorted_tasks[0].deadline += sorted_tasks[0].time_period
            proc_demand = self.dbf(t)
            if proc_demand > t:
                self.is_schedulable = False
                return False

        self.is_schedulable = True
        return True

    def get_hyperperiod(self, task_templates):
        periods = [template.time_period for template in task_templates]
        lcm = periods[0]
        for period in periods[1:]:
            lcm = lcm * period // gcd(lcm, period)
        return lcm
    
    def get_d_max(self):
        d_max = 0
        for task in self.tasks:
            if task.deadline > d_max:
                d_max = task.deadline
        return d_max

    def get_l_star_and_demand(self):
        num = 0
        U = 0
        for task in self.tasks:
            U_i = task.worst_case_time/task.time_period
            num += (task.time_period - task.deadline) * U_i
            U += U_i

        return num/(1 - U), U
    
    def is_deadline_eq_period(self):
        for task in self.tasks:
            if task.time_period != task.deadline:
                return False
        return True

    def dbf(self, t):
        proc_demand = 0
        for task in self.tasks:
            comp_time = task.worst_case_time
            proc_demand += int( (t + task.time_period - task.deadline) / task.time_period) * comp_time
        return proc_demand
    

    def _sort(self, tasks):
        # self.tasks.sort(key=lambda x: x.deadline) # Yea no.
        self._quicksort(tasks, 0, len(self.tasks)-1)

    def _quicksort(self, tasks, low, high): # Yes, I implemented quicksort by hand. Take it up with HR
        if low >= high:
            return

        i, j = low, high
        p = tasks[low].deadline

        while i < j:
            while i < high and tasks[i].deadline <= p:
                i += 1
            while j > low and tasks[j].deadline > p:
                j -= 1

            if i < j: # Swap
                self._swap(tasks, i, j)

        self._swap(tasks, low, j)
        self._quicksort(tasks, low, j-1)
        self._quicksort(tasks, j+1, high)

    def _swap(self, tasks, i, j):
        tmp = tasks[i]
        tasks[i] = tasks[j]
        tasks[j] = tmp

    def plotter(self):
        t = []
        demands = []
        self._sort(self.tasks)

        for i in range(10000):
            t.append(i)
            demands.append(self.dbf(i))
        demands = np.array(demands)
        t = np.array(t)
        plt.plot(t, demands)
        plt.plot(t, t)
        plt.show()