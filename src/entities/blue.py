import pygame  # [library import] - pygame: main game library for sprites, surfaces, rects, etc.
import os      # [library import] - os: for file path operations
import math    # [library import] - math: for potential math operations (not used directly here)

# [class] - NPC enemy sprite, handles animation, health, and collision
class Blue(pygame.sprite.Sprite):
    """blue class representing an NPC opponent."""

    # [constructor] - initializes all state, loads sprites, sets up animation and health
    def __init__(self, projectile_manager, position=(300, 300)):
        """Initialize the blue sprite with image and starting position."""
        super().__init__()

        # [attribute] - tuple, size to scale all sprite images to
        self.scaled_size = (64, 64)
        # [attribute] - reference to projectile manager for interaction
        self.projectile_manager = projectile_manager

        # [method call] - loads all sprite images and animation frames
        self._load_sprites()

        # [attribute] - pygame.Rect, main sprite rectangle for positioning
        self.rect = self.image.get_rect()
        self.rect.center = position

        # [attribute] - pygame.Rect, hitbox for collision (smaller than sprite)
        self.hitbox = pygame.Rect(0, 0, self.scaled_size[0] * 0.8, self.scaled_size[1] * 0.8)
        self.hitbox.center = self.rect.center

        # [method call] - sets up animation state and timers
        self._setup_animation()

        # [attribute] - int, health points
        self.health = 100
        # [attribute] - bool, whether currently in damage state
        self.is_damaged = False
        # [attribute] - int, time when last damaged
        self.damage_timer = 0
        # [attribute] - int, duration of damage animation in ms
        self.damage_duration = 500  # milliseconds

    # [helper method] - loads all sprite images and animation frames
    def _load_sprites(self):
        """Load all sprite animations for the blue."""
        try:
            # [attribute] - list of left idle animation frames
            self.left_idle_sprites = []
            # [attribute] - list of right idle animation frames
            self.right_idle_sprites = []
            # [attribute] - list of left damage animation frames
            self.damage_left_sprites = []
            # [attribute] - list of right damage animation frames
            self.damage_right_sprites = []

            # [method call] - loads idle animation frames
            self._load_idle_animations()
            # [method call] - loads damage animation frames
            self._load_damage_animations()

            # [attribute] - current animation frame list
            self.current_animation = self.left_idle_sprites
            # [attribute] - current image to display
            self.image = self.current_animation[0]

        except pygame.error as e:
            print(f"Error loading blue image: {e}")
            # [fallback] - creates a simple colored surface if images fail to load
            self._create_fallback_sprites()

    # [helper method] - loads idle animation frames for both directions
    def _load_idle_animations(self):
        """Load idle animation frames."""
        base_dir = os.path.dirname(__file__)

        # [loop] - loads left idle frames
        for i in range(1, 3):
            path = os.path.join(base_dir, f'../assets/sprites/enemies/blue/left_idle_{i}.png')
            try:
                original = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(original, self.scaled_size)
                self.left_idle_sprites.append(scaled)
            except pygame.error as e:
                print(f"Error loading left idle frame {i}: {e}")

        # [loop] - loads right idle frames
        for i in range(1, 3):
            path = os.path.join(base_dir, f'../assets/sprites/enemies/blue/right_idle_{i}.png')
            try:
                original = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(original, self.scaled_size)
                self.right_idle_sprites.append(scaled)
            except pygame.error as e:
                print(f"Error loading right idle frame {i}: {e}")

    # [helper method] - loads damage animation frames for both directions
    def _load_damage_animations(self):
        """Load damage animation frames."""
        base_dir = os.path.dirname(__file__)

        # [loop] - loads left damage frames
        for i in range(1, 3):
            path = os.path.join(base_dir, f'../assets/sprites/enemies/blue/damage_left_{i}.png')
            try:
                original = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(original, self.scaled_size)
                self.damage_left_sprites.append(scaled)
            except pygame.error as e:
                print(f"Error loading left damage frame {i}: {e}")

        # [loop] - loads right damage frames
        for i in range(1, 3):
            path = os.path.join(base_dir, f'../assets/sprites/enemies/blue/damage_right_{i}.png')
            try:
                original = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.scale(original, self.scaled_size)
                self.damage_right_sprites.append(scaled)
            except pygame.error as e:
                print(f"Error loading right damage frame {i}: {e}")

    # [fallback method] - creates a simple colored surface if sprite images fail to load
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

    # [helper method] - sets up animation state and timers
    def _setup_animation(self):
        """Initialize animation timers and counters."""
        # [attribute] - current animation frame index
        self.current_sprite = 0
        # [attribute] - timer for animation frame switching
        self.animation_timer = 0
        # [attribute] - delay between animation frames (ms)
        self.animation_delay = 200  # milliseconds
        # [attribute] - last time animation was updated
        self.last_update = pygame.time.get_ticks()
        # [attribute] - direction the sprite is facing
        self.facing_left = True

    # [public method] - applies damage, triggers damage animation, checks for defeat
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

    # [public method] - updates state every frame (animation, damage, hitbox)
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

    # [public method] - checks if a projectile collides with the hitbox
    def check_projectile_collision(self, projectile):
        """Check if a projectile has collided with the blue's hitbox."""
        if self.hitbox.colliderect(projectile.rect):
            return True
        return False

    # [helper method] - advances animation frame if enough time has passed
    def _update_animation(self):
        """Update animation frames."""
        now = pygame.time.get_ticks()
        self.animation_timer += now - self.last_update
        self.last_update = now

        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_sprite = (self.current_sprite + 1) % len(self.current_animation)
            self.image = self.current_animation[self.current_sprite]

    # [public method] - draws the hitbox for debugging
    def draw_hitbox(self, screen):
        """Draw the hitbox for debugging purposes."""
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 1)
