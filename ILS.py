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
                if solution_occupancy[d] + int(
                        family.n_people) <= Parameters.initial_solution_fill_factor * Data.max_people:
                    representation[d].append(family.id)
                    solution_occupancy[d] += int(family.n_people)
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

    def create_exact_solution(self):
        representation = list()
        solution_occupancy = list()
        for current_day in range(Data.n_days):
            day = list()
            day_occupancy = 0
            representation.append(day)
            solution_occupancy.append(day_occupancy)
        for family in self.family_list:
            day = family.choice[0]
            representation[day].append(family.id)
            solution_occupancy[day] += int(family.n_people)
        for current_day in range(Data.n_days):
            while solution_occupancy[current_day] > Data.max_people:
                family_id = representation[current_day][0]
                family_is_assigned = False
                choice_list = self.family_list[family_id].choice
                family_members = self.family_list[family_id].n_people
                for j in range(1, len(choice_list), 1):
                    alternative_day = choice_list[j]
                    if solution_occupancy[alternative_day] + int(family_members) <= Data.max_people:
                        representation[current_day].pop(0)
                        representation[alternative_day].append(family_id)
                        solution_occupancy[current_day] -= int(family_members)
                        solution_occupancy[alternative_day] += int(family_members)
                        family_is_assigned = True
                        break
                if family_is_assigned:
                    continue
                else:
                    for another_day in range(Data.n_days):
                        if another_day not in choice_list and \
                                solution_occupancy[another_day] + int(family_members) <= Data.max_people:
                            representation[current_day].pop(0)
                            representation[another_day].append(family_id)
                            solution_occupancy[another_day] -= int(family_members)
                            solution_occupancy[another_day] += int(family_members)
                            break
        for current_day in range(Data.n_days):
            while solution_occupancy[current_day] > self.average_people_per_day:
                if current_day < len(representation[current_day]):
                    family_id = representation[current_day][0]
                    family_is_assigned = False
                    choice_list = self.family_list[family_id].choice
                    family_members = self.family_list[family_id].n_people
                    for j in range(1, len(choice_list), 1):
                        alternative_day = choice_list[j]
                        if solution_occupancy[alternative_day] < Data.min_people:
                            representation[current_day].pop(0)
                            representation[alternative_day].append(family_id)
                            solution_occupancy[current_day] -= int(family_members)
                            solution_occupancy[alternative_day] += int(family_members)
                            family_is_assigned = True
                            break
                    if family_is_assigned:
                        continue
                    else:
                        for another_day in range(Data.n_days):
                            if another_day not in choice_list and \
                                    solution_occupancy[another_day] < self.average_people_per_day:
                                representation[current_day].pop(0)
                                representation[another_day].append(family_id)
                                solution_occupancy[another_day] -= int(family_members)
                                solution_occupancy[another_day] += int(family_members)
                                break
                else:
                    break
        pref_cost = Evaluation.get_preference_cost(representation, self.family_list, self.family_choices)
        acc_penalty = Evaluation.get_accounting_penalty(solution_occupancy)
        result = Solution.Solution(representation, solution_occupancy, pref_cost, acc_penalty)
        self.print_solution(result)
        return result

    def print_solution(self, solution: Solution):
        for i in range(Data.n_days):
            print('{:5s}'.format(str(i + 1)), end="")
        print()
        for i in solution.occupancy:
            print('{:5s}'.format(str(i)), end="")
        s = 0
        print()
        for i in range(len(solution.representation)):
            s += len(solution.representation[i])
            print('{:5s}'.format(str(len(solution.representation[i]))), end="")
        print()
        print("pref_cost: " + str(solution.preference_cost))
        print("acc_penalty: " + str(solution.accounting_penalty))
        print("Evaluation: " + str(solution.evaluation))

    def select_top_min(self, occupancy):
        min_load_days = list()
        i = 0
        while i < len(occupancy) and len(min_load_days) < Parameters.selection_threshold:
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
            max_family_penalty = max_preference[0] + int(self.family_list[max_family_id].n_people) \
                                 * (max_preference[1] + max_preference[2])
            max_penalty_index = i
            for j in range(i + 1, len(day_family_list), 1):
                family_id = day_family_list[j]
                preference = Data.preference_cost[family_choices[family_id][remove_day]]
                family_penalty = preference[0] + int(self.family_list[family_id].n_people) \
                                 * (preference[1] + preference[2])
                if family_penalty > max_family_penalty:
                    max_family_penalty = family_penalty
                    max_penalty_index = j
            if max_penalty_index not in max_list:
                max_list.append(max_penalty_index)
            i = i + 1
        return max_list

    def max_difference(self, a, b, c):
        return max(abs(a - b), abs(a - c), abs(b - c))

    def select_top_disbalancing_days(self, occupancy):
        top_list = list()
        i = 0
        while i < len(occupancy) and len(top_list) < Parameters.selection_threshold:
            if i != 0 and i != Data.n_days - 1:
                max_load_difference = self.max_difference(occupancy[i - 1], occupancy[i], occupancy[i + 1])
            elif i == Data.n_days - 1:
                max_load_difference = abs(occupancy[i - 1] - occupancy[i])
            else:
                max_load_difference = abs(occupancy[i] - occupancy[i + 1])
            max_load_index = i
            for j in range(i + 1, Data.n_days, 1):
                if j != Data.n_days - 1:
                    load_difference = self.max_difference(occupancy[j - 1], occupancy[j], occupancy[j + 1])
                else:
                    load_difference = abs(occupancy[j - 1] - occupancy[j])
                if load_difference > max_load_difference:
                    max_load_difference = load_difference
                    max_load_index = j
            if max_load_index not in top_list:
                top_list.append(max_load_index)
            i = i + 1
        return top_list

    def select_top_balancing_days(self, occupancy):
        top_list = list()
        i = 0
        while i < len(occupancy) and len(top_list) < Parameters.selection_threshold:
            if i != 0 and i != Data.n_days - 1:
                min_load_difference = self.max_difference(occupancy[i - 1], occupancy[i], occupancy[i + 1])
            elif i == Data.n_days - 1:
                min_load_difference = abs(occupancy[i - 1] - occupancy[i])
            else:
                min_load_difference = abs(occupancy[i] - occupancy[i + 1])
            min_load_index = i
            for j in range(i + 1, Data.n_days, 1):
                if j != Data.n_days - 1:
                    load_difference = self.max_difference(occupancy[j - 1], occupancy[j], occupancy[j + 1])
                else:
                    load_difference = abs(occupancy[j - 1] - occupancy[j])
                if load_difference < min_load_difference:
                    min_load_difference = load_difference
                    min_load_index = j
            if min_load_index not in top_list:
                top_list.append(min_load_index)
            i = i + 1
        return top_list

    def change(self, s: Solution):
        representation = deepcopy(s.representation)
        occupancy = deepcopy(s.occupancy)
        change_applied = False
        for i in range(Parameters.change_intensity):
            # max_load_days = self.select_top_max(occupancy)
            # remove_day = max_load_days[random.randrange(0, len(max_load_days))]
            min_load_days = self.select_top_min(occupancy)
            # max_load_differences = self.select_top_disbalancing_days(s.occupancy)
            # min_load_differences = self.select_top_balancing_days(occupancy)
            remove_day, insert_day = random.sample(range(0, Data.n_days), k=2)
            # remove_day = max_load_differences[random.randrange(0, len(max_load_differences))]
            # insert_day = min_load_differences[random.randrange(0, len(min_load_differences))]
            # insert_day = min_load_days[random.randrange(0, len(min_load_days))]
            max_preference_families = self.select_top_max_preference_families(representation[remove_day], \
                                                                              self.family_choices, remove_day)
            # change_family_index = random.randrange(0, len(representation[remove_day]))
            change_family_index = max_preference_families[random.randrange(0, len(max_preference_families))]
            family_id = representation[remove_day][change_family_index]
            day_load_change = int(self.family_list[family_id].n_people)
            is_origin_feasible = occupancy[remove_day] - day_load_change >= Data.min_people
            is_destination_feasible = occupancy[insert_day] + day_load_change <= Data.max_people
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

    def swap_families(self, s: Solution):
        representation = deepcopy(s.representation)
        occupancy = deepcopy(s.occupancy)
        change_applied = False
        for i in range(Parameters.change_intensity):
            first_day, second_day = random.sample(range(0, Data.n_days), k=2)
            # remove_day = max_load_differences[random.randrange(0, len(max_load_differences))]
            # insert_day = min_load_differences[random.randrange(0, len(min_load_differences))]
            # insert_day = min_load_days[random.randrange(0, len(min_load_days))]
            # max_preference_families = self.select_top_max_preference_families(s.representation[first_day], \
            #                                                                   self.family_choices, first_day)
            first_family_index = random.randrange(0, len(representation[first_day]))
            second_family_index = random.randrange(0, len(representation[second_day]))
            # change_family_index = max_preference_families[random.randrange(0, len(max_preference_families))]
            first_family_id = representation[first_day][first_family_index]
            second_family_id = representation[second_day][second_family_index]
            first_day_load_change = int(self.family_list[first_family_id].n_people)
            second_day_load_change = int(self.family_list[second_family_id].n_people)
            first_day_foreseen_load = occupancy[first_day] - first_day_load_change + second_day_load_change
            is_first_feasible = (first_day_foreseen_load >= Data.min_people) and \
                                (first_day_foreseen_load <= Data.max_people)
            second_day_foreseen_load = occupancy[second_day] - second_day_load_change + first_day_load_change
            is_second_feasible = (second_day_foreseen_load <= Data.max_people) and \
                                 (second_day_foreseen_load >= Data.min_people)
            if is_first_feasible and is_second_feasible:
                representation[first_day].pop(first_family_index)
                representation[second_day].append(first_family_id)
                representation[second_day].pop(second_family_index)
                representation[first_day].append(second_family_id)
                occupancy[first_day] = first_day_foreseen_load
                occupancy[second_day] = second_day_foreseen_load
                change_applied = True
        preference_cost = Evaluation.get_preference_cost(representation, \
                                                         self.family_list, self.family_choices)
        accounting_penalty = Evaluation.get_accounting_penalty(occupancy)
        r = Solution.Solution(representation, occupancy, preference_cost, accounting_penalty)
        return r

    def swap_days(self, representation, occupancy):
        remove_day, insert_day = random.sample(range(0, Data.n_days), k=2)
        temp = list(representation[remove_day])
        representation[remove_day] = list(representation[insert_day])
        representation[insert_day] = list(temp)
        temp_occupancy = occupancy[remove_day]
        occupancy[remove_day] = occupancy[insert_day]
        occupancy[insert_day] = temp_occupancy
        preference_cost = Evaluation.get_preference_cost(representation, self.family_list, self.family_choices)
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
            local_search_time = Parameters.T[random.randrange(0, len(Parameters.T))]
            j = 1
            while j <= local_search_time:
                if i % 5 == 0:
                    r = self.swap_families(current)
                else:
                    r = self.change(current)
                is_acceptable = r.accounting_penalty <= current.accounting_penalty or \
                                r.evaluation <= current.evaluation or \
                                random.randrange(0, 100) < Parameters.acceptance_chance
                if is_acceptable:
                    current = Solution.copy(r)
                j += 1
            print("Current solution: " + str(current.evaluation))
            if current.evaluation < best.evaluation:
                best = Solution.copy(current)
            else:
                iterations_without_improvment += 1
            if current.evaluation <= home.evaluation:
                home = Solution.copy(current)
            if iterations_without_improvment == 50:
                home = self.swap_families(home)
            current = Solution.copy(home)
            i += 1
            if i % Parameters.save_to_file_frequency == 0 or i == 2:
                print("Writing best solution " + str(round(best.evaluation, 2)) + " to file...")
                # Data.write_family_data(best, self.seed_millis)
        self.print_solution(best)
        Evaluation.get_preference_cost(best.representation, self.family_list, self.family_choices)
        return best


def main():
    ils = ILS()
    ils.ils_algorithm()
    # ils.create_exact_solution()


main()
