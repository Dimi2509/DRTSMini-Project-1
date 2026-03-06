import argparse
import glob
import os

import pandas
from pandas import DataFrame

from Job import Job
from TaskTemplate import TaskTemplate

def parse_csv_files(
    folder_path="datasets/", dataset_name="automotive", utilization=None, verbose=False
) -> list[DataFrame]:
    """
    Prase CSV files from the selected dataset, with an optional filter for utilization percentage.

    Args:
        folder_path (str): Base path to the datasets folder.
        dataset_name (str): Name of the dataset to parse. Should be either "automotive" or "uunifast".
        utilization (str, optional): Utilization value to filter datasets. Should be in the format '0.50' for 50% utilization. If None, all utilization percentages will be processed.
    Returns:
        list[DataFrame]: A list of pandas DataFrames, each containing the data from one CSV file.
    """
    dataset_map = {
        "automotive": os.path.join(
            "automotive-utilDist", 
            "automotive-perDist", 
            "1-core", 
            "25-task", 
            "0-jitter"
        ),
        "uunifast": os.path.join(
            "uunifast-utilDist",
            "uniform-discrete-perDist",
            "1-core",
            "25-task",
            "0-jitter",
        ),
    }

    if dataset_name not in dataset_map:
        raise ValueError(f"Unknown dataset_name: {dataset_name}")

    dataset_path = os.path.join(folder_path, dataset_map[dataset_name])

    if utilization:
        # Select specific utilization percentage
        util_folders = glob.glob(os.path.join(dataset_path, f"{utilization}-util"))
        util_folders = [
            os.path.join(util_folder, "tasksets") for util_folder in util_folders
        ]
    else:
        # Select all utilization percentages and add /tasksets
        util_folders = glob.glob(os.path.join(dataset_path, "*-util"))
        util_folders = [
            os.path.join(util_folder, "tasksets") for util_folder in util_folders
        ]

    if verbose:
        for util_folder in util_folders:
            print(f"Processing folder: {util_folder}")

    # Load csv files
    all_dataframes = []
    for taskset in util_folders:
        csv_files = glob.glob(os.path.join(taskset, "*.csv"))
        for csv_file in csv_files:
            df = pandas.read_csv(csv_file)
            all_dataframes.append(df)

    if verbose:
        print(f"Total utilization folders processed: {len(util_folders)}")
        print(f"Total CSV files processed: {len(all_dataframes)}")
        print(f"Head of first DataFrame:\n{all_dataframes[0].head()}")

    return all_dataframes


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
            pe=row["PE"]
        )
        task_templates.append(task_template)
    return task_templates

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse CSV files for a given dataset.")
    parser.add_argument(
        "--folder_path",
        type=str,
        default="datasets/",
        help="Path to the datasets folder.",
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        choices=["automotive", "uunifast"],
        default="automotive",
        help="Name of the dataset to parse.",
    )
    parser.add_argument(
        "--utilization",
        type=str,
        default=None,
        help="Utilization value to filter datasets. Should be in the format '0.50' for 50% utilization.",
    )

    args = parser.parse_args()

    dataset = parse_csv_files(
        folder_path=args.folder_path,
        dataset_name=args.dataset_name,
        utilization=args.utilization,
    )

    # Example of converting to TaskTemplates
    task_templates = []
    for i in range(len(dataset)):
        task_template_set = dataframe_to_task_templates(dataset[i])
        task_templates.append(task_template_set)
    
    print(f"Loaded task templates: {len(task_templates)} sets of task templates")
    print(f"First task template: {len(task_templates[0])}")

