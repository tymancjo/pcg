import pygame
import random
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


import pcg


# PCG things

rows = 120
cols = 35


WIDTH = cols * 6
HEIGHT = rows * 6
FPS = 500

pixelCellW = int(WIDTH / cols)
pixelCellH = int(HEIGHT / rows)

theGrid = [
    [
        pcg.Cell(
            x=pixelCellW * x,
            y=pixelCellH * y,
            w=pixelCellW,
            h=pixelCellH,
            temperature=0,
        )
        for x in range(cols)
    ]
    for y in range(rows)
]

MT = np.zeros_like(theGrid) + 1
print(MT.shape)

timeV = []
maxTV = []

dt = 1 / 1.2
N = 1
dx = 0.01
g = 9.81
s = 0


copper = pcg.material()
copper.gas = False
copper.cp = 385  # J/kg.K
copper.Sigma = 400e-0  # W/m.K
copper.ro = 8830  # kg/m3

stell = pcg.material()
stell.gas = False
stell.cp = 0.88e3  # J/kg.K
stell.Sigma = 55e-20  # W/m.K
stell.ro = 8000  # kg/m3

# testing the obstacle made of steel.
# for cell in theGrid[5][15:35]:
#     cell.material = stell
#     # cell.gas = false
#     # cell.cp = 0.88e3  # j/kg.k
#     # cell.sigma = 55  # w/m.k
#     # cell.ro = 8000  # kg/m3
#     cell.updateData()

# testing the source cells made of copper
A = 40
a = 20
B = 15
startT = 00

bH = 3

srcCells = []

for r in [A + a, A + a + 5, 16 + A + a, 16 + A + a + 5, 32 + A + a, 32 + A + a + 5]:
    # for r in [A + 20, A + 30, A + 40]:
    for row in theGrid[r : r + bH]:
        for cell in row[B : B + 5 : 2]:
            cell.dP = 10  # W
            cell.material = copper
            # cell.gas = False
            # cell.cp = 1.46e3  # J/kg.K
            # cell.Sigma = 400  # W/m.k
            # cell.ro = 8940  # kg/m3
            cell.T = startT
            cell.updateData()
            srcCells.append(cell)
    if bH == 3:
        bH = 4
    else:
        bH = 3


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
font = pygame.font.Font(pygame.font.get_default_font(), 14)


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
isGas = pcg.powietrze
gravity = True
reading = 0
mouseR = mouseC = mouseCol = mouseRow = 0
simTime = 0
realstart_time = nowIs = pygame.time.get_ticks()

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
                isGas = stell

            if event.key == pygame.K_r:
                isGas = pcg.powietrze

            if event.key == pygame.K_h:

                sourceActive = not sourceActive

            if event.key == pygame.K_g:
                gravity = not gravity

            if event.key == pygame.K_p:
                if editMode:
                    plt.plot(timeV, maxTV)
                    plt.show()

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
                    theGrid[mouseRow][mouseCol].material = isGas
                    theGrid[mouseRow][mouseCol].updateData()
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
            if cell.gas:
                pygame.draw.rect(
                    screen, cell.color, pygame.Rect(cell.x, cell.y, cell.w, cell.h)
                )
            else:
                pygame.draw.rect(
                    screen,
                    cell.color,
                    pygame.Rect(cell.x + 1, cell.y + 1, cell.w - 2, cell.h - 2),
                )

    if not editMode:

        # if makeStep > N or simTime == 0:
        if True:
            currentMax = MT.max()
            pcg.airSimCond(theGrid, MT, cols, rows, g=gravity, dt=dt)
            pcg.borders(theGrid, hs=0.9, ht=1.0, h=0)

            makeStep = 0
            simTime += dt

            frameTime = (pygame.time.get_ticks() - nowIs) / 1000

            nowIs = pygame.time.get_ticks()

            frameRatio = dt / frameTime

            realTime = (nowIs - realstart_time) / 1000
            timeRatio = simTime / realTime

            timeV.append(simTime)
            maxTV.append(currentMax)

            s = g * (((currentMax + 35) / 35) - 1) * dt * dt
            N = math.floor(s / dx) + 1

            maxNup = 5
            if N > maxNup:
                dt = dt * maxNup / N
                s = g * (((currentMax + 35) / 35) - 1) * dt * dt
                N = math.floor(s / dx)

            # if sourceActive:
            #     theGrid[mouseRow][mouseCol].T += 100
            #     theGrid[mouseRow][mouseCol].update()

        for _ in range(N):
            pcg.airSimConv(theGrid, MT, cols, rows, g=gravity, dt=dt, maxT=currentMax)

        # reading = theGrid[mouseRow][mouseCol].T
        reading = MT[mouseRow][mouseCol]

        makeStep += 1

    else:
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0, 0, 20, 20))

    simH = math.floor(simTime / 3600)
    simMin = math.floor((simTime - simH * 3600) / 60)
    simSec = math.floor(simTime - simH * 3600 - simMin * 60)

    text_string = f"dT:{reading:.4f}K".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 0))

    text_string = f"maxT: {currentMax:.4f}K".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 15))

    text_string = f"time: {simH:02d}:{simMin:02d}:{simSec:02d}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 30))

    text_string = f"s: {1000*s:.2f}mm / {N}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 45))

    text_string = f"S/R: {timeRatio:.3f} / Fr{frameRatio:.2f}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 60))

    tick += deltaTick
    if tick > WIDTH - 60 or tick < 0:
        deltaTick *= -1
    ########################

    ## Done after drawing everything to the screen
    pygame.display.flip()

plt.plot(timeV, maxTV)
plt.show()

pygame.quit()
