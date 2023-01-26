import pygame
import math
import numpy as np
import matplotlib.pyplot as plt

import pcg_v2 as pcg
import materials as mt


# material database for the solver
# define the materials needed by making a list
materials = [mt.airCell, mt.steelCell, mt.copperCell, mt.waterCell]

# generating required arrays ###########################
m_name = [c.name for c in materials]
m_Rth = np.array([c.Rth for c in materials])
m_massCp = np.array([c.massCp for c in materials])
m_gas = np.array([c.gas for c in materials])
m_colors = [c.color for c in materials]
# ######################################################

# Simulation grid size definition
rows = 200
cols = 60

# display and pixel data
pixelSize = int(min(1000 / cols, 1000 / rows))
W0 = cols * pixelSize
H0 = rows * pixelSize
WIDTH = HEIGHT = max(W0, H0)
FPS = 500
BLACK = (0, 0, 0)
offset_pix_x = int((WIDTH - W0) / 2)
offset_pix_y = int((HEIGHT - H0) / 2)

pixelCellW = pW0 = int(W0 / cols)
pixelCellH = pH0 = int(H0 / rows)

screen_size0 = max(W0, H0)

# some handy data fo the navi panel
# Navi pane size
navi_size = 200  # px
navi_start = WIDTH
navi_left = navi_start + 10
WIDTH += navi_size

# Defining the world grid ###############
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


# ########################################
# pre processor to prepare the arrays
T, dP, m_ID, vV = pcg.pre_processor(theGrid)
dispVal = T


# initial global conditions ##############
dt = 1 / 10
N = 6
dx = theGrid[0][0].length
g = 9.81
s = 0
# keepers for the solution data for plot
timeV = [0]
maxTV = [0]

# needed global values ##############################
editMode = True  # we start in stopped mode
drawing = False  # for the track of edit behavior
zoom = 1
zoom_left = 0
zoom_right = cols
zoom_top = 0
zoom_bottom = rows

drawMode = 1
viewMode = 0
stepsToDraw = 10
simTime = 0
maxNup = 6
makeStep = 100
frameRatioV = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
frameRatio = 0
showPlot = True
colorsT = not True
plotSteps = 0
selected_material = 1
selectedCells = []
mouseR = mouseC = mouseCol = mouseRow = 0
dKeyCount = 0  # used to count "Q" presses for reset
nowIs = 0

move_vector = [0, 0]
move_frame = 0

# initial text to put on screen
reading = 0
powerloss = 0
material = m_name[selected_material]


## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Cell Grid")
clock = pygame.time.Clock()  ## For syncing the FPS
font = pygame.font.Font(pygame.font.get_default_font(), 12)


## Simulation animation main loop
running = True

while running:
    # 1 Process input/events
    clock.tick(FPS)  ## will make the loop run at the same speed all the time
    for event in pygame.event.get():
        # gets all the events which have occurred till now and keeps tab of them.
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False

        # keys used:
        # space - simulation/edit mode toggle
        # g - turn on/off gravity
        # v - cycle over view modes - result field with shapes, materials, just result field
        # p - [in edit mode] plots the temperature plot
        # w = [in edit mode] save the simulation data - will ask about filename in terminal
        # l - [in edit mode] loads the simulation data - will ask about filename in terminal
        # q - [in edit mode] if pressed 5 times reset the solution to initial state.
        # d - [in edit mode] toggle drawing mode from rectangle to paint mode
        # d - [in sim mode] toggle the result field [Temperature, Velocity]
        # z/x - zoom in and out
        #
        # 1 .. 4 - [in edit mode] select the Nth material from database
        # 1 - [in sim mode] decrease the maxN value
        # 2 - [in sim mode] increase the maxN value
        #
        # 7 - [in edit mode] increase selected cells power loss by 0.1
        # 8 - [in edit mode] increase selected cells power loss by 1
        # 9 - [in edit mode] increase selected cells power loss by 10
        # 0 - [in edit mode] rester selected cells power loss to 0

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                move_vector = [0, 0]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                editMode = not editMode

            if event.key == pygame.K_g:
                if g:
                    g = 0
                else:
                    g = 9.81

            if event.key == pygame.K_v:
                viewMode += 1
                if viewMode > 2:
                    viewMode = 0

            if event.key == pygame.K_p:
                if editMode:
                    plt.plot(timeV, maxTV)
                    plt.show()

            if event.key == pygame.K_w:
                if editMode:
                    dane = pcg.dataKeeper(
                        # [T, dP, Rth, massCp, gas, dt, g, timeV, maxTV]
                        [
                            T,
                            dP,
                            m_ID,
                            m_massCp,
                            m_Rth,
                            m_gas,
                            m_name,
                            m_colors,
                            dt,
                            g,
                            timeV,
                            maxTV,
                        ]
                    )
                    if pcg.save_data(dane):
                        print("Save successful!")
                    else:
                        print("Issue with making save!")

            if event.key == pygame.K_l:
                if editMode:
                    dane = pcg.load_data()
                    if dane:
                        (
                            T,
                            dP,
                            m_ID,
                            m_massCp,
                            m_Rth,
                            m_gas,
                            m_name,
                            m_colors,
                            dt,
                            g,
                            timeV,
                            maxTV,
                        ) = dane.get_data()
                        simTime = timeV[-1]

                        # just hacking the steel color:
                        m_colors[1] = (25, 25, 25)

            if event.key == pygame.K_q:
                if editMode:
                    dKeyCount += 1
                    if dKeyCount > 3:
                        dKeyCount = 0
                        timeV = [0]
                        maxTV = [0]
                        T[:, :] = 0.0
                        simTime = 0

            if event.key == pygame.K_d:
                if editMode:
                    drawMode += 1
                    if drawMode > 1:
                        drawMode = 0
                else:
                    if colorsT:
                        dispVal = vV
                        colorsT = False
                    else:
                        dispVal = T
                        colorsT = True

            if event.key == pygame.K_z:
                zoom += 1
                if zoom > 4:
                    zoom = 4

                # if zoom > 1:
                if True:
                    pixelCellH = pH0 * zoom
                    pixelCellW = pW0 * zoom

                    maxCellsCols = math.floor((screen_size0 / pixelCellW))
                    maxCellsRows = math.floor((screen_size0 / pixelCellH))

                    zoom_right = min(maxCellsCols, T.shape[1])
                    zoom_bottom = min(maxCellsRows, T.shape[0])

                    if zoom_left + zoom_right >= T.shape[1]:
                        zoom_left = T.shape[1] - zoom_right
                    if zoom_left >= zoom_right:
                        zoom_left = max(0, zoom_right - maxCellsCols)

                    if zoom_top + zoom_bottom >= T.shape[0]:
                        zoom_top = T.shape[0] - zoom_bottom
                    if zoom_top >= zoom_bottom:
                        zoom_top = max(0, zoom_bottom - maxCellsRows)

                print(f"zoom top {zoom_top, zoom_bottom}, left {zoom_left,zoom_right}")

            if event.key == pygame.K_x:
                zoom -= 1
                if zoom < 1:
                    zoom = 1

                if True:
                    pixelCellH = pH0 * zoom
                    pixelCellW = pW0 * zoom

                    maxCellsCols = math.floor((screen_size0 / pixelCellW))
                    maxCellsRows = math.floor((screen_size0 / pixelCellH))

                    zoom_right = min(maxCellsCols, T.shape[1])
                    zoom_bottom = min(maxCellsRows, T.shape[0])

                    if zoom_left + zoom_right >= T.shape[1]:
                        zoom_left = T.shape[1] - zoom_right
                    if zoom_left >= zoom_right:
                        zoom_left = max(0, zoom_right - maxCellsCols)

                    if zoom_top + zoom_bottom >= T.shape[0]:
                        zoom_top = T.shape[0] - zoom_bottom
                    if zoom_top >= zoom_bottom:
                        zoom_top = max(0, zoom_bottom - maxCellsRows)

                print(f"zoom top {zoom_top, zoom_bottom}, left {zoom_left,zoom_right}")

            if event.key == pygame.K_LEFT:
                move_vector[0] = -1

            if event.key == pygame.K_RIGHT:
                move_vector[0] = 1

            if event.key == pygame.K_UP:
                move_vector[1] = -1

            if event.key == pygame.K_DOWN:
                move_vector[1] = 1

            if event.key == pygame.K_1:
                if editMode:
                    selected_material = 0
                    if drawMode == 1:
                        thisID[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] = 0
                else:
                    maxNup = max(3, maxNup - 1)

            if event.key == pygame.K_2:
                if editMode:
                    selected_material = 1
                    if drawMode == 1:
                        thisID[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] = 1
                else:
                    maxNup = min(500, maxNup + 1)

            if event.key == pygame.K_3:
                if editMode:
                    selected_material = 2
                    if drawMode == 1:
                        thisID[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] = 2

            if event.key == pygame.K_4:
                if editMode:
                    selected_material = 3
                    if drawMode == 1:
                        thisID[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] = 3

            if event.key == pygame.K_7:
                if editMode:
                    if drawMode == 1:
                        this_dP[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] += 0.1

            if event.key == pygame.K_8:
                if editMode:
                    if drawMode == 1:
                        this_dP[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] += 1

            if event.key == pygame.K_9:
                if editMode:
                    if drawMode == 1:
                        this_dP[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] += 10

            if event.key == pygame.K_0:
                if editMode:
                    if drawMode == 1:
                        this_dP[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] = 0

        # handle MOUSEBUTTONUP
        if event.type == pygame.MOUSEBUTTONDOWN:

            pos = pygame.mouse.get_pos()
            mx, my = pos

            if mx < navi_start and (offset_pix_x <= mx and offset_pix_y <= my):
                mx -= offset_pix_x
                my -= offset_pix_y
                mouseRow = math.floor(my / pixelCellH)
                mouseCol = math.floor(mx / pixelCellW)
                drawing = True

        if event.type == pygame.MOUSEMOTION:

            pos = pygame.mouse.get_pos()
            mx, my = pos

            if mx < navi_start and (offset_pix_x <= mx and offset_pix_y <= my):
                mx -= offset_pix_x
                my -= offset_pix_y
                mouseR = math.floor(my / pixelCellH)
                mouseC = math.floor(mx / pixelCellW)
                print(mouseC, mouseR)

                if drawing:
                    # mouseRow, mouseCol = mouseR, mouseC
                    if editMode:
                        if drawMode == 0:
                            # just setting the given cell to a material
                            m_ID[mouseR][mouseC] = selected_material
                        elif drawMode == 1:
                            # drawing the rectangle
                            pass

                else:
                    # reading = dispVal[mouseR][mouseC]
                    pass

        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            mx, my = pos
            if mx < navi_start and (offset_pix_x <= mx and offset_pix_y <= my):
                drawing = False
                if drawMode > 0:
                    selectedCells = [mouseCol, mouseRow, mouseC, mouseR]

    # 3Draw/render step count - to not draw each calculation step
    makeStep += 1

    if makeStep > stepsToDraw or editMode:
        makeStep = 0

        # cleaning the screen
        pygame.draw.rect(
            screen, (10, 10, 10), pygame.Rect(0, 0, screen_size0, screen_size0)
        )

        if colorsT:
            dispVal = vV[zoom_top:zoom_bottom:, zoom_left:zoom_right:]
            currentMax = dispVal.max()
        else:
            dispVal = T[zoom_top:zoom_bottom:, zoom_left:zoom_right:]
            currentMax = dispVal.max()

        # ################### #
        # handling scrolling: #
        # ################### #
        move_frame += 1
        if move_frame == 1 and (move_vector[0] != 0 or move_vector[1] != 0):
            zoom_left += move_vector[0]
            zoom_left = max(
                0,
                min(zoom_left, T.shape[1] - math.floor(screen_size0 / pixelCellW)),
            )
            zoom_right = zoom_left + math.floor(screen_size0 / pixelCellW)

            zoom_top += move_vector[1]
            zoom_top = min(zoom_top, T.shape[0] - math.floor(screen_size0 / pixelCellH))
            zoom_top = max(0, zoom_top)
            zoom_bottom = zoom_top + math.floor(screen_size0 / pixelCellH)

        if move_frame > 5:
            move_frame = 0

        thisID = m_ID[zoom_top:zoom_bottom:, zoom_left:zoom_right:]
        this_dP = dP[zoom_top:zoom_bottom:, zoom_left:zoom_right:]
        rows, cols = dispVal.shape

        pixelCellH = pixelCellW = math.floor(
            min(screen_size0 / rows, screen_size0 / cols)
        )

        offset_pix_x = int((screen_size0 - pixelCellW * cols) / 2)
        offset_pix_y = int((screen_size0 - pixelCellH * rows) / 2)

        # drawing the colors of the temperatures
        for r in range(rows):
            for c in range(cols):
                pos_x = pixelCellW * c + offset_pix_x
                pos_y = pixelCellH * r + offset_pix_y

                if m_gas[thisID[r, c]] or viewMode == 2:
                    # avT = T[r, c - 1 : c + 2].sum() / 3
                    # color = pcg.getColor(avT, 0, currentMax)
                    color = pcg.getColor(dispVal[r, c], 0, currentMax)
                    if viewMode == 1:
                        color = m_colors[thisID[r, c]]

                    pygame.draw.rect(
                        screen,
                        color,
                        pygame.Rect(pos_x, pos_y, pixelCellW, pixelCellH),
                    )
                else:

                    color = pcg.getColor(dispVal[r, c], 0, currentMax)
                    pygame.draw.rect(
                        screen,
                        m_colors[thisID[r, c]],
                        pygame.Rect(pos_x, pos_y, pixelCellW, pixelCellH),
                    )
                    if viewMode != 1:
                        pygame.draw.rect(
                            screen,
                            color,
                            pygame.Rect(
                                pos_x + 1, pos_y + 1, pixelCellW - 2, pixelCellH - 2
                            ),
                        )

        if editMode:
            if drawing:
                # taking care of the edit drawings
                if drawMode == 1:
                    # rectangle stuff
                    Xs = mouseCol * pixelCellW + offset_pix_x
                    Ys = mouseRow * pixelCellH + offset_pix_y
                    Xe = mouseC * pixelCellW + offset_pix_x
                    Ye = mouseR * pixelCellH + offset_pix_y

                    for POS in [
                        (Xs, Ys, Xe, Ys),
                        (Xe, Ys, Xe, Ye),
                        (Xe, Ye, Xs, Ye),
                        (Xs, Ye, Xs, Ys),
                    ]:
                        pygame.draw.line(
                            screen,
                            (255, 25, 25),
                            (POS[0], POS[1]),
                            (POS[2], POS[3]),
                        )
            elif selectedCells and drawMode == 1:
                # rectangle stuff
                Xs = selectedCells[0] * pixelCellW + offset_pix_x
                Ys = selectedCells[1] * pixelCellH + offset_pix_y
                Xe = selectedCells[2] * pixelCellW + offset_pix_x
                Ye = selectedCells[3] * pixelCellH + offset_pix_y

                for POS in [
                    (Xs, Ys, Xe, Ys),
                    (Xe, Ys, Xe, Ye),
                    (Xe, Ye, Xs, Ye),
                    (Xs, Ye, Xs, Ys),
                ]:
                    pygame.draw.line(
                        screen,
                        (255, 255, 255),
                        (POS[0], POS[1]),
                        (POS[2], POS[3]),
                    )

    if not editMode:
        if True:

            vV[:, :] = 0  # clearing the velocity vector
            ######
            pcg.solve_cond_with_v(T, dP, vV, m_ID, m_massCp, m_Rth, m_gas, dx, dt, g)
            ######
            pcg.open_air_boundary(T, vV)
            ######

            simTime += dt

            frameTime = (pygame.time.get_ticks() - nowIs) / 1000
            nowIs = pygame.time.get_ticks()

            if frameTime != 0:
                frameRatio = dt / frameTime
            else:
                frameRatio = 0

            ##############
            # this piece is potentially slow - so maybe will be dropped
            frameRatioV.append(frameRatio)
            if len(frameRatioV) > 100:
                frameRatioV.pop(0)
            frameRatio = sum(frameRatioV) / len(frameRatioV)
            ################

            timeV.append(simTime)
            maxTV.append(T.max())

            s = vV.max() * dt

        if s > 0:
            pcg.solve_conv(T, m_ID, vV, m_gas, dx, N, dt)

            if s > dx / 2:
                N = math.floor(s / dx) + 1
                N = max(2, N)

                if N > maxNup:
                    dt = dt * maxNup / N
                    s = vV.max() * dt
                    N = math.floor(s / dx) + 1
                if N < maxNup and simTime > 30:
                    dt = dt * maxNup / N
                    s = vV.max() * dt
                    N = math.floor(s / dx) + 1

                # N = max(2, N)
                # if dt < 1 / 50_000:
                #     dt = 1 / 1000

        mouseRow = max(0, min(mouseRow, dispVal.shape[0] - 1))
        mouseCol = max(0, min(mouseCol, dispVal.shape[1] - 1))
        reading = dispVal[mouseRow][mouseCol]
        material = m_name[thisID[mouseRow][mouseCol]]
        powerloss = this_dP[mouseRow][mouseCol]

        # pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(navi_start, 0, 10, 10))
    else:
        pass
        # pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(navi_start, 0, 10, 10))

    # Navi pane
    color = (25, 75, 25)
    if editMode:
        color = (75, 25, 25)
    pygame.draw.rect(
        screen, color, pygame.Rect(navi_start, 0, navi_size, HEIGHT - 10 - 150)
    )

    if showPlot:
        # making the mini plot of the max temp history.
        plotSteps += 1
        if plotSteps > 100:
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                pygame.Rect(navi_start, HEIGHT - 10 - 150, navi_size, 160),
            )
            plotSteps = 0
            # the number of points:
            plot_dt = max(1, math.floor(len(maxTV) / (navi_size - 20)))
            plot_height = 150  # px
            if max(maxTV) > 0:
                plot_scale = plot_height / (max(maxTV) - min(maxTV))
            else:
                plot_scale = 0

            plot_y = HEIGHT - 10

            pygame.draw.line(
                screen,
                (125, 125, 125),
                (navi_left, plot_y),
                (navi_left, plot_y - plot_height),
            )
            pygame.draw.line(
                screen,
                (125, 125, 125),
                (navi_left, plot_y),
                (navi_left + navi_size, plot_y),
            )

            for i, t in enumerate(maxTV[::plot_dt]):
                x = navi_left + i
                y = plot_y - int(plot_scale * t)

                pygame.draw.line(screen, (255, 255, 255), (x, y), (x + 1, y))

    simH = math.floor(simTime / 3600)
    simMin = math.floor((simTime - simH * 3600) / 60)
    simSec = math.floor(simTime - simH * 3600 - simMin * 60)

    text_string = f"{material} dT:{reading:.2f}K dP:{powerloss:.1f}W".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, 0))

    text_string = f"maxT: {currentMax:.4f}K".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, 15))

    text_string = f"time: {simH:02d}:{simMin:02d}:{simSec:02d}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, 30))

    text_string = f"s: {1000*s:.2f}mm / {N} // {maxNup}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, 45))

    text_string = f" Fr {frameRatio:.2f} vm: {viewMode}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, 60))

    text_string = f"Selected: {m_name[selected_material]}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, 100))

    if editMode:
        text_string = f"Selecton: {abs(mouseCol - mouseC)}x{abs(mouseRow-mouseR)} @ Dm: {drawMode}".encode()
        text_surface = font.render(text_string, True, (255, 255, 255))
        screen.blit(text_surface, dest=(navi_left, 120))

    for i, mat in enumerate(m_name):
        text_string = f"{i+1}: {mat}".encode()
        text_surface = font.render(text_string, True, (255, 255, 255))
        screen.blit(text_surface, dest=(navi_left, 140 + 15 * i))

    ## Done after drawing everything to the screen
    pygame.display.flip()

# plt.plot(timeV, maxTV)
# plt.show()

pygame.quit()
