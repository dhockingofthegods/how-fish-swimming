import unittest
import numpy as np
import pygame as pg # Needed for vector math
from src.boid import Boid
from src import config

class TestBoid(unittest.TestCase):
    def setUp(self):
        pg.init()
        # Mock screen
        self.screen = pg.Surface((100, 100))
        self.shared_data = np.zeros((10, 4), dtype=float)

    def test_boid_initialization(self):
        boid = Boid(0, self.screen, self.shared_data)
        self.assertIsInstance(boid.pos, pg.Vector2)
        self.assertTrue(0 <= boid.angle <= 360)
        
        # Check if shared data was updated
        self.assertEqual(self.shared_data[0, 0], boid.pos.x)
        self.assertEqual(self.shared_data[0, 1], boid.pos.y)

    def tearDown(self):
        pg.quit()

if __name__ == '__main__':
    unittest.main()
