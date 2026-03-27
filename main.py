import argparse
import graphs
import RMSimulation
import EDFSimulation
from AnalyzerEDF import AnalyzerEDF
from parser import parse_csv_files, dataframe_to_jobs, dataframe_to_task_templates
from graph_hyperperiod import graph_hyperperiod 
import TaskTemplate
from Job import Job

def main():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse CSV files for a given dataset.")
    parser.add_argument(
        "--folder-path",
        type=str,
        default="datasets/",
        help="Path to the datasets folder.",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        choices=["automotive", "uunifast", "test", "other"],
        default="automotive",
        help="Name of the dataset to parse.",
    )
    parser.add_argument(
        "--path-to-csv",
        type=str,
        default="",
        help="Path to other dataset CSV file. Only used if dataset-name is 'other'.",
    )
    parser.add_argument(
        "--utilization",
        type=str,
        default="0.10",
        help="Utilization value to filter datasets. Defaults to 0.10 ",
    )
    parser.add_argument(
        "--simulator",
        type=str,
        choices=["EDF", "RM"],
        default=None,
        help="Name of the simulator to use, leave blank if you want to run both schedulers. Default is None. Choices are 'EDF' or 'RM'.",
    )
    parser.add_argument(
        "--taskset-index",
        type=lambda x: int(x) if x.lower() != "none" else None,
        default=None,
        help="Index of the taskset to return. If None, return a random taskset from the selected dataset and utilization.",
    )
    parser.add_argument(
        "--schedulable",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Whether to load schedulable tasksets from the test dataset. Only works if using test dataset. Should be 'true' or 'false'. Default is 'true'.",
    )

    args = parser.parse_args()

    print('# Simulation Configuration')
    for key, value in sorted(vars(args).items()):
        print(key, '=', value)

    dataset, job_title = parse_csv_files(
        folder_path=args.folder_path,
        dataset_name=args.dataset_name,
        utilization=args.utilization,
        taskset_index=args.taskset_index,
        schedulable=args.schedulable,
        path_to_csv=args.path_to_csv
    )

    # Example of converting to TaskTemplates
    task_templates = []
    for i in range(len(dataset)):
        task_template_set = dataframe_to_task_templates(dataset[i])
        task_templates.append(task_template_set)

    # task_templates = [
    #     [],
    #     [
    #     TaskTemplate.TaskTemplate(
    #         id=1,
    #         best_case_time=1,
    #         worst_case_time=2,
    #         time_period=6,
    #         deadline=4,
    #         jitter=0,
    #     ),
    #     TaskTemplate.TaskTemplate(
    #         id=2,
    #         best_case_time=1,
    #         worst_case_time=2,
    #         time_period=8,
    #         deadline=5,
    #         jitter=0,
    #     ),
    #     TaskTemplate.TaskTemplate(
    #         id=3,
    #         best_case_time=1,
    #         worst_case_time=3,
    #         time_period=9,
    #         deadline=7,
    #         jitter=0,
    #     ),
    #     ],
    # ]

    # Check schedulability
    analyzer = AnalyzerEDF(task_templates[0])
    schedulable = analyzer.analyze_aperiodic()
    # schedulable = analyzer.analyze_periodic()
    if schedulable:
        print("The set is schedulable")
    else:
        print("The set is not schedulable")

    # Prepare simulation configuration
    simulators_to_run = [args.simulator] if args.simulator else ["EDF", "RM"]
    for simulator in simulators_to_run:
        temp_job_title = job_title + " " + simulator
        for i, templates in enumerate(task_templates):
            print(f"\nRunning {simulator} Simulation for dataset {i+1}...")
            if simulator == "EDF":
                simulation = EDFSimulation.EDFSimulation(templates, num_tasks=1, use_worst_case=True, use_hyperperiod=True)
                job_log = simulation.run()
                # print(job_log)

                for job in job_log:
                    # print(job)
                    if job.end_time > job.deadline:
                        print(f"##bad## job.id: {job.id}")
                graphs.graph(job_log, temp_job_title, True, True)
                print(f"############################################################################################################################################################################################################################################################################################################################################################## first thing")

            else:
                simulation = RMSimulation.RMSimulation(templates)  # Hyperperiod auto-calculated
                job_log, hyperperiod = simulation.run()
                # print(job_log)
                for job in job_log:
                    # print(job)
                    if job.end_time > job.deadline:
                        print(f"##bad## job.id: {job.id}")
                graph_hyperperiod(job_log, temp_job_title, hyperperiod=hyperperiod, use_deadlines=True, use_period=True)
