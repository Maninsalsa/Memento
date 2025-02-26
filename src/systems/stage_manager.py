"""Stage manager system"""

class StageManager:
    def __init__(self):
        self.current_stage = 0

    def load_stage(self, stage_number):
        """Load a specific stage"""
        self.current_stage = stage_number
        print(f"Loading stage {stage_number}")
