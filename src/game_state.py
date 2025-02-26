class GameState:
    def __init__(self):
        """Core game state variables"""
        self.is_running = True
        self.current_stage = 0
        self.is_paused = False
        self.game_over = False
        self.game_won = False
        self.score = 0


    def start_game(self):
        """Initialize or restart the game variables"""
        self.is_running = True
        self.is_paused = False
        self.game_over = False
        self.game_won = False
        self.score = 0
        self.level = 0


    def pause_game(self, won=False):
        """Toggle the pause state."""
        self.is_running = False
        self.game_over = True
        self.game_won = won
    

    def game_over(self, player):
        """Check if player's health is 0 and handle game over state
        
        Args:
            player: The player object containing health information
            
        Returns:
            bool: True if game should continue, False if game over
        """
        if player.health.current_health <= 0:
            self.is_running = False
            self.game_over = True
            self.game_won = False

            while True:
                continue_game = input("Do you want to continue the game? (y/n): ").lower()
                if continue_game in ['y', 'n']:
                    return continue_game == 'y'
                print("Invalid input. Please enter 'y' or 'n'.")
        return True
