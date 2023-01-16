# This is a library file for the PCG experiment
import cmap as cc
import pickle


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


class Cell:
    def __init__(self, x=0, y=0, w=10, h=10, gas=True, temperature=0):
        self.gas = gas
        self.T = temperature
        self.x = x
        self.y = y

        self.w = w
        self.h = h

        self.color = (255, 255, 255)

        self.dP = 0

        self.update()

    def update(self):
        self.T = clamp(self.T)
        self.color = getColor(self.T)


def borders(Grid, ht=0.01, hs=0.02, h=0):

    # top row bonduary condition
    A = 1 - ht
    for cell in Grid[0]:
        cell.T *= A
        cell.update()
    A = 1 - hs

    for row in Grid[h:]:
        row[0].T *= A
        row[0].update()

        row[-1].T *= A
        row[-1].update()


def segregator(Grid, cols, rows, ht=0.05, g=True):
    """
    This procedure manage the main air convection simulation.
    It is somehow simmilar to cellular automata of a kind.

    it is about transitting temperature to the cells left right and below. And if the temp of the cell is bigger than the average od left bottom and right one - the cell moves up.

    To eliminate the numerical viscocity the rows are analyzed from left to right and from right to left alternativly.

    """

    direction = -1
    for row, cellRow in enumerate(Grid):

        direction *= -1
        for col, cell in enumerate(cellRow[::direction]):
            if direction == -1:
                col = cols - col - 1

            if cell.gas:
                # heating cells around
                if col < cols - 1:

                    cell2 = cellRow[col + 1]
                    cellR = cell2
                    dT = cell.T
                    # dT = cell.T - cell2.T
                    if dT > 0 and cell2.gas:
                        cell2.T += ht * dT
                        cell.T -= ht * dT
                        cell2.update()

                if col > 0:

                    cell2 = cellRow[col - 1]
                    cellL = cell2
                    dT = cell.T
                    # dT = cell.T - cell2.T
                    if dT > 0 and cell2.gas:
                        cell2.T += ht * dT
                        cell.T -= ht * dT
                        cell2.update()

                if row < rows - 1:

                    cell2 = Grid[row + 1][col]
                    cellB = cell2
                    dT = cell.T
                    # dT = cell.T - cell2.T
                    if dT > 0 and cell2.gas:
                        cell2.T += ht * dT
                        cell.T -= ht * dT
                        cell2.update()

                if row > 0:

                    cell2 = Grid[row - 1][col]
                    cellT = cell2
                    dT = cell.T
                    # dT = cell.T - cell2.T
                    if dT > 0 and cell2.gas:
                        cell2.T += ht * dT
                        cell.T -= ht * dT
                        cell2.update()

                # look up - convection
                if row > 0 and g:
                    if cell.T > cellL.T or cell.T > cellR.T:
                        # if we are hotter than others around
                        # trying to go up
                        cellUp = Grid[row - 1][col]
                        if cell.T > cellUp.T and cellUp.gas:
                            cell.T, cellUp.T = cellUp.T, cell.T
                            cellUp.update()
                        else:
                            cellUp = Grid[row - 1][min(col + 1, cols - 1)]

                            if cell.T > cellUp.T and cellUp.gas:
                                cell.T, cellUp.T = cellUp.T, cell.T
                                cellUp.update()

                            else:

                                cellUp = Grid[row - 1][max(col - 1, 0)]

                                if cell.T > cellUp.T and cellUp.gas:
                                    cell.T, cellUp.T = cellUp.T, cell.T
                                    cellUp.update()

                                else:  # no way to move up.
                                    if cellL.gas:
                                        cellL.T += ht * 1 * cell.T
                                        cell.T -= ht * 1 * cell.T
                                        cellL.update()
                                    if cellR.gas:
                                        cellR.T += ht * 1 * cell.T
                                        cell.T -= ht * 1 * cell.T
                                        cellR.update()

                                    # if cellB.gas and 0:
                                    #     cellB.T += ht * 2 * cell.T
                                    #     cell.T -= ht * 2 * cell.T
                                    #     cellR.update()
            cell.update()


def heatConduction(cellA, cellB, htc=1, area=0.01 * 1, length=0.01, dt=1 / 10):

    dT = cellA.T - cellB.T
    if cellA.gas and cellB.gas:

        roAir = 1.29  # kg/m3
        mass = area * length * roAir  # kg

        # Air thermal conductivity
        # 26 mW/mK = 26e-3 W/mK
        airSigma = 26e-3

        # thermal conduction
        airS = area * airSigma / length

        # (T1-T2)*S = Q (to było Q? czy P... hmmm)
        dP = dT * airS
        dQ = dP * dt

        # ciepło właściwe
        # [J/kgK] -> cp=Q/m.dT
        # dT = Q/m.cp
        cpAir = 1.003e3  # J/kg K

        deltaT = dQ / (mass * cpAir)

        cellA.T -= deltaT
        cellB.T += deltaT

        cellA.update()
        cellB.update()


def airSim(Grid, cols, rows, ht=0.05, g=True, dt=1e-9):
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

            if True:
                # As this conduction part is for all type of cells.

                # heat exchange to neighbor cells
                # left
                if col < cols - 1:
                    cell2 = cellRow[col + 1]
                    cellR = cell2
                    heatConduction(cell, cell2)

                # right
                if col > 0:
                    cell2 = cellRow[col - 1]
                    cellL = cell2
                    heatConduction(cell, cell2)

                # below
                if row < rows - 1:
                    cell2 = Grid[row + 1][col]
                    cellB = cell2
                    heatConduction(cell, cell2)

                # above
                if row > 0:
                    cell2 = Grid[row - 1][col]
                    cellT = cell2
                    heatConduction(cell, cell2)

            if cell.gas:  # if this is a gas cell

                # look up - convection
                if row > 0 and g:
                    if cell.T > cellL.T or cell.T > cellR.T:
                        # if we are hotter than others around
                        # trying to go up
                        cellUp = Grid[row - 1][col]
                        if cell.T > cellUp.T and cellUp.gas:
                            cell.T, cellUp.T = cellUp.T, cell.T
                            cellUp.update()
                        else:
                            cellUp = Grid[row - 1][min(col + 1, cols - 1)]

                            if cell.T > cellUp.T and cellUp.gas:
                                cell.T, cellUp.T = cellUp.T, cell.T
                                cellUp.update()

                            else:

                                cellUp = Grid[row - 1][max(col - 1, 0)]

                                if cell.T > cellUp.T and cellUp.gas:
                                    cell.T, cellUp.T = cellUp.T, cell.T
                                    cellUp.update()

                                else:  # no way to move up.
                                    heatConduction(cell, cellL)
                                    heatConduction(cell, cellR)
            else:
                # taking care of the not gas cell.
                pass

            cell.update()


def clamp(A: int, minimum=0, maximum=254):
    return min(maximum, max(minimum, A))


def getColor(A: int, minimum=0, maximum=200):
    A = clamp(A, minimum, maximum)
    A = int((A - minimum) / (maximum - minimum) * 255)

    return cc.cmap[A]


def getColorOld(A: int, minimum=0, maximum=254):
    A = clamp(A, minimum, maximum)
    A = int((A - minimum) / (maximum - minimum) * 254)
    R = A
    G = clamp(128 - A)
    B = 255 - A

    return (R, G, B)
