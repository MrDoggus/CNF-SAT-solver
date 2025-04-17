from typing import *
from enum import Enum
import bisect
# import typing

class CNF_IsSAT(Enum):
    UNSAT = 0
    SAT = 1
    UNRESOLVED = 2

class CNF_Literal: 
    def __init__(self, var_idx: int, sign: bool):
        self.var_idx: int = var_idx  # Variable index
        self.sign: bool = sign        # If false, variable is inverted

    def __str__(self):
        if (self.sign):
            return f"x{self.var_idx}"
        else:
            return f"x{self.var_idx}\'"
 

class CNF_Clause: 
    def __init__(self, literals: List[CNF_Literal], isConflict = False):
        self.literals: List[CNF_Literal] = literals    # List of literals
        self.literals.sort(key=lambda x: x.var_idx)

        # self.lit_assigns: List[bool] = [None] * len(self.literals)
        
        self.sat: CNF_IsSAT = CNF_IsSAT.UNRESOLVED
        self.isConflict = isConflict

    # Given var assignment, determine if clause is SAT, UNSAT, or Unresolved
    # Sets and returns satisfiability 
    def eval(self, assigns: List[bool]) -> CNF_IsSAT: 
        
        hasUnresolved = False
        for lit in self.literals: 

            if (assigns[lit.var_idx] is None): 
                hasUnresolved = True
            elif (assigns[lit.var_idx] == lit.sign):
                self.sat = CNF_IsSAT.SAT
                return CNF_IsSAT.SAT

        # Since SAT literal was not found, if clause has unresolved literal, clause is unresolbed
        if (hasUnresolved): 
            self.sat = CNF_IsSAT.UNRESOLVED
            return CNF_IsSAT.UNRESOLVED
        else: 
            self.sat = CNF_IsSAT.UNSAT
            return CNF_IsSAT.UNSAT
            
    def __str__(self):
        return f"({' + '.join(map(str, self.literals))})"


class CNF_Formula:
    def __init__(self, clauses: List[CNF_Clause], num_vars: int = 0):
        self.clauses: List[CNF_Clause] = clauses  # List of clauses
        self.clauses.sort(key=lambda x: len(x.literals))

        self.max_conflict_size = len(self.clauses[-1].literals) ** 2

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

    # Given assignment list, determine if clause is SAT, UNSAT, or Unresolved
    def eval(self, assigns: List[bool], deep: bool = False) -> Tuple[CNF_IsSAT, int]:
        foundUnresolved: bool = False
        
        for c, clause in enumerate(self.clauses):
            # if clause is sat and we arent doing a deep eval, skip clause
            if (not deep and clause.sat == CNF_IsSAT.SAT):
                continue

            # Evaluate clause
            ceval = clause.eval(assigns)

            # If one clause is unsat, formula will never be sat or unresolved
            if (ceval == CNF_IsSAT.UNSAT):
                return (CNF_IsSAT.UNSAT, c)
            # Formula cant be sat if clause is unresolved
            elif (ceval == CNF_IsSAT.UNRESOLVED):
                foundUnresolved = True

        if (foundUnresolved):
            return (CNF_IsSAT.UNRESOLVED, None)
        else: 
            return (CNF_IsSAT.SAT, None)
    
    # Given two clauses that resulted in an UNSAT, generates a new conflict clause
    def add_conflict_clause(self, cidx1: int, cidx2: int, pivot: int):
        lit_list: List[CNF_Literal] = []
        for lit in self.clauses[cidx1].literals:
            if (lit.var_idx != pivot):
                lit_list.append(lit)
        for lit in self.clauses[cidx2].literals:
            skip = False
            # Ignore duplicates and pivot variable
            for l in lit_list:
                if (lit.var_idx == l.var_idx):
                    skip = True
                    break
            if (lit.var_idx != pivot and not skip):
                lit_list.append(lit)     
        
        c = CNF_Clause(lit_list)
        
        if (len(c.literals) <= self.max_conflict_size):
            # print(f"Conflict clause added: {c.__str__()}")
            bisect.insort(self.clauses, c, key=lambda x: len(x.literals))


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
    
    def __str__(self):
        return f"".join(map(str,self.clauses))