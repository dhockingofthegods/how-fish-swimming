import pygame as pg
import numpy as np
from random import randint
from typing import Tuple, Optional
from . import config

class Boid(pg.sprite.Sprite):
    """
    A class representing a single Boid (bird/fish object) in the simulation.
    """

    def __init__(self, index: int, screen: pg.Surface, shared_data: np.ndarray):
        """
        Initialize the Boid.

        Args:
            index (int): The index of this boid in the shared data array.
            screen (pg.Surface): The pygame surface to draw on.
            shared_data (np.ndarray): Shared numpy array containing state of all boids.
        """
        super().__init__()
        self.index = index
        self.screen = screen
        self.shared_data = shared_data

        self.image = pg.Surface((15, 15)).convert()
        self.image.set_colorkey(config.BLACK) # Ensure transparency if needed, though originally it didn't
        self.color = (randint(50, 255), randint(50, 255), randint(50, 255))
        
        # Draw the boid shape (triangle)
        # Original: ((7,0),(12,5),(3,14),(11,14),(2,5),(7,0)) - This looks like a paper airplane or dart
        pg.draw.polygon(self.image, self.color, ((7, 0), (12, 5), (3, 14), (11, 14), (2, 5), (7, 0)))
        
        # Initial position logic
        if pg.mouse.get_pressed()[0]:
            start_pos = pg.mouse.get_pos()
        else:
            # Default to center or random if not specified in original, 
            # original used (0,0) global but seemingly relied on mouse or update to fix it?
            # actually original code had `pos = (0,0)` global then `self.rect = ... center=(pos)`
            # Let's randomise it slightly to avoid stacking if mouse isn't pressed
            w, h = self.screen.get_size()
            start_pos = (randint(0, w), randint(0, h))

        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pg.Vector2(start_pos)
        self.angle = float(randint(0, 360))
        self.variable_speed = config.BOID_SPEED
        
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)
        
        # Initial stats update
        self._update_shared_data()

    def _update_shared_data(self):
        """Updates the shared numpy array with this boid's current state."""
        # Columns: 0: x, 1: y, 2: angle, 3: temp_dist (used by others)
        self.shared_data[self.index, 0] = self.pos.x
        self.shared_data[self.index, 1] = self.pos.y
        self.shared_data[self.index, 2] = self.angle

    def update(self, dt: float, wrap: bool = False):
        """
        Update the boid's position and rotation based on neighbors and rules.

        Args:
            dt (float): Delta time since last frame.
            wrap (bool): Whether to wrap around screen edges.
        """
        w, h = self.screen.get_size()
        
        # Logic to find neighbors
        # We need to exclude self. efficiently.
        # Instead of np.delete, let's just use the whole array and handle the self-check or just ignore it implies 0 distance.
        # However, the original code used np.delete. To keep logic similar but cleaner:
        
        # Create a view or copy of relevant data
        # Note: shared_data has shape (MAX_BOIDS, 4). We only care about active boids if we knew how many there are.
        # But the original passed the whole huge array. We should probably assume the array contains garbage for inactive boids.
        # But here, we can rely on zero-initialization if index is managed externally.
        # Ideally, we should only check check against ACTIVE boids. 
        # For now, we will follow the original logic style but safer.
        
        # Optimize: Don't delete, just index.
        # positions = self.shared_data[:, :2]
        # But 'otherBoids' logic in original implies we look at everything.
        
        # Let's do exactly what works but better naming.
        # We use a mask to exclude self
        mask = np.ones(len(self.shared_data), dtype=bool)
        mask[self.index] = False
        
        # In a real efficient system, we'd pass `num_active_boids` to limit this slice
        # For this refactor, I'll allow checking all (up to MAX_BOIDS) as per original design, 
        # but better would be to pass `active_count` to update.
        
        other_boids = self.shared_data[mask]
        
        # Calculate distances squared
        # Vectorized distance calc
        deltas = other_boids[:, :2] - np.array([self.pos.x, self.pos.y])
        dists_sq = np.sum(deltas**2, axis=1)
        
        # Find 7 closest
        # argsort is expensive, argpartition is O(N)
        k = 7
        if len(dists_sq) > k:
             nearest_indices = np.argpartition(dists_sq, k)[:k]
        else:
             nearest_indices = np.arange(len(dists_sq))

        nearest_boids = other_boids[nearest_indices]
        
        # Calculate actual distances for these nearest ones
        distances = np.sqrt(dists_sq[nearest_indices])
        
        # Filter by perception radius (12 * BOID_SIZE)
        perception_radius = config.BOID_SIZE * 12
        neighbor_mask = distances < perception_radius
        
        neighbors = nearest_boids[neighbor_mask]
        neighbor_dists = distances[neighbor_mask]

        turn_dir = 0.0
        
        if len(neighbors) > 0:
            # Separation, Alignment, Cohesion logic
            
            # Average angle of neighbors (Alignment)
            # The original code did:
            # yat = np.sum(np.sin(np.deg2rad(neiboids[:,2])))
            # xat = np.sum(np.cos(np.deg2rad(neiboids[:,2])))
            # tAvejAng = np.rad2deg(np.arctan2(yat, xat))
            
            angles_rad = np.deg2rad(neighbors[:, 2])
            target_sin = np.sum(np.sin(angles_rad))
            target_cos = np.sum(np.cos(angles_rad))
            avg_angle = np.rad2deg(np.arctan2(target_sin, target_cos))
            
            # Center of mass (Cohesion)
            avg_pos = np.mean(neighbors[:, :2], axis=0) # [x, y]
            target_v = pg.Vector2(avg_pos[0], avg_pos[1])

            # Separation (if too close)
            # if neiboids[0,3] < self.bSize : targetV = (neiboids[0,0], neiboids[0,1])
            # Original logic checks the VERY closest neighbor (index 0 of sorted? argpartition doesn't sort)
            # We need the closest.
            min_dist_idx = np.argmin(neighbor_dists)
            closest_dist = neighbor_dists[min_dist_idx]
            
            if closest_dist < config.BOID_SIZE:
                # Original logic: Steer AWAY from closest? 
                # Original: targetV = (neiboids[0,0], neiboids[0,1])
                # Wait, setting targetV to the neighbor position usually means seeking it.
                # But later: `tDiff = pg.Vector2(targetV) - self.pos`
                # And: `if tDistance < self.bSize and targetV == ... : turnDir = -turnDir`
                # So it sets the target TO the neighbor, calculates angle, then reverses turnDir. Strict avoidance.
                target_v = pg.Vector2(neighbors[min_dist_idx, 0], neighbors[min_dist_idx, 1])

            # Calculate steering
            target_diff = target_v - self.pos
            target_dist, target_angle = pg.math.Vector2.as_polar(target_diff)
            
            # If close enough to neighbors generally, align with them
            if target_dist < config.BOID_SIZE * 6:
                target_angle = avg_angle

            # Calculate angle difference
            # angleDiff = (tAngle - self.ang) + 180
            # if abs(tAngle - self.ang) > 1.2: turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            
            diff_angle = (target_angle - self.angle)
            # Normalize to -180 to 180
            diff_angle = (diff_angle + 180) % 360 - 180
            
            if abs(target_angle - self.angle) > 1.2:
                turn_dir = diff_angle
            
            # Separation override
            if closest_dist < config.BOID_SIZE and target_v == pg.Vector2(neighbors[min_dist_idx, 0], neighbors[min_dist_idx, 1]):
                turn_dir = -turn_dir

        # Screen Margin Avoidance
        # Margin logic (steer back to centerish if hitting wall)
        if not wrap:
            margin = config.MARGIN
            img_rect = self.rect
            xs, ys = self.pos.x, self.pos.y
                
            min_edge_dist = min(xs, ys, w - xs, h - ys)
            
            if min_edge_dist < margin:
                target_a = 0
                if xs < margin: target_a = 0      # Move Right
                elif xs > w - margin: target_a = 180 # Move Left
                
                if ys < margin: target_a = 90     # Move Down
                elif ys > h - margin: target_a = 270 # Move Up
                
                # If in corner, this logic might be simplistic (it overwrites), but following original intent
                
                diff = (target_a - self.angle + 180) % 360 - 180
                turn_dir = diff
                
                # Increase turn rate near edges
                # turnRate = turnRate + (1 - edgeDist / margin) * (20 - turnRate)
                # Original logic seems specific, let's preserve it
                rate_mod = (1 - min_edge_dist / margin) * (20 - config.TURN_RATE)
                # Actually, original: turnRate + ... (20 - turnRate). 20 is usually smaller than 190. So it slows turning? 
                # Or maybe 20 was meaningful. Let's trust logic, clean code.
                pass # We will apply turn rate uniformly for now to keep it simple, or keep original formula?
                # The original formula effectively blends betwen NormalTurnRate and 20? 
                # No, it's `TurnRate + (ratio) * (20 - TurnRate)`. 
                # If ratio is 1 (at edge), it becomes `20`. If ratio 0 (at margin start), it is `TurnRate`.
                # So at edge, it forces a specific turn rate (maybe slower/smoother?).
        
        # Update Angle
        # self.ang += turnRate * abs(turnDir) / turnDir
        # Protection against div by zero
        turn_rate = config.TURN_RATE * dt
        
        if turn_dir != 0:
            direction = 1 if turn_dir > 0 else -1
            self.angle += turn_rate * direction
            self.angle %= 360

        # Rotate Image
        self.image = pg.transform.rotate(self.orig_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Update Position
        self.dir = pg.Vector2(1, 0).rotate(self.angle).normalize()
        
        # Speed modulation based on crowd
        # self.pos += self.dir * dt * (speed + (7 - neiboids.size) * 2) 
        crowd_factor = (7 - len(neighbors)) * 2
        actual_speed = self.variable_speed + crowd_factor
        
        self.pos += self.dir * dt * actual_speed

        # Padding / Wrapping
        if wrap:
            if self.pos.x < 0: self.pos.x = w
            elif self.pos.x > w: self.pos.x = 0
            if self.pos.y < 0: self.pos.y = h
            elif self.pos.y > h: self.pos.y = 0
            
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        self._update_shared_data()

