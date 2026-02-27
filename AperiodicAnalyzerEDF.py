class AperiodicAnalyzerEDF:
    def __init__(self, jobs):
        self.jobs = jobs 
        self.is_schedulable = None
        # self.analyze_aperiodic()
    
    def add_job(self, job):
        self.jobs.append(job)
        self.analyze_aperiodic()

    def analyze_aperiodic(self, current_time=0):
        self._sort()

        prev_f_time = current_time
        for job in self.jobs:
            remain_exec_time = job.end_time - current_time # Remaining execution time of job
            finish_time = prev_f_time + remain_exec_time
            if finish_time > job.deadline:
                self.is_schedulable = False
                return False
        
        self.is_schedulable = True
        return True
    
    def analyze_periodic(self, t):
        proc_demand = 0
        for job in self.jobs:
            comp_time = job.end_time - t
            proc_demand += int( (t + job.time_period - job.deadline) / job.time_period) * comp_time
        if proc_demand > t:
            self.is_schedulable = False
            return False

        self.is_schedulable = True
        return True

    def _sort(self):
        # self.jobs.sort(key=lambda x: x.deadline) # Yea no.
        self._quicksort(0, len(self.jobs)-1)

    def _quicksort(self, low, high): # Yes, I implemented quicksort by hand. Take it up with HR
        if low >= high:
            return

        i, j = low, high
        p = self.jobs[low].deadline

        while i < j:
            while i < high and self.jobs[i].deadline <= p:
                i += 1
            while j > low and self.jobs[j].deadline > p:
                j -= 1

            if i < j: # Swap
                self._swap(i, j)

        self._swap(low, j)
        self._quicksort(low, j-1)
        self._quicksort(j+1, high)

    def _swap(self, i, j):
        tmp = self.jobs[i]
        self.jobs[i] = self.jobs[j]
        self.jobs[j] = tmp