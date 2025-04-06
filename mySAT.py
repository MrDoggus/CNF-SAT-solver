import sys
from SAT_structs import *

if __name__ == "__main__":
    cnf_file = sys.argv[1]

    formula = CNF_Formula.from_dimacs_file(cnf_file)
    print(formula)
        