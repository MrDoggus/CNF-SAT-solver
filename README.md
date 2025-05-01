# CNF-SAT-solver

Boolean Satisfiability solver for ECE51216 at Purdue University. Given a CNF formula, finds assignment of variables that makes the formula true. 
This project aims to implement Variable State Independent Decaying Sum (VSIDS) and Conflict-Driven Clause Learning (CDCL) heuristics in the DPLL algorithm.
There are several applications for SAT within EDA, including automatic test pattern generation and combinational equivalence checking. 
Since SAT is known to be an NP-Complete problem, generalized algorithms for solving SAT may not be enough of a solution. 
Additional information about circuit structure, alongside heuristics, can be used to significantly speed up the algorithm. 

## Code and Directory Structure 

The `aim/` and `cnf_bench/` directories contains `.cnf` testcase files to help evaluate the correctness and performance. 
`mySAT.py` parses command line arguments to configure and run the SAT solving algorithms designed for this project. 
`dpll.py` is a simple SAT solver created to be a baseline to compare against our implemented heuristics. 
It uses recursive functions to solve SAT problems. 
`SAT_solver.py` contains the logic that implements VSIDS and CDCL heuristics. 
It uses recursive data structures instead of recursive functions to simplify backtracking and sharing information between iterations. 
Finally there is `SAT_structs.py`, which contains data structures used in `SAT_solver.py`. 

## How to Run Solver 