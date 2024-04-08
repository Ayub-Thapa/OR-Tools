from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional
from ortools.sat.python import cp_model
import collections

app = FastAPI()

class TaskData(BaseModel):
    tasks_data: List[List[Tuple[int, int, int]]]
    technician_skills: Dict[int, List[int]]
    job_time_windows: Dict[int, Tuple[int, int]]
    skill_types: Dict[int, str]


@app.post("/solve/")
async def solve(task_data: TaskData):
    print("Received Job Specifications:")
    print("Tasks Data:")
    for task_id, tasks in enumerate(task_data.tasks_data):
        print(f"  Job {task_id}:")
        for subtask_id, (skill_required, duration, required_personnel) in enumerate(tasks):
            # Lookup the skill name using the skill_required ID
            skill_name = task_data.skill_types.get(skill_required, "Unknown Skill")
            print(f"    Sub-task {subtask_id}: Skill Required={skill_name}, Duration={duration}, Required Personnel={required_personnel}")

    print("\nTechnician Skills:")
    for technician_id, skills in task_data.technician_skills.items():
        # Convert skill IDs to skill names for each technician
        skill_names = [task_data.skill_types.get(skill, "Unknown Skill") for skill in skills]
        print(f"  Technician {technician_id}: Skills={', '.join(skill_names)}")

    print("\nJob Time Windows:")
    for job_id, (start, end) in task_data.job_time_windows.items():
        print(f"  Job {job_id}: Start={start}, End={end}")
    # Technician skills definition
    # 0: plumber, 1: electrician, 2: multi-skilled (can do both)
    technician_skills = task_data.technician_skills    
    # Expanded task data with more jobs and sub-tasks
    tasks_data = task_data.tasks_data    # Define job-level start and end times
    job_time_windows = task_data.job_time_windows
    # Define technician types if not already defined
    skill_types = task_data.skill_types
    # Expanded workday hours: 8 AM to 6 PM represented as 0 to 10 (10-hour workday)
    work_start = 0  # Start of workday in "hours" after 8 AM
    work_end = 10   # End of workday in "hours" after 8 AM
    # Constants
    workday_hours = work_end - work_start  # Total workday hours, adjust as necessary
   
    # Model setup
    model = cp_model.CpModel()
    
    # Named tuple for tasks
    TaskType = collections.namedtuple('TaskType', 'start end interval presence')
    
    # Store all tasks
    all_tasks = {}
    # Track tasks assigned to technicians for sequencing and fulfillment tracking
    technician_tasks = collections.defaultdict(list)
    job_subtasks = collections.defaultdict(list)  # To keep track of sub-tasks within each job for sequencing
    subtask_fulfillment = {}  # Maps sub-task to a variable indicating if it's fully staffed
    
    for task_id, task in enumerate(tasks_data):
        job_start, job_end = job_time_windows.get(task_id, (0, 10))
        previous_end_var = None
        
        for subtask_id, (skill_required, duration, required_personnel) in enumerate(task):
            presence_vars = []
            start_vars = []
            
            for technician in technician_skills:
                if skill_required in technician_skills[technician]:
                    suffix = f'_{task_id}_{subtask_id}_tech{technician}'
                    earliest_start = job_start
                    latest_start = job_end - duration
                    start_var = model.NewIntVar(earliest_start, latest_start, 'start' + suffix)
                    end_var = model.NewIntVar(earliest_start + duration, job_end, 'end' + suffix)
                    presence_var = model.NewBoolVar('presence' + suffix)
                    interval_var = model.NewOptionalIntervalVar(start_var, duration, end_var, presence_var, 'interval' + suffix)
                    
                    all_tasks[(task_id, subtask_id, technician)] = TaskType(start=start_var, end=end_var, interval=interval_var, presence=presence_var)
                    technician_tasks[technician].append(all_tasks[(task_id, subtask_id, technician)])
                    presence_vars.append(presence_var)
                    start_vars.append(start_var)
                    
                    if previous_end_var is not None:
                        model.Add(start_var >= previous_end_var)
                    job_subtasks[task_id].append((start_var, end_var))
            
            previous_end_var = model.NewIntVar(job_start, job_end, f'end_subtask_{task_id}_{subtask_id}')
            model.AddMaxEquality(previous_end_var, [end_var for _, end_var in job_subtasks[task_id]])
            
            if required_personnel > 0:
                fulfill_var = model.NewBoolVar(f'fulfill_{task_id}_{subtask_id}')
                model.Add(sum(presence_vars) >= required_personnel).OnlyEnforceIf(fulfill_var)
                model.Add(sum(presence_vars) < required_personnel).OnlyEnforceIf(fulfill_var.Not())
                subtask_fulfillment[(task_id, subtask_id)] = fulfill_var
                
            # Enforcing same start time for technicians on the same sub-task
            if len(start_vars) > 1 and required_personnel > 1:
                for i in range(len(start_vars)):
                    for j in range(i + 1, len(start_vars)):
                        model.Add(start_vars[i] == start_vars[j])

    for technician, tasks in technician_tasks.items():
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                task1 = tasks[i]
                task2 = tasks[j]
                model.AddNoOverlap([task1.interval, task2.interval])


    # Objective: Maximize the number of fully staffed sub-tasks
    model.Maximize(sum(subtask_fulfillment.values()))
    
    # Solver setup and solution finding
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    output = ""
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print('Solution found:')
        for (task_id, subtask_id), var in subtask_fulfillment.items():
            if solver.Value(var):
                print(f'Sub-task {task_id}-{subtask_id} successfully staffed.')
                output += f'\nSub-task {task_id}-{subtask_id} successfully staffed.'
            else:
                print(f'Sub-task {task_id}-{subtask_id} could not be fully staffed.')
                output += f'\nSub-task {task_id}-{subtask_id} could not be fully staffed.'
    else:
        print('No solution found.')
        return {"message": "No Solution found"}

    # Output solution
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print('Solution:')
        for task_id, task in enumerate(tasks_data):
            for subtask_id, _ in enumerate(task):
                for tech in technician_skills:
                    if (task_id, subtask_id, tech) in all_tasks and solver.Value(all_tasks[(task_id, subtask_id, tech)].presence):
                        start = solver.Value(all_tasks[(task_id, subtask_id, tech)].start)
                        end = solver.Value(all_tasks[(task_id, subtask_id, tech)].end)
                        print(f'Task {task_id}, Subtask {subtask_id} assigned to Technician {tech}: Start at {start}, End at {end}')
                        output += f'\nTask {task_id}, Subtask {subtask_id} assigned to Technician {tech}: Start at {start}, End at {end}'
    else:
        print('No solution found.')
        return {"message": "No Solution found"}

    ###Technician View:
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print('Solution:')
        
        # Initialize a dictionary to hold the schedule for each technician
        technician_schedule = collections.defaultdict(list)
        
        # Populate the schedule with tasks assigned to each technician
        for (task_id, subtask_id, technician), task in all_tasks.items():
            if solver.Value(task.presence):
                start = solver.Value(task.start)
                end = solver.Value(task.end)
                technician_schedule[technician].append((task_id, subtask_id, start, end))
        
        # Sort tasks for each technician by start time and print the schedule
        for tech, tasks in technician_schedule.items():
            tasks.sort(key=lambda x: x[2])  # Sort by start time
            print(f'Technician {tech} schedule:')
            output +=f'\nTechnician {tech} schedule:'
            for task_id, subtask_id, start, end in tasks:
                print(f'  Task {task_id}, Subtask {subtask_id}: Start at {start}, End at {end}')
                output += f'\n  Task {task_id}, Subtask {subtask_id}: Start at {start}, End at {end}'
        # Assuming each technician works for the entire available period
        total_available_hours_per_technician = workday_hours  # Total workday hours

        # Initialize a workday representation for each technician
        workday_visualization = {tech: ['-' for _ in range(workday_hours)] for tech in technician_skills}
        
        for task_id, task in enumerate(tasks_data):
            for subtask_id, _ in enumerate(task):
                for tech in technician_skills:
                    if (task_id, subtask_id, tech) in all_tasks and solver.Value(all_tasks[(task_id, subtask_id, tech)].presence):
                        start = solver.Value(all_tasks[(task_id, subtask_id, tech)].start)
                        end = solver.Value(all_tasks[(task_id, subtask_id, tech)].end)
                        # Mark the hours as busy ('*') for the duration of this task
                        for hour in range(start, end):
                            workday_visualization[tech][hour] = '*'
        
        # Print the visualization for each technician
        for tech, hours in workday_visualization.items():
            print(f'Technician {tech} workday: ' + ''.join(hours))
            output += f'\nTechnician {tech} workday: ' + ''.join(hours)

        print("\nTechnician Utilization Rates:")
        for tech, tasks in technician_schedule.items():
            total_worked_hours = sum(end - start for _, _, start, end in tasks)
            utilization_percentage = (total_worked_hours / total_available_hours_per_technician) * 100
            skills = technician_skills[tech]  # Get list of skill IDs for the technician
            skill_names = [skill_types[skill] for skill in skills if skill in skill_types]  # Convert skill IDs to names
            skill_str = ', '.join(skill_names)  # Join skill names into a single string
           
            print(f'Technician {tech} ({skill_str}): {utilization_percentage:.2f}% utilized')
            output += f'Technician {tech} ({skill_str}): {utilization_percentage:.2f}% utilized'
    else:
        print('No solution found.')
        return {"message": "No Solution found"}
    return {"message": "Solution found", "data": output}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)