from ortools.constraint_solver import  pywrapcp


def main():
    solver = pywrapcp.Solver("CP is Fun!")

    base = 10

    digits = list(range(0,base))
    digit_var_without_zero = list(range(1,base))

    c = solver.IntVar(digit_var_without_zero,'C')
    p=solver.IntVar(digits,'P')
    i=solver.IntVar(digit_var_without_zero,'I')
    s=solver.IntVar(digits,'S')
    f=solver.IntVar(digit_var_without_zero,'F')
    u=solver.IntVar(digits,'U')
    n=solver.IntVar(digits,'N')
    t=solver.IntVar(digit_var_without_zero,'T')
    r=solver.IntVar(digits,'R')
    e=solver.IntVar(digits,'E')

    letters=[c,p,i,s,f,u,n,t,r,e]

    assert base >= len(letters)

    solver.Add(solver.AllDifferent(letters))

    # CP + IS + FUN = TRUE
    solver.Add(
        p + s + n + base * (c + i + u) + base * base * f
        == e + base * u + base * base * r + base * base * base * t
    )

    solution_count = 0
    db = solver.Phase(letters,solver.INT_VAR_DEFAULT,solver.INT_VALUE_DEFAULT)
    solver.NewSearch(db)

    while solver.NextSolution():
        print(letters)

        assert(
            base * c.Value()
            + p.Value()
            + base * i.Value()
            + s.Value()
            + base * base * f.Value()
            + base * u.Value()
            + n.Value()
            == base * base * base * t.Value()
            + base * base * r.Value()
            + base * u.Value()
            + e.Value()
        )
        solution_count += 1
        
    solver.EndSearch()
    print(f"number of solution : {solution_count}")


if __name__ == '__main__':
    main()        