import argparse
import graphs
import RMSimulation
import EDFSimulation
from AnalyzerEDF import AnalyzerEDF
from parser import parse_csv_files, dataframe_to_task_templates
from graph_hyperperiod import graph_hyperperiod
from dm_analysis_Flora import compute_dm_wcrts


def get_completed_jobs(job_log):
    return [job for job in job_log if job.completed]


def summarize_job_log(job_log):
    completed_jobs = get_completed_jobs(job_log)

    total_jobs = len(completed_jobs)
    deadline_misses = 0
    max_lateness = float("-inf")
    total_response_time = 0

    per_task = {}

    for job in completed_jobs:
        lateness = job.end_time - job.deadline
        response_time = job.end_time - job.release_time

        total_response_time += response_time

        if lateness > 0:
            deadline_misses += 1

        max_lateness = max(max_lateness, lateness)

        if job.id not in per_task:
            per_task[job.id] = {
                "count": 0,
                "misses": 0,
                "max_lateness": float("-inf"),
                "response_time_sum": 0,
                "max_response_time": float("-inf"),
            }

        per_task[job.id]["count"] += 1
        per_task[job.id]["response_time_sum"] += response_time
        per_task[job.id]["max_response_time"] = max(
            per_task[job.id]["max_response_time"],
            response_time,
        )
        per_task[job.id]["max_lateness"] = max(
            per_task[job.id]["max_lateness"],
            lateness,
        )

        if lateness > 0:
            per_task[job.id]["misses"] += 1

    avg_response_time = total_response_time / total_jobs if total_jobs > 0 else 0
    max_lateness = max_lateness if total_jobs > 0 else 0

    print("\n# Simulation Summary")
    print(f"Completed jobs: {total_jobs}")
    print(f"Deadline misses: {deadline_misses}")
    print(f"Jobs meeting deadlines: {total_jobs - deadline_misses}")
    print(f"Max lateness: {max_lateness}")
    print(f"Average response time: {avg_response_time:.2f}")

    return {
        "total_jobs": total_jobs,
        "deadline_misses": deadline_misses,
        "jobs_meeting_deadlines": total_jobs - deadline_misses,
        "max_lateness": max_lateness,
        "average_response_time": avg_response_time,
        "per_task": per_task,
    }


def get_simulated_max_response_times(job_log):
    completed_jobs = get_completed_jobs(job_log)
    simulated = {}

    for job in completed_jobs:
        response_time = job.end_time - job.release_time

        if job.id not in simulated:
            simulated[job.id] = response_time
        else:
            simulated[job.id] = max(simulated[job.id], response_time)

    return simulated


def compare_analysis_and_simulation(analytical_wcrts, simulated_max_response_times):
    rows = []

    for task_id, analytical_wcrt in analytical_wcrts.items():
        simulated_rt = simulated_max_response_times.get(task_id)

        if simulated_rt is None:
            rows.append({
                "task_id": task_id,
                "analytical_wcrt": analytical_wcrt,
                "simulated_max_response_time": None,
                "valid": False,
                "difference": None,
            })
            continue

        rows.append({
            "task_id": task_id,
            "analytical_wcrt": analytical_wcrt,
            "simulated_max_response_time": simulated_rt,
            "valid": simulated_rt <= analytical_wcrt,
            "difference": analytical_wcrt - simulated_rt,
        })

    return rows


def print_wcrt_comparison_table(rows):
    print("\n# Analytical WCRT vs Simulated Max Response Time")
    print(
        f"{'Task':<8}"
        f"{'Analytical WCRT':<20}"
        f"{'Simulated Max RT':<20}"
        f"{'Difference':<15}"
        f"{'Valid':<8}"
    )
    print("-" * 75)

    for row in rows:
        print(
            f"{row['task_id']:<8}"
            f"{row['analytical_wcrt']:<20}"
            f"{str(row['simulated_max_response_time']):<20}"
            f"{str(row['difference']):<15}"
            f"{str(row['valid']):<8}"
        )


def print_edf_analysis_result(edf_schedulable, edf_wcrt_result):
    print("\n# EDF Analytical Result")
    print(f"DBF schedulable: {edf_schedulable}")
    print(f"WCRT schedulable: {edf_wcrt_result['schedulable']}")
    print(f"Hyperperiod: {edf_wcrt_result['hyperperiod']}")
    print(f"Response times: {edf_wcrt_result['response_times']}")


def main():
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
        help="Utilization value to filter datasets. Defaults to 0.10.",
    )
    parser.add_argument(
        "--simulator",
        type=str,
        choices=["EDF", "RM"],
        default=None,
        help="Name of the simulator to use. Leave blank to run both.",
    )
    parser.add_argument(
        "--taskset-index",
        type=lambda x: int(x) if x.lower() != "none" else None,
        default=None,
        help="Index of the taskset to return.",
    )
    parser.add_argument(
        "--schedulable",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Whether to load schedulable tasksets from the test dataset.",
    )

    args = parser.parse_args()

    print("# Simulation Configuration")
    for key, value in sorted(vars(args).items()):
        print(key, "=", value)

    dataset, job_title = parse_csv_files(
        folder_path=args.folder_path,
        dataset_name=args.dataset_name,
        utilization=args.utilization,
        taskset_index=args.taskset_index,
        schedulable=args.schedulable,
        path_to_csv=args.path_to_csv,
    )

    task_templates = []
    for i in range(len(dataset)):
        task_template_set = dataframe_to_task_templates(dataset[i])
        task_templates.append(task_template_set)

    simulators_to_run = [args.simulator] if args.simulator else ["EDF", "RM"]

    for simulator in simulators_to_run:
        temp_job_title = job_title + " " + simulator

        for i, templates in enumerate(task_templates):
            print(f"\nRunning {simulator} Simulation for dataset {i + 1}...")

            if simulator == "EDF":
                analyzer = AnalyzerEDF(templates)

                edf_schedulable = analyzer.analyze_periodic()
                edf_wcrt_result = analyzer.compute_edf_wcrts()

                print_edf_analysis_result(edf_schedulable, edf_wcrt_result)

                simulation = EDFSimulation.EDFSimulation(
                    templates,
                    num_tasks=1,
                    use_worst_case=True,
                    use_hyperperiod=True,
                )

                job_log = simulation.run()
                summarize_job_log(job_log)

                simulated_max_response_times = get_simulated_max_response_times(job_log)

                comparison_rows = compare_analysis_and_simulation(
                    edf_wcrt_result["response_times"],
                    simulated_max_response_times,
                )

                print_wcrt_comparison_table(comparison_rows)

                graphs.graph(job_log, temp_job_title, True, True)

            else:
                dm_result = compute_dm_wcrts(templates)

                print("\n# Deadline Monotonic / Rate Monotonic Analytical Result")
                print(f"Schedulable: {dm_result['schedulable']}")
                print(f"Utilization: {dm_result['utilization']:.4f}")
                print(f"Priority order: {dm_result['priority_order']}")

                if not dm_result["schedulable"]:
                    print(f"Failed task: {dm_result['failed_task_id']}")

                simulation = RMSimulation.RMSimulation(templates)
                job_log, hyperperiod = simulation.run()

                summarize_job_log(job_log)
                print(f"\nHyperperiod: {hyperperiod}")

                simulated_max_response_times = get_simulated_max_response_times(job_log)

                comparison_rows = compare_analysis_and_simulation(
                    dm_result["response_times"],
                    simulated_max_response_times,
                )

                print_wcrt_comparison_table(comparison_rows)

                graph_hyperperiod(
                    job_log,
                    temp_job_title,
                    hyperperiod=hyperperiod,
                    use_deadlines=True,
                )


if __name__ == "__main__":
    main()