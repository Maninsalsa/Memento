import pygame
import logging

class DebugSystem:
    def __init__(self):
        self.debug_font = pygame.font.Font(None, 36)
        self.enabled = False
        self.show_hitboxes = False
        
    def setup_logging(self):
        logging.basicConfig(
            filename='game_debug.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def toggle(self):
        self.enabled = not self.enabled
        
    def toggle_hitboxes(self):
        self.show_hitboxes = not self.show_hitboxes
    
    def render_debug_info(self, screen, player, clock):
        if not self.enabled:
            return
            
        debug_info = [
            f"Player pos: {player.rect.center}",
            f"Current sprite: {player.current_sprite}",
            f"FPS: {clock.get_fps():.1f}"
        ]
        
        for i, text in enumerate(debug_info):
            debug_surface = self.debug_font.render(text, True, (255, 255, 255))
            screen.blit(debug_surface, (10, 10 + (i * 30))) 