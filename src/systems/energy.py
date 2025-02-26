class Energy:
    """Energy is used for special abilities and shields"""
    def __init__(self, max_nrg, current_nrg, regen_rate, regen_delay):
        self.max_nrg = max_nrg
        self.current_nrg = current_nrg
        self.regen_rate = regen_rate
        self.regen_delay = regen_delay

    def update(self):
        pass