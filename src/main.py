import pygame
import sys
import os
from systems.projectile_manager import ProjectileManager
from entities.player import Player
from entities.blue import Blue  # Add import for Blue
import logging
from systems.debug import DebugSystem as DS


# def setup_logging():
#     logging.basicConfig(
#         filename='game_debug.log', 
#         level=logging.DEBUG,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )

"""main executes all moodules and initializes an instance of the game"""
    
def main():
    # First, store the directory in a variable to be reused
    # base_path = os.path.dirname(os.path.abspath(__file__))  # [BUILT-IN] os module method
    base_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_path)  # [BUILT-IN] os module method - Change working directory to src/
    
    pygame.init()  # [EXTERNAL] pygame module method
    pygame.font.init()  # [EXTERNAL] pygame.font module method

    # Set up display
    screen = pygame.display.set_mode((1000, 1000))  # [EXTERNAL] pygame.display method
    clock = pygame.time.Clock()  # [EXTERNAL] pygame.time method

    # Initialize managers first
    projectile_manager = ProjectileManager()  # [CUSTOM] systems.projectile_manager.ProjectileManager instance
    
    # Initialize the player with the projectile manager
    player = Player(projectile_manager)  # [CUSTOM] entities.player.Player instance
    
    # Initialize the blue with the projectile manager
    blue_enemy = Blue(projectile_manager, position=(500, 200))  # [CUSTOM] entities.blue.Blue instance
    
    # Register blue as a target for projectiles
    projectile_manager.add_target(blue_enemy)  # [CUSTOM] systems.projectile_manager.ProjectileManager.add_target method

    # Add player to the sprite group
    all_sprites = pygame.sprite.Group()  # [EXTERNAL] pygame.sprite method
    all_sprites.add(player)  # [EXTERNAL] pygame.sprite.Group.add method
    all_sprites.add(blue_enemy)  # [EXTERNAL] pygame.sprite.Group.add method

    debug_system = DS()  # [CUSTOM] systems.debug.DebugSystem instance

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():  # [EXTERNAL] pygame.event method
            # Window close button clicked
            if event.type == pygame.QUIT:  # System event
                running = False
            
            # Game exits if escape is pressed
            if event.type == pygame.KEYDOWN:  # Keyboard event
                if event.key == pygame.K_ESCAPE:  # Specific key check
                    running = False
                if event.key == pygame.K_d:  # Press 'D' to toggle debug mode
                    debug_system.toggle()  # [CUSTOM] systems.debug.DebugSystem.toggle method
                if event.key == pygame.K_h:  # Press 'H' to show hitboxes
                    debug_system.toggle_hitboxes()  # [CUSTOM] systems.debug.DebugSystem.toggle_hitboxes method

        # Update all game objects
        all_sprites.update()  # [EXTERNAL] pygame.sprite.Group.update method
        projectile_manager.update_projectiles()  # [CUSTOM] systems.projectile_manager.ProjectileManager.update_projectiles method

        # Render everything
        screen.fill((0, 0, 0))  # [EXTERNAL] pygame.Surface.fill method
        all_sprites.draw(screen)  # [EXTERNAL] pygame.sprite.Group.draw method
        projectile_manager.draw_projectiles(screen)  # [CUSTOM] systems.projectile_manager.ProjectileManager.draw_projectiles method
        
        # Draw hitboxes when debug mode is enabled
        if debug_system.show_hitboxes:  # [CUSTOM] systems.debug.DebugSystem.show_hitboxes attribute
            blue_enemy.draw_hitbox(screen)  # [CUSTOM] entities.blue.Blue.draw_hitbox method
        
        # Render debug info at the end
        debug_system.render_debug_info(screen, player, clock)  # [CUSTOM] systems.debug.DebugSystem.render_debug_info method
        
        pygame.display.flip()  # [EXTERNAL] pygame.display method

        # Cap the frame rate
        clock.tick(60)  # [EXTERNAL] pygame.time.Clock.tick method

        # Instead of print statements, use logging
        logging.debug(f"Player position: {player.rect.center}")  # [BUILT-IN] logging module method
        logging.debug(f"blue position: {blue_enemy.rect.center}")  # [BUILT-IN] logging module method

    # Clean up properly
    pygame.quit()  # [EXTERNAL] pygame module method
    sys.exit()  # [BUILT-IN] sys module method

if __name__ == "__main__":
    main()
