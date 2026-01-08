# Fish Swarming Simulation

A Boid flocking simulation written in Python using Pygame and NumPy. This project demonstrates the emergence of complex flocking behavior from simple rules (Alignment, Cohesion, and Separation).

## Structure

- `src/`: Source code for the simulation.
    - `simulation.py`: Main entry point and loop.
    - `boid.py`: The Boid agent class and logic.
    - `config.py`: Configuration constants.
- `tests/`: Unit tests.

## Installation

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Run the simulation:
```sh
python -m src.simulation
```

## Controls

- **Left Mouse Button**: Hold to spawn new boids at the cursor location.
- **ESC**: Exit the simulation.

## Algorithm

The simulation implements the standard Reynolds' Boids algorithm with:
1. **Separation**: Steer to avoid crowding local flockmates.
2. **Alignment**: Steer towards the average heading of local flockmates.
3. **Cohesion**: Steer to move toward the average position (center of mass) of local flockmates.
