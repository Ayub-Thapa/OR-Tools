"""Code sample that solves a model and displays a small number of solutions."""

from ortools.sat.python import cp_model


class VarArraySolutionPrinterWithLimit(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables: list[cp_model.IntVar], limit: int):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.__solution_limit = limit

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        for v in self.__variables:
            print(f"{v}={self.value(v)}", end=" ")
        print()
        if self.__solution_count >= self.__solution_limit:
            print(f"Stop search after {self.__solution_limit} solutions")
            self.stop_search()

    @property
    def solution_count(self) -> int:
        return self.__solution_count


def stop_after_n_solutions_sample_sat():
    """Showcases calling the solver to search for small number of solutions."""
    # Creates the model.
    model = cp_model.CpModel()
    # Creates the variables.
    num_vals = 3
    x = model.new_int_var(0, num_vals - 1, "x")
    y = model.new_int_var(0, num_vals - 1, "y")
    z = model.new_int_var(0, num_vals - 1, "z")

    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinterWithLimit([x, y, z], 5)
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.solve(model, solution_printer)
    print(f"Status = {solver.status_name(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")
    assert solution_printer.solution_count == 5


stop_after_n_solutions_sample_sat()