import argparse
import graphs
import RMSimulation
import EDFSimulation

from parser import parse_csv_files, dataframe_to_jobs, dataframe_to_task_templates


def main(args):

    dataset = parse_csv_files(
        folder_path=args.folder_path,
        dataset_name=args.dataset_name,
        utilization=args.utilization,
        taskset_index=args.taskset_index,
    )

    # Convert datasets to TaskTemplates
    task_templates = []
    for i in range(len(dataset)):
        task_template_set = dataframe_to_task_templates(dataset[i])
        task_templates.append(task_template_set)

    print(f"Loaded task templates: {len(task_templates)} sets of task templates")

    if len(task_templates) > 0:
        print(f"First task template: {task_templates[0][0]}")

    # Run selected simulator
    for i, templates in enumerate(task_templates):

        print(
            f"\nRunning {args.simulator} Simulation for dataset {i+1} "
            f"with {len(templates)} task templates..."
        )

        # SELECT SCHEDULER
        if args.simulator == "EDF":
            simulation = EDFSimulation.EDFSimulation(templates, num_tasks=1)

        elif args.simulator == "RM":
            simulation = RMSimulation.RMSimulation(templates, num_tasks=1)

        job_log = simulation.run()

        print(f"Simulation completed for dataset {i+1}. Job log:")

        for job in job_log:
            print(job)

        graphs.graph(job_log)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Parse CSV files for a given dataset."
    )

    parser.add_argument(
        "--folder-path",
        type=str,
        default="datasets/",
        help="Path to the datasets folder.",
    )

    parser.add_argument(
        "--dataset-name",
        type=str,
        choices=["automotive", "uunifast"],
        default="automotive",
        help="Name of the dataset to parse.",
    )

    parser.add_argument(
        "--utilization",
        type=str,
        default="0.10",
        help="Utilization value to filter datasets.",
    )

    parser.add_argument(
        "--simulator",
        type=str,
        choices=["EDF", "RM"],
        default="EDF",
        help="Name of the simulator to use.",
    )

    parser.add_argument(
        "--taskset-index",
        type=lambda x: int(x) if x.lower() != "none" else None,
        default=None,
        help="Index of the taskset to return.",
    )

    args = parser.parse_args()

    print("# Simulation Configuration")
    for key, value in sorted(vars(args).items()):
        print(key, "=", value)

    main(args)