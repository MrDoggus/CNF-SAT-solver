import sys
from SAT_structs import *
from SAT_solver import SAT_solver

if __name__ == "__main__":
    cnf_file = sys.argv[1]

    formula = CNF_Formula.from_dimacs_file(cnf_file)
    
    solver = SAT_solver(formula)
    print(solver.solve())
    print(solver.iter_count)
        