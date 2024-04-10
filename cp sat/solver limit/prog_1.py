from ortools.sat.python import cp_model

def solve_with_time_limit():
    model = cp_model.CpModel()
    num_var = 3
    x = model.new_int_var(0,num_var-1,"X")
    y = model.new_int_var(0,num_var-1,"Y")
    z = model.new_int_var(0,num_var-1,"Z")

    model.add(x != y)

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    # Sets a time limit of 10 seconds.
    solver.parameters.max_time_in_seconds = 10.0

    if status == cp_model.OPTIMAL:
        print(f"x = {solver.value(x)}")
        print(f"y = {solver.value(y)}")
        print(f"z = {solver.value(z)}")

        
solve_with_time_limit()