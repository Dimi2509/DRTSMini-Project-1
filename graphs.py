import matplotlib.pyplot as plt

def graph():
    # Declaring a figure "gnt"
    fig, gnt = plt.subplots()

    # Task characteristics
    n_of_tasks = 2

    # Setting Y-axis limits
    y_unit = 10    
    y_padding = 4
    gnt.set_ylim(0, n_of_tasks * y_unit + 2 * y_padding + 50)

    # Setting X-axis limits
    gnt.set_xlim(0, 160)

    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('Time')
    gnt.set_ylabel('Task ID')

    
    # Task 1 
    # X pos
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

    # Setting graph attribute
    gnt.grid(False)

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
graph()