import sys
import time
import glob
import csv
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
    
    metrics = []  # Store metrics for CSV

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
#        try:
        start_time = time.time()
    
        if useDPLL:
            if (debug or showMetrics):
                print(f"--- Solving {cnf_file} using DPLL ---")
            clauses = parse_dimacs_file(cnf_file)
            (solution, iter_count) = dpll(clauses, {}, 0, log=debug)
        else:
            formula = CNF_Formula.from_dimacs_file(cnf_file)
            solver = SAT_solver(formula, log=debug)
            if useCDCL:
                if (debug or showMetrics):
                    print(f"--- Solving {cnf_file} using CDCL ---")
                solution = solver.solve()
            else:
                if (debug or showMetrics):
                    print(f"--- Solving {cnf_file} using CDCL w/ VSIDS ---")
                solution = solver.solve(useVSIDS=True)
            iter_count = solver.iter_count
                

        end_time = time.time()
        single_file_processing_time = end_time - start_time
        
        result = "UNSAT" if solution is None else "SAT"
        print(f"RESULT:{result}")
        if result == "SAT":
            assignStr = "ASSIGNMENT:" + " ".join([f"{i}={"1" if solution[i] else "0"}" for i in range(1,len(solution))])
            print(assignStr)

        if (debug or showMetrics):
            print(f"Number of iterations: {iter_count:.2f}")
            print(f"Processing time: {single_file_processing_time:.4f} seconds")

        # Store metrics for this file
        metrics.append({
            "filename": cnf_file,
            "result": result,
            "iterations": iter_count,
            "time_sec": f"{single_file_processing_time:.4f}"
        })

        total_iterations += iter_count
        total_processing_time += single_file_processing_time
        file_count += 1

#        except Exception as e:
#            print(f"Failed to parse {cnf_file}: {e}")
#            continue

    if (debug or showMetrics):
        avg_iter_count = total_iterations / file_count if file_count > 0 else 0
        print("\n==============================")
        print(f"Total Processing time: {total_processing_time:.4f} seconds")
        print(f"Average number of iterations over {file_count} successful files: {avg_iter_count:.2f}")

    # Write metrics to CSV
    if showMetrics and metrics:
        csv_filename = "solver_metrics.csv"
        with open(csv_filename, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["filename", "result", "iterations", "time_sec"])
            writer.writeheader()
            writer.writerows(metrics)
        print(f"\nMetrics saved to {csv_filename}")
