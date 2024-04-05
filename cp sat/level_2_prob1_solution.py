from ortools.sat.python import cp_model

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self,variables:list[cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self) -> None :
        self.__solution_count += 1

        for v in self.__variables:
            print(f"{v} = {self.value(v)}",end='')
        print() 

    @property
    def solution_count(self) -> int:
        return self.__solution_count       


def get_all_solution():
    model  = cp_model.CpModel()

    num_var = 3
    x = model.new_int_var(0,num_var-1,'x')
    y = model.new_int_var(0,num_var-1,'y')
    z = model.new_int_var(0,num_var-1,'z')

    model.add(x != y)#contraints
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter([x,y,z])    

    # enumerate all the solution
    solver.parameters.enumerate_all_solutions = True

    status = solver.solve(model,solution_printer)

    print(f"Status {solver.status_name(status)}")
    print(f"Count {solution_printer.solution_count}")


get_all_solution()
