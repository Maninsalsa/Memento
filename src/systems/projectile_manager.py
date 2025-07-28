import pygame   # [library import] - pygame: used for display, rects, and blitting
import math     # [library import] - math: used for distance and range calculations
from entities.projectiles import Projectile  # [class import] - Projectile: represents a single projectile entity

# [manager class] - Handles all projectile logic, including creation, updates, collision, and rendering
class ProjectileManager:
    # [constructor] - Initializes projectile and target lists
    def __init__(self) -> None:
        """Initialize the Projectile Manager"""
        self.projectiles = []  # [attribute] - list of active projectiles
        self.targets = []      # [attribute] - list of potential targets (e.g., enemies, rivals)

    # [public method] - Adds a new target for collision detection
    def add_target(self, target):
        """Add a target that projectiles can collide with."""
        if target not in self.targets:
            self.targets.append(target)

    # [public method] - Fires a new projectile from a source to a target
    def fire_projectile(self, name: str, damage: float, speed: float, range: float, p_source: tuple, p_target: tuple):
        """Create and fire a new projectile toward the mouse position"""
        print(f"Firing projectile: {name} at target: {p_target}")  # [debug] - logs firing event
        
        # [object instantiation] - create a new projectile instance
        new_projectile = Projectile(
            name=name,
            damage=damage,
            speed=speed,
            range=range,
            p_source=p_source,
            p_target=p_target
        )
        
        # [list operation] - add projectile to active list
        self.projectiles.append(new_projectile)
        print(f"Active projectiles: {len(self.projectiles)}")  # [debug] - logs number of projectiles

    # [public method] - Updates all projectiles: movement, range, collision, and removal
    def update_projectiles(self):
        """Update all projectiles (movement and range checks)"""
        screen_rect = pygame.display.get_surface().get_rect()  # [local variable] - screen bounds for off-screen checks
        
        for projectile in self.projectiles[:]:  # [iteration] - copy to allow safe removal
            # [movement] - update projectile position by velocity
            projectile.rect.x += projectile.velocity.x
            projectile.rect.y += projectile.velocity.y
            
            # [range reduction] - decrease range by distance traveled this frame
            projectile.range -= math.sqrt(projectile.velocity.x ** 2 + projectile.velocity.y ** 2)
            
            # [collision detection] - check for collision with any target
            collision_occurred = False  # [flag] - tracks if collision happened
            for target in self.targets:
                if hasattr(target, 'check_projectile_collision'):  # [duck typing] - ensure method exists
                    if target.check_projectile_collision(projectile):
                        target.take_damage(projectile.damage)  # [damage trigger] - apply damage to target
                        self.projectiles.remove(projectile)    # [removal] - remove projectile on hit
                        collision_occurred = True
                        break
            
            if collision_occurred:
                continue  # [control flow] - skip further checks if already collided
            
            # [removal condition] - remove if out of range or off screen
            if (projectile.range <= 0 or  # [range check] - depleted range
                not screen_rect.contains(projectile.rect)):  # [screen bounds check]
                self.projectiles.remove(projectile)
                continue

            # [redundant collision check] - if p_target is a sprite, check direct collision
            if projectile.p_target and not isinstance(projectile.p_target, tuple):
                if projectile.rect.colliderect(projectile.p_target.rect):
                    self.projectiles.remove(projectile)

    # [public method] - Draws all active projectiles to the screen
    def draw_projectiles(self, screen):
        """Draw all active projectiles on the screen"""
        for projectile in self.projectiles:
            screen.blit(projectile.image, projectile.rect.topleft)  # [render] - draw projectile at its position

