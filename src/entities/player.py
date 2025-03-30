import pygame
import os
from systems.projectile_manager import ProjectileManager
import math

"""
Player module

"""


class Player(pygame.sprite.Sprite):
    """Player class representing the main character controlled by the user."""
    
    def __init__(self, projectile_manager):
        """Initialize the player sprite with image and starting position."""
        super().__init__()
        
        # Debug: Print current working directory and file paths
        self._setup_debug_info()
        
        # Initialize sprite attributes
        self.projectile_manager = projectile_manager
        self.scaled_size = (64, 64)
        
        # Load sprites and animations
        self._load_sprites()
        
        # Setup player rectangle and position
        self.rect = self.image.get_rect()
        self.rect.center = (500, 500)
        
        # Animation settings
        self._setup_animation()
        
        # Movement settings
        self._setup_movement()
        
        # Shooting settings
        self._setup_shooting()

    def _setup_debug_info(self):
        """Setup debug information and paths."""
        self.base_dir = os.path.dirname(__file__)
        print(f"Current directory: {os.getcwd()}")
        print(f"Base directory: {self.base_dir}")

    def _load_sprites(self):
        """Load all sprite animations for the player."""
        try:
            # Load base image
            self._load_base_image()
            
            # Initialize animation lists
            self.idle_sprites = []
            self.left_move_sprites = []
            self.right_move_sprites = []
            
            # Load all animation frames
            self._load_idle_animations()
            self._load_movement_animations()
            
        except pygame.error as e:
            print(f"Error loading player image: {e}")
            self._create_fallback_sprites()

    def _load_base_image(self):
        """Load and scale the base player image."""
        idle_path = os.path.join(self.base_dir, '../assets/sprites/player/idle/Left_idle_1.png')
        print(f"Loading idle sprite from: {idle_path}")
        original_image = pygame.image.load(idle_path).convert_alpha()
        self.image = pygame.transform.scale(original_image, self.scaled_size)

    def _load_idle_animations(self):
        """Load idle animation frames."""
        # Initialize separate lists for left and right idle animations
        self.left_idle_sprites = []
        self.right_idle_sprites = []
        
        # Load left idle frames
        for frame in ['Left_idle_1.png', 'Left_idle_2.png']:
            path = os.path.join(self.base_dir, f'../assets/sprites/player/idle/{frame}')
            print(f"Loading left idle frame from: {path}")
            original = pygame.image.load(path).convert_alpha()
            scaled = pygame.transform.scale(original, self.scaled_size)
            self.left_idle_sprites.append(scaled)
        
        # Load right idle frames
        for frame in ['Right_idle_1.png', 'Right_idle_2.png']:
            path = os.path.join(self.base_dir, f'../assets/sprites/player/idle/{frame}')
            print(f"Loading right idle frame from: {path}")
            original = pygame.image.load(path).convert_alpha()
            scaled = pygame.transform.scale(original, self.scaled_size)
            self.right_idle_sprites.append(scaled)
            
        # Set default idle sprites to left (will be updated based on player direction)
        self.idle_sprites = self.left_idle_sprites

    def _load_movement_animations(self):
        """Load movement animation frames for left and right directions."""
        for i in range(1, 4):
            # Define paths
            left_path = os.path.join(self.base_dir, f'../assets/sprites/player/moving/move_left/left_move_{i}.png')
            right_path = os.path.join(self.base_dir, f'../assets/sprites/player/moving/move_right/move_right_{i}.png')
            
            # Check if files exist
            if not os.path.exists(left_path):
                print(f"Warning: Left movement sprite {i} not found at {left_path}")
            if not os.path.exists(right_path):
                print(f"Warning: Right movement sprite {i} not found at {right_path}")
            
            try:
                # Load and scale sprites
                left = pygame.image.load(left_path).convert_alpha()
                right = pygame.image.load(right_path).convert_alpha()
                
                self.left_move_sprites.append(pygame.transform.scale(left, self.scaled_size))
                self.right_move_sprites.append(pygame.transform.scale(right, self.scaled_size))
            except (pygame.error, FileNotFoundError) as e:
                print(f"Error loading movement sprite: {e}")
                self._create_fallback_movement_sprite(i, left_path)

    def _create_fallback_movement_sprite(self, index, path):
        """Create fallback sprites when loading fails."""
        fallback = pygame.Surface(self.scaled_size)
        fallback.fill((255, 0, 0) if 'left' in path else (0, 0, 255))
        self.left_move_sprites.append(fallback)
        self.right_move_sprites.append(fallback)

    def _create_fallback_sprites(self):
        """Create fallback sprites when all loading fails."""
        self.image = pygame.Surface(self.scaled_size)
        self.image.fill((255, 0, 0))
        self.idle_sprites = [self.image, self.image]
        self.left_move_sprites = [self.image] * 3
        self.right_move_sprites = [self.image] * 3

    def _setup_animation(self):
        """Setup animation timers and initial state."""
        self.current_sprite = 0
        self.animation_timer = 0
        self.animation_delay = 167
        self.last_update = pygame.time.get_ticks()
        self.facing_left = True  # Track which direction the player is facing
        self.current_animation = self.left_idle_sprites  # Start with left idle animation
        
        # Set initial image
        self.image = self.current_animation[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.center = (500, 500)

    def _setup_movement(self):
        """Setup movement related attributes."""
        self.target_pos = None
        self.speed = 5

    def _setup_shooting(self):
        """Setup shooting related attributes."""
        self.can_shoot = True  # Flag to track if we can shoot
        self.projectile_range = 500  # Adjustable range for projectiles

    def set_destination(self, pos):
        """Set new destination for the player to move to."""
        self.target_pos = pos

    def update(self):
        """Update player state and handle input."""
        self._handle_input()
        self._handle_movement()
        self._handle_shooting()
        self._update_animation()

    def _handle_input(self):
        """Handle mouse input for movement."""
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[2]:  # Right click
            self.target_pos = pygame.mouse.get_pos()

    def _handle_movement(self):
        """Handle player movement logic."""
        if not self.target_pos:
            return
            
        dx = self.target_pos[0] - self.rect.centerx
        dy = self.target_pos[1] - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.speed:
            # Calculate movement
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed
            
            # Update position
            self.rect.x += move_x
            self.rect.y += move_y
            
            # Set appropriate animation based on movement direction
            if move_x < 0:
                self.current_animation = self.left_move_sprites
                self.facing_left = True
            else:
                self.current_animation = self.right_move_sprites
                self.facing_left = False
        else:
            # Reached destination
            self.rect.center = self.target_pos
            self.target_pos = None
            # Use the appropriate idle animation based on which way the player is facing
            self.current_animation = self.left_idle_sprites if self.facing_left else self.right_idle_sprites

    def _handle_shooting(self):
        """Handle projectile firing logic."""
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_SPACE]:
            self.can_shoot = True  # Reset flag when space is released
        elif keys[pygame.K_SPACE] and self.can_shoot:  # Only shoot if space just pressed
            self.projectile_manager.fire_projectile(
                name='basic',
                damage=10,
                speed=10,
                range=self.projectile_range,  # Use the adjustable range
                p_source=self,
                p_target=pygame.mouse.get_pos()
            )
            self.can_shoot = False  # Prevent shooting until space is released

    def _update_animation(self):
        """Update animation frames."""
        now = pygame.time.get_ticks()
        self.animation_timer += now - self.last_update
        self.last_update = now
        
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.current_sprite = (self.current_sprite + 1) % len(self.current_animation)
            self.image = self.current_animation[self.current_sprite]

    def set_projectile_range(self, new_range):
        """Adjust the range of projectiles."""
        self.projectile_range = new_range