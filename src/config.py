"""
Configuration settings for the Boid simulation.
"""

from typing import Tuple

# Window settings
FULLSCREEN: bool = True
WIDTH: int = 1000
HEIGHT: int = 800
CAPTION: str = "Boid Simulation"

# Colors (R, G, B)
WHITE: Tuple[int, int, int] = (255, 255, 255)
BLACK: Tuple[int, int, int] = (0, 0, 0)
BACKGROUND_COLOR: Tuple[int, int, int] = BLACK

# Boid settings
BOID_SIZE: int = 17
BOID_SPEED: float = 170.0
TURN_RATE: float = 190.0
MARGIN: int = 42
WRAP_EDGES: bool = False

# Simulation settings
MAX_BOIDS: int = 500
FPS: int = 60
