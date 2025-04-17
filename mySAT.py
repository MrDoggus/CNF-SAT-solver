import sys
from SAT_structs import *
from SAT_solver import SAT_solver

if __name__ == "__main__":
    cnf_file = sys.argv[1]

    formula = CNF_Formula.from_dimacs_file(cnf_file)
    
    solver = SAT_solver(formula)
    assignl = solver.solve()
    if (assignl is None):
        print("RESULT:UNSAT")
    else: 
        print("RESULT:SAT")
        assignStr = "ASSIGNMENT:" + " ".join([f"{i}={"1" if assignl[i] else "0"}" for i in range(1,len(assignl))])
        print(assignStr)

    # print(assignl)
    # print(solver.iter_count)
        