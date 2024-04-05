from ortools.sat.python import cp_model

def simple_sat_program():
    model  = cp_model.CpModel()

    num_var = 3
    x = model.new_int_var(0,num_var-1,'x')
    y = model.new_int_var(0,num_var-1,'y')
    z = model.new_int_var(0,num_var-1,'z')

    model.add(x != y)#contraints

    # call the solver
    solver = cp_model.CpSolver()
    status =  solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("This means that x takes the value 1, while both y and z take the value 0, satisfying the constraint x != y.")
        print(f"x = {solver.value(x)}")
        print(f"y = {solver.value(y)}")
        print(f"z = {solver.value(z)}")
    else:
        print('No Solution Found')
        

simple_sat_program()       