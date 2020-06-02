# https:#lodev.org/cgtutor/raycasting3.html
import pygame,sys
from pygame.locals import *
import math
import time

import gameWindow

# my additions, to seperate the animation from the keypress, causing a trigger
left_rotation_trigger = 0
right_rotation_trigger = 0
move_trigger = 0
redraw_pos = 1

map3= [
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,1,0,1,0,1,0,0,0,1,0,0,1,1,0,1,0,1],
[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,1,1,0,1],
[1,0,0,1,0,1,0,0,1,0,0,1,0,0,1,1,1,1,0,1],
[1,0,0,1,0,1,1,0,1,0,0,1,0,0,1,0,0,1,0,1],
[1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1],
[1,0,0,0,1,0,1,0,1,0,0,1,0,0,0,0,0,1,0,1],
[1,0,0,0,1,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1],
[1,0,0,0,1,1,1,0,1,0,0,1,0,0,1,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,1,0,1,0,1,0,0,0,1,0,0,1,1,0,1,0,1],
[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,1],
[1,0,0,1,0,1,0,1,0,0,0,1,0,0,1,1,0,1,0,1],
[1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,1],
[1,0,0,1,0,1,0,1,0,0,0,1,0,0,1,1,0,1,0,1],
[1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,1],
[1,0,0,1,0,1,0,1,0,0,0,1,0,0,1,1,0,1,0,1],
[1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],				
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

CLOCK=pygame.time.Clock()

pygame.init()
screen = gameWindow.gameWindow(640, 480, "Permidi Raycast Tutorial")
screen.loadMapSegment(map3)
#screen.placePlayer(1.5*screen.TILE_SIZE, 2.5*screen.TILE_SIZE, 0)
screen.placePlayer(100, 160, screen.ANGLE90)

#the following toggle options
screen.toggleFloor()        # doDrawFloor defaults off, toggle it on
screen.toggleBackground()   # doDrawBackground defaults off, toggle it on
#screen.toggleCeiling()   # doDrawBackground defaults off, toggle it on
#screen.toggleShadow()   # doDrawBackground defaults off, toggle it on

# initialize movement keys
move_trigger = 0
left_rotation_trigger = 0
right_rotation_trigger = 0

while True:
    
    #loop speed limitation
    #30 frames per second is enough
    CLOCK.tick(30)
    for event in pygame.event.get():    #wait for events
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if redraw_pos > 0:
        redraw_pos = 0
        screen.clearScreen()
        screen.drawBackground()
        screen.drawOverheadMap()
        screen.raycast()
        pygame.display.update()

    screen.playerArcDelta=0

    if keys[K_LEFT]:
        screen.fPlayerArc-=screen.ANGLE5
        screen.playerArcDelta=-screen.ANGLE5
        if (screen.fPlayerArc<screen.ANGLE0):
            screen.fPlayerArc+=screen.ANGLE360
        redraw_pos = 1
    elif keys[K_RIGHT]:
        screen.fPlayerArc+=screen.ANGLE5
        screen.playerArcDelta=screen.ANGLE5
        if (screen.fPlayerArc>=screen.ANGLE360):
                screen.fPlayerArc-=screen.ANGLE360
        redraw_pos = 1
    screen.fBackgroundImageArc-=screen.playerArcDelta
    if (screen.doDrawBackground):
        # panoramic view, no ceiling
        if (screen.fBackgroundImageArc<-screen.PROJECTIONPLANEWIDTH*2):
                screen.fBackgroundImageArc=screen.PROJECTIONPLANEWIDTH*2+(screen.fBackgroundImageArc);
        elif (screen.fBackgroundImageArc>0):
                screen.fBackgroundImageArc=-(960-screen.PROJECTIONPLANEWIDTH- (screen.fBackgroundImageArc));			

    #  _____     _
    # |\ arc     |
    # |  \       y
    # |    \     |
    #            -
    # |--x--|  
    #
    #  sin(arc)=y/diagonal
    #  cos(arc)=x/diagonal   where diagonal=speed
    playerXDir=screen.fCosTable[screen.fPlayerArc]
    playerYDir=screen.fSinTable[screen.fPlayerArc]

    dx=0
    dy=0

    if keys[K_UP]:
        dx=round(playerXDir*screen.fPlayerSpeed)
        dy=round(playerYDir*screen.fPlayerSpeed)
        redraw_pos = 1
    elif keys[K_DOWN]:
        dx=-round(playerXDir*screen.fPlayerSpeed);
        dy=-round(playerYDir*screen.fPlayerSpeed);
        redraw_pos = 1

    if (dx != 0 or dy != 0):
#        print("we are moving")

        playerXCell = math.floor((screen.fPlayerX+dx)/screen.TILE_SIZE)
        playerYCell = math.floor((screen.fPlayerY+dy)/screen.TILE_SIZE)

        if (screen.fMap[playerYCell][playerXCell] > 0):
            print("blocked by a wall")
        else:
            screen.fPlayerX+=dx
            screen.fPlayerY+=dy
    
        screen.fPlayerMapX=screen.PROJECTIONPLANEWIDTH+((screen.fPlayerX/screen.TILE_SIZE) * screen.fMinimapWidth);
        screen.fPlayerMapY=((screen.fPlayerY/screen.TILE_SIZE) * screen.fMinimapWidth);
            
