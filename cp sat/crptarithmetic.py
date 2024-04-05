from ortools.sat.python import cp_model

model = cp_model.CpModel()
base = 10
c = model.new_int_var(1,base-1,'C')
p = model.new_int_var(0,base-1,'P')
i = model.new_int_var(1,base-1,'I')
s = model.new_int_var(0,base-1,'S')
f = model.new_int_var(1,base-1,'F')
u = model.new_int_var(0,base-1,'U')
n = model.new_int_var(0,base-1,'N')
t = model.new_int_var(1,base-1,'T')
r = model.new_int_var(0,base-1,'R')
e = model.new_int_var(0,base-1,'E')

# We need to group variables in a list to use the constraint AllDifferent.
letters = [c, p, i, s, f, u, n, t, r, e]

assert base >= len(letters)

model.add_all_different(letters)

# CP + IS + FUN = TRUE
model.add(
    c * base + p + i * base + s + f * base * base + u * base + n
    == t * base * base * base + r * base * base + u * base + e
)

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables: list[cp_model.IntVar]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        for v in self.__variables:
            print(f"{v}={self.value(v)}", end=" ")
        print()

    @property
    def solution_count(self) -> int:
        return self.__solution_count 


solver = cp_model.CpSolver()
solution_printer =    VarArraySolutionPrinter(letters)

# enumerate
solver.parameters.enumerate_all_solutions = True

status = solver.solve(model,solution_printer) 