class AnalyzerEDF:
    def __init__(self, tasks):
        self.tasks = tasks
        self.is_schedulable = None
    
    def add_task(self, task):
        self.tasks.append(task)
        self.analyze_aperiodic()

    def analyze_aperiodic(self, current_time=0):
        self._sort()

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
        t = 0
        proc_demand = 0
        for task in self.tasks:
            t += task.worst_case_time
            proc_demand = self.dbf(t)
            if proc_demand > t:
                self.is_schedulable = False
                return False

        self.is_schedulable = True
        return True

    def dbf(self, t):
        proc_demand = 0
        for task in self.tasks:
            comp_time = task.worst_case_time
            proc_demand += int( (t + task.time_period - task.deadline) / task.time_period) * comp_time
        return proc_demand

    def _sort(self):
        # self.tasks.sort(key=lambda x: x.deadline) # Yea no.
        self._quicksort(0, len(self.tasks)-1)

    def _quicksort(self, low, high): # Yes, I implemented quicksort by hand. Take it up with HR
        if low >= high:
            return

        i, j = low, high
        p = self.tasks[low].deadline

        while i < j:
            while i < high and self.tasks[i].deadline <= p:
                i += 1
            while j > low and self.tasks[j].deadline > p:
                j -= 1

            if i < j: # Swap
                self._swap(i, j)

        self._swap(low, j)
        self._quicksort(low, j-1)
        self._quicksort(j+1, high)

    def _swap(self, i, j):
        tmp = self.tasks[i]
        self.tasks[i] = self.tasks[j]
        self.tasks[j] = tmp