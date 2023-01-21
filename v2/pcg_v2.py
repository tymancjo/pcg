# This is a library file for the PCG experiment
import cmap as cc
import pickle
import numpy as np
from numba import njit


class dataKeeper:
    def __init__(self, dataList):
        self.data = dataList

    def get_data(self):
        return self.data


def save_data(obj):
    filename = input("Filename: ")
    try:
        filehandler = open(filename, "wb")
    except:
        return False

    pickle.dump(obj, filehandler)
    return True


def load_data():
    filename = input("Filename: ")
    try:
        filehandler = open(filename, "rb")
    except:
        return False

    obj = pickle.load(filehandler)
    return obj


class material:
    def __init__(self):
        # default as air
        self.cp = 1.003e3  # J/kg K
        self.ro = 1.29  # kg/m^3
        self.Sigma = 1 * 26e-3  # W/mK
        self.gas = True
        self.ID = 0


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

        self.ID = 0

        self.updateData()
        self.update()

    def updateData(self):
        self.mass = self.area * self.length * self.material.ro
        self.Rth = 0.5 * self.length / (self.area * self.material.Sigma)
        self.gas = self.material.gas
        self.massCp = self.mass * self.material.cp

    def calc(self, dQ):
        self.T += dQ / self.massCp

    def update(self, maxT=255):
        self.color = getColor(self.T, minimum=0, maximum=maxT)

    def heat(self, dt):
        self.calc(self.dP * dt)


def clamp(A: int, minimum=0, maximum=254):
    return min(maximum, max(minimum, A))


def getColor(A, minimum=0, maximum=200):
    # A = clamp(A, minimum, maximum)
    if (maximum - minimum) != 0:
        return cc.cmap[max(0, min(int((A - minimum) / (maximum - minimum) * 255), 255))]
    return cc.cmap[0]


# the plan for a faster solution compatible with numba
#
# not use the objects, but define the separate matrices (arrays) for the values
#
# T_array
# dP_array
# Rth_array
# massCp_array
#
# those can be prepared based on the world grid list by a pre-processor.


def pre_processor(the_grid):
    # converting the object based world grid to arrays
    # initially just for convenience to get the shape right
    grid_as_array = np.array(the_grid)
    the_shape = grid_as_array.shape

    # now let's make the required arrays of values.
    T_array = np.zeros(the_shape)
    dP_array = np.zeros(the_shape)
    material_ID = np.zeros(the_shape)
    gas_array = np.zeros(the_shape)

    # now let's fill them up with the data:
    for r, row in enumerate(the_grid):
        for c, cell in enumerate(row):
            T_array[r, c] = cell.T
            dP_array[r, c] = cell.dP
            material_ID[r, c] = int(cell.ID)
            # gas_array[r, c] = cell.gas

    return T_array, dP_array, material_ID.astype(int)  # , gas_array


@njit
def solve_heat(T_array, dP_array, massCp_array, dt=1 / 100):
    rows, cols = T_array.shape

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            T_array[r, c] += dP_array[r, c] * dt / massCp_array[r, c]


@njit
def solve_cond(T_array, dP_array, m_ID, massCp_array, Rth_array, dt=1 / 100):
    # T, dP, m_ID, m_massCp, m_Rth, dt
    rows, cols = T_array.shape
    direction = True

    for r in range(1, rows - 1):

        for c in range(1, cols - 1):
            # heat generation temp rise
            T_array[r, c] += dP_array[r, c] * dt / massCp_array[m_ID[r, c]]

            # Thermal conduction
            # to the left
            DT = T_array[r, c] - T_array[r, c - 1]
            heatSigma = 1 / (Rth_array[m_ID[r, c]] + Rth_array[m_ID[r, c - 1]])
            dP = DT * heatSigma
            dQ = dP * dt
            T_array[r, c] -= dQ / massCp_array[m_ID[r, c]]
            T_array[r, c - 1] += dQ / massCp_array[m_ID[r, c - 1]]

            # to the right
            DT = T_array[r, c] - T_array[r, c + 1]
            heatSigma = 1 / (Rth_array[m_ID[r, c]] + Rth_array[m_ID[r, c + 1]])
            dP = DT * heatSigma
            dQ = dP * dt
            T_array[r, c] -= dQ / massCp_array[m_ID[r, c]]
            T_array[r, c + 1] += dQ / massCp_array[m_ID[r, c + 1]]

            # to the top
            DT = T_array[r, c] - T_array[r - 1, c]
            heatSigma = 1 / (Rth_array[m_ID[r, c]] + Rth_array[m_ID[r - 1, c]])
            dP = DT * heatSigma
            dQ = dP * dt
            T_array[r, c] -= dQ / massCp_array[m_ID[r, c]]
            T_array[r - 1, c] += dQ / massCp_array[m_ID[r - 1, c]]

            # to the bottom
            DT = T_array[r, c] - T_array[r + 1, c]
            heatSigma = 1 / (Rth_array[m_ID[r, c]] + Rth_array[m_ID[r + 1, c]])
            dP = DT * heatSigma
            dQ = dP * dt
            T_array[r, c] -= dQ / massCp_array[m_ID[r, c]]
            T_array[r + 1, c] += dQ / massCp_array[m_ID[r + 1, c]]


@njit
def solve_conv(T_array, m_ID, gas_array, dt=1 / 100):

    rows, cols = T_array.shape

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if gas_array[m_ID[r, c]] and (
                T_array[r, c] > T_array[r, c - 1] or T_array[r, c + 1]
            ):
                # if this is a gas cell and it's hotter then the adjacted ones (L or R)
                # up
                if (T_array[r, c] > T_array[r - 1, c]) and gas_array[m_ID[r - 1, c]]:
                    T_array[r - 1, c], T_array[r, c] = T_array[r, c], T_array[r - 1, c]
                # up-left
                elif (
                    T_array[r, c] > T_array[r - 1, c - 1]
                    and gas_array[m_ID[r - 1, c - 1]]
                ):
                    T_array[r - 1, c - 1], T_array[r, c] = (
                        T_array[r, c],
                        T_array[r - 1, c - 1],
                    )
                # up-right
                elif (
                    T_array[r, c] > T_array[r - 1, c + 1]
                    and gas_array[m_ID[r - 1, c + 1]]
                ):
                    T_array[r - 1, c + 1], T_array[r, c] = (
                        T_array[r, c],
                        T_array[r - 1, c + 1],
                    )
                # -left
                elif T_array[r, c] > T_array[r, c - 1] and gas_array[m_ID[r, c - 1]]:
                    T_array[r, c - 1], T_array[r, c] = T_array[r, c], T_array[r, c - 1]
                # -right
                elif T_array[r, c] > T_array[r, c + 1] and gas_array[m_ID[r, c + 1]]:
                    T_array[r, c + 1], T_array[r, c] = T_array[r, c], T_array[r, c + 1]


def open_air_boundary(T_array):
    rows, cols = T_array.shape

    T_array[0, :] *= 0.25
    T_array[-1, :] = 0
    T_array[:, 0] = 0
    T_array[:, -1] = 0
