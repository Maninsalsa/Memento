import pygame
import sys
import os
from systems.projectile_manager import ProjectileManager
from entities.player import Player
from entities.blue import Blue  # Add import for Blue
import logging
from systems.debug import DebugSystem as DS


def setup_logging():
    logging.basicConfig(
        filename='game_debug.log', 
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
def main():
    # setup_logging()
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
    
    # Initialize the blue with the projectile manager
    blue_enemy = Blue(projectile_manager, position=(500, 200))  # Pass projectile_manager and position
    
    # Register blue as a target for projectiles
    projectile_manager.add_target(blue_enemy)

    # Add player to the sprite group
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(blue_enemy)  # Add blue to sprite group

    debug_system = DS()

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            # Window close button clicked
            if event.type == pygame.QUIT:  # System event
                running = False
            
            # Game exits if escape is pressed
            if event.type == pygame.KEYDOWN:  # Keyboard event
                if event.key == pygame.K_ESCAPE:  # Specific key check
                    running = False
                if event.key == pygame.K_d:  # Press 'D' to toggle debug mode
                    debug_system.toggle()
                if event.key == pygame.K_h:  # Press 'H' to show hitboxes
                    debug_system.toggle_hitboxes()

        # Update all game objects
        all_sprites.update()
        projectile_manager.update_projectiles()

        # Render everything
        screen.fill((0, 0, 0))  # Clear the screen with black
        all_sprites.draw(screen)  # Draw player and other sprites
        projectile_manager.draw_projectiles(screen)  # Draw projectiles
        
        # Draw hitboxes when debug mode is enabled
        if debug_system.show_hitboxes:
            blue_enemy.draw_hitbox(screen)
        
        # Render debug info at the end
        debug_system.render_debug_info(screen, player, clock)
        
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

        # Instead of print statements, use logging
        logging.debug(f"Player position: {player.rect.center}")
        logging.debug(f"blue position: {blue_enemy.rect.center}")  # Log blue position

    # Clean up properly
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
