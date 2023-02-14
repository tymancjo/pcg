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
copper.Sigma = 400  # W/m.K
copper.ro = 8830  # kg/m3
copper.ID = 2

super_copper = pcg.material()
super_copper.gas = False
super_copper.cp = 385  # J/kg.K
super_copper.Sigma = 400e-0  # W/m.K
super_copper.ro = 8830  # kg/m3
super_copper.ID = 5

Insulation = pcg.material()
Insulation.gas = False
Insulation.cp = 385  # J/kg.K
Insulation.Sigma = 1e-10  # W/m.K
Insulation.ro = 8830  # kg/m3
Insulation.ID = 6

stell = pcg.material()
stell.gas = False
stell.cp = 0.88e3  # J/kg.K
stell.Sigma = 55  # W/m.K
stell.ro = 8000  # kg/m3
stell.ID = 1

steelCell = pcg.Cell()
steelCell.material = stell
# steelCell.length = 2e-3
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
waterCell.material = super_copper
waterCell.ID = 3
waterCell.name = "SupCopp"
waterCell.color = (30, 30, 255)
waterCell.updateData()

waterCell = pcg.Cell()
waterCell.material = Insulation
waterCell.ID = 4
waterCell.name = "Insul."
waterCell.color = (123, 123, 123)
waterCell.updateData()

airCell = pcg.Cell()
airCell.ID = 0
airCell.name = "Air"
airCell.color = (200, 200, 255)
