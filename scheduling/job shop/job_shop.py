# job 0 = [(0, 3), (1, 2), (2, 2)]
# job 1 = [(0, 2), (2, 1), (1, 4)]
# job 2 = [(1, 4), (2, 3)]
# In the example, job 0 has three tasks. The first, (0, 3), must be processed on machine 0 in 3 units of time. The second, (1, 2), 
# must be processed on machine 1 in 2 units of time, and so on. Altogether, there are eight tasks.

import collections
from ortools.sat.python import cp_model

jobs_data = [  # task = (machine_id, processing_time).
    [(0, 3), (1, 2), (2, 2)],  # Job0
    [(0, 2), (2, 1), (1, 4)],  # Job1
    [(1, 4), (2, 3)],  # Job2
]

machines_count = 1 + max(task[0] for job in jobs_data for task in job)
print(machines_count)
all_machines = range(machines_count)
print(all_machines)

horizon = sum(task[1] for job in jobs_data for task in job)
print(horizon)