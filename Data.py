import csv

import Evaluation
import Familly
import Solution

min_people: int = 125
max_people: int = 300
n_days: int = 100
n_families: int = 5000
preference_cost = {0: [0, 0, 0],
                   1: [50, 0, 0],
                   2: [50, 9, 0],
                   3: [100, 9, 0],
                   4: [200, 9, 0],
                   5: [200, 18, 0],
                   6: [300, 18, 0],
                   7: [300, 36, 0],
                   8: [400, 36, 0],
                   9: [500, 36, 199],
                   10: [500, 36, 398]}  # Otherwise


def read_family_data():
    family_list = list()
    with open('family_data.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                family_id = int(row[0])
                choice_list = list()
                for c in range(1, 11, 1):
                    choice_list.append(int(row[c]) - 1)  # Transposing DAY index from 1 based to zero based
                n_people = (row[11])
                # print(f'\t{family_id} - {n_people}.')
                line_count += 1
                family_list.append(Familly.Family(family_id, choice_list, n_people))
    return family_list


def write_family_data(solution: Solution, seed_millis):
    with open('submission_' + str(seed_millis) + '.csv', mode='w', newline='') as family_file:
        family_writer = csv.writer(family_file, delimiter=',')
        family_day_list = list()
        for d in range(len(solution.representation)):
            day = solution.representation[d]
            for f in day:
                family_day_list.append([f, d + 1])  # Transposing back DAY index from 0 based to one based
        family_day_list.sort(key=lambda c: c[0])
        family_writer.writerow(['family_id', 'assigned_day'])
        for fd in family_day_list:
            family_writer.writerow([fd[0], fd[1]])


def load_solution_from_file(family_list, family_choices):
    representation = list()
    occupancy = list()
    for i in range(n_days):
        day = list()
        day_occupancy = 0
        representation.append(day)
        occupancy.append(day_occupancy)
    solution_name = input("Enter solution name: ")
    with open(solution_name + '.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                family_id = int(row[0])
                assigned_day = int(row[1])
                representation[assigned_day - 1].append(family_id)  # zero based index
                occupancy[assigned_day - 1] += int(family_list[family_id].n_people)
                line_count += 1
        pref_cost = Evaluation.get_preference_cost(representation, family_list, family_choices)
        accounting_cost = Evaluation.get_accounting_penalty(occupancy)
        s = Solution.Solution(representation, occupancy, pref_cost, accounting_cost)
    return s


def get_family_choice(family_list):
    family_choices = list()
    for f in family_list:
        day_choices = f.choice
        family_c = list()
        for d in range(n_days):
            family_c.append(10)  # Otherwise
        for c in range(len(day_choices)):
            family_c[day_choices[c]] = c
        family_choices.append(family_c)
    return family_choices


def get_day_choice(family_list):
    day_choices = list()
    for d in range(n_days):
        single_day_choice = list()
        day_choices.append(single_day_choice)
    for f in range(len(family_list)):
        for c in family_list[f].choice:
            day_choices[c].append(f)
    return day_choices
