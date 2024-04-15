from ortools.sat.python import cp_model

num_nurse = 5
num_shift =3
num_days = 7
all_nurse =range(num_nurse)
all_shift = range(num_shift)
all_day = range(num_days)
shift_request = [
    [[0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 1]],
    [[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1]],
    [[0, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0], [0, 0, 0]],
    [[0, 0, 1], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0]],
]
model = cp_model.CpModel()
shift = {}
for n in all_nurse:
    for d in all_day:
        for s in all_shift:
            shift[(n,d,s) ]= model.new_bool_var(f"shift_n{n}_d{d}_s{s}")

for d in all_day:
    for s in all_shift:
        model.add_exactly_one(shift[(n, d, s)] for n in all_nurse)

# Try to distribute the shifts evenly, so that each nurse works
# min_shifts_per_nurse shifts. If this is not possible, because the total
# number of shifts is not divisible by the number of nurses, some nurses will
# be assigned one more shift.
min_shifts_per_nurse = (num_shift * num_days) // num_nurse
if num_shift * num_days % num_nurse == 0:
    max_shifts_per_nurse = min_shifts_per_nurse
else:
    max_shifts_per_nurse = min_shifts_per_nurse + 1
for n in all_nurse:
    num_shifts_worked = 0
    for d in all_day:
        for s in all_shift:
            num_shifts_worked += shift[(n, d, s)]
    model.add(min_shifts_per_nurse <= num_shifts_worked)
    model.add(num_shifts_worked <= max_shifts_per_nurse)

model.maximize(
    sum(shift_request[n][d][s]*shift[(n, d, s)]
        for n in all_nurse
        for d in all_day
        for s in all_shift
        )
)

# Since shift_requests[n][d][s] * shifts[(n, d, s) is 1 if shift s is assigned to nurse n on day d and that nurse requested that shift (and 0 otherwise), the objective is the number shift of assignments that meet a request.

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL:
    print("Solution:")
    for d in all_day:
        print("Day", d)
        for n in all_nurse:
            for s in all_shift:
                if solver.value(shift[(n, d, s)]) == 1:
                    if shift_request[n][d][s] == 1:
                        print("Nurse", n, "works shift", s, "(requested).")
                    else:
                        print("Nurse", n, "works shift", s, "(not requested).")
        print()
    print(
        f"Number of shift requests met = {solver.objective_value}",
        f"(out of {num_nurse * min_shifts_per_nurse})",
    )
else:
    print("No optimal solution found !")