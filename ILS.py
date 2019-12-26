import random
import time
from copy import deepcopy

import Data
import Evaluation
import Parameters
import Solution


class ILS:
    def __init__(self):
        self.family_list = Data.read_family_data()
        self.family_choices = Data.get_family_choice(self.family_list)
        self.total_people = self.get_total_people()
        self.average_people_per_day = self.total_people / Data.n_days
        self.seed_millis = int(round(time.time() * 1000))
        random.seed(self.seed_millis)
        self.shuffled_days = list(range(1, 101))
        random.shuffle(self.shuffled_days)

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
        representation = list()
        solution_occupancy = list()
        for i in range(Data.n_days):
            day = list()
            day_occupancy = 0
            representation.append(day)
            solution_occupancy.append(day_occupancy)
        while len(family_index_random_order) > 0:
            f = family_index_random_order[0]
            family = self.family_list[f]
            family_assigned = False
            for d in family.choice:
                if solution_occupancy[d - 1] + int(
                        family.n_people) <= Parameters.initial_solution_fill_factor * Data.max_people:
                    representation[d - 1].append(family.id)
                    solution_occupancy[d - 1] += int(family.n_people)
                    family_index_random_order.pop(0)
                    family_assigned = True
                    break
            if not family_assigned:
                for d in self.shuffled_days:
                    is_valid_assignment = (solution_occupancy[d - 1] + int(
                        family.n_people) <= Data.max_people) and (solution_occupancy[d - 1] + int(
                        family.n_people) >= Data.min_people)
                    if is_valid_assignment:
                        representation[d - 1].append(family.id)
                        solution_occupancy[d - 1] += int(family.n_people)
                        family_index_random_order.pop(0)
                        break
        pref_cost = Evaluation.get_preference_cost(representation, self.family_list, self.family_choices)
        acc_penalty = Evaluation.get_accounting_penalty(solution_occupancy)
        result = Solution.Solution(representation, solution_occupancy, pref_cost, acc_penalty)
        return result

    def select_top_min(self, occupancy):
        min_load_days = list()
        i = 0
        while i < len(occupancy)and len(min_load_days) < Parameters.selection_threshold:
            min_day_load = occupancy[i]
            min_day_index = i
            for j in range(i + 1, Data.n_days, 1):
                if occupancy[j] < min_day_load:
                    min_day_load = occupancy[j]
                    min_day_index = j
            if min_day_index not in min_load_days:
                min_load_days.append(min_day_index)
            i = i + 1
        return min_load_days

    def select_top_max(self, occupancy):
        max_load_days = list()
        i = 0
        while i < len(occupancy) and len(max_load_days) < Parameters.selection_threshold:
            max_day_load = occupancy[i]
            max_day_index = i
            for j in range(i + 1, Data.n_days, 1):
                if occupancy[j] > max_day_load:
                    max_day_load = occupancy[j]
                    max_day_index = j
            if max_day_index not in max_load_days:
                max_load_days.append(max_day_index)
            i = i + 1
        return max_load_days

    def select_top_max_preference_families(self, day_family_list, family_choices, remove_day):
        max_list = list()
        i = 0
        while i < len(day_family_list) and len(max_list) < Parameters.selection_threshold:
            max_family_id = day_family_list[i]
            max_preference = Data.preference_cost[family_choices[max_family_id][remove_day]]
            max_preference_index = i
            for j in range(i + 1, len(day_family_list), 1):
                family_id = day_family_list[j]
                preference = Data.preference_cost[family_choices[family_id][remove_day]]
                if preference > max_preference:
                    max_preference = preference
                    max_preference_index = j
            if max_preference_index not in max_list:
                max_list.append(max_preference_index)
            i = i + 1
        return max_list

    def change(self, s: Solution):
        representation = deepcopy(s.representation)
        occupancy = deepcopy(s.occupancy)
        change_applied = False
        while not change_applied:
            min_load_days = self.select_top_min(s.occupancy)
            max_load_days = self.select_top_max(s.occupancy)
            # remove_day, insert_day = random.sample(range(0, Data.n_days), k=2)
            remove_day = max_load_days[random.randrange(0, len(max_load_days))]
            insert_day = min_load_days[random.randrange(0, len(min_load_days))]
            max_preference_families = self.select_top_max_preference_families(s.representation[remove_day], \
                                                                              self.family_choices, remove_day)
            # change_family_index = random.randrange(0, len(representation[remove_day]))
            change_family_index = max_preference_families[random.randrange(0, len(max_preference_families))]
            family_id = representation[remove_day][change_family_index]
            day_load_change = int(self.family_list[family_id].n_people)
            is_origin_feasible = occupancy[remove_day] - day_load_change >= Data.min_people
            is_destination_feasible = occupancy[insert_day] + int(
                self.family_list[family_id].n_people) <= Data.max_people
            if is_origin_feasible and is_destination_feasible:
                representation[remove_day].pop(change_family_index)
                representation[insert_day].append(family_id)
                occupancy[remove_day] -= day_load_change
                occupancy[insert_day] += day_load_change
                change_applied = True
                preference_cost = Evaluation.get_preference_cost(representation, \
                                                                 self.family_list, self.family_choices)
                accounting_penalty = Evaluation.get_accounting_penalty(occupancy)
                r = Solution.Solution(representation, occupancy, preference_cost, accounting_penalty)
        return r

    def ils_algorithm(self):
        init_sol = int(input("What type of initial solution (0-random, 1-from file): "))
        if init_sol == 0:
            current: Solution = self.create_initial_solution()
        else:
            current: Solution = Data.load_solution_from_file(self.family_list, self.family_choices)
        home: Solution = Solution.copy(current)
        best: Solution = Solution.copy(current)
        i = 1
        iterations_without_improvment = 0
        home_base_current = False
        while Parameters.nonstop_run or i <= Parameters.total_time:
            time = Parameters.T[random.randrange(0, len(Parameters.T))]
            j = 1
            while j <= time:
                r = self.change(current)
                if r.evaluation <= current.evaluation:
                    current = Solution.copy(r)
                j += 1
            if current.evaluation < best.evaluation:
                best = Solution.copy(current)
            if current.evaluation <= home.evaluation:
                home = Solution.copy(current)
            for p in range(Parameters.perturb_iterations):
                home = Solution.copy(home)
            current = Solution.copy(home)
            i += 1
            if i % 30 == 0 or i == 2:
                print("Changed solution: " + str(r.evaluation))
                print("Writing best solution " + str(round(best.evaluation, 2)) + " to file...")
                Data.write_family_data(best, self.seed_millis)
        return best


def main():
    ils = ILS()
    ils.ils_algorithm()


main()
