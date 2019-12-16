import csv

import Familly

min_people = 125
max_people = 300
n_days = 100
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
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                family_id = int(row[0])
                choice_list = list()
                for c in range(1, 11, 1):
                    choice_list.append(int(row[c]))
                n_people = (row[11])
                # print(f'\t{family_id} - {n_people}.')
                line_count += 1
                family_list.append(Familly.Family(family_id, choice_list, n_people))
    return family_list


def get_family_choice(family_list):
    family_choices = list()
    for f in family_list:
        day_choices = f.choice
        family_c = list()
        for d in range(n_days):
            family_c.append(10)  # Otherwise
        for c in range(len(day_choices)):
            family_c[day_choices[c] - 1] = c  # day is converted to a zero based index
        family_choices.append(family_c)
    return family_choices
