# This is a library file for the PCG experiment
import cmap as cc
import pickle
import numpy


class dataKeeper:
    def __init__(
        self, grid, width, height, rows, cols, sourceActive, mouseRow, mouseCol
    ):
        self.grid = grid
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.sourceActive = sourceActive
        self.mouseRow = mouseRow
        self.mouseCol = mouseCol


class material:
    def __init__(self):
        # default as air
        self.cp = 1.003e3  # J/kg K
        self.ro = 1.29  # kg/m^3
        self.Sigma = 1 * 26e-3  # W/mK
        self.gas = True


# Materiały

powietrze = material()


class Cell:
    def __init__(self, x=0, y=0, w=10, h=10, gas=True, temperature=0):
        self.material = powietrze

        self.gas = self.material.gas
        self.T = temperature
        self.x = x
        self.y = y

        self.w = w
        self.h = h

        self.color = (255, 255, 255)

        self.dP = 0
        self.area = 0.01 * 1
        self.length = 0.01

        self.updateData()
        self.update()

    def updateData(self):
        self.mass = self.area * self.length * self.material.ro

        self.Rth = 0.5 * self.length / (self.area * self.material.Sigma)

        self.gas = self.material.gas

    def calc(self, dQ):
        self.T += dQ / (self.mass * self.material.cp)

    def update(self, maxT=255):
        # self.T = clamp(self.T)
        self.color = getColor(self.T, minimum=0, maximum=maxT)

    def heat(self, dt):
        self.calc(self.dP * dt)


def borders(Grid, ht=0.01, hs=0.02, h=0):

    # top row bonduary condition
    A = 1 - ht
    for cell in Grid[0]:
        cell.T *= A
        # cell.update()
    A = 1 - hs

    for row in Grid[h:]:
        row[0].T *= A
        row[0].update()

        row[-1].T *= A
        row[-1].update()


def heatGeneration(cell, dt=1 / 1000):
    cell.calc(cell.dP * dt)


def heatConduction(cellA, cellB, dt=1 / 1000):
    dT = cellA.T - cellB.T

    # Power transferred
    # if (not cellA.gas) and cellB.gas:
    #     heatSigma = 1 / (1.0 * cellA.Rth + 1.0 * cellB.Rth)
    # else:
    #     heatSigma = 1 / (1.0 * cellA.Rth + 1.0 * cellB.Rth)
    heatSigma = 1 / (1.0 * cellA.Rth + 1.0 * cellB.Rth)

    dP = dT * heatSigma
    dQ = dP * dt

    cellA.calc(-dQ)
    cellB.calc(dQ)


def airSimCond(Grid, arrT, cols, rows, g=True, dt=1e-9):
    """
    This procedure manage the main air convection simulation.
    It is somehow similar to cellular automata of a kind.

    it is about transmitting temperature to the cells left right and below. And if the temp of the cell is bigger than the average od left bottom and right one - the cell moves up.

    To eliminate the numerical viscosity the rows are analyzed from left to right and from right to left alternatively.

    """

    direction = -1
    for row, cellRow in enumerate(Grid):

        direction *= -1
        for col, cell in enumerate(cellRow[::direction]):
            if direction == -1:
                col = cols - col - 1

            # let's make it in the wat that we will deal with the:
            # heat generation
            # conduction
            # convection

            # heat generation
            cell.heat(dt)
            # heatGeneration(cell)

            if True:
                # As this conduction part is for all type of cells.

                # heat exchange to neighbor cells
                # left
                if col < cols - 1:
                    cell2 = cellRow[col + 1]
                    cellR = cell2
                    heatConduction(cell, cell2, dt=dt)

                # right
                if col > 0:
                    cell2 = cellRow[col - 1]
                    cellL = cell2
                    heatConduction(cell, cell2, dt=dt)

                # below
                if row < rows - 1:
                    cell2 = Grid[row + 1][col]
                    cellB = cell2
                    heatConduction(cell, cell2, dt=dt)

                # above
                if row > 0:
                    cell2 = Grid[row - 1][col]
                    cellT = cell2
                    heatConduction(cell, cell2, dt=dt)


def airSimConv(Grid, arrT, cols, rows, g=True, dt=1e-9, maxT=255):
    """
    This procedure manage the main air convection simulation.
    It is somehow similar to cellular automata of a kind.

    it is about transmitting temperature to the cells left right and below. And if the temp of the cell is bigger than the average od left bottom and right one - the cell moves up.

    To eliminate the numerical viscosity the rows are analyzed from left to right and from right to left alternatively.

    """

    direction = -1
    for row, cellRow in enumerate(Grid):

        direction *= -1
        for col, cell in enumerate(cellRow[::direction]):
            if direction == -1:
                col = cols - col - 1

            if cell.gas:  # if this is a gas cell
                # the idea to speed up the simulation is to
                # make 5 time more up moves than the convection ones.
                # it's for now only as a kind of hacking thing

                # look up - convection
                if row > 0 and g and col > 0 and col < cols - 1:

                    cellR = cellRow[col + 1]
                    cellL = cellRow[col - 1]

                    if cell.T > cellL.T or cell.T > cellR.T:
                        # if we are hotter than others around
                        # trying to go up
                        cellUp = Grid[row - 1][col]
                        if cell.T > cellUp.T and cellUp.gas:
                            cell.T, cellUp.T = cellUp.T, cell.T
                            # cellUp.update(maxT)
                        else:
                            cellUp = Grid[row - 1][min(col + 1, cols - 1)]

                            if cell.T > cellUp.T and cellUp.gas:
                                cell.T, cellUp.T = cellUp.T, cell.T
                                # cellUp.update(maxT)

                            else:

                                cellUp = Grid[row - 1][max(col - 1, 0)]

                                if cell.T > cellUp.T and cellUp.gas:
                                    cell.T, cellUp.T = cellUp.T, cell.T
                                    # cellUp.update(maxT)

                                else:  # no way to move up.
                                    heatConduction(cell, cellR, dt=dt)
                                    heatConduction(cell, cellL, dt=dt)
            else:
                # taking care of the not gas cell.
                pass

            arrT[row][col] = cell.T
            cell.update(maxT=maxT)


def clamp(A: int, minimum=0, maximum=254):
    return min(maximum, max(minimum, A))


def getColor(A, minimum=0, maximum=200):
    # A = clamp(A, minimum, maximum)
    A = int((A - minimum) / (maximum - minimum) * 255)

    return cc.cmap[max(0, min(A, 255))]


def getColorOld(A: int, minimum=0, maximum=254):
    A = clamp(A, minimum, maximum)
    A = int((A - minimum) / (maximum - minimum) * 254)
    R = A
    G = clamp(128 - A)
    B = 255 - A

    return (R, G, B)
