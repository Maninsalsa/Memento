class Defense:
    """contains a character's defense stats"""
    def __init__(self, innate_defense, lvl_defense_mod, current_defense):
        self.innate_defense = innate_defense # defense value
        self.lvl_defense_mod = lvl_defense_mod
        self.current_defense = current_defense
        
