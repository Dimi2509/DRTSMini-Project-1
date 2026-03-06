import argparse

import EDFSimulation
from parser import parse_csv_files, dataframe_to_jobs, dataframe_to_task_templates
import argparse

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
    print(f"First task template: {task_templates[0][0]}")
