class Family:
    """Models a family """

    def __init__(self, family_id: int, choice_list: list, n_people: int):
        self.id = family_id
        self.choice = choice_list
        self.n_people = n_people
