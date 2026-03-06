# DRTS-Mini-Project-1
Distributed Real-Time Systems Mini Project 1 Repository


## Parser

The `parser.py` module loads taskset CSV files from the `datasets/` directory and converts them into Python objects for further analysis.

### Dataset Structure

Two datasets are supported:

| Dataset | Key | Period Distribution |
|---|---|---|
| Automotive | `automotive` | automotive-perDist |
| UUniFast | `uunifast` | uniform-discrete-perDist |

Each dataset contains tasksets at utilization levels from `0.10` to `1.00` (10 levels, 100 tasksets each).

CSV columns: `TaskID`, `Jitter`, `BCET`, `WCET`, `Period`, `Deadline`, `PE`

### CLI Usage

```bash
# Load all utilization levels from the automotive dataset
python parser.py --dataset-name automotive

# Load only 50% utilization tasksets
python parser.py --dataset-name automotive --utilization 0.50

# Load from a custom datasets folder
python parser.py --folder-path path/to/datasets/ --dataset-name uunifast --utilization 0.30
```