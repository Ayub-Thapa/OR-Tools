from ortools.linear_solver import pywraplp

def linear_test():
    # Create the linear solver with the GLOP backend.
    solver= pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        return
    # Create the variables x and y.
    x = solver.NumVar(0,1,'x')
    y = solver.NumVar(0,2,'y')

    print(f"Number of Variable : {solver.NumVariables()}")

    # Create a linear constraint, 0 <= x + y <= 2.
    ct = solver.Constraint(0,2,'ct')
    ct.SetCoefficient(x,1)
    ct.SetCoefficient(y,1)
    print(f"Number of constraint : {solver.NumConstraints()}")

    # Create the objective function, 3 * x + y.
    objective = solver.Objective()
    
    objective.SetCoefficient(x,3)
    objective.SetCoefficient(y,1)
    objective.SetMaximization()

    # Invoke the solver and display the results.
    print(f"Solving with {solver.SolverVersion()}")
    solver.Solve()
    print('Solution')
    print("Objective value =", objective.Value())
    print(f"x : {x.solution_value()}")
    print(f"y : {y.solution_value()}")


linear_test()    
    