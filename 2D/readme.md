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
        - [x] Set power generation
- [ ] Visual stuff 
    - [ ] Display modes 
        - [x] Normal 
        - [ ] Temperature
        - [ ] Materials

## Engine expansion ideas
- [x] Add Velocity array and calculate the N up steps for each cell.
    - do this in the conduction solver loop (to not add another loop)
    - set the maxN loops based on the max s / or max velocity 
    - do the convection looping 
        - each cell move up only as many time as the individual need

