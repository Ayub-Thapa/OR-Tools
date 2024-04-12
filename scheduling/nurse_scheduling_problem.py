from ortools.sat.python import cp_model

class NurseSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self,shift,num_nurse,num_days,num_shift,limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shift = shift
        self._num_days = num_days
        self.num_shift = num_shift
        self._num_nurse = num_nurse
        self._solution_count=0
        self._solution_limit =limit

    def on_solution_callback(self):
        self._solution_count += 1
        print(f"Soltion {self._solution_count}")
        for d in range(self._num_days):
            print(f"Days : {d}")
            for n in range(self._num_days):
                is_working =False
                for s in range(self.num_shift):
                    if self.value(self._shift[(d,n,s)]):
                        is_working = True
                        print(f" Nurse {n} WorkShift {s}")
                if not is_working:
                    print(f"Nurse {n} Does Not Work")
        if self._solution_count >= self._solution_limit:
            print(f"Stop Search After {self._solution_count} solution")
            
            self.stop_search()    
                 
num_nurse = 4
num_shift=3
num_days=3

all_nurse = range(num_nurse)
all_shift = range(num_shift)
all_days = range(num_days)

model = cp_model.CpModel()

shift = {}
# Create the variables
for n in all_nurse:
    for d in all_days:
        for s in all_shift:
            shift[(n,d,s)] = model.new_bool_var(f"shift_n{n}_d{d}_s{s}")

# Assign nurses to shifts

for d in all_days:
    for s in all_shift:
        model.add_exactly_one(shift[(n,d,s)] for s in all_shift)

# Assign shifts evenly

min_shift_per_nurse = (num_shift*num_days) // num_nurse

if num_shift*num_days % num_nurse == 0:
    max_shift_per_nurse = min_shift_per_nurse
else:
    max_shift_per_nurse = min_shift_per_nurse+1

for n  in all_nurse:
    shift_worked = []
    for d in all_days:
        for s in all_shift:
            shift_worked.append(shift[(n,d,s)])
    model.add(min_shift_per_nurse <= sum(shift_worked))
    model.add(sum(shift_worked) >= max_shift_per_nurse)

solver =  cp_model.CpSolver()
solver.parameters.linearization_level = 0
solver.parameters.enumerate_all_solutions = True

# Display the first five solutions.
solution_limit = 5

solution_printer = NurseSolutionPrinter(shift,num_nurse,num_days,num_shift,solution_limit)
            


solver.solve(model, solution_printer)
