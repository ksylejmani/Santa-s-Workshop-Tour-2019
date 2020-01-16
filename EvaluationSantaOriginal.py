import Data


def get_preference_cost(representation, family_list, family_choices):
    penalty = 0
    for d in range(len(representation)):
        day = representation[d]
        # print("Day " + str(d + 1) + ": ", end="")
        for f in day:
            pc = Data.preference_cost[family_choices[f][d]]
            family_penalty = pc[0] + int(family_list[f].n_people) * (pc[1] + pc[2])
            # print("[" + str(f) + ", " + str(family_penalty)+"]", end=" ")
            penalty += family_penalty
        # print()
    return penalty


def get_preference_cost_delta(e, family_choices, remove_day, insert_day, family_id, day_load_change):
    penalty = e
    pc_rd = Data.preference_cost[family_choices[family_id][remove_day]]
    pc_id = Data.preference_cost[family_choices[family_id][insert_day]]
    penalty -= (pc_rd[0] + day_load_change * (pc_rd[1] + pc_rd[2]))
    penalty += (pc_id[0] + day_load_change * (pc_id[1] + pc_id[2]))
    return penalty


def get_accounting_penalty(solution_occupancy):
    p = 0
    for i in range(len(solution_occupancy) - 1):
        occupancy_current = solution_occupancy[i]
        occupancy_next = solution_occupancy[i + 1]
        day_penalty = ((occupancy_current - 125) / 400.0) * occupancy_current ** (
                1 / 2 + (abs(occupancy_current - occupancy_next) / 50.0))
        # print(day_penalty, end=" ")
        p = p + day_penalty
    last_occupancy = solution_occupancy[len(solution_occupancy) - 1]
    p += ((last_occupancy - 125) / 400.0) * last_occupancy ** (1 / 2.0)
    return p


def get_accounting_penalty_delta(solution_occupancy, e, remove_day, insert_day, day_load_change):
    p = e
    occupancy_current_remove_day = solution_occupancy[remove_day]
    occupancy_current_insert_day = solution_occupancy[insert_day]
    remove_coefficent = 0
    insert_coefficent = 0
    if remove_day == 0 and insert_day != Data.n_days - 1:
        occupancy_next_remove_day = solution_occupancy[remove_day + 1]
        occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
        occupancy_next_insert_day = solution_occupancy[insert_day + 1]
        remove_coefficent = 1
    elif remove_day == 0 and insert_day == Data.n_days:
        occupancy_next_remove_day = solution_occupancy[remove_day + 1]
        occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
        occupancy_next_insert_day = occupancy_current_insert_day
    elif remove_day != Data.n_days - 1 and insert_day == 0:
        occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
        occupancy_next_remove_day = solution_occupancy[remove_day + 1]
        occupancy_next_insert_day = solution_occupancy[insert_day + 1]
    elif remove_day == Data.n_days - 1 and insert_day == 0:
        occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
        occupancy_next_remove_day = occupancy_current_remove_day
        occupancy_next_insert_day = solution_occupancy[insert_day + 1]
    elif remove_day == Data.n_days - 1 and insert_day != Data.n_days - 1:
        occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
        occupancy_next_remove_day = occupancy_current_remove_day
        occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
        occupancy_next_insert_day = solution_occupancy[insert_day + 1]
    elif remove_day != Data.n_days - 1 and insert_day == Data.n_days - 1:
        occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
        occupancy_next_remove_day = solution_occupancy[remove_day + 1]
        occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
        occupancy_next_insert_day = occupancy_current_insert_day
    elif remove_day != Data.n_days - 1 and insert_day != Data.n_days - 1:
        occupancy_previous_remove_day = solution_occupancy[remove_day - 1]
        occupancy_next_remove_day = solution_occupancy[remove_day + 1]
        occupancy_previous_insert_day = solution_occupancy[insert_day - 1]
        occupancy_next_insert_day = solution_occupancy[insert_day + 1]

    if remove_day == insert_day - 1 or remove_day == insert_day + 1:
        """ In case insert and remove days are one after the other """
        occupancy_current_remove_day -= day_load_change
        occupancy_current_insert_day += day_load_change

    penalty_to_remove = ((occupancy_current_remove_day - 125) / 400.0) * occupancy_current_remove_day ** (
            1 / 2 + (abs(occupancy_current_remove_day - occupancy_next_remove_day) / 50.0))
    penalty_to_add = ((occupancy_current_insert_day - 125) / 400.0) * occupancy_current_insert_day ** (
            1 / 2 + (abs(occupancy_current_insert_day - occupancy_next_insert_day) / 50.0))
    last_occupancy_remove_day = solution_occupancy[remove_day]
    penalty_to_remove = ((last_occupancy_remove_day - 125) / 400.0) * last_occupancy_remove_day ** (1 / 2.0)
    occupancy_next_insert_day = solution_occupancy[insert_day + 1]
    penalty_to_add = ((occupancy_current_insert_day - 125) / 400.0) * occupancy_current_insert_day ** (
            1 / 2 + (abs(occupancy_current_insert_day - occupancy_next_insert_day) / 50.0))

    occupancy_current_remove_day = solution_occupancy[remove_day]
    occupancy_next_remove_day = solution_occupancy[remove_day + 1]
    penalty_to_remove = ((occupancy_current_remove_day - 125) / 400.0) * occupancy_current_remove_day ** (
            1 / 2 + (abs(occupancy_current_remove_day - occupancy_next_remove_day) / 50.0))
    last_occupancy_insert_day = solution_occupancy[insert_day]
    penalty_to_add = ((last_occupancy_insert_day - 125) / 400.0) * last_occupancy_insert_day ** (1 / 2.0)

    last_occupancy_remove_day = solution_occupancy[remove_day]
    penalty_to_remove = ((last_occupancy_remove_day - 125) / 400.0) * last_occupancy_remove_day ** (1 / 2.0)
    last_occupancy_insert_day = solution_occupancy[insert_day]
    penalty_to_add = ((last_occupancy_insert_day - 125) / 400.0) * last_occupancy_insert_day ** (1 / 2.0)
    p -= penalty_to_remove
    p += penalty_to_add
    if p < 0:
        print("Test")
    return p
