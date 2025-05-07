import sys
import time
import glob
from dpll import *
from SAT_structs import *
from SAT_solver import SAT_solver

if __name__ == "__main__":
    total_iterations = 0
    successful_files = 0
    total_processing_time = 0
    file_count = 0
    useDPLL = False
    useCDCL = False
    useVSIDS = False
    debug = False
    showMetrics = False
    
    if len(sys.argv) < 2:
        print("Usage: python new_SAT_solver.py [-dpll | -no_vsids | -debug | -metrics] *.cnf")
        sys.exit(1)
    
    args = sys.argv[1:]
    cnf_files = []
    for arg in args:
        if arg == "-dpll":
            useDPLL = True
        elif arg == "-no_vsids":
            useCDCL = True
        elif arg == "-debug":
            debug = True
        elif arg == "-metrics":
            showMetrics = True
        else:
            cnf_files.append(arg)

    if len(cnf_files) == 1:
        cnf_files = glob.glob(cnf_files[0])

    if not cnf_files:
        print("No CNF files provided.")
        sys.exit(1)

    for cnf_file in cnf_files:
        if (debug or showMetrics):
            print("\n")
        try:
            start_time = time.time()
        
            if useDPLL == True:
                if (debug or showMetrics):
                    print(f"--- Solving {cnf_file} using DPLL ---")
                clauses = parse_dimacs_file(cnf_file)
                (solution, iter_count) = dpll(clauses, {}, 0, log=debug)
            else:
                formula = CNF_Formula.from_dimacs_file(cnf_file)
                solver = SAT_solver(formula, log=debug)
                if useCDCL == True:
                    if (debug or showMetrics):
                        print(f"--- Solving {cnf_file} using CDCL ---")
                    solution = solver.solve()  # Default useVSIDS=False
                else:
                    if (debug or showMetrics):
                        print(f"--- Solving {cnf_file} using CDCL w/ VSIDS ---")
                    solution = solver.solve(useVSIDS=True)
                iter_count = solver.iter_count
                    

            end_time = time.time()
            single_file_processing_time = end_time - start_time
            
            if (solution is None):
                print("RESULT:UNSAT")
            else: 
                print("RESULT:SAT")
                assignStr = "ASSIGNMENT:" + " ".join([f"{i}={"1" if solution[i] else "0"}" for i in range(1,len(solution))])
                print(assignStr)

            if (debug or showMetrics):
                print(f"Number of iterations: {iter_count:.2f}")
                print(f"Processing time: {single_file_processing_time:.4f} seconds")
                
            total_iterations += iter_count
            file_count += 1
            total_processing_time += single_file_processing_time
        except Exception as e:
            print(f"Failed to parse {cnf_file}: {e}")
            continue  # Skip broken files


    if (debug or showMetrics):
        avg_iter_count = total_iterations / file_count
        print("\n==============================")
        print(f"Total Processing time: {total_processing_time:.4f} seconds")
        print(f"Average number of iterations over {file_count} successful files: {avg_iter_count:.2f}")
