# PCG stands for a Particle in Cells Grid

It's a prototype or more proof of concept for 2D thermal solver of natural cooling in air. 
The basic principle is to make a quick solver to simulate the cooling of objects in the air. 

## What's in it?

The solver basically solves the system in form of simulation - this means iterative over time, just like in the real world. The simulated heat  mechanisms simulated are:

- Heat generation due to power losses
- Heat conduction (thermal conduction)
- Heat convection (however quite nicely working - it's simplified approximation model)