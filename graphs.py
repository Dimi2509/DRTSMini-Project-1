import matplotlib.pyplot as plt
import numpy as np

def get_color_from_id(id_val, total_expected=100):
    """
    Returns a color for a given ID using a perceptually broad colormap.
    """
    # Using 'gist_ncar' or 'nipy_spectral' as they contain many 
    # distinct color transitions suitable for many categories.
    #cmap = plt.colormaps['gist_ncar']
    cmap = plt.colormaps['nipy_spectral']
    
    # Normalize the ID to a 0-1 range based on the total
    normalized_id = (id_val % total_expected) / total_expected
    return cmap(normalized_id)

def graph(job_log):
    print("Graphing started")
    # Declaring a figure "gnt"
    fig, gnt = plt.subplots()

    gnt.grid(False)

    # Max end time as the x axis limit
    end_times = []
    [end_times.append(x.end_time) for x in job_log]
    max_end_time = max(end_times)
    x_padding = 50
    gnt.set_xlim(0 - x_padding, max_end_time + x_padding)

    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('Time')
    gnt.set_ylabel('Task ID')

    # Getting deduplicated length
    ids = [x.id for x in job_log]
    dedup_n = []
    [dedup_n.append(x) for x in ids if x not in dedup_n]
    print(dedup_n)
    n = len(dedup_n)
    print(f"Number of tasks: {n}")

    # Setting Y-axis limits
    y_unit = 10    
    y_per_task_padding = 5
    y_bottom_padding = 10
    y_top_padding = 10
    ylim = n * (y_unit + y_per_task_padding)
    print(f"ylim: {ylim}")
    print(f"true ylim: {ylim + y_bottom_padding + y_top_padding}")
    gnt.set_ylim(0, ylim + y_bottom_padding + y_top_padding)

    y_ticks = []
    y_ticklabels = []

    for job in job_log:
        y_bottom = ylim - (job.id + 1) * (y_unit + y_per_task_padding)
        gnt.broken_barh([(job.start_time, job.end_time - job.start_time)], (y_bottom + y_bottom_padding, y_unit), facecolor=get_color_from_id(job.id + 1, n))
        y_ticks.append(y_bottom + y_unit/2 + y_bottom_padding)
        y_ticklabels.append(job.id)

        gnt.axhline(y_bottom + y_bottom_padding, color='black', linestyle='-', linewidth=1)

        # Starting arrow
        gnt.arrow(job.start_time, y_bottom + y_bottom_padding, 0, y_unit + y_per_task_padding/2, head_width=64, width=24, length_includes_head=True, head_length=y_per_task_padding, facecolor='black')

        # Ending arrow
        gnt.arrow(job.end_time, y_bottom + y_bottom_padding + y_unit + y_per_task_padding/2, 0, -(y_unit + y_per_task_padding/2), head_width=48, width=24, length_includes_head=True, head_length=y_per_task_padding, facecolor='black')

        print(f"Job ID: {job.id}")
        print(f"y_bottom: {y_bottom}")
        print(f"job start: {job.start_time}, job end: {job.end_time}")
    

    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(y_ticklabels)
    plt.show()



    # Task 1 
    # X pos
    '''
    start1 = [0, 10]
    end1 = [20, 40]
    task_1 = [(start1[0], end1[0]), (start1[1], end1[1])]
    # Task 1
    # Y pos
    task_ids_pos = [y_padding, y_padding + 1 * y_unit, y_padding + 2 * y_unit]
    task_ids = ['1', '2', '3']

    task_ids_middle = [(x + y_unit/2) for x in task_ids_pos]
    gnt.set_yticks(task_ids_middle)
    gnt.set_yticklabels(task_ids)
    #gnt.set_yticks(False)


    # Declaring a bar in schedule
    gnt.broken_barh(task_1, (task_ids_pos[0], y_unit), facecolors =('tab:orange'))
    gnt.axhline(task_ids_pos[0], color='black', linestyle='-')

    # Declaring multiple bars in at same level and same width
    gnt.broken_barh([(110, 10), (150, 10)], (task_ids_pos[1], y_unit),
                         facecolors ='tab:blue')

    gnt.broken_barh([(10, 50), (100, 20), (130, 10)], (task_ids_pos[2], y_unit),
                                  facecolors =('tab:red'))
    
    fig.savefig("gantt1.png")
    print("Graph saved")

    #plt.savefig("gantt1.png")
    plt.show()
    '''
#graph()