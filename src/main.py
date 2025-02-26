import pygame
import sys
import os
from systems.projectile_manager import ProjectileManager
from entities.player import Player
import logging
from systems.debug import DebugSystem as DS


def setup_logging():
    logging.basicConfig(
        filename='game_debug.log', 
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def handle_input(event, player, projectile_manager):
    # Remove the projectile firing code from here since it's handled in player.py
    pass


def main():
    setup_logging()
    # Set up the base path relative to this file's location
    base_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_path)  # Change working directory to src/
    
    pygame.init()
    pygame.font.init()

    # Set up display
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()

    # Initialize managers first
    projectile_manager = ProjectileManager()
    
    # Initialize the player with the projectile manager
    player = Player(projectile_manager)  # Pass the manager to player

    # Add player to the sprite group
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    debug_system = DS()

    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            # Window close button clicked
            if event.type == pygame.QUIT:  # System event
                pygame.quit()
                sys.exit()
            
            # Game exits if escape is pressed
            if event.type == pygame.KEYDOWN:  # Keyboard event
                if event.key == pygame.K_ESCAPE:  # Specific key check
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_d:  # Press 'D' to toggle debug mode
                    debug_system.toggle()
                if event.key == pygame.K_h:  # Press 'H' to show hitboxes
                    debug_system.toggle_hitboxes()
                handle_input(event, player, projectile_manager)

        # Update all game objects
        all_sprites.update()
        projectile_manager.update_projectiles()

        # Render everything
        screen.fill((0, 0, 0))  # Clear the screen with black
        all_sprites.draw(screen)  # Draw player and other sprites
        projectile_manager.draw_projectiles(screen)  # Draw projectiles
        
        # Render debug info at the end
        debug_system.render_debug_info(screen, player, clock)
        
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

        # Instead of print statements, use logging
        logging.debug(f"Player position: {player.rect.center}")


if __name__ == "__main__":
    main()
