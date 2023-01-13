# This is a library file for the PCG experiment
import cmap as cc

class Cell:
    def __init__(self, x=0,y=0, w=10, h=10,gas=True, temperature = 0):
        self.gas = gas
        self.T = temperature
        self.x = x
        self.y = y

        self.w = w
        self.h = h

        self.color = (255,255,255)

        self.update()

    def update(self):
        self.T = clamp(self.T)
        if self.gas:
            self.color = getColor(self.T)
        else:
            self.color = (10,10,10)

def borders(Grid,ht=0.01, hs=0.02,h=0):

    #top row bondary condition
    A = 1-ht
    for cell in Grid[0]:
        cell.T *=A
        cell.update()
    A = 1 - hs

    for row in Grid[h:]:
        row[0].T *= A
        row[0].update()

        row[-1].T *= A
        row[-1].update()

def segregator(Grid, cols, rows, ht=0.05):
    '''
    This procedure manage the main air convection simulation.
    It is somehow simmilar to cellular automata of a kind. 

    it is about transitting temperature to the cells left right and below. And if the temp of the cell is bigger than the average od left bottom and right one - the cell moves up.

    To eliminate the numerical viscocity the rows are analyzed from left to right and from right to left alternativly. 

    '''

    direction = -1
    for row,cellRow in enumerate(Grid):

        direction *= -1
        for col,cell in enumerate(cellRow[::direction]):
            if direction == -1:
                col = cols - col - 1

            # heating cells around
            if  col < cols-1:

                cell2 = cellRow[col + 1]
                cellR = cell2
                dT = cell.T - cell2.T
                if dT > 0 and cell2.gas:
                    cell2.T += ht*dT
                    cell.T -= ht*dT
                    cell2.update()           

            if  col > 0:

                cell2 = cellRow[col-1]
                cellL = cell2
                dT = cell.T - cell2.T
                if dT > 0 and cell2.gas:
                    cell2.T += ht*dT
                    cell.T -= ht*dT
                    cell2.update()           

            if row < rows-1:

                cell2 = Grid[row+1][col]
                cellB = cell2
                dT = cell.T - cell2.T
                if dT > 0 and cell2.gas:
                    cell2.T += ht*dT
                    cell.T -= ht*dT
                    cell2.update()           

            

            # look up - convection
            if row > 0:
                if cell.T-(cellL.T+cellR.T+cellB.T)/3 > 0:
                    # if we are hotter than others around
                    #trying to go up
                    cellUp = Grid[row-1][col]
                    if cell.T > cellUp.T and cellUp.gas:
                        cell.T, cellUp.T = cellUp.T, cell.T
                        cellUp.update()
                    else:
                        cellUp = Grid[row-1][min(col+1,cols-1)]

                        if cell.T > cellUp.T and cellUp.gas:
                            cell.T, cellUp.T = cellUp.T, cell.T
                            cellUp.update()
                            
                        else:

                            cellUp = Grid[row-1][max(col-1,0)]

                            if cell.T > cellUp.T and cellUp.gas:
                                cell.T, cellUp.T = cellUp.T, cell.T
                                cellUp.update()
                            
            cell.update()

def clamp (A:int, minimum = 0, maximum = 254):
    return min(maximum,max(minimum,A))

def getColor (A: int, minimum = 0, maximum = 254):
    A = clamp(A,minimum, maximum)
    A = int((A-minimum)/(maximum-minimum)*255)

    return cc.cmap[A]

    
def getColorOld (A: int, minimum = 0, maximum = 254):
    A = clamp(A,minimum, maximum)
    A = int((A-minimum)/(maximum-minimum)*254)
    R = A
    G = clamp(128 - A)
    B = 255 - A

    return (R,G,B)
    
