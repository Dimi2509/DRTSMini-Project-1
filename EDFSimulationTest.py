import EDFSimulation
import TaskTemplate
import graphs
import unittest


class test_edf_simulation(unittest.TestCase):

    def test_normal_schedulable_tasks(self):
        task_templates = [
            TaskTemplate.TaskTemplate(
                id=1,
                best_case_time=1000,
                worst_case_time=3000,
                time_period=5000,
                deadline=5000,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=2,
                best_case_time=2000,
                worst_case_time=4000,
                time_period=10000,
                deadline=10000,
                jitter=0,
            ),
        ]
        simulation = EDFSimulation.EDFSimulation(task_templates, num_tasks=3)
        job_log = simulation.run()
        # graphs.graph(job_log, True, True)
        for job in job_log:
            self.assertLessEqual(
                job.end_time, job.deadline, f"Job {job.id} missed its deadline!"
            )

    def test_worst_case_schedulable_tasks(self):
        task_templates = [
            TaskTemplate.TaskTemplate(
                id=1,
                best_case_time=1,
                worst_case_time=3000,
                time_period=5000,
                deadline=5000,
                jitter=0,
            ),
            TaskTemplate.TaskTemplate(
                id=2,
                best_case_time=1,
                worst_case_time=4000,
                time_period=10000,
                deadline=10000,
                jitter=0,
            ),
        ]
        simulation = EDFSimulation.EDFSimulation(
            task_templates, num_tasks=1, use_worst_case=True
        )
        job_log = simulation.run()
        for job in job_log:
            self.assertEqual(
                job.deadline,
                task_templates[job.id - 1].deadline,
                f"Job {job.id} deadline should be equal to the task template deadline!",
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
        simulation = EDFSimulation.EDFSimulation(task_templates, num_tasks=3)
        job_log = simulation.run()
        for job in job_log:
            with self.assertRaises(
                AssertionError, msg=f"Job {job.id} should have missed its deadline!"
            ):
                self.assertLessEqual(
                    job.end_time, job.deadline, f"Job {job.id} missed its deadline!"
                )


if __name__ == "__main__":
    unittest.main()
