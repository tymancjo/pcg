# material definition file
import pcg_v2 as pcg


water = pcg.material()
water.gas = True
water.cp = 4.186e3  # J/kg.K
water.Sigma = 600e-3  # W/m.K
water.ro = 997  # kg/m3
water.ID = 3

copper = pcg.material()
copper.gas = False
copper.cp = 385  # J/kg.K
copper.Sigma = 400e-0  # W/m.K
copper.ro = 8830  # kg/m3
copper.ID = 2

stell = pcg.material()
stell.gas = False
stell.cp = 0.88e3  # J/kg.K
stell.Sigma = 55  # W/m.K
stell.ro = 8000  # kg/m3
stell.ID = 1

steelCell = pcg.Cell()
steelCell.material = stell
steelCell.length = 2e-3
steelCell.ID = 1
steelCell.name = "Steel"
steelCell.color = (50, 50, 200)
steelCell.updateData()

copperCell = pcg.Cell()
copperCell.material = copper
copperCell.ID = 2
copperCell.name = "Copper"
copperCell.color = (130, 130, 5)
copperCell.updateData()

waterCell = pcg.Cell()
waterCell.material = water
waterCell.ID = 3
waterCell.name = "Water"
waterCell.color = (30, 30, 255)
waterCell.updateData()

airCell = pcg.Cell()
airCell.ID = 0
airCell.name = "Air"
airCell.color = (200, 200, 255)
