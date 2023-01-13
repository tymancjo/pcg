
import pygame
import random
import math

import pcg




WIDTH = 800
HEIGHT = 800
FPS = 200

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Cell Grid")
clock = pygame.time.Clock()     ## For syncing the FPS


## group all the sprites together for ease of update
# all_sprites = pygame.sprite.Group()

# PCG things

rows = 100
cols = 100

pixelCellW = int(WIDTH / cols)
pixelCellH = int(HEIGHT / rows)

theGrid = [[pcg.Cell(x=pixelCellW*x, y=pixelCellH*y, w=pixelCellW,h=pixelCellH, temperature=0*random.random()*254) for x in range(cols) ] for y in range(rows)]


# testing the obstacle
for cell in theGrid[23][30:45]:
    cell.gas = False

## Game loop
running = True

tick = 0
deltaTick = 5
makeStep = 0
sourceActive = False
editMode = False
subSteps = 1

#cell = pcg.Cell()
#cell.T = 100
#cell.update()

while running:
    #1 Process input/events
    clock.tick(FPS)     ## will make the loop run at the same speed all the time
    for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                editMode = not editMode

                if editMode and sourceActive:
                    sourcePos = (mouseRow, mouseCol)
                
                if not editMode and sourceActive:
                    mouseRow, mouseCol = sourcePos
                    


        # handle MOUSEBUTTONUP
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()

            mouseRow = math.floor(pos[1] / pixelCellH)
            mouseCol = math.floor(pos[0] / pixelCellW)

            if editMode:
                theGrid[mouseRow][mouseCol].gas = not theGrid[mouseRow][mouseCol].gas 

                theGrid[mouseRow][mouseCol].update()
            
            else:
                if event.button == 1:
                    sourceActive = True
                else:
                    sourceActive = False

                    
            



    #3 Draw/render
    screen.fill(BLACK)

    


    ### Your code comes here
    # Initializing Color
    color = pcg.getColor(tick, 0, WIDTH)

    #pygame.draw.rect(screen, color, pygame.Rect(tick, 30, 60, 60))

    for row in theGrid:
        for cell in row:
            pygame.draw.rect(screen, cell.color, pygame.Rect(cell.x, cell.y, cell.w, cell.h))

    #if makeStep > 1:
    if not editMode:
        for _ in range(subSteps):
            pcg.segregator(theGrid, cols, rows, ht=0.005)
            pcg.borders(theGrid, hs=0.01, ht=0, h=0)

            if sourceActive:
                theGrid[mouseRow][mouseCol].T += 100
                theGrid[mouseRow][mouseCol].update()

    else:
        pygame.draw.rect(screen,(255,0,0),pygame.Rect(0,0,20,20))

    makeStep += 1


    tick += deltaTick
    if tick > WIDTH - 60 or tick < 0:
        deltaTick *= -1
    ########################

    ## Done after drawing everything to the screen
    pygame.display.flip()       

pygame.quit()



