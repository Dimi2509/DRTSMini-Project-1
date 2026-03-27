# DRTS-Mini-Project-1
Distributed Real-Time Systems Mini Project 1 Repository


## Parser

The `parser.py` module loads taskset CSV files from the `datasets/` directory and converts them into Python objects for further analysis.

### Dataset Structure

Three datasets are supported:

| Dataset | Key | Period Distribution |
|---|---|---|
| Automotive | `automotive` | automotive-perDist |
| UUniFast | `uunifast` | uniform-discrete-perDist |
| Test | `test` | test_tasks |

Each dataset contains tasksets at utilization levels from `0.10` to `1.00` (10 levels, 100 tasksets each).

CSV columns: `TaskID`, `Jitter`, `BCET`, `WCET`, `Period`, `Deadline`, `PE`

The test dataset contains schedulable and unschedulable tasksets, which can be filtered using the `--schedulable` flag.
### CLI Usage

```bash
# Load all utilization levels from the automotive dataset
python parser.py --dataset-name automotive

# Load only 50% utilization tasksets
python parser.py --dataset-name automotive --utilization 0.50

# Load from a custom datasets folder
python parser.py --folder-path path/to/datasets/ --dataset-name uunifast --utilization 0.30

# Use the test dataset with schedulable tasksets only
python parser.py --dataset-name test --schedulable true
```

## EDF-Simulator

The `EDFSimulation.py` module implements an Earliest Deadline First scheduler for periodic real-time tasks.

### EDF simulation behavior
Takes task templates as input, and outputs a list of jobs as execution logs from simulation.

### Simulator features
- Number of tasks (per task type) to be scheduled can be specified 
- The execution time of each task is calculated from a Gaussian distribution based on the worst and best execution time
- The execution time of tasks can be configured to use only the worst case time, useful for doing analysis and comparison
- Support for hyperperiod bounding.
- Unit tests covering common scenarios

### Usage
Update the task templates in the main function with desired data and specify the flags if needed
```python
# Example usage
    task_templates = [
        TaskTemplate(
            id=1,
            best_case_time=1,
            worst_case_time=3,
            time_period=5,
            deadline=5,
            jitter=0,
        ),
        TaskTemplate(
            id=2,
            best_case_time=2,
            worst_case_time=4,
            time_period=10,
            deadline=10,
            jitter=0,
        ),
    ]
    simulation = EDFSimulation(task_templates, num_tasks=3)
    job_log = simulation.run()
    for job in job_log:
        print(job)
```
The returned job_log can be visualized by calling graph.graph(job_log)

## Main Entry Point

The `main.py` script is the current command-line entrypoint for loading one taskset, converting it into task templates, running a simulation, and plotting the resulting schedule.

When executed, `main.py`:

1. Parses command-line arguments.
2. Loads one CSV taskset from the selected dataset.
3. Converts the CSV rows into `TaskTemplate` objects.
4. Runs a simulation.
5. Prints the generated job log.
6. Opens a Matplotlib plot of the schedule.

### CLI Arguments

| Argument | Type | Default | Description |
|---|---|---|---|
| `--folder-path` | `str` | `datasets/` | Base path to the datasets folder. |
| `--dataset-name` | `str` | `automotive` | Dataset to load. Supported values: `automotive`, `uunifast`, `test`, `other`. |
| `--path-to-csv` | `str` | `None` | Path to a custom CSV file. Used only when `--dataset-name other` is selected. |
| `--utilization` | `str` | `0.10` | Utilization level to use for `automotive` and `uunifast`. Example: `0.50`. |
| `--simulator` | `str` | `EDF` | Intended simulator selector. Supported values: `EDF`, `RM`. |
| `--taskset-index` | `int` or `None` | `None` | Index of the taskset CSV file to load. If omitted, a random taskset is selected. |
| `--schedulable` | `bool` | `true` | Only used with the `test` dataset. Loads from `schedulable` when `true`, otherwise from `not_schedulable`. |

### Usage Examples

```bash
# Run the default configuration
python main.py

# Run one automotive taskset at 30% utilization
python main.py --dataset-name automotive --utilization 0.30 --taskset-index 0

# Run one UUniFast taskset at 70% utilization
python main.py --dataset-name uunifast --utilization 0.70 --taskset-index 4

# Run the schedulable test taskset
python main.py --dataset-name test --schedulable true

# Run the unschedulable test taskset
python main.py --dataset-name test --schedulable false

# Run a custom CSV dataset from a local folder
python main.py --dataset-name other --folder-path . --path-to-csv path/to/custom/tasksets
```

### Notes

- If `--taskset-index` is not provided, `main.py` selects a random CSV file from the chosen dataset folder.
- The `--utilization` argument is ignored for the `test` dataset.
