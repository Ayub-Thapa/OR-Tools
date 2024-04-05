from ortools.sat.python import cp_model
# Maximize 2x + 2y + 3z 
# x + 7⁄2 y + 3⁄2 z	≤	25
# 3x - 5y + 7z	≤	45
# 5x + 2y - 6z	≤	37
# x, y, z	≥	0
# x, y, z integers
model = cp_model.CpModel()

var_ub = max(50,45,37)
x=model.new_int_var(0,var_ub,'x')
y=model.new_int_var(0,var_ub,'y')
z=model.new_int_var(0,var_ub,'z')

# contraints
model.add(2*x+7*y+3*z <= 50)
model.add(3*x-5*y+7*z <= 45)
model.add(5*x+2*y-6*z <=37)

# maximize
model.maximize(2*x+2*y+3*z)

solver = cp_model.CpSolver()
status =solver.solve(model)


if cp_model.OPTIMAL or cp_model.FEASIBLE :
    print(f"Maximum of Objectives Function: {solver.objective_value}")
    print(f"x : {solver.value(x)}")
    print(f"y : {solver.value(y)}")
    print(f"z : {solver.value(z)}")
else:
    print(f"No Solution Found")
        