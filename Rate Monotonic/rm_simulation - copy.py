#RM simulation
import csv
import math
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import TABLEAU_COLORS

class Task:
    def __init__(self, tid, jitter, bcet, wcet, period, deadline, pe):
        self.tid = tid
        self.jitter = int(jitter)
        self.bcet = int(bcet)
        self.wcet = int(wcet)  # We use WCET for safety analysis
        self.period = int(period)
        self.deadline = int(deadline)
        self.pe = pe.strip()

        # runtime state
        self.remaining_time = 0
        self.abs_deadline = 0
        self.next_arrival = 0      # When the period triggers (k*T)
        self.actual_release = 0    # When the task enters ready queue (k*T + Jitter)
        self.is_ready = False      # True if current time >= actual_release

    def __repr__(self):
        return f"{self.tid}(P={self.period}, C={self.wcet}, PE={self.pe})"

def load_tasks(filename):
    tasks = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Strip whitespace from keys/values just in case
                row = {k.strip(): v.strip() for k, v in row.items()}
                
                t = Task(
                    row['TaskID'], row['Jitter'], row['BCET'], 
                    row['WCET'], row['Period'], row['Deadline'], row['PE']
                )
                tasks.append(t)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    return tasks

def get_hyperperiod(tasks):
    if not tasks: return 0
    lcm = tasks[0].period
    for t in tasks[1:]:
        lcm = (lcm * t.period) // math.gcd(lcm, t.period)
    return lcm

def simulate_pe(pe_name, tasks):
    # 1. Sort by Period (RM Priority: Shorter Period = Higher Priority)
    # Note: If periods are equal, you might break ties by ID or Deadline
    tasks.sort(key=lambda x: x.period)

    hyperperiod = get_hyperperiod(tasks)
    print(f"\n{'='*40}")
    print(f" Simulating Processor: {pe_name}")
    print(f" Hyperperiod: {hyperperiod}")
    print(f" Tasks: {[t.tid for t in tasks]}")
    print(f"{'='*40}")

    timeline = []

    # Initialize first arrival
    for t in tasks:
        t.next_arrival = 0
        t.remaining_time = 0
        t.is_ready = False

    # Time Loop
    for time in range(hyperperiod):
        
        # --- A. Check for New Arrivals ---
        for t in tasks:
            # If we reached the start of a period
            if time == t.next_arrival:
                # Calculate when it actually becomes ready (Period + Jitter)
                t.actual_release = time + t.jitter
                t.abs_deadline = time + t.deadline
                
                # Check for deadline miss from PREVIOUS job
                if t.remaining_time > 0:
                     print(f"!! CRITICAL FAILURE at t={time}: Task {t.tid} missed deadline!")

                # Reset job
                t.remaining_time = t.wcet 
                t.next_arrival += t.period # Schedule next period
                t.is_ready = False # Not ready yet if Jitter > 0

            # If Jitter time has passed, mark as ready
            if not t.is_ready and time >= t.actual_release:
                t.is_ready = True

        # --- B. Select Highest Priority Ready Task ---
        active_task = None
        for t in tasks:
            # Must be ready AND have work to do
            if t.is_ready and t.remaining_time > 0:
                active_task = t
                break # Since list is sorted by Period, first found is highest priority

        # --- C. Execute ---
        if active_task:
            # Check if we already passed the deadline
            if time > active_task.abs_deadline:
                print(f"!! DEADLINE MISS DETECTED for {active_task.tid} at t={time}")
            
            timeline.append(active_task.tid)
            active_task.remaining_time -= 1
            
            # If finished, it's no longer ready/active until next period
            if active_task.remaining_time == 0:
                active_task.is_ready = False
        else:
            timeline.append("IDLE")

    return timeline

def print_gantt(timeline, pe_name="PE"):
    if not timeline: return
    # Compress timeline for display: (Task, Duration)
    compressed = []
    if not timeline: return
    
    current = timeline[0]
    count = 1
    for i in range(1, len(timeline)):
        if timeline[i] == current:
            count += 1
        else:
            compressed.append((current, count))
            current = timeline[i]
            count = 1
    compressed.append((current, count))

    print("\nExecution Log:")
    t = 0
    for task, duration in compressed:
        print(f"[{t:03} -> {t+duration:03}] : {task}")
        t += duration
    
    return compressed

def visualize_gantt(compressed, timeline, pe_name="PE"):
    """Create a Gantt chart visualization"""
    if not compressed:
        return
    
    # Get unique tasks (excluding IDLE)
    tasks = sorted(list(set([task for task, _ in compressed if task != "IDLE"])))
    
    # Create color map for tasks
    colors = list(TABLEAU_COLORS.values())
    color_map = {task: colors[i % len(colors)] for i, task in enumerate(tasks)}
    color_map["IDLE"] = "#EEEEEE"
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot Gantt bars
    y_pos = 0
    y_labels = []
    y_ticks = []
    
    task_schedule = {task: [] for task in tasks}
    
    # Extract schedule for each task
    t = 0
    for task, duration in compressed:
        if task != "IDLE":
            task_schedule[task].append((t, duration))
        t += duration
    
    # Plot bars
    for idx, task in enumerate(tasks):
        for start, duration in task_schedule[task]:
            ax.barh(idx, duration, left=start, height=0.6, 
                   color=color_map[task], edgecolor="black", linewidth=0.5)
        
        y_ticks.append(idx)
        y_labels.append(f"Task {task}")
    
    # Add IDLE regions for reference
    t = 0
    for task, duration in compressed:
        if task == "IDLE":
            ax.barh(-0.5, duration, left=t, height=0.6,
                   color=color_map["IDLE"], edgecolor="gray", linewidth=0.5, alpha=0.5)
        t += duration
    
    # Set labels and title
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Time (units)", fontsize=12)
    ax.set_title(f"Gantt Diagram - {pe_name}", fontsize=14, fontweight='bold')
    ax.set_xlim(0, len(timeline))
    ax.set_ylim(-1, len(tasks))
    ax.grid(axis='x', alpha=0.3)
    
    # Add legend
    handles = [mpatches.Patch(facecolor=color_map[task], edgecolor='black', label=f'Task {task}') 
               for task in tasks]
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.01, 1))
    
    plt.tight_layout()
    plt.savefig(f'gantt_{pe_name}.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Gantt diagram saved as 'gantt_{pe_name}.png'")
    plt.show()

# --- Main Execution ---
filename = 'tasks_example2.csv' # Make sure this file exists
all_tasks = load_tasks(filename)

if all_tasks:
    # Group tasks by PE
    tasks_by_pe = defaultdict(list)
    for t in all_tasks:
        tasks_by_pe[t.pe].append(t)

    # Run simulation for each PE
    for pe, tasks in tasks_by_pe.items():
        history = simulate_pe(pe, tasks)
        compressed = print_gantt(history, pe_name=pe)
        visualize_gantt(compressed, history, pe_name=pe)