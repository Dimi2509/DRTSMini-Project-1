import matplotlib.pyplot as plt
import random

def get_color_from_id(id_val, total_expected=500):
    """
    Returns a color for a given ID using a perceptually broad colormap.
    """
    cmap = plt.colormaps['gist_ncar']
    normalized_id = (id_val % total_expected) / total_expected
    return cmap(normalized_id)

def graph_hyperperiod(job_log, job_title="Schedule", hyperperiod=None, use_deadlines=False, use_period=False):
    """
    Plots the schedule of tasks up to the hyperperiod.
    """
    print("Graphing started")

    fig, gnt = plt.subplots()
    gnt.set_title(job_title)
    gnt.set_xlabel('Time')
    gnt.set_ylabel('Task ID')
    gnt.grid(False)

    # Deduplicate task IDs
    ids = [x.id for x in job_log]
    dedup_n = []
    [dedup_n.append(x) for x in ids if x not in dedup_n]
    n = len(dedup_n)

    # Y-axis configuration
    y_unit = 10    
    y_per_task_padding = 5
    y_bottom_padding = 10
    y_top_padding = 10
    ylim = n * (y_unit + y_per_task_padding)
    gnt.set_ylim(0, ylim + y_bottom_padding + y_top_padding)

    y_ticks = []
    y_ticklabels = []

    # X-axis configuration
    if hyperperiod is None:
        max_time = max([job.end_time for job in job_log])
    else:
        max_time = hyperperiod

    x_padding_to_xlim = 0.05
    x_padding = max_time * x_padding_to_xlim
    gnt.set_xlim(0 - x_padding, max_time + x_padding)

    arrow_width_to_xlim = 0.002
    arrow_width = max_time * arrow_width_to_xlim
    time_period_to_arrow_width = 0.6
    time_period_width = time_period_to_arrow_width * arrow_width

    # Plot each job
    for job in job_log:
        y_bottom = ylim - (job.id + 1) * (y_unit + y_per_task_padding)
        gnt.broken_barh([(job.start_time, job.end_time - job.start_time)], 
                        (y_bottom + y_bottom_padding, y_unit), 
                        facecolor=get_color_from_id(job.id + 1, n))

        y_ticks.append(y_bottom + y_unit/2 + y_bottom_padding)
        y_ticklabels.append(job.id)

        gnt.axhline(y_bottom + y_bottom_padding, color='black', linestyle='-', linewidth=1)

        # Start arrow
        gnt.arrow(job.start_time, y_bottom + y_bottom_padding, 0, y_unit + y_per_task_padding/2,
                  head_width=arrow_width*2, width=arrow_width, length_includes_head=True,
                  head_length=y_per_task_padding, facecolor='black')

        # End arrow
        gnt.arrow(job.end_time, y_bottom + y_bottom_padding + y_unit + y_per_task_padding/2, 0, -(y_unit + y_per_task_padding/2),
                  head_width=arrow_width*2, width=arrow_width, length_includes_head=True,
                  head_length=y_per_task_padding, facecolor='black')

        if use_deadlines:
            gnt.arrow(job.deadline, y_bottom + y_bottom_padding + y_unit + y_per_task_padding/2, 0, -(y_unit + y_per_task_padding/2),
                      head_width=arrow_width*2, width=arrow_width, length_includes_head=True,
                      head_length=y_per_task_padding, facecolor='red', edgecolor='red')

        if use_period:
            gnt.broken_barh([(job.time_period - time_period_width/2, time_period_width)],
                            (y_bottom + y_bottom_padding, y_unit + 5), facecolor='blue')

    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(y_ticklabels)
    plt.show()