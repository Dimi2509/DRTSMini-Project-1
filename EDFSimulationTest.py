import EDFSimulation
import TaskTemplate
import graphs
import unittest
from parser import parse_csv_files, dataframe_to_jobs, dataframe_to_task_templates


class test_edf_simulation(unittest.TestCase):

    def test_normal_schedulable_tasks(self):
        task_templates = [
            TaskTemplate.TaskTemplate(
                id=1,
                best_case_time=10,
                worst_case_time=30,
                time_period=50,
                deadline=40,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=0,
                best_case_time=20,
                worst_case_time=40,
                time_period=100,
                deadline=80,
                jitter=0,
            ),
        ]
        num_tasks = 3
        simulation = EDFSimulation.EDFSimulation(task_templates, num_tasks=num_tasks)
        job_log = simulation.run()
        # graphs.graph(job_log, True, True)
        for job in job_log:
            self.assertLessEqual(
                job.end_time, job.deadline, f"Job {job.id} missed its deadline!"
            )
        self.assertGreaterEqual(
            len(job_log),
            num_tasks * len(task_templates),
            f"Number of jobs should be more than or equal to num_tasks * number of task templates!",
        )

    def test_worst_case_schedulable_tasks(self):
        task_templates = [
            TaskTemplate.TaskTemplate(
                id=1,
                best_case_time=1,
                worst_case_time=3000,
                time_period=5000,
                deadline=500,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=2,
                best_case_time=1,
                worst_case_time=4000,
                time_period=10000,
                deadline=1000,
                jitter=0,
            ),
        ]
        num_tasks = 3
        simulation = EDFSimulation.EDFSimulation(
            task_templates, num_tasks=num_tasks, use_worst_case=True
        )
        job_log = simulation.run()
        for job in job_log:
            with self.assertRaises(
                AssertionError, msg=f"Job {job.id} should have missed its deadline!"
            ):
                self.assertLessEqual(
                    job.end_time, job.deadline, f"Job {job.id} missed its deadline!"
                )
        self.assertGreaterEqual(
            len(job_log),
            num_tasks * len(task_templates),
            f"Number of jobs should be more than or equal to num_tasks * number of task templates!",
        )

    def test_unschedulable_tasks(self):
        task_templates = [
            TaskTemplate.TaskTemplate(
                id=1,
                best_case_time=3000,
                worst_case_time=3000,
                time_period=5000,
                deadline=500,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=2,
                best_case_time=4000,
                worst_case_time=4000,
                time_period=10000,
                deadline=1000,
                jitter=0,
            ),
        ]
        num_tasks = 3
        simulation = EDFSimulation.EDFSimulation(task_templates, num_tasks=num_tasks)
        job_log = simulation.run()
        for job in job_log:
            with self.assertRaises(
                AssertionError, msg=f"Job {job.id} should have missed its deadline!"
            ):
                self.assertLessEqual(
                    job.end_time, job.deadline, f"Job {job.id} missed its deadline!"
                )
        self.assertGreaterEqual(
            len(job_log),
            num_tasks * len(task_templates),
            f"Number of jobs should be more than or equal to num_tasks * number of task templates!",
        )

    def test_hyperperiod_tasks(self):
        task_templates = [
            TaskTemplate.TaskTemplate(
                id=1,
                best_case_time=1,
                worst_case_time=5,
                time_period=10,
                deadline=9,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=2,
                best_case_time=2,
                worst_case_time=5,
                time_period=10,
                deadline=11,
                jitter=0,
            ),
        ]
        num_tasks = 3
        simulation = EDFSimulation.EDFSimulation(
            task_templates,
            num_tasks=num_tasks,
            use_worst_case=True,
            use_hyperperiod=True,
        )
        job_log = simulation.run()
        for job in job_log:
            self.assertLessEqual(
                job.start_time, 10, f"Job {job.id} missed its deadline!"
            )
        self.assertGreaterEqual(
            len(job_log),
            2,
            f"There should be 2 jobs in this hyperperiod!",
        )

    def test_example_from_book(self):
        task_templates = [
            TaskTemplate.TaskTemplate(
                id=1,
                best_case_time=1,
                worst_case_time=2,
                time_period=6,
                deadline=4,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=2,
                best_case_time=1,
                worst_case_time=2,
                time_period=8,
                deadline=5,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=3,
                best_case_time=1,
                worst_case_time=3,
                time_period=9,
                deadline=7,
                jitter=0,
            ),
        ]
        num_tasks = 5
        simulation = EDFSimulation.EDFSimulation(
            task_templates,
            num_tasks=num_tasks,
            use_worst_case=True,
            use_hyperperiod=True,
        )
        job_log = simulation.run()
        for job in job_log:
            self.assertLessEqual(
                job.end_time, job.deadline, f"Job {job.id} missed its deadline!"
            )
    
    def test_edf_but_not_rm(self):
        task_templates = [
            TaskTemplate.TaskTemplate(
                id=1,
                best_case_time=1,
                worst_case_time=2,
                time_period=5,
                deadline=5,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=2,
                best_case_time=1,
                worst_case_time=4,
                time_period=7,
                deadline=7,
                jitter=0,
            ),
        ]
        num_tasks = 5
        simulation = EDFSimulation.EDFSimulation(
            task_templates, num_tasks=num_tasks, use_worst_case=True
        )
        job_log = simulation.run()
        graphs.graph(job_log, True, True)
        for job in job_log:
            self.assertLessEqual(
                job.end_time, job.deadline, f"Job {job.id} missed its deadline!"
            )


if __name__ == "__main__":
    unittest.main()
