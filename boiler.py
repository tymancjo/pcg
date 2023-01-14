import pygame
import random
import math

import pcg


# PCG things

rows = 50
cols = 50


WIDTH = int(800 / cols) * cols
HEIGHT = int(800 / rows) * rows
FPS = 200

pixelCellW = int(WIDTH / cols)
pixelCellH = int(HEIGHT / rows)

theGrid = [
    [
        pcg.Cell(
            x=pixelCellW * x,
            y=pixelCellH * y,
            w=pixelCellW,
            h=pixelCellH,
            temperature=0 * random.random() * 254,
        )
        for x in range(cols)
    ]
    for y in range(rows)
]


# testing the obstacle
for cell in theGrid[23][30:45]:
    cell.gas = False
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
clock = pygame.time.Clock()  ## For syncing the FPS
font = pygame.font.Font(pygame.font.get_default_font(), 20)


## group all the sprites together for ease of update
# all_sprites = pygame.sprite.Group()

## Game loop
running = True

tick = 0
deltaTick = 5
makeStep = 0
sourceActive = False
editMode = False
drawing = False
subSteps = 1
isGas = False
gravity = True
reading = 0
mouseR = mouseC = 0

# cell = pcg.Cell()
# cell.T = 100
# cell.update()

while running:
    # 1 Process input/events
    clock.tick(FPS)  ## will make the loop run at the same speed all the time
    for (
        event
    ) in (
        pygame.event.get()
    ):  # gets all the events which have occured till now and keeps tab of them.
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

            if event.key == pygame.K_s:
                isGas = False

            if event.key == pygame.K_r:
                isGas = True

            if event.key == pygame.K_h:

                sourceActive = not sourceActive

            if event.key == pygame.K_g:
                gravity = not gravity

        # handle MOUSEBUTTONUP
        if event.type == pygame.MOUSEBUTTONDOWN:

            pos = pygame.mouse.get_pos()

            mouseRow = math.floor(pos[1] / pixelCellH)
            mouseCol = math.floor(pos[0] / pixelCellW)

            drawing = True

            if not editMode:
                if event.button == 1:
                    sourceActive = True
                else:
                    sourceActive = not True

        if event.type == pygame.MOUSEMOTION:

            pos = pygame.mouse.get_pos()

            mouseR = math.floor(pos[1] / pixelCellH)
            mouseC = math.floor(pos[0] / pixelCellW)

            if drawing:
                mouseRow, mouseCol = mouseR, mouseC
                if editMode:
                    theGrid[mouseRow][mouseCol].gas = isGas
                    theGrid[mouseRow][mouseCol].update()

            else:
                reading = theGrid[mouseR][mouseC].T

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

    # 3 Draw/render
    screen.fill(BLACK)

    ### Your code comes here
    # Initializing Color
    color = pcg.getColor(tick, 0, WIDTH)

    # pygame.draw.rect(screen, color, pygame.Rect(tick, 30, 60, 60))

    for row in theGrid:
        for cell in row:
            pygame.draw.rect(
                screen, cell.color, pygame.Rect(cell.x, cell.y, cell.w, cell.h)
            )

    # if makeStep > 1:
    if not editMode:
        for _ in range(subSteps):
            ht = rows * cols * (0.5 / 40000)

            pcg.segregator2(theGrid, cols, rows, ht=ht, g=gravity)
            pcg.borders(theGrid, hs=0.02, ht=1, h=0)

            if sourceActive:
                theGrid[mouseRow][mouseCol].T += 100
                theGrid[mouseRow][mouseCol].update()

            reading = theGrid[mouseR][mouseC].T

            text_surface = font.render(str(reading).encode(), True, (0, 0, 0))
            screen.blit(text_surface, dest=(0, 0))

    else:
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0, 0, 20, 20))

    makeStep += 1

    tick += deltaTick
    if tick > WIDTH - 60 or tick < 0:
        deltaTick *= -1
    ########################

    ## Done after drawing everything to the screen
    pygame.display.flip()

pygame.quit()
