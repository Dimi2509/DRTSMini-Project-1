import matplotlib.pyplot as plt

def graph(job_log):
    # Declaring a figure "gnt"
    fig, gnt = plt.subplots()

    gnt.grid(False)

    # Setting default X-axis limits
    xlim_rolling = 100
    gnt.set_xlim(0, xlim_rolling)

    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('Time')
    gnt.set_ylabel('Task ID')

    n = len(job_log)
    print(n)

    # Setting Y-axis limits
    y_unit = 10    
    y_per_task_padding = 4
    ylim = n * (y_unit + y_per_task_padding) + 14
    gnt.set_ylim(0, ylim)

    for job in job_log:
        gnt.set_xlim(0, job.deadline)
        print(job.deadline)

        y_bottom = ylim - job.id * (y_unit + y_per_task_padding)
        y_top = y_bottom + y_unit
        gnt.broken_barh([(job.start_time, job.end_time)], (y_bottom, y_top), facecolors=('tab:orange'))
    
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