from typing import *
from SAT_structs import *

# Represents a node in the SAT problem tree
class SAT_node: 
    def __init__(self, assign: Tuple[int, bool], parents: List['SAT_node']):

        # Assignment that resulted in a branch to this node
        self.assign: Tuple[int, bool] = assign

        # Variable that is assigned by left/right children 
        self.next_var: int = 0

        # List of ancestors/parents
        if (parents is None): 
            self.parents: List[SAT_node] = []
        else:
            self.parents: List[SAT_node] = parents.copy()


        self.isUnsat: bool = False  # True if this all children of this node  (or the node itself) are UNSAT
        self.unsatCIdx: int = None  # If the variable assignment at this location resulted in UNSAT, stores clause that resulted in UNSAT
        
        # Node children
        self.choice_true: SAT_node = None
        self.choice_false: SAT_node = None
    
    # Generates an assignment list from the parent list. 
    # Assignment list is indexed by the var number
    def assign_list(self, num_vars) -> List[bool]: 
        assignl = [None] * (num_vars + 1)

        for i in self.parents:
            if (i is not None and i.assign is not None):
                assignl[i.assign[0]] = i.assign[1]

        if (self.assign is not None):
            assignl[self.assign[0]] = self.assign[1]

        return assignl
    
    # Stores list of integers that represent a variables assignment.
    # If a number is negitive, this represents a 0 assignment 
    def assign_list_condensed(self) -> List[int]:
        assignl = []

        for i in self.parents:
            if (i is not None and i.assign is not None):
                assignl.append(i.assign[0] if i.assign[1] else -i.assign[0])

        if (self.assign is not None):
            assignl.append(self.assign[0] if self.assign[1] else -self.assign[0])

        return assignl

class SAT_solver: 

    def __init__(self, formula: CNF_Formula, log = False):
        self.formula:CNF_Formula = formula
        self.log = log
        self.iter_count = 0
        
        # self.isSAT = None

    # Solves SAT problem
    # Returns assignList if SAT, None if unsat
    def solve(self) -> List[bool]:

        # Create head
        head = SAT_node(assign = None, parents = [])
        curr = head
        backtracked = False
        self.iter_count = 0

        while (True):
            self.iter_count += 1

            assigns = curr.assign_list(self.formula.num_vars)
            sat, curr.unsatCIdx = self.formula.eval(assigns, backtracked)

            backtracked = False

            if (self.log):
                print(f"var: {curr.next_var}, sat: {sat}, assigns: {curr.assign_list_condensed()}")

            # If formula is SAT, return assigns to indicate 
            if (sat == CNF_IsSAT.SAT):
                return assigns
            
            # If unresolved, choose new branch to explore
            elif (sat == CNF_IsSAT.UNRESOLVED):
                # If next var hasnt been choosen for this node, choose a next var
                if (curr.next_var == 0): 
                    choice = SAT_solver.decider_iter.choice(self.formula, assigns)
                    if (choice[0] != 0):
                        curr.next_var = choice[0]
                    else: 
                        print("ERROR: Assigned all literals but still unresolved?")
                        exit(1)

                    # choose pos or neg branch
                    if (choice[1]):
                        if (self.log):
                            print(f"First branch {curr.next_var}")
                        curr.choice_true = SAT_node(choice, parents=curr.parents + [curr])
                        curr = curr.choice_true
                    else:
                        if (self.log):
                            print(f"First branch -{curr.next_var}")
                        curr.choice_false = SAT_node(choice, parents=curr.parents + [curr])
                        curr = curr.choice_false

                # Since one path was expored already, try the other path
                elif(curr.choice_true is None):
                    if (self.log):
                        print(f"Exploring unexplored {curr.next_var}")
                    curr.choice_true = SAT_node((curr.next_var, True), parents=curr.parents + [curr])
                    curr = curr.choice_true
                elif(curr.choice_false is None):
                    if (self.log):
                        print(f"Exploring unexplored -{curr.next_var}")
                    curr.choice_false = SAT_node((curr.next_var, False), parents=curr.parents + [curr])
                    curr = curr.choice_false

                # Since both paths were explored, find path that is only partially explored
                elif (not curr.choice_true.isUnsat):
                    if (self.log):
                        print(f"Exploring partially explored {curr.next_var}")
                    curr = curr.choice_true
                elif (not curr.choice_false.isUnsat):
                    if (self.log):
                        print(f"Exploring partially explored -{curr.next_var}")
                    curr = curr.choice_false

                # All branches fully explored, backtrack one step
                else: 
                    if (self.log):
                        print("All branches explored, attempting backtrack")
                    curr.isUnsat = True
                    if (len(curr.parents) != 0):
                        # Generate conflict clause if possible
                        if (curr.choice_true.unsatCIdx is not None and curr.choice_false.unsatCIdx is not None):
                            self.formula.add_conflict_clause(curr.choice_true.unsatCIdx, curr.choice_false.unsatCIdx, curr.next_var)
                        curr = curr.parents[-1]
                        backtracked = True
                    else: # We are at the head, so formula is UNSAT
                        return None

                
            # If UNSAT, backtrack
            else:
                curr.isUnsat = True
                curr = curr.parents[-1]
                backtracked = True
                if (self.log):
                    print("Backtracking due to UNSAT")

    # Simple variable decider
    class decider_iter:

        @staticmethod
        def choice(formula: CNF_Formula, assigns: List[bool]) -> Tuple[int, bool]:
            
            # Find unresolved clause
            for i, clause in enumerate(formula.clauses):
                if clause.sat == CNF_IsSAT.SAT: 
                    continue

                # Find unassigned literal in clause
                for j, lit in enumerate(clause.literals):
                    if (assigns[lit.var_idx] is None):
                        return (lit.var_idx, lit.sign)
                    
            # Couldnt find unassigned literal
            return (0, None)