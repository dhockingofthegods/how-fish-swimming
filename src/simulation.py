import pygame as pg
import numpy as np
import sys
from . import config
from .boid import Boid

class Simulation:
    """
    Main class to handle the Boid simulation.
    """

    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self._init_screen()
        
        self.running = True
        self.boids_group = pg.sprite.Group()
        
        # Shared data array for optimized neighbor usage
        # [x, y, angle, extra_slot]
        self.shared_data = np.zeros((config.MAX_BOIDS, 4), dtype=float)
        
        self.num_boids = 0

    def _init_screen(self):
        if config.FULLSCREEN:
            info = pg.display.Info()
            self.screen = pg.display.set_mode((info.current_w, info.current_h), pg.SCALED)
        else:
            self.screen = pg.display.set_mode((config.WIDTH, config.HEIGHT), pg.RESIZABLE)
        pg.display.set_caption(config.CAPTION)

    def add_boid(self):
        """Adds a new boid to the simulation if limits allow."""
        if self.num_boids < config.MAX_BOIDS:
            new_boid = Boid(self.num_boids, self.screen, self.shared_data)
            self.boids_group.add(new_boid)
            self.num_boids += 1

    def handle_input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False

        # Generate boid on click
        if pg.mouse.get_pressed()[0]:
            self.add_boid()

    def update(self):
        dt = self.clock.tick(config.FPS) / 1000.0
        self.boids_group.update(dt, wrap=config.WRAP_EDGES)

    def draw(self):
        self.screen.fill(config.BACKGROUND_COLOR)
        self.boids_group.draw(self.screen)
        pg.display.flip()

    def run(self):
        """Main game loop."""
        # Initial boid
        self.add_boid()
        
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
        
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
