import sys

def parse_dimacs_file(filepath):
    clauses = []
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if line == '' or line.startswith('c') or line.startswith('p'):
                continue
            literals = list(map(int, line.split()))
            if literals[-1] == 0:
                literals = literals[:-1]
            clauses.append(literals)
    return clauses

def getUnsatisfiedClauses(clauses, assignment):
    unsatisfied = []

    for clause in clauses:
        clause_satisfied = False
        for lit in clause:
            var = abs(lit)
            val = assignment.get(var)
            if val is not None:
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_satisfied = True
                    break
        if not clause_satisfied:
            unsatisfied.append(clause)
    return unsatisfied

def dpll(clauses, assignment, depth):
    if depth == 0:
        dpll.total_iterations = 0
        
    dpll.total_iterations += 1

    indent = "\t" * depth
##    print(f"{indent}dpll")
##    print(f"{indent}\tclauses: {clauses}")
##    print(f"{indent}\tassignment: {assignment}")

    clauses = getUnsatisfiedClauses(clauses, assignment)
##    print(f"{indent}\tUnsatisfied clauses: {clauses}")

    if len(clauses) == 0:
        return (assignment, dpll.total_iterations)

    simplifiedClauses = []
    for clause in clauses:
        simplifiedClause = [lit for lit in clause if assignment.get(abs(lit)) != (-lit > 0)]
        if not simplifiedClause:
##            print(f"{indent}\tConflict for {assignment}")
            return (False, dpll.total_iterations)
        simplifiedClauses.append(simplifiedClause)

##    print(f"{indent}\tsimplified_clause: {simplifiedClauses}")

    variable = abs(simplifiedClauses[0][0])

##    print(f"{indent}\tSet Assignment Var {variable} to True")
    assignmentCopy = dict(assignment)
    assignmentCopy[variable] = True
    (result, iterations) = dpll(simplifiedClauses, assignmentCopy, depth + 1)
    
    if result == False:
##        print(f"{indent}\tSet Assignment Var {variable} to False")
        assignmentCopy = dict(assignment)
        assignmentCopy[variable] = False
        (result, iterations) = dpll(simplifiedClauses, assignmentCopy, depth + 1)
        if result:
            return (result, dpll.total_iterations)
        else:
            return (False, dpll.total_iterations)
    else:
        return (result, dpll.total_iterations)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python basic_sat.py *.cnf")
        sys.exit(1)

    cnf_files = sys.argv[1:]

    if not cnf_files:
        print("No CNF files provided.")
        sys.exit(1)

    for cnf_file in cnf_files:
        print(f"--- Solving {cnf_file} ---")
        try:
            clauses = parse_dimacs_file(cnf_file)
        except Exception as e:
            print(f"Failed to parse {cnf_file}: {e}")
            continue  # Skip broken files

        start_time = time.time()

        solution = dpll(clauses, {}, 0)

        end_time = time.time()
        difference = end_time - start_time

        if solution:
            print("SAT")
            print("Assignment:", solution)
        else:
            print("UNSAT")

        successful_files += 1
        total_time += difference

    print(f"Time difference: {total_time:.4f} seconds\n")
    print(f"Average iter_count over {total_iterations} successful files: {successful_files:.2f}")
