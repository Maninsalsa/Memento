import pygame
import os
import math

class Projectile:
    def __init__(self, name, damage, speed, range, p_source, p_target):
        self.name = name
        self.damage = damage
        self.speed = speed
        self.range = range
        self.p_source = p_source
        self.p_target = p_target

        try:
            # Load projectile image
            projectile_img_path = os.path.join(os.path.dirname(__file__), '../assets/sprites/player/projectile_sub.png')
            if not os.path.exists(projectile_img_path):
                print(f"Warning: Projectile image not found at {projectile_img_path}")
                raise FileNotFoundError
                
            self.image = pygame.image.load(projectile_img_path).convert_alpha()
            # Scale the image to a smaller size
            self.image = pygame.transform.scale(self.image, (16, 16))  # Adjust size as needed
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading projectile image: {e}")
            print(f"Attempted to load from: {projectile_img_path}")
            # Create a default surface if image fails to load
            self.image = pygame.Surface((16, 16))
            self.image.fill((255, 0, 0))  # Red rectangle as fallback
        
        # Set up the rect and position it at the source's center
        self.rect = self.image.get_rect()
        self.rect.center = p_source.rect.center
        
        # Calculate velocity based on target position
        if isinstance(p_target, tuple):  # If p_target is a position tuple
            target_x, target_y = p_target
        else:  # If p_target is an object with rect
            target_x, target_y = p_target.rect.center
            
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = math.hypot(dx, dy)
        self.velocity = pygame.math.Vector2(dx/distance * speed if distance > 0 else 0, 
                                          dy/distance * speed if distance > 0 else 0)
