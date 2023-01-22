# PCG V2 concept of work to be done

The base is the fast version 
The solver already is working fine and nice. 
So the missing ideas or features are:

- better support for many materials 
- decent editor
- some basic gui to use it. 

## Stage one:
1. Adding the materials. 
My idea is to keep the solver untouched just make it easier for the material assignment. 
The idea would be - to add additional matrix / np.array which will keep the material ID number (int). And then just refer to the material base to get the proper values. 

In the initial concept, current solution can support different wall/cell size by just making the massCp and the Rth different. 

This might work further, just let's make it in the material definitions database. 

## Cells definitions database concept
it will be made of:
- **Rth** array
- **massCp** array 
- **gas** array

the logic will be:
Solver check the ctn = CellTypeNumber and gets the required values from the arrays:
- **Rth[ctn]** 
- **massCp[ctn]**
- **gas[ctn]**
TODO:
    - Fix save and load
    - [x] Edit mode using material ID

## World Editor concept
It's about more user friendly way of editing the simulation domain. 
To do plan:
- [x] Side panel with buttons
    - [ ] Run/Pause
    - [ ] Save
    - [ ] Load
    - [ ] Edit Mode Toggle
- [ ] In edit mode:
    - [x] Cell type selection 
    - [ ] Shape drawing
        - [ ] Lines
        - [x] Boxes
        - [ ] Circles 
    - [ ] Source definition
        - [ ] Set temperature
        - [ ] Set power generation

## Engine expansion ideas
- [ ] Add Velocity array and calculate the N up steps for each cell.
    - do this in the conduction solver loop (to not add another loop)
    - set the maxN loops based on the max s / or max velocity 
    - do the convection looping 
        - each cell move up only as many time as the individual need


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
            cell.ID = copper.ID
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


