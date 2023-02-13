import pygame
import math
import numpy as np

import matplotlib.pyplot as plt
import plotly.graph_objects as go

import pcg_v2 as pcg
import materials as mt
import cmap as cc


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
rows = 300
cols = 60

# display and pixel data
pixelSize = int(min(1000 / cols, 1000 / rows))
W0 = cols * pixelSize
H0 = rows * pixelSize
WIDTH = HEIGHT = max(W0, H0)
FPS = 2000
BLACK = (0, 0, 0)
offset_pix_x = int((WIDTH - W0) / 2)
offset_pix_y = int((HEIGHT - H0) / 2)

pixelCellW = pW0 = int(W0 / cols)
pixelCellH = pH0 = int(H0 / rows)

screen_size0 = max(W0, H0)
grid_size = int(screen_size0 / pixelSize)

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
this_slice = 0
number_of_slices = 1
slice_size = 1000


# initial global conditions ##############
dt = 1 / 1000
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

drawMode = 0
viewMode = 0
stepsToDraw = 1
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
fieldDrawMode = 0
filedName = "Delta T [K]"
fast_display = 0
front_display = False

move_vector = [0, 0]
move_frame = 0


# initial text to put on screen
reading = 0
powerloss = 0
material = m_name[selected_material]
source_power = 0

# vectorization of functions
CLRS = np.array(cc.cmap)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()  # For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Cell Grid")
clock = pygame.time.Clock()  # For syncing the FPS
font = pygame.font.Font(pygame.font.get_default_font(), 12)


# Simulation animation main loop
running = True

while running:
    # 1 Process input/events
    clock.tick(FPS)  # will make the loop run at the same speed all the time
    for event in pygame.event.get():
        # gets all the events which have occurred till now and keeps tab of them.
        # listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False

        # keys used:
        # space - simulation/edit mode toggle
        # g - turn on/off gravity
        # v - cycle over view modes - result field with shapes, materials, just result field
        # f - cycle over normal and fast (grayscale) field display mode
        # p - [in edit mode] plots the temperature plot
        # SHIFT p - [in edit mode] plots the 3d temperature volumetric plot
        # w = [in edit mode] save the simulation data - will ask about filename in terminal
        # l - [in edit mode] loads the simulation data - will ask about filename in terminal
        # q - [in edit mode] if pressed 5 times reset the solution to initial state.
        # d - [in edit mode] toggle drawing mode from rectangle to paint mode
        # d - [in sim mode] toggle the result field [Temperature, Velocity]
        # SHIFT c - crop the analysis domain to marked size

        # z/x - zoom in and out
        # arrow keys - moving canvas in zoom mode
        #
        # 1 .. 4 - [in edit mode] select the Nth material from database
        # 1 - [in sim mode] decrease the maxN value
        # 2 - [in sim mode] increase the maxN value
        #
        # 7 - [in edit mode] increase (decrease with Shift) defined source power loss by 0.1
        # 8 - [in edit mode] increase (decrease with Shift) defined source power loss by 1
        # 9 - [in edit mode] increase (decrease with Shift) defined source power loss by 10
        # 0 - [in edit mode] reset defined source power loss to 0
        # ENTER - apply defined source dP value to selected cells

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                move_vector = [0, 0]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                editMode = not editMode

            if event.key == pygame.K_r:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    # resetting the simulation cavas and setup
                    grid_size = int(screen_size0 / pixelSize)
                    pixelCellH = pixelCellW = pixelSize

                    T = np.zeros((grid_size, grid_size))
                    vV = np.zeros((grid_size, grid_size))
                    dP = np.zeros((grid_size, grid_size))
                    m_ID = np.zeros((grid_size, grid_size)).astype(int)

                    dt = 1 / 1000
                    dx = 10e-3
                    g = 9.81
                    timeV = [0]
                    maxTV = [0]
                    simTime = 0

                    zoom = 1
                    zoom_left = zoom_top = 0
                    zoom_right = zoom_bottom = grid_size

            if event.key == pygame.K_RIGHTBRACKET:
                this_slice += 1
                if this_slice >= number_of_slices:
                    this_slice = number_of_slices - 1

            if event.key == pygame.K_LEFTBRACKET:
                this_slice -= 1
                this_slice = max(0, this_slice)

            if event.key == pygame.K_s:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    front_display = not front_display
                    if front_display:
                        front_display_row = min(mouseCol, mouseC)

                elif mods & pygame.KMOD_CTRL:
                    new_slice_size = float(
                        input(f"Set the slice size in mm [current: {slice_size}mm] :")
                    )
                    k = new_slice_size / slice_size
                    m_massCp = m_massCp * k
                    m_Rth = m_Rth * (1 / k)
                    dP = dP * k
                    dt *= k

                    slice_size = new_slice_size

                else:
                    T, dP, vV, m_ID = pcg.add_slice(T, dP, vV, m_ID, this_slice)

            if event.key == pygame.K_g:
                if g:
                    g = 0
                else:
                    g = 9.81

            if event.key == pygame.K_v:
                viewMode += 1
                if viewMode > 2:
                    viewMode = 0

            if event.key == pygame.K_f:
                fast_display += 1
                if fast_display > 2:
                    fast_display = 0

            if event.key == pygame.K_p:
                if editMode:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL:

                        pcg.plot_3d_plt(m_ID, T, CLRS, m_id=selected_material, slices=2)
                        # showing the voxel data on the copper elements
                        # filtering the array to only take the copper one into account

                        # m_ID_scaled = np.repeat(m_ID, 5, axis=2)
                        # copper_array = np.logical_or(m_ID_scaled == 2, m_ID_scaled == 1)
                        # T_scaled = np.repeat(T, 5, axis=2)

                        # indx = np.indices(copper_array.shape)

                        # colors_array = (
                        #     255 * T_scaled[tuple(indx)] / (T.max() + 1e-15)
                        # ).astype(int)

                        # # combine the color components
                        # colors = np.zeros(colors_array.shape + (3,))
                        # colors = CLRS[colors_array] / 255

                        # # copper_array = np.repeat(copper_array, 6, axis=2)
                        # # colors = np.repeat(colors_array, 6, axis=2)

                        # rot_axes = (2, 0)
                        # copper_array = np.rot90(copper_array, k=1, axes=rot_axes)
                        # colors = np.rot90(colors, k=1, axes=rot_axes)

                        # ax = plt.figure().add_subplot(projection="3d")
                        # ax.voxels(copper_array, facecolors=colors, edgecolor="none")
                        # ax.set_aspect("equal")
                        # plt.show()

                    elif mods & pygame.KMOD_SHIFT:
                        # showing the 3d volumetric plot of the temperature.
                        T_scaled = np.repeat(T, 5, axis=2)
                        # T_scaled = T
                        Tz, Ty, Tx = T_scaled.shape
                        Txyz_max = max(Tx, Ty, Tz)

                        X, Y, Z = np.mgrid[
                            :Tx,
                            :Ty,
                            :Tz,
                        ]
                        volume = T_scaled[Z, Y, X]

                        fig3d = go.Figure(
                            data=go.Volume(
                                x=X.flatten(),
                                y=Y.flatten(),
                                z=Z.flatten(),
                                value=volume.flatten(),
                                isomin=0,
                                isomax=T.max(),
                                opacity=0.1,
                                surface_count=22,
                                colorscale="Turbo",
                                # opacityscale=[[0, 0], [0.1, 0], [0.3, 1], [1.1]],
                            )
                        )
                        fig3d.update_layout(
                            scene={
                                "zaxis": {
                                    "autorange": "reversed"
                                },  # reverse automatically
                                # 'yaxis': {'range': (100, 0)},       # manually set certain range in reverse order
                            },
                            scene_aspectmode="manual",
                            scene_aspectratio=dict(
                                x=Tx / Txyz_max,
                                y=Ty / Txyz_max,
                                z=Tz / Txyz_max,
                            ),
                            width=800,
                            height=800,
                        )
                        fig3d.show()
                        pass

                    else:
                        # the 2d plot of max temperature
                        # plt.plot(timeV, maxTV)
                        # plt.show()
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=timeV, y=maxTV))
                        fig.show()

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
                        if T.ndim > 2:
                            number_of_slices = T.shape[2]
                        else:
                            number_of_slices = 1

                        # just hacking the steel color:
                        m_colors[1] = (25, 25, 25)
                        zoom = 1
                        zoom_left = zoom_top = 0
                        zoom_right = zoom_bottom = grid_size

            if event.key == pygame.K_c:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    # cropping the analysis doman size.
                    start_c = min(mouseC, mouseCol)
                    start_r = min(mouseR, mouseRow)
                    end_c = max(mouseC, mouseCol)
                    end_r = max(mouseR, mouseRow)

                    if T.ndim > 2:
                        T = T[start_r:end_r, start_c:end_c, :]
                        dP = dP[start_r:end_r, start_c:end_c, :]
                        m_ID = m_ID[start_r:end_r, start_c:end_c, :]
                    else:
                        T = T[start_r:end_r, start_c:end_c]
                        dP = dP[start_r:end_r, start_c:end_c]
                        m_ID = m_ID[start_r:end_r, start_c:end_c]

            if event.key == pygame.K_q:
                if editMode:
                    dKeyCount += 1
                    if dKeyCount > 3:
                        dKeyCount = 0
                        timeV = [0]
                        maxTV = [0]
                        T *= 0.0
                        vV * 0.0
                        simTime = 0

            if event.key == pygame.K_d:
                if editMode:
                    drawMode += 1
                    if drawMode > 1:
                        drawMode = 0
                else:
                    fieldDrawMode += 1
                    if fieldDrawMode > 2:
                        fieldDrawMode = 0

                    # if colorsT:
                    #     dispVal = vV
                    #     colorsT = False
                    # else:
                    #     dispVal = T
                    #     colorsT = True

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

                # print(f"zoom top {zoom_top, zoom_bottom}, left {zoom_left,zoom_right}")

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

                # print(f"zoom top {zoom_top, zoom_bottom}, left {zoom_left,zoom_right}")

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
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    source_power -= 0.1
                else:
                    source_power += 0.1

            if event.key == pygame.K_8:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    source_power -= 1
                else:
                    source_power += 1

            if event.key == pygame.K_9:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    source_power -= 10
                else:
                    source_power += 10

            if event.key == pygame.K_0:
                source_power = 0

            if event.key == pygame.K_RETURN:
                if editMode:
                    if drawMode == 1:
                        this_dP[
                            min(selectedCells[1], selectedCells[3]) : max(
                                selectedCells[1], selectedCells[3]
                            ),
                            min(selectedCells[0], selectedCells[2]) : max(
                                selectedCells[0], selectedCells[2]
                            ),
                        ] = source_power

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
                # print(mouseC, mouseR)

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

    if makeStep > (stepsToDraw) or editMode:
        makeStep = 0

        # cleaning the screen
        pygame.draw.rect(
            screen, (25, 25, 50), pygame.Rect(0, 0, screen_size0, screen_size0)
        )

        if T.ndim < 3:
            if fieldDrawMode == 0:
                dispVal = T[zoom_top:zoom_bottom:, zoom_left:zoom_right:]
                filedName = "Delta T [K]"
            elif fieldDrawMode == 1:
                dispVal = vV[zoom_top:zoom_bottom:, zoom_left:zoom_right:]
                filedName = "Velocity [m/s]"
            elif fieldDrawMode == 2:
                dispVal = dP[zoom_top:zoom_bottom:, zoom_left:zoom_right:]
                filedName = "Power Losses [W/m]"

            thisID = m_ID[zoom_top:zoom_bottom:, zoom_left:zoom_right:]
            this_dP = dP[zoom_top:zoom_bottom:, zoom_left:zoom_right:]

        else:
            # we have 3d arrays
            number_of_slices = T.shape[2]
            if this_slice >= number_of_slices:
                this_slice = number_of_slices - 1

            if fieldDrawMode == 0:
                dispVal = T[zoom_top:zoom_bottom:, zoom_left:zoom_right:, this_slice]
                filedName = "Delta T [K]"
            elif fieldDrawMode == 1:
                dispVal = vV[zoom_top:zoom_bottom:, zoom_left:zoom_right:, this_slice]
                filedName = "Velocity [m/s]"
            elif fieldDrawMode == 2:
                dispVal = dP[zoom_top:zoom_bottom:, zoom_left:zoom_right:, this_slice]
                filedName = "Power Losses [W/m]"

            thisID = m_ID[zoom_top:zoom_bottom:, zoom_left:zoom_right:, this_slice]
            this_dP = dP[zoom_top:zoom_bottom:, zoom_left:zoom_right:, this_slice]

        rows, cols = dispVal.shape
        if fieldDrawMode:
            currentMax = dispVal.max()
        else:
            currentMax = T.max()

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

        pixelCellH = pixelCellW = math.floor(
            min(screen_size0 / rows, screen_size0 / cols)
        )

        offset_pix_x = int((screen_size0 - pixelCellW * cols) / 2)
        offset_pix_y = int((screen_size0 - pixelCellH * rows) / 2)

        if fast_display > 0:
            # alternative way of main field plotting - try if this might be more efficient.
            # Idea - prepare a np array of colors and blit it to screen
            if fast_display == 1:
                # the full colormap
                normalizer_dispVal = np.clip(
                    255 * dispVal.T / (dispVal.max() + 1e-15), 0, 255
                ).astype(np.int16)

                R_to_blit = CLRS[normalizer_dispVal, 0]
                G_to_blit = CLRS[normalizer_dispVal, 1]
                B_to_blit = CLRS[normalizer_dispVal, 2]
            else:
                # the BW version
                normalizer_dispVal = 1 - (dispVal.T / (dispVal.max() + 1e-15))
                R_to_blit = normalizer_dispVal * 255
                G_to_blit = normalizer_dispVal * 255
                B_to_blit = normalizer_dispVal * 255

            RGB_to_blit = np.dstack([R_to_blit, G_to_blit, B_to_blit])
            RGB_to_blit = pygame.surfarray.make_surface(RGB_to_blit)
            RGB_to_blit = pygame.transform.scale(
                RGB_to_blit, (cols * pixelCellW, rows * pixelCellH)
            )
            screen.blit(RGB_to_blit, dest=(offset_pix_x, offset_pix_y))

        else:
            # drawing the colors of the temperatures
            for r in range(rows):
                for c in range(cols):
                    pos_x = pixelCellW * c + offset_pix_x
                    pos_y = pixelCellH * r + offset_pix_y

                    if thisID.ndim < 3:
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
                                        pos_x + 1,
                                        pos_y + 1,
                                        pixelCellW - 2,
                                        pixelCellH - 2,
                                    ),
                                )
                    else:
                        if m_gas[thisID[r, c, this_slice]] or viewMode == 2:
                            # avT = T[r, c - 1 : c + 2].sum() / 3
                            # color = pcg.getColor(avT, 0, currentMax)
                            color = pcg.getColor(dispVal[r, c], 0, currentMax)
                            if viewMode == 1:
                                color = m_colors[thisID[r, c, this_slice]]

                            pygame.draw.rect(
                                screen,
                                color,
                                pygame.Rect(pos_x, pos_y, pixelCellW, pixelCellH),
                            )
                        else:

                            color = pcg.getColor(dispVal[r, c], 0, currentMax)
                            pygame.draw.rect(
                                screen,
                                m_colors[thisID[r, c, this_slice]],
                                pygame.Rect(pos_x, pos_y, pixelCellW, pixelCellH),
                            )
                            if viewMode != 1:
                                pygame.draw.rect(
                                    screen,
                                    color,
                                    pygame.Rect(
                                        pos_x + 1,
                                        pos_y + 1,
                                        pixelCellW - 2,
                                        pixelCellH - 2,
                                    ),
                                )
        if front_display and T.ndim > 2:
            # let's show the front back xcut of the system

            front_display_array = T[:, front_display_row, :]
            normalized_front_display_array = (
                255 * front_display_array.T / (T.max() + 1e-15)
            ).astype(np.int16)

            R_to_blit = CLRS[normalized_front_display_array, 0]
            G_to_blit = CLRS[normalized_front_display_array, 1]
            B_to_blit = CLRS[normalized_front_display_array, 2]

            RGB_to_blit = np.dstack([R_to_blit, G_to_blit, B_to_blit])
            RGB_to_blit = pygame.surfarray.make_surface(RGB_to_blit)
            RGB_to_blit = pygame.transform.scale(
                RGB_to_blit, (10 * number_of_slices * pixelCellW, rows * pixelCellH)
            )
            screen.blit(RGB_to_blit, dest=(0, offset_pix_y))

            hW = int(pixelCellW / 2) * 10

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                pygame.Rect(this_slice * 10 * pixelCellW + hW, 3, 1, rows * pixelCellH),
            )

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                pygame.Rect(
                    pixelCellW * front_display_row + offset_pix_x,
                    3,
                    1,
                    rows * pixelCellH + offset_pix_y,
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

            vV = np.zeros(T.shape)  # clearing the velocity vector
            prev_T = T.copy()  # keeping the current sate of the field

            ######
            if T.ndim > 2:
                # using the solver for 3D case
                pcg.solve_3d_cond_with_v(
                    T,
                    dP,
                    vV,
                    m_ID,
                    m_massCp,
                    m_Rth,
                    m_gas,
                    dx,
                    dt,
                    g,
                    slice_size=slice_size,
                )
            else:
                # the 2D case solver
                pcg.solve_cond_with_v(
                    T, dP, vV, m_ID, m_massCp, m_Rth, m_gas, dx, dt, g
                )
            ##### quick fix to NaN in the solution T array
            T = np.nan_to_num(T)
            ######
            pcg.open_air_boundary(T, vV)
            ######

            # if this stem max T difference is more than assumed - need to fix
            this_step_dT = abs(T.max() - prev_T.max())
            print(f"{this_step_dT:10.4e} / {dt:10.4e}", end="\r")

            if this_step_dT > 10:
                dt = dt * 10 / this_step_dT
                dt = max(1 / 500, min(1 / 50, dt))
                vV[:] = 0
                s = 0
                T = prev_T.copy()
            else:
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

                if this_step_dT < 0.1:
                    dt = dt * 0.01 / this_step_dT
                    dt = max(1 / 500, min(1 / 50, dt))

        if s > 0:
            if T.ndim < 3:
                pcg.solve_conv(T, m_ID, vV, m_gas, dx, N, dt)
            else:
                pcg.solve_3d_conv(T, m_ID, vV, m_gas, dx, N, dt)

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

                dt = max(1 / 500, min(1 / 50, dt))

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

    tT = 2
    dT = 20

    tN = 0

    text_surface = font.render(filedName, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 2
    text_string = f"{material} dT:{reading:.2f}K dP:{powerloss:.1f}W".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 1
    text_string = f"maxT: {currentMax:.4f}K".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 1
    text_string = f"time: {simH:02d}:{simMin:02d}:{simSec:02d}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 1
    text_string = f"s: {1000*s:.2f}mm / {N} // {maxNup}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 1
    text_string = (
        f" Fr {frameRatio:.2f} vm: {viewMode} fps: {int(clock.get_fps())}".encode()
    )
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 2
    text_string = f"Selected: {m_name[selected_material]}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 1
    if editMode:
        text_string = f"Selecton: {abs(mouseCol - mouseC)}x{abs(mouseRow-mouseR)} @ Dm: {drawMode}".encode()
        text_surface = font.render(text_string, True, (255, 255, 255))
        screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 2
    text_string = f"Source dP: {source_power:.2f} [W/m]".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    tN += 1
    for i, mat in enumerate(m_name):
        text_string = f"{i+1}: {mat}".encode()
        text_surface = font.render(text_string, True, (255, 255, 255))
        screen.blit(text_surface, dest=(navi_left, tT + (tN) * dT))
        tN += 1

    tN += 2
    text_string = f"Slice: {this_slice+1} of {number_of_slices}".encode()
    text_surface = font.render(text_string, True, (255, 255, 255))
    screen.blit(text_surface, dest=(navi_left, tT + tN * dT))

    # Done after drawing everything to the screen
    pygame.display.flip()


# plt.plot(timeV, maxTV)
# plt.show()

pygame.quit()
