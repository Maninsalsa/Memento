import pygame
import math
from entities.projectiles import Projectile

class ProjectileManager:
    def __init__(self) -> None:
        """Initialize the Projectile Manager"""
        self.projectiles = []  # List to hold active projectiles

    def fire_projectile(self, name: str, damage: float, speed: float, range: float, p_source: tuple, p_target: tuple):
        """Create and fire a new projectile toward the mouse position"""
        print(f"Firing projectile: {name} at target: {p_target}")  # Debug print
        
        # Create projectile instance
        new_projectile = Projectile(
            name=name,
            damage=damage,
            speed=speed,
            range=range,
            p_source=p_source,
            p_target=p_target
        )
        
        # Add the projectile to the active list
        self.projectiles.append(new_projectile)
        print(f"Active projectiles: {len(self.projectiles)}")  # Debug print

    def update_projectiles(self):
        """Update all projectiles (movement and range checks)"""
        screen_rect = pygame.display.get_surface().get_rect()
        
        for projectile in self.projectiles[:]:
            # Update position
            projectile.rect.x += projectile.velocity.x
            projectile.rect.y += projectile.velocity.y
            
            # Reduce range - this is how range is consumed
            projectile.range -= math.sqrt(projectile.velocity.x ** 2 + projectile.velocity.y ** 2)
            
            # Remove projectile if it exceeds its range or goes off screen
            if (projectile.range <= 0 or  # This checks if range is depleted
                not screen_rect.contains(projectile.rect)):
                self.projectiles.remove(projectile)
                continue

            # Check for collision with target only if target is a sprite (not a position tuple)
            if projectile.p_target and not isinstance(projectile.p_target, tuple):
                if projectile.rect.colliderect(projectile.p_target.rect):
                    self.projectiles.remove(projectile)

    def draw_projectiles(self, screen):
        """Draw all active projectiles on the screen"""
        for projectile in self.projectiles:
            screen.blit(projectile.image, projectile.rect.topleft)

