import pygame
import os
import math

class Blue(pygame.sprite.Sprite):
    """blue class representing an NPC opponent."""
    
    def __init__(self, projectile_manager, position=(300, 300)):
        """Initialize the blue sprite with image and starting position."""
        super().__init__()
        
        # Initialize sprite attributes
        self.scaled_size = (64, 64)
        self.projectile_manager = projectile_manager
        
        # Load sprites and animations
        self._load_sprites()
        
        # Setup blue rectangle and position
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        # Create hitbox for collision detection (slightly smaller than the sprite)
        self.hitbox = pygame.Rect(0, 0, self.scaled_size[0] * 0.8, self.scaled_size[1] * 0.8)
        self.hitbox.center = self.rect.center
        
        # Animation settings
        self._setup_animation()
        
        # Health and damage settings
        self.health = 100
        self.is_damaged = False
        self.damage_timer = 0
        self.damage_duration = 500  # milliseconds

    def _load_sprites(self):
        """Load all sprite animations for the blue."""
        try:
            # Initialize animation lists
            self.left_idle_sprites = []
            self.right_idle_sprites = []
            self.damage_left_sprites = []
            self.damage_right_sprites = []
            
            # Load all animation frames
            self._load_idle_animations()
            self._load_damage_animations()
            
            # Set default animation
            self.current_animation = self.left_idle_sprites
            self.image = self.current_animation[0]
            
        except pygame.error as e:
            print(f"Error loading blue image: {e}")
            self._create_fallback_sprites()

    def _load_idle_animations(self):
        """Load idle animation frames."""
        base_dir = os.path.dirname(__file__)
        
        # Load left idle frames
        for i in range(1, 3):
            path = os.path.join(base_dir, f'../assets/sprites/enemies/blue/left_idle_{i}.png')
            try:
                original = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(original, self.scaled_size)
                self.left_idle_sprites.append(scaled)
            except pygame.error as e:
                print(f"Error loading left idle frame {i}: {e}")
        
        # Load right idle frames
        for i in range(1, 3):
            path = os.path.join(base_dir, f'../assets/sprites/enemies/blue/right_idle_{i}.png')
            try:
                original = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(original, self.scaled_size)
                self.right_idle_sprites.append(scaled)
            except pygame.error as e:
                print(f"Error loading right idle frame {i}: {e}")

    def _load_damage_animations(self):
        """Load damage animation frames."""
        base_dir = os.path.dirname(__file__)
        
        # Load left damage frames
        for i in range(1, 3):
            path = os.path.join(base_dir, f'../assets/sprites/enemies/blue/damage_left_{i}.png')
            try:
                original = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(original, self.scaled_size)
                self.damage_left_sprites.append(scaled)
            except pygame.error as e:
                print(f"Error loading left damage frame {i}: {e}")
        
        # Load right damage frames
        for i in range(1, 3):
            path = os.path.join(base_dir, f'../assets/sprites/enemies/blue/damage_right_{i}.png')
            try:
                original = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(original, self.scaled_size)
                self.damage_right_sprites.append(scaled)
            except pygame.error as e:
                print(f"Error loading right damage frame {i}: {e}")

    def _create_fallback_sprites(self):
        """Create a simple fallback sprite if images can't be loaded."""
        surface = pygame.Surface(self.scaled_size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 0), (0, 0, self.scaled_size[0], self.scaled_size[1]))
        pygame.draw.line(surface, (0, 0, 0), (0, 0), (self.scaled_size[0], self.scaled_size[1]), 2)
        pygame.draw.line(surface, (0, 0, 0), (0, self.scaled_size[1]), (self.scaled_size[0], 0), 2)
        
        self.image = surface
        self.left_idle_sprites = [surface.copy()]
        self.right_idle_sprites = [surface.copy()]
        self.damage_left_sprites = [surface.copy()]
        self.damage_right_sprites = [surface.copy()]
        self.current_animation = self.left_idle_sprites

    def _setup_animation(self):
        """Initialize animation timers and counters."""
        self.current_sprite = 0
        self.animation_timer = 0
        self.animation_delay = 200  # milliseconds
        self.last_update = pygame.time.get_ticks()
        self.facing_left = True

    def take_damage(self, amount):
        """Handle taking damage and trigger damage animation."""
        self.health -= amount
        self.is_damaged = True
        self.damage_timer = pygame.time.get_ticks()
        
        # Switch to damage animation based on facing direction
        self.current_animation = self.damage_left_sprites if self.facing_left else self.damage_right_sprites
        self.current_sprite = 0
        
        # Check if defeated
        if self.health <= 0:
            self.health = 0
            # Could trigger death animation or removal here

    def update(self):
        """Update the blue's state each frame."""
        current_time = pygame.time.get_ticks()
        
        # Check if damage animation should end
        if self.is_damaged and current_time - self.damage_timer > self.damage_duration:
            self.is_damaged = False
            # Return to idle animation based on facing direction
            self.current_animation = self.left_idle_sprites if self.facing_left else self.right_idle_sprites
        
        # Update hitbox position to follow sprite
        self.hitbox.center = self.rect.center
        
        # Update animation frame
        self._update_animation()

    def check_projectile_collision(self, projectile):
        """Check if a projectile has collided with the blue's hitbox."""
        if self.hitbox.colliderect(projectile.rect):
            return True
        return False

    def _update_animation(self):
        """Update animation frames."""
        now = pygame.time.get_ticks()
        self.animation_timer += now - self.last_update
        self.last_update = now
        
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_sprite = (self.current_sprite + 1) % len(self.current_animation)
            self.image = self.current_animation[self.current_sprite]

    def draw_hitbox(self, screen):
        """Draw the hitbox for debugging purposes."""
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 1)
