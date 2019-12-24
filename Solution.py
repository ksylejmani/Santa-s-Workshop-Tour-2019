from copy import deepcopy
class Solution:
    def __init__(self, r, o, pc, ap):
        self.representation = r
        self.occupancy = o
        self.preference_cost = pc
        self.accounting_penalty = ap
        self.evaluation = self.preference_cost + self.accounting_penalty


def copy(s):
    new_copy: Solution = Solution(
        deepcopy(s.representation),
        deepcopy(s.occupancy),
        s.preference_cost,
        s.accounting_penalty)
    new_copy.evaluation = s.preference_cost + s.accounting_penalty
    return new_copy
