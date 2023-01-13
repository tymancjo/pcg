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

    for row,cellRow in enumerate(Grid):

        for col,cell in enumerate(cellRow):

            # heating cells around
            if  col < cols-1:
                cellR = cellRow[col + 1]

                if cell.T > cellR.T and cellR.gas:
                    cellR.T += ht*cell.T
                    cell.T -= ht*cell.T
                    cellR.update()           

            if  col > 0:
                cellL = cellRow[col-1]

                if cell.T > cellL.T and cellL.gas:
                    cellL.T += ht*cell.T
                    cell.T -= ht*cell.T
                    cellL.update()           

            if row < rows-1:
                cellB = Grid[row+1][col]

                if cell.T > cellB.T and cellB.gas:
                    cellB.T += ht*cell.T
                    cell.T -= ht*cell.T
                    cellB.update()           

            

            # look up - convection
            if row > 0:
                if cell.T-(cellL.T+cellR.T+cellB.T)/3 > 0:
                    # if we are hotter than others around
                    #trying to go up
                    cellUp = Grid[row-1][col]
                    if cell.T > cellUp.T and cellUp.gas:
                        #cell.x, cellUp.x = cellUp.x, cell.x
                        #cell.y, cellUp.y = cellUp.y, cell.y
                        cell.T, cellUp.T = cellUp.T, cell.T
                        pass
                        cellUp.update()
                    else:
                        cellUp = Grid[row-1][min(col+1,cols-1)]

                        if cell.T > cellUp.T and cellUp.gas:
                            #cell.x, cellUp.x = cellUp.x, cell.x
                            #cell.y, cellUp.y = cellUp.y, cell.y
                            cell.T, cellUp.T = cellUp.T, cell.T
                            pass
                            cellUp.update()
                            
                        else:

                            cellUp = Grid[row-1][max(col-1,0)]

                            if cell.T > cellUp.T and cellUp.gas:
                                #cell.x, cellUp.x = cellUp.x, cell.x
                                #cell.y, cellUp.y = cellUp.y, cell.y
                                cell.T, cellUp.T = cellUp.T, cell.T
                                pass
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
    
