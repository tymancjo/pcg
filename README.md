# PCG stands for a Particle in Cells Grid

It's a prototype or more proof of concept for 2D thermal solver of natural cooling in air.
The basic principle is to make a quick solver to simulate the cooling of objects in the air.

## What's in it?

The solver basically solves the system in form of simulation - this means iterative over time, just like in the real world. The simulated heat mechanisms simulated are:

- Heat generation due to power losses
- Heat conduction (thermal conduction)
- Heat convection (however quite nicely working - it's simplified approximation model)

# Basic info of usage

        # keys used:
        # space - simulation/edit mode toggle
        # g - turn on/off gravity
        # v - cycle over view modes - result field with shapes, materials, just result field
        # f - cycle over normal and fast ( color and grayscale) field display mode
        # p - [in edit mode] plots the temperature plot
        # CTRL p - [in edit mode] plot 3d mesh of currently selected material cell
        # SHIFT p - [in edit mode] plots the 3d temperature volumetric plot
        # w = [in edit mode] save the simulation data - will ask about filename in terminal
        # l - [in edit mode] loads the simulation data - will ask about filename in terminal
        # q - [in edit mode] if pressed 5 times reset the solution to initial state.
        # d - [in edit mode] toggle drawing mode from rectangle to paint mode
        # d - [in sim mode] toggle the result field [Temperature, Velocity]
        # SHIFT c - crop the analysis domain to marked size
        # SHIFT r - reset the canvas and all simulation to empty
        # s - add another slice in 3d based on current selected slice
        # CTRL s - ask in console for a slice size in [mm]
        # SHIFT s - toggle the front view display (it use the last mouse click to determine the cur plane)
        # [ ] - brackets - move between slices in 3d.


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

# PCG V2 2D concept of work

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
  TODO: - [x] Fix save and load - [x] Edit mode using material ID

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
  - [x] Source definition
    - [x] Set power generation

- [x] Visual stuff

  - [x] Zoom
  - [x] Pan
    - [x] Manual pan
    - [x] Auto pan with pressed keys
  - [x] Display modes
    - [x] Normal
    - [x] Temperature
    - [x] Materials
  - [x] Result field selection
    - [x] Temperatures
    - [x] Velocities
    - [x] Power Losses

- [ ] Import external data

  - [ ] Data from CSD
  - [ ] Geometry from picture

- [ ] Improve on solutions

  - [ ] Trim analysis area
    - [ ] Just trim the domain
    - [ ] Limit the solution to the selected part

- [ ] Edit features
  - [ ] Copy/Paste data in the domain

## Engine expansion ideas

- [x] Add Velocity array and calculate the N up steps for each cell.
  - do this in the conduction solver loop (to not add another loop)
  - set the maxN loops based on the max s / or max velocity
  - do the convection looping
    - each cell move up only as many time as the individual need

### 3D modeling and simulation in the - model of slices /mos/

The idea:
Single slice of is just a 2D analysis - as it is working nice already.
To make it 3D -> let's just put the 3D together made out of slices.

- [ ] Simulation
  - [ ] Stuck slices and make them transport heat only by conduction
  - [ ] ad another dimension to convection
- [ ] Display
  - [ ] Select displayed slice and show it as it is now (2D)
