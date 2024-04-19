#!/usr/bin/env python3
from random import randint
import pygame as pg
import numpy as np
# Nguyễn Đắc Học 21020913 final
FLLSCRN = True
number_of_initial_boils = 50
WHITE = (255, 255, 255)
background = WHITE
number_boild_generate = 1
pos = (0,0)
WIDTH = 1000
HEIGHT = 800
BGCOLOR = (0, 0, 0) 
SPEED = 170 
WRAP = False

class BOILS(pg.sprite.Sprite):
    def __init__(self,boidNum, display_Sur, data) -> None: # boidNum: number of boils, display_sur = screen
        super().__init__()  
        self.data = data                               #data : pos, dir of boild
        self.display_Sur = display_Sur
        self.bnum = boidNum
        self.image = pg.Surface((15,15)).convert()
        boils_color = (randint(0,255), randint(0,255), randint(0,255), randint(0,255))
        self.color = boils_color
        if pg.mouse.get_pressed(num_buttons=3)[0]: # get position of a fish have generate from left click
            pos = pg.mouse.get_pos()
        self.rect = self.image.get_rect(center =(pos))
        self.ang = randint(0,360)
        pg.draw.polygon(self.image, self.color,((7,0),(12,5),(3,14),(11,14),(2,5),(7,0)))
        self.dir = pg.Vector2(1, 0)
        self.bSize = 17
        self.pos = pg.Vector2(self.rect.center)
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)
    def update(self,dt,speed, ejWrap=False) -> None:
        W, H = self.display_Sur.get_size()
        turnDir = xvt = yvt = yat = xat = 0
        turnRate = 190 * dt
        margin = 42 #The margin value determines how close the boid can get to the screen edge before adjusting its behavior.
        otherBoids = np.delete(self.data, self.bnum, 0)
        array_dists = (self.pos.x - otherBoids[:,0])**2 + (self.pos.y - otherBoids[:,1])**2
        closeBoidIs = np.argsort(array_dists)[:7] # sort the array to get 7 boils nearby
        neiboids = otherBoids[closeBoidIs]
        neiboids[:,3] = np.sqrt(array_dists[closeBoidIs])
        neiboids = neiboids[neiboids[:,3] < self.bSize*12]
        if neiboids.size > 1:  # if has neighborS, do math and sim rules
            yat = np.sum(np.sin(np.deg2rad(neiboids[:,2])))
            xat = np.sum(np.cos(np.deg2rad(neiboids[:,2])))
            # averages the positions and angles of neighbors
            tAvejAng = np.rad2deg(np.arctan2(yat, xat))
            targetV = (np.mean(neiboids[:,0]), np.mean(neiboids[:,1]))
            # if too close, move away from closest neighbor
            if neiboids[0,3] < self.bSize : targetV = (neiboids[0,0], neiboids[0,1])
            # get angle differences for steering
            tDiff = pg.Vector2(targetV) - self.pos
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)
            # if boid is close enough to neighbors, match their average angle
            if tDistance < self.bSize*6 : tAngle = tAvejAng
            # computes the difference to reach target angle, for smooth steering
            angleDiff = (tAngle - self.ang) + 180
            if abs(tAngle - self.ang) > 1.2: turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            # if boid gets too close to target, steer away
            if tDistance < self.bSize and targetV == (neiboids[0,0], neiboids[0,1]) : turnDir = -turnDir
        # Avoid edges of screen by turning toward the edge normal-angle
        if not ejWrap and min(self.pos.x, self.pos.y, W - self.pos.x, H - self.pos.y) < margin:
            if self.pos.x < margin : tAngle = 0
            elif self.pos.x > W - margin : tAngle = 180
            if self.pos.y < margin : tAngle = 90
            elif self.pos.y > H - margin : tAngle = 270
            angleDiff = (tAngle - self.ang) + 180  # if in margin, increase turnRate to ensure stays on screen
            turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            edgeDist = min(self.pos.x, self.pos.y, W - self.pos.x, H - self.pos.y)
            turnRate = turnRate + (1 - edgeDist / margin) * (20 - turnRate) #minRate+(1-dist/margin)*(maxRate-minRate)
        if turnDir != 0:  # steers based on turnDir, handles left or right
            self.ang += turnRate * abs(turnDir) / turnDir
            self.ang %= 360  # ensures that the angle stays within 0-360
        # Adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.orig_image, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        self.dir = pg.Vector2(1, 0).rotate(self.ang).normalize()
        self.pos += self.dir * dt * (speed + (7 - neiboids.size) * 2)  # movement speed
        # Optional screen wrap
        if ejWrap and not self.drawSurf.get_rect().contains(self.rect):
            if self.rect.bottom < 0 : self.pos.y = H
            elif self.rect.top > H : self.pos.y = 0
            if self.rect.right < 0 : self.pos.x = W
            elif self.rect.left > W : self.pos.x = 0
        # Actually update position of boid
        self.rect.center = self.pos
        # Finally, output pos/ang to array
        self.data[self.bnum,:3] = [self.pos[0], self.pos[1], self.ang]
def main():
    pg.init()
    initial_boils = 1
    number_boild_generate = 1
    clock = pg.time.Clock()
    if FLLSCRN: # full screen mode or not
        curren_sceen = (pg.display.Info().current_w,pg.display.Info().current_h)
        screen = pg.display.set_mode((curren_sceen), pg.SCALED)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
    nBoids = pg.sprite.Group()
    #dataArray = Save_boild()
    dataArray = np.zeros((500,4),dtype=float)
    while True:
        for event in pg.event.get():
            if event.type is pg.QUIT:
                return
        if pg.mouse.get_pressed(num_buttons=3)[0]:
            nBoids.add(BOILS(number_boild_generate,screen, dataArray)) 
            number_boild_generate +=1
        screen.fill(BGCOLOR)
        dt = clock.tick(60)/1000
        nBoids.update(dt, SPEED, WRAP)
        nBoids.draw(screen)
        pg.display.update()
if __name__ == '__main__':
    main()
    pg.quit()