import random

import Data
import Parameters


class ILS:
    def __init__(self):
        self.family_list = Data.read_family_data()
        self.family_choices = Data.get_family_choice(self.family_list)
        self.total_people = self.get_total_people()
        self.average_people_per_day = self.total_people / Data.n_days

    def get_total_people(self):
        s = 0
        for i in self.family_list:
            s += int(i.n_people);
        return s

    def create_initial_solution(self):
        family_index_in_order = list()
        for i in range(len(self.family_list)):
            family_index_in_order.append(i)
        family_index_random_order = list()
        for i in range(len(self.family_list)):
            random_index = random.randrange(0, len(family_index_in_order))
            family_index_random_order.append(family_index_in_order[random_index])
            family_index_in_order.pop(random_index)
        solution = list()
        solution_occupancy = list()
        for i in range(Data.n_days):
            day = list()
            day_occupancy = 0
            while day_occupancy <= Parameters.average_percentage_day_people * self.average_people_per_day:
                random_index = random.randrange(0, len(family_index_random_order))
                family_id = family_index_random_order[random_index]
                family_n_people = int(self.family_list[family_id].n_people)
                day_occupancy += family_n_people
                day.append(family_id)
                family_index_random_order.pop(random_index)
            solution.append(day)
            solution_occupancy.append(day_occupancy)
        return solution, solution_occupancy

    def accounting_penalty(self, solution_occupancy):
        p = 0
        for i in range(len(solution_occupancy) - 1):
            occupancy_current = solution_occupancy[i]
            occupancy_next = solution_occupancy[i + 1]
            p = p + ((occupancy_current - 125) / 400.0) * occupancy_current ** (
                    1 / 2 + (abs(occupancy_current - occupancy_next) / 50.0))
        last_occupancy = solution_occupancy[len(solution_occupancy) - 1]
        p += ((last_occupancy - 125) / 400.0) * last_occupancy ** (1 / 2.0)
        return p

    def preference_cost(self, solution):
        penalty = 0
        for d in range(len(solution)):
            day = solution[d]
            for f in day:
                pc = Data.preference_cost[self.family_choices[f][d]]
                print("Test")

    def ils_algorithm(self):
        s, so = self.create_initial_solution()
        self.accounting_penalty(so)
        self.preference_cost(s)
        h = list(s)
        best = list(s)
        best[0] = [-1]
        i = 1
        while i <= Parameters.total_time:
            time = Parameters.T[random.randrange(0, len(Parameters.T))]
            pass


def main():
    ils = ILS()
    ils.ils_algorithm()
    print("Test")


main()
