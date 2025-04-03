# Memento

A top-down shooter/roguelite game with MOBA-inspired controls and mechanics.

## Overview

Arcane Archer is a 2D game built with Pygame where you control a character with abilities and projectile-based combat. The game features:

- MOBA-style controls similar to Warcraft III and League of Legends
- Ability-based combat system with Q, W, E, R hotkeys
- Mouse-driven movement and targeting
- Projectile physics and collision detection

## Controls

- **Movement**: Right-click to move to a location
- **Abilities**: Q, W, E, R keys to activate special abilities
- **Attack**: Left-click to fire projectiles at target location
- **Debug**: D key toggles debug mode, H key shows hitboxes

## Technical Details

This project serves as an exploration into:
- Building a custom 2D physics engine
- Optimizing performance with Cython
- Implementing entity component systems with Pygame-CE
- Creating smooth animations and projectile mechanics

## Development Status

This game is currently in active development. Features and mechanics are subject to change.

## Getting Started

1. Ensure you have the requirements installed and you're running it through a VENV
2. Clone this repository
3. Run `python src/main.py` to start the game

## Project Structure

- `src/`: Source code
  - `entities/`: Game objects (player, projectiles)
  - `systems/`: Game systems (projectile management, debug)
  - `assets/`: Game assets (sprites, sounds)