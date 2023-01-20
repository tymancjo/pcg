import pygame
import math
import numpy as np
import matplotlib.pyplot as plt


import pcg_fast as pcg


# PCG things
rows = 200
cols = 60

WIDTH = cols * 6
HEIGHT = rows * 6
FPS = 500
BLACK = (0, 0, 0)

pixelCellW = int(WIDTH / cols)
pixelCellH = int(HEIGHT / rows)

# Defining the world
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


# initial global conditions
dt = 1 / 10
N = 6
dx = theGrid[0][0].length
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
stell.Sigma = 55  # W/m.K
stell.ro = 8000  # kg/m3

steelCell = pcg.Cell()
steelCell.material = stell
steelCell.length = 2e-3
steelCell.updateData()

airCell = pcg.Cell()

# testing the obstacle made of steel.
# for cell in theGrid[5][15:35]:
#     cell.material = stell
#     # cell.gas = false
#     # cell.cp = 0.88e3  # j/kg.k
#     # cell.sigma = 55  # w/m.k
#     # cell.ro = 8000  # kg/m3
#     cell.updateData()

# testing the source cells made of copper
A = 50
a = 20
B = 40
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

loads = []

a = 8
b = 5.6
c = 8
d = 16.5
e = 13
f = 16.5
loads1 = [a, b, c, a, b, c, a, b, c, d, e, f, d, e, f, d, e, f, d, e, f]
loads.extend(loads1)

a = 14.7
b = 9.7
c = 14.7
d = 16.5
e = 14
f = 16.5
loads1 = [a, b, c, a, b, c, a, b, c, d, e, f, d, e, f, d, e, f, d, e, f]
loads.extend(loads1)

a = 21.3
b = 15
c = 21.3
d = 7.7
e = 5.75
f = 7.7
loads1 = [a, b, c, a, b, c, a, b, c, d, e, f, d, e, f, d, e, f, d, e, f]
loads.extend(loads1)

for n, cell in enumerate(srcCells):
    cell.dP = loads[n]


## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Cell Grid")
clock = pygame.time.Clock()  ## For syncing the FPS
font = pygame.font.Font(pygame.font.get_default_font(), 14)


## Game loop
running = True

sourceActive = False
editMode = False
drawing = False
isGas = True
reading = 0
mouseR = mouseC = mouseCol = mouseRow = 0
simTime = 0
realstart_time = nowIs = pygame.time.get_ticks()
maxNup = 6
makeStep = 100

# q = input("Load any data? ")
q = ""
if any(c in ["y", "Y", "t", "T"] for c in q):
    dane = pcg.load_data()
    if dane:
        T, dP, Rth, massCp, gas, dt, g, timeV, maxTV = dane.get_data()
        simTime = timeV[-1]
else:
    ### Array based solution thing
    # pre processor to prepare the arrays
    T, dP, Rth, massCp, gas = pcg.pre_processor(theGrid)
    print(f"Array shape: {T.shape}")
    # keepers for the solution data for plot
    timeV = []
    maxTV = []


while running:
    # 1 Process input/events
    clock.tick(FPS)  ## will make the loop run at the same speed all the time
    for (
        event
    ) in (
        pygame.event.get()
    ):  # gets all the events which have occurred till now and keeps tab of them.
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
                if g:
                    g = 0
                else:
                    g = 9.81

            if event.key == pygame.K_p:
                if editMode:
                    plt.plot(timeV, maxTV)
                    plt.show()

            if event.key == pygame.K_w:
                if editMode:
                    dane = pcg.dataKeeper(
                        [T, dP, Rth, massCp, gas, dt, g, timeV, maxTV]
                    )
                    if pcg.save_data(dane):
                        print("Save successful!")
                    else:
                        print("Issue with making save!")

            if event.key == pygame.K_l:
                if editMode:
                    dane = pcg.load_data()
                    if dane:
                        T, dP, Rth, massCp, gas, dt, g, timeV, maxTV = dane.get_data()
                        simTime = timeV[-1]

            if event.key == pygame.K_1:
                maxNup = max(3, maxNup - 1)

            if event.key == pygame.K_2:
                maxNup = min(500, maxNup + 1)

            if event.key == pygame.K_d:
                if editMode:
                    if "y" in input("y-to confirm "):
                        timeV = []
                        maxTV = []

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

                    gas[mouseRow][mouseCol] = isGas
                    if isGas:
                        Rth[mouseRow][mouseCol] = airCell.Rth
                        massCp[mouseRow][mouseCol] = airCell.massCp
                    else:
                        Rth[mouseRow][mouseCol] = steelCell.Rth
                        massCp[mouseRow][mouseCol] = steelCell.massCp

            else:
                reading = T[mouseR][mouseC]

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

    # 3 Draw/render
    makeStep += 1

    ### Your code comes here
    # Initializing Color

    currentMax = T.max()

    if makeStep > 5 or editMode:
        makeStep = 0

        screen.fill(BLACK)

        rows, cols = T.shape
        for r in range(rows):
            for c in range(cols):
                pos_x = pixelCellW * c
                pos_y = pixelCellH * r
                if gas[r, c]:
                    avT = T[r, c - 1 : c + 2].sum() / 3
                    color = pcg.getColor(avT, 0, currentMax)
                    pygame.draw.rect(
                        screen,
                        color,
                        pygame.Rect(pos_x, pos_y, pixelCellW, pixelCellH),
                    )
                else:
                    color = pcg.getColor(T[r, c], 0, currentMax)
                    pygame.draw.rect(
                        screen,
                        (0, 0, 0),
                        pygame.Rect(pos_x, pos_y, pixelCellW, pixelCellH),
                    )
                    pygame.draw.rect(
                        screen,
                        color,
                        pygame.Rect(
                            pos_x + 1, pos_y + 1, pixelCellW - 2, pixelCellH - 2
                        ),
                    )

    if not editMode:
        if True:

            ######
            pcg.solve_cond(T, dP, massCp, Rth, dt)
            ######
            pcg.open_air_boundary(T)
            ######

            simTime += dt

            frameTime = (pygame.time.get_ticks() - nowIs) / 1000

            nowIs = pygame.time.get_ticks()

            if frameTime != 0:
                frameRatio = dt / frameTime
            else:
                frameRatio = 0

            realTime = (nowIs - realstart_time) / 1000
            timeRatio = simTime / realTime

            timeV.append(simTime)
            maxTV.append(currentMax)

            s = g * (((currentMax + 35) / 35) - 1) * dt * dt
            N = math.floor(s / dx) + 1
            N = max(2, N)

            if N > maxNup:
                dt = dt * maxNup / N
                s = g * (((currentMax + 35) / 35) - 1) * dt * dt
                N = math.floor(s / dx) + 1
            if N < maxNup and simTime > 30:
                dt = dt * maxNup / N
                s = g * (((currentMax + 35) / 35) - 1) * dt * dt
                N = math.floor(s / dx) + 1

            N = max(2, N)
            if dt < 1 / 50_000:
                dt = 1 / 1000

        for _ in range(N):
            pcg.solve_conv(T, gas, dt)

        # reading = theGrid[mouseRow][mouseCol].T
        reading = T[mouseRow][mouseCol]

    else:
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0, 0, 20, 20))

    simH = math.floor(simTime / 3600)
    simMin = math.floor((simTime - simH * 3600) / 60)
    simSec = math.floor(simTime - simH * 3600 - simMin * 60)

    pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, 150, 100))

    text_string = f"dT:{reading:.4f}K".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 0))

    text_string = f"maxT: {currentMax:.4f}K".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 15))

    text_string = f"time: {simH:02d}:{simMin:02d}:{simSec:02d}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 30))

    text_string = f"s: {1000*s:.2f}mm / {N} // {maxNup}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 45))

    text_string = f"S/R: {timeRatio:.3f} / Fr{frameRatio:.2f}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(0, 60))

    # tick += deltaTick
    # if tick > WIDTH - 60 or tick < 0:
    #     deltaTick *= -1
    ########################

    ## Done after drawing everything to the screen
    pygame.display.flip()

plt.plot(timeV, maxTV)
plt.show()

pygame.quit()
