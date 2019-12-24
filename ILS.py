import random
from copy import deepcopy

import Data
import Parameters
import Solution


class ILS:
    def __init__(self):
        self.family_list = Data.read_family_data()
        self.family_choices = Data.get_family_choice(self.family_list)
        self.total_people = self.get_total_people()
        self.average_people_per_day = self.total_people / Data.n_days
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
        solution = list()
        solution_occupancy = list()
        for i in range(Data.n_days):
            day = list()
            day_occupancy = 0
            solution.append(day)
            solution_occupancy.append(day_occupancy)
        while len(family_index_random_order) > 0:
            f = family_index_random_order[0]
            family = self.family_list[f]
            family_assigned = False
            for d in family.choice:
                if solution_occupancy[d - 1] + int(
                        family.n_people) <= Parameters.initial_solution_fill_factor * Data.max_people:
                    solution[d - 1].append(family.id)
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
                        solution[d - 1].append(family.id)
                        solution_occupancy[d - 1] += int(family.n_people)
                        family_index_random_order.pop(0)
                        break
        pref_cost = self.preference_cost(solution)
        acc_penalty = self.accounting_penalty(solution_occupancy)
        result = Solution.Solution(solution, solution_occupancy, pref_cost, acc_penalty)
        return result

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

    def accounting_penalty_delta(self, solution_occupancy, e, remove_day, insert_day):
        p = e
        occupancy_current_remove_day = solution_occupancy[remove_day]
        occupancy_current_insert_day = solution_occupancy[insert_day]
        if remove_day == 0 and insert_day != Data.n_days - 1:
            occupancy_next_remove_day = solution_occupancy[remove_day + 1]
            occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
            occupancy_next_insert_day = solution_occupancy[insert_day + 1]
        elif remove_day == 0 and insert_day == Data.n_days:
            occupancy_next_remove_day = solution_occupancy[remove_day + 1]
            occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
            occupancy_next_insert_day = occupancy_current_insert_day
        elif remove_day != Data.n_days - 1 and insert_day == 0:
            occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
            occupancy_next_remove_day = solution_occupancy[remove_day + 1]
            occupancy_next_insert_day = solution_occupancy[insert_day+1]
        elif remove_day == Data.n_days - 1 and insert_day == 0:
            occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
            occupancy_next_remove_day = occupancy_current_remove_day
            occupancy_next_insert_day = solution_occupancy[insert_day+1]
        elif remove_day == Data.n_days - 1 and insert_day != Data.n_days-1:
            occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
            occupancy_next_remove_day = occupancy_current_remove_day
            occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
            occupancy_next_insert_day = solution_occupancy[insert_day+1]
        elif remove_day != Data.n_days - 1 and insert_day == Data.n_days-1:
            occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
            occupancy_next_remove_day = solution_occupancy[remove_day+1]
            occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
            occupancy_next_insert_day = occupancy_current_insert_day
        elif remove_day != Data.n_days - 1 and insert_day != Data.n_days - 1:
            occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
            occupancy_next_remove_day = solution_occupancy[remove_day + 1]
            occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
            occupancy_next_insert_day = solution_occupancy[insert_day+1]

        occupancy_next_remove_day = solution_occupancy[remove_day + 1]
        pa_rd = ((occupancy_current_remove_day - 125) / 400.0) * occupancy_current_remove_day ** (
                1 / 2 + (abs(occupancy_current_remove_day - occupancy_next_remove_day) / 50.0))
        occupancy_next_insert_day = solution_occupancy[insert_day + 1]
        pa_id = ((occupancy_current_insert_day - 125) / 400.0) * occupancy_current_insert_day ** (
                1 / 2 + (abs(occupancy_current_insert_day - occupancy_next_insert_day) / 50.0))
        last_occupancy_remove_day = solution_occupancy[remove_day]
        pa_rd = ((last_occupancy_remove_day - 125) / 400.0) * last_occupancy_remove_day ** (1 / 2.0)
        occupancy_next_insert_day = solution_occupancy[insert_day + 1]
        pa_id = ((occupancy_current_insert_day - 125) / 400.0) * occupancy_current_insert_day ** (
                1 / 2 + (abs(occupancy_current_insert_day - occupancy_next_insert_day) / 50.0))

        occupancy_current_remove_day = solution_occupancy[remove_day]
        occupancy_next_remove_day = solution_occupancy[remove_day + 1]
        pa_rd = ((occupancy_current_remove_day - 125) / 400.0) * occupancy_current_remove_day ** (
                1 / 2 + (abs(occupancy_current_remove_day - occupancy_next_remove_day) / 50.0))
        last_occupancy_insert_day = solution_occupancy[insert_day]
        pa_id = ((last_occupancy_insert_day - 125) / 400.0) * last_occupancy_insert_day ** (1 / 2.0)

        last_occupancy_remove_day = solution_occupancy[remove_day]
        pa_rd = ((last_occupancy_remove_day - 125) / 400.0) * last_occupancy_remove_day ** (1 / 2.0)
        last_occupancy_insert_day = solution_occupancy[insert_day]
        pa_id = ((last_occupancy_insert_day - 125) / 400.0) * last_occupancy_insert_day ** (1 / 2.0)
        p -= pa_rd
        p += pa_id
        if p < 0:
            print("Test")
        return p

    def preference_cost(self, solution):
        penalty = 0
        for d in range(len(solution)):
            day = solution[d]
            for f in day:
                pc = Data.preference_cost[self.family_choices[f][d]]
                penalty += (pc[0] + int(self.family_list[f].n_people) * (pc[1] + pc[2]))
        return penalty

    def preference_cost_delta(self, e, remove_day, insert_day, family_id):
        penalty = e
        pc_rd = Data.preference_cost[self.family_choices[family_id][remove_day]]
        pc_id = Data.preference_cost[self.family_choices[family_id][insert_day]]
        penalty -= (pc_rd[0] + int(self.family_list[family_id].n_people) * (pc_rd[1] + pc_rd[2]))
        penalty += (pc_id[0] + int(self.family_list[family_id].n_people) * (pc_id[1] + pc_id[2]))
        return penalty

    def change(self, s: Solution):
        representation = deepcopy(s.representation)
        occupancy = deepcopy(s.occupancy)
        change_applied = False
        while not change_applied:
            remove_day, insert_day = random.sample(range(0, Data.n_days), k=2)
            change_family_index = random.randrange(0, len(representation[remove_day]))
            family_id = representation[remove_day][change_family_index]
            is_origin_feasible = occupancy[remove_day] - int(self.family_list[family_id].n_people) >= Data.min_people
            is_destination_feasible = occupancy[insert_day] + int(
                self.family_list[family_id].n_people) <= Data.max_people
            if is_origin_feasible and is_destination_feasible:
                representation[remove_day].pop(change_family_index)
                representation[insert_day].append(family_id)
                occupancy[remove_day] -= int(self.family_list[family_id].n_people)
                occupancy[insert_day] += int(self.family_list[family_id].n_people)
                change_applied = True
                preference_cost = self.preference_cost(representation)
                accounting_penalty = self.accounting_penalty(occupancy)
                # preference_cost = self.preference_cost_delta(s.preference_cost, remove_day, insert_day, family_id)
                # accounting_penalty = self.accounting_penalty_delta(s.occupancy, s.accounting_penalty, remove_day,
                # insert_day)
                r = Solution.Solution(representation, occupancy, preference_cost, accounting_penalty)
        return r

    def ils_algorithm(self):
        current: Solution = self.create_initial_solution()
        home: Solution = Solution.copy(current)
        best: Solution = Solution.copy(current)
        i = 1
        while i <= Parameters.total_time:
            time = Parameters.T[random.randrange(0, len(Parameters.T))]
            j = 1
            while j <= time:
                r = self.change(current)
                if r.evaluation <= current.evaluation:
                    current = Solution.copy(r)
                j += 1
            if current.evaluation < best.evaluation:
                best = Solution.copy(current)
                print(best.evaluation)
            if current.evaluation <= home.evaluation:
                home = Solution.copy(current)
            for p in range(Parameters.perturb_iterations):
                home = Solution.copy(home)
            current = Solution.copy(home)
            i += 1
        return best


def main():
    ils = ILS()
    best = ils.ils_algorithm()
    print(best.representation)
    print(best.evaluation)
    # for day in range(Data.n_days):
    #     print(best.occupancy[day])
    #     if best.occupancy[day] > Data.max_people or best.occupancy[day] < Data.min_people:
    #         print("Test")
    Data.write_family_data(best)
    print("Family data written to file!")


main()
