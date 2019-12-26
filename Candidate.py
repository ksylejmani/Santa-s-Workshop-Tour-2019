class Candidate:
    def __init__(self, remove_day, insert_day, family_id, family_index, load_change, preference, accounting):
        self.remove_day = remove_day
        self.insert_day = insert_day
        self.family_id = family_id
        self.family_index=family_index
        self.load_change = load_change
        self.preference = preference
        self.accounting = accounting
        self.evaluation = self.preference + self.accounting
