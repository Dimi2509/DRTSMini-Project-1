import argparse
import glob
import os

import pandas
from pandas import DataFrame

from Job import Job
from TaskTemplate import TaskTemplate


def parse_csv_files(
    folder_path="datasets/", dataset_name="automotive", utilization=None, verbose=False, taskset_index=None, schedulable=True
) -> tuple[list[DataFrame], str]:
    """
    Prase CSV files from the selected dataset, with an optional filter for utilization percentage.

    Args:
        folder_path (str): Base path to the datasets folder.
        dataset_name (str): Name of the dataset to parse. Choices are "automotive", "uunifast", or "test".
        utilization (str, optional): Utilization value to filter datasets. Should be in the format '0.50' for 50% utilization. If None, all utilization percentages will be processed.
        verbose (bool): Whether to print detailed information about the parsing process. Default is False.
        taskset_index (int): Index of the taskset to return. If None, return a random taskset from the selected dataset and utilization.
        schedulable (bool): Whether to load schedulable tasksets from the test dataset. Should be 'true' or 'false'. Default is 'true'.
    Returns:
        list[DataFrame]: A list of pandas DataFrames, each containing the data from one CSV file.
        str: A string describing the dataset and filters used for loading the data.
    """
    dataset_map = {
        "automotive": os.path.join(
            "automotive-utilDist", "automotive-perDist", "1-core", "25-task", "0-jitter"
        ),
        "uunifast": os.path.join(
            "uunifast-utilDist",
            "uniform-discrete-perDist",
            "1-core",
            "25-task",
            "0-jitter",
        ),
        "test": os.path.join(
            "test_tasks"
        ),
    }

    if dataset_name not in dataset_map:
        raise ValueError(f"Unknown dataset_name: {dataset_name}")

    if utilization is not None:
        try:
            util_float = float(utilization)
            utilization = f"{util_float:.2f}"
        except ValueError:
            raise ValueError(
                f"Invalid utilization format: {utilization}. Should be a float like '0.50'."
            )

    dataset_path = os.path.join(folder_path, dataset_map[dataset_name])

    if utilization and dataset_name != "test":
        # Select specific utilization percentage
        util_folders = glob.glob(os.path.join(dataset_path, f"{utilization}-util"))
        util_folders = [
            os.path.join(util_folder, "tasksets") for util_folder in util_folders
        ]
    else:
        # Load Test dataset 
        if schedulable:
            util_folders = [os.path.join(dataset_path, "schedulable")]
        else:
            util_folders = [os.path.join(dataset_path, "not_schedulable")]
        print(f"Loading {'schedulable' if schedulable else 'not_schedulable'} tasksets from test dataset from {util_folders}")


    if verbose:
        for util_folder in util_folders:
            print(f"Processing folder: {util_folder}")

    # Load csv files
    all_dataframes = []
    for taskset in util_folders:
        csv_files = glob.glob(os.path.join(taskset, "*.csv"))
        if taskset_index is not None and taskset_index < len(csv_files):
            csv_files = [csv_files[taskset_index]]  # Select only the specified taskset index
        elif taskset_index is None:
            # Pick a random taskset from the available CSV files
            import random
            print(f"Selecting random taskset")
            selected_taskset = random.choice(csv_files)
            taskset_index = csv_files.index(selected_taskset)
            csv_files = [selected_taskset]
        else:
            raise IndexError(f"taskset_index {taskset_index} is out of range for folder {taskset} with {len(csv_files)} CSV files.")
        for csv_file in csv_files:
            df = pandas.read_csv(csv_file)
            all_dataframes.append(df)

    if verbose:
        print(f"Total utilization folders processed: {len(util_folders)}")
        print(f"Total CSV files processed: {len(all_dataframes)}")
        print(f"Head of first DataFrame:\n{all_dataframes[0].head()}")

    return all_dataframes, f"Dataset {dataset_name}/{utilization if dataset_name != 'test' else 'schedulable' if schedulable else 'not_schedulable'}/Index {taskset_index}"


def dataframe_to_jobs(df) -> list[Job]:
    """
    Convert a pandas DataFrame into a list of Job objects.
    Args:
        df (DataFrame): A pandas DataFrame containing the taskset data.
    Returns:
        list[Job]: A list of Job objects created from the DataFrame.
    """
    jobs = []
    for _, row in df.iterrows():
        job = Job(
            id=row["TaskID"],
            deadline=row["Deadline"],
            start_time=None,  # Set appropriately if available
            end_time=None,  # Set appropriately if available
            time_period=row["Period"],
        )
        jobs.append(job)
    return jobs


def dataframe_to_task_templates(df) -> list[TaskTemplate]:
    """
    Convert a pandas DataFrame into a list of TaskTemplate objects.
    Args:
        df (DataFrame): A pandas DataFrame containing the taskset data.
    Returns:
        list[TaskTemplate]: A list of TaskTemplate objects created from the DataFrame.
    """
    task_templates = []
    for _, row in df.iterrows():
        task_template = TaskTemplate(
            id=row["TaskID"],
            best_case_time=row["BCET"],
            worst_case_time=row["WCET"],
            time_period=row["Period"],
            deadline=row["Deadline"],
            jitter=row["Jitter"],
            pe=row["PE"],
        )
        task_templates.append(task_template)
    return task_templates


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
        choices=["automotive", "uunifast", "test"],
        default="automotive",
        help="Name of the dataset to parse.",
    )
    parser.add_argument(
        "--utilization",
        type=str,
        default=0.10,
        help="Utilization value to filter datasets. Should be in the format '0.50' for 50% utilization.",
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
        help="Whether to load schedulable tasksets from the test dataset. Should be 'true' or 'false'. Default is 'true'.",
    )

    args = parser.parse_args()

    dataset, csv_files = parse_csv_files(
        folder_path=args.folder_path,
        dataset_name=args.dataset_name,
        utilization=args.utilization,
        taskset_index=args.taskset_index,
        schedulable=args.schedulable,
    )

    # Example of converting to TaskTemplates
    task_templates = []
    for i in range(len(dataset)):
        task_template_set = dataframe_to_task_templates(dataset[i])
        task_templates.append(task_template_set)

    print(f"Loaded task templates: {len(task_templates)} sets of task templates")
    print(f"First task template: {len(task_templates[0])}")
    print(f"CSV files processed: {csv_files}")
