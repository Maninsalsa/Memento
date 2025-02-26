class Health:
    def __init__(self, max_health, current_health, regen_rate, regen_delay):
        self.max_health = max_health
        self.current_health = current_health
        self.regen_rate = regen_rate
        self.regen_delay = regen_delay

    def update(self):
        pass