# [MODULE] src/entities/player.py

import pygame  # [IMPORT] pygame library for game development
import os      # [IMPORT] os module for file path operations
from systems.projectile_manager import ProjectileManager  # [IMPORT] ProjectileManager for handling projectiles
import math    # [IMPORT] math module for mathematical operations

# [COMMENT] Player Module
# [COMMENT] This class is used in:
# [COMMENT] - src/main.py (for creating and updating the player)
# [COMMENT] - src/scenes/game_scene.py (for player-scene interactions)
# [COMMENT] - src/systems/collision_system.py (for collision detection)

class Player(pygame.sprite.Sprite):  # [CLASS] Player
    """Player class representing the main character controlled by the user."""
    
    def __init__(self, projectile_manager):  # [METHOD] __init__
        """Initialize the player sprite with image and starting position."""
        # [CALL] super().__init__() - Initialize parent Sprite class
        super().__init__()
        
        # [CALL] self._setup_debug_info() - Print debug info
        self._setup_debug_info()
        
        # [ATTRIBUTE] projectile_manager: stores the projectile manager instance
        self.projectile_manager = projectile_manager
        # [ATTRIBUTE] scaled_size: tuple for sprite scaling
        self.scaled_size = (64, 64)
        
        # [CALL] self._load_sprites() - Load all player sprites and animations
        self._load_sprites()
        
        # [ATTRIBUTE] rect: pygame.Rect for player position and collision
        self.rect = self.image.get_rect()
        self.rect.center = (500, 500)
        
        # [CALL] self._setup_animation() - Initialize animation state
        self._setup_animation()
        
        # [CALL] self._setup_movement() - Initialize movement state
        self._setup_movement()
        
        # [CALL] self._setup_shooting() - Initialize shooting state
        self._setup_shooting()

    def _setup_debug_info(self):  # [METHOD] _setup_debug_info
        """Setup debug information and paths."""
        # [ATTRIBUTE] base_dir: base directory of this file
        self.base_dir = os.path.dirname(__file__)
        print(f"Current directory: {os.getcwd()}")  # [DEBUG] Print current working directory
        print(f"Base directory: {self.base_dir}")   # [DEBUG] Print base directory

    def _load_sprites(self):  # [METHOD] _load_sprites
        """Load all sprite animations for the player."""
        try:
            # [CALL] self._load_base_image() - Load base image
            self._load_base_image()
            
            # [ATTRIBUTE] idle_sprites: list for idle animation frames
            self.idle_sprites = []
            # [ATTRIBUTE] left_move_sprites: list for left movement frames
            self.left_move_sprites = []
            # [ATTRIBUTE] right_move_sprites: list for right movement frames
            self.right_move_sprites = []
            
            # [CALL] self._load_idle_animations() - Load idle animations
            self._load_idle_animations()
            # [CALL] self._load_movement_animations() - Load movement animations
            self._load_movement_animations()
            
        except pygame.error as e:  # [EXCEPTION] pygame.error
            print(f"Error loading player image: {e}")  # [DEBUG] Print error
            # [CALL] self._create_fallback_sprites() - Create fallback sprites
            self._create_fallback_sprites()

    def _load_base_image(self):  # [METHOD] _load_base_image
        """Load and scale the base player image."""
        idle_path = os.path.join(self.base_dir, '../assets/sprites/player/left_idle_1.png')  # [PATH] Idle sprite path
        print(f"Loading idle sprite from: {idle_path}")  # [DEBUG] Print path
        original_image = pygame.image.load(idle_path).convert_alpha()  # [LOAD] Load image
        self.image = pygame.transform.scale(original_image, self.scaled_size)  # [SCALE] Scale image

    def _load_idle_animations(self):  # [METHOD] _load_idle_animations
        """Load idle animation frames."""
        # [ATTRIBUTE] left_idle_sprites: list for left idle frames
        self.left_idle_sprites = []
        # [ATTRIBUTE] right_idle_sprites: list for right idle frames
        self.right_idle_sprites = []
        
        # [LOOP] Load left idle frames
        for frame in ['left_idle_1.png', 'left_idle_2.png']:
            path = os.path.join(self.base_dir, f'../assets/sprites/player/{frame}')  # [PATH] Left idle frame path
            print(f"Loading left idle frame from: {path}")  # [DEBUG] Print path
            original = pygame.image.load(path).convert_alpha()  # [LOAD] Load image
            scaled = pygame.transform.scale(original, self.scaled_size)  # [SCALE] Scale image
            self.left_idle_sprites.append(scaled)  # [APPEND] Add to left idle sprites
        
        # [LOOP] Load right idle frames
        for frame in ['right_idle_1.png', 'right_idle_2.png']:
            path = os.path.join(self.base_dir, f'../assets/sprites/player/{frame}')  # [PATH] Right idle frame path
            print(f"Loading right idle frame from: {path}")  # [DEBUG] Print path
            original = pygame.image.load(path).convert_alpha()  # [LOAD] Load image
            scaled = pygame.transform.scale(original, self.scaled_size)  # [SCALE] Scale image
            self.right_idle_sprites.append(scaled)  # [APPEND] Add to right idle sprites
            
        # [ASSIGN] Set default idle sprites to left
        self.idle_sprites = self.left_idle_sprites

    def _load_movement_animations(self):  # [METHOD] _load_movement_animations
        """Load movement animation frames for left and right directions."""
        for i in range(1, 4):  # [LOOP] For each movement frame
            left_path = os.path.join(self.base_dir, f'../assets/sprites/player/left_move_{i}.png')  # [PATH] Left move
            right_path = os.path.join(self.base_dir, f'../assets/sprites/player/move_right_{i}.png')  # [PATH] Right move
            
            # [CHECK] File existence
            if not os.path.exists(left_path):
                print(f"Warning: Left movement sprite {i} not found at {left_path}")  # [DEBUG] Warn missing left
            if not os.path.exists(right_path):
                print(f"Warning: Right movement sprite {i} not found at {right_path}")  # [DEBUG] Warn missing right
            
            try:
                left = pygame.image.load(left_path).convert_alpha()  # [LOAD] Load left
                right = pygame.image.load(right_path).convert_alpha()  # [LOAD] Load right
                
                self.left_move_sprites.append(pygame.transform.scale(left, self.scaled_size))  # [APPEND] Left move
                self.right_move_sprites.append(pygame.transform.scale(right, self.scaled_size))  # [APPEND] Right move
            except (pygame.error, FileNotFoundError) as e:  # [EXCEPTION] Loading error
                print(f"Error loading movement sprite: {e}")  # [DEBUG] Print error
                self._create_fallback_movement_sprite(i, left_path)  # [CALL] Fallback

    def _create_fallback_movement_sprite(self, index, path):  # [METHOD] _create_fallback_movement_sprite
        """Create fallback sprites when loading fails."""
        fallback = pygame.Surface(self.scaled_size)  # [CREATE] Fallback surface
        fallback.fill((255, 0, 0) if 'left' in path else (0, 0, 255))  # [COLOR] Red for left, blue for right
        self.left_move_sprites.append(fallback)  # [APPEND] Fallback left
        self.right_move_sprites.append(fallback)  # [APPEND] Fallback right

    def _create_fallback_sprites(self):  # [METHOD] _create_fallback_sprites
        """Create fallback sprites when all loading fails."""
        self.image = pygame.Surface(self.scaled_size)  # [CREATE] Fallback image
        self.image.fill((255, 0, 0))  # [COLOR] Red
        self.idle_sprites = [self.image, self.image]  # [ASSIGN] Fallback idle
        self.left_move_sprites = [self.image] * 3     # [ASSIGN] Fallback left move
        self.right_move_sprites = [self.image] * 3    # [ASSIGN] Fallback right move

    def _setup_animation(self):  # [METHOD] _setup_animation
        """Setup animation timers and initial state."""
        self.current_sprite = 0  # [ATTRIBUTE] Current animation frame index
        self.animation_timer = 0  # [ATTRIBUTE] Animation timer
        self.animation_delay = 167  # [ATTRIBUTE] Animation frame delay (ms)
        self.last_update = pygame.time.get_ticks()  # [ATTRIBUTE] Last update time
        self.facing_left = True  # [ATTRIBUTE] Facing direction
        self.current_animation = self.left_idle_sprites  # [ATTRIBUTE] Current animation list
        
        self.image = self.current_animation[self.current_sprite]  # [ASSIGN] Initial image
        self.rect = self.image.get_rect()  # [ASSIGN] Update rect
        self.rect.center = (500, 500)      # [ASSIGN] Initial position

    def _setup_movement(self):  # [METHOD] _setup_movement
        """Setup movement related attributes."""
        self.target_pos = None  # [ATTRIBUTE] Target position for movement
        self.speed = 5          # [ATTRIBUTE] Movement speed

    def _setup_shooting(self):  # [METHOD] _setup_shooting
        """Setup shooting related attributes."""
        self.can_shoot = True         # [ATTRIBUTE] Can shoot flag
        self.projectile_range = 500   # [ATTRIBUTE] Projectile range

    # def set_destination(self, pos):  # [METHOD] set_destination (commented)
    #     """Set new destination for the player to move to."""
    #     self.target_pos = pos

    def update(self):  # [METHOD] update
        """Update player state and handle input."""
        self._handle_input()      # [CALL] Handle input
        self._handle_movement()   # [CALL] Handle movement
        self._handle_shooting()   # [CALL] Handle shooting
        self._update_animation()  # [CALL] Update animation

    def _handle_input(self):  # [METHOD] _handle_input
        """Handle mouse input for movement."""
        mouse_buttons = pygame.mouse.get_pressed()  # [INPUT] Mouse buttons
        if mouse_buttons[2]:  # [CHECK] Right click
            self.target_pos = pygame.mouse.get_pos()  # [ASSIGN] Set target position

    def _handle_movement(self):  # [METHOD] _handle_movement
        """Handle player movement logic."""
        if not self.target_pos:  # [CHECK] No target
            return
            
        dx = self.target_pos[0] - self.rect.centerx  # [CALC] X distance
        dy = self.target_pos[1] - self.rect.centery  # [CALC] Y distance
        distance = math.sqrt(dx * dx + dy * dy)      # [CALC] Euclidean distance
        
        if distance > self.speed:  # [CHECK] Need to move
            move_x = (dx / distance) * self.speed  # [CALC] X movement
            move_y = (dy / distance) * self.speed  # [CALC] Y movement
            
            self.rect.x += move_x  # [MOVE] Update x
            self.rect.y += move_y  # [MOVE] Update y
            
            if move_x < 0:  # [CHECK] Moving left
                self.current_animation = self.left_move_sprites  # [ANIMATION] Left move
                self.facing_left = True
            else:           # [CHECK] Moving right
                self.current_animation = self.right_move_sprites  # [ANIMATION] Right move
                self.facing_left = False
        else:
            self.rect.center = self.target_pos  # [ASSIGN] Snap to target
            self.target_pos = None              # [RESET] Clear target
            self.current_animation = self.left_idle_sprites if self.facing_left else self.right_idle_sprites  # [ANIMATION] Idle

    def _handle_shooting(self):  # [METHOD] _handle_shooting
        """Handle projectile firing logic."""
        keys = pygame.key.get_pressed()  # [INPUT] Keyboard state
        if not keys[pygame.K_SPACE]:     # [CHECK] Space not pressed
            self.can_shoot = True        # [RESET] Can shoot again
        elif keys[pygame.K_SPACE] and self.can_shoot:  # [CHECK] Space just pressed
            self.projectile_manager.fire_projectile(   # [CALL] Fire projectile
                name='basic',
                damage=10,
                speed=10,
                range=self.projectile_range,
                p_source=self,
                p_target=pygame.mouse.get_pos()
            )
            self.can_shoot = False  # [RESET] Prevent shooting until released

    def _update_animation(self):  # [METHOD] _update_animation
        """Update animation frames."""
        now = pygame.time.get_ticks()  # [TIME] Current time
        self.animation_timer += now - self.last_update  # [TIMER] Update timer
        self.last_update = now
        
        if self.animation_timer >= self.animation_delay:  # [CHECK] Advance frame
            self.animation_timer = 0
            self.current_sprite = (self.current_sprite + 1) % len(self.current_animation)  # [FRAME] Next frame
            self.image = self.current_animation[self.current_sprite]  # [ASSIGN] Update image

    # def set_projectile_range(self, new_range):  # [METHOD] set_projectile_range (commented)
    #     """Adjust the range of projectiles."""
    #     self.projectile_range = new_range
