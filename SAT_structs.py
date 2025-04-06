from typing import *
# import typing

class CNF_Literal: 
    def __init__(self, var_idx: int, sign: bool):
        self.var_idx = var_idx
        self.sign = sign

    def __str__(self):
        if (self.sign):
            return f"x{self.var_idx}"
        else:
            return f"x{self.var_idx}\'"
 

class CNF_Clause: 
    def __init__(self, literals: List[CNF_Literal]):
        self.literals = literals
        self.literals.sort(key=lambda x: x.var_idx)

    def __str__(self):
        return f"({' + '.join(map(str, self.literals))})"


class CNF_Formula: 
    def __init__(self, clauses: List[CNF_Clause], num_vars: int = 0):
        self.clauses = clauses

        # Set num vars
        if (num_vars == 0):
            for clause in clauses:
                for literal in clause.literals:
                    if literal.var_idx > num_vars:
                        self.num_vars = literal.var_idx
        else:
            self.num_vars = num_vars

        # Initialize appearance lists
        self.appears_pos = [False] * (self.num_vars + 1)
        self.appears_neg = [False] * (self.num_vars + 1)
        self.appearance_cnt = [0] * (self.num_vars + 1)

        # Note if variable appears in positive or negative form
        for clause in clauses:
            for literal in clause.literals:
                self.appearance_cnt[literal.var_idx] += 1

                if literal.sign:
                    self.appears_pos[literal.var_idx] = True
                else:
                    self.appears_neg[literal.var_idx] = True

    def __str__(self):
        return f"".join(map(str,self.clauses))
    
    @staticmethod
    def from_dimacs_file(file_path: str) -> 'CNF_Formula':
        # Read the CNF file
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        clauses = []
        literals = []
        num_vars = 0

        # Parse the CNF file
        for line in lines:
            line = line.strip()

            # Skip metadata
            if line.startswith('c'):
                continue
            elif line.startswith('p'):
               num_vars = int(line.split()[2])
               continue

            # Loop through literals 
            for lit in line.split():
                lit = int(lit)

                # If end of clause
                if lit == 0:
                    clauses.append(CNF_Clause(literals))    # Create new cluase from literal list
                    literals = []                           # Reset literal list  
                    break

                sign = lit > 0
                literals.append(CNF_Literal(abs(lit), sign))

        return CNF_Formula(clauses, num_vars)