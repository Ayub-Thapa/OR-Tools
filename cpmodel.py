from ortools.sat.python import  cp_model

a = [2,3,2,3,5]
b=[3,4,2,4,2]

model = cp_model.CpModel()
strip_heigth = model.NewIntVar(1,10000000,'strip height')

in_strip_vars = []
roatated_instrips_vars = []

for i in range(len(a)):
    in_strip_vars.append(model.NewBoolVar('rectangle %d in strip'%i))
    roatated_instrips_vars.append(model.NewBoolVar('rectangle %d rotated in strip'%i))
    model.Add(a[i] == strip_heigth).OnlyEnforceIf(in_strip_vars[i])
    model.Add(b[i] == strip_heigth).OnlyEnforceIf(roatated_instrips_vars[i])


model.Maximize(sum(in_strip_vars + roatated_instrips_vars)) #count the number of true bool

solver = cp_model.CpSolver()

solver.parameters.log_search_progress = True
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    for i in range(len(a)):
        if solver.Value(in_strip_vars[i]):
            print('In Strip: %d x %d '% (b[i],a[i]))
        elif solver.value(roatated_instrips_vars[i]):
            print('In strip rotated : %d x %d' %(a[i],b[i]))
                