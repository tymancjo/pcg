# This is a library file for the PCG experiment
import cmap as cc
import pickle
import numpy as np
from numba import njit

CLRS = np.array(cc.cmap)


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


def getColorAsArrayR(A):
    return CLRS[max(0, min(int(A * 255), 255)), 0]
    # c = 0
    # return cc.cmap[max(0, min(int(A * 255), 255))][c]


def getColorAsArrayG(A):
    return CLRS[max(0, min(int(A * 255), 255)), 1]
    # c = 1
    # return cc.cmap[max(0, min(int(A * 255), 255))][c]


def getColorAsArrayB(A):
    return CLRS[max(0, min(int(A * 255), 255)), 2]
    # c = 2
    # return cc.cmap[max(0, min(int(A * 255), 255))][c]


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
    the_shape = (the_shape[0], the_shape[1], 1)

    # now let's make the required arrays of values.
    T_array = np.zeros(the_shape)
    dP_array = np.zeros(the_shape)
    material_ID = np.zeros(the_shape)
    s_array = np.zeros(the_shape)

    # now let's fill them up with the data:
    for r, row in enumerate(the_grid):
        for c, cell in enumerate(row):
            T_array[r, c] = cell.T
            dP_array[r, c] = cell.dP
            material_ID[r, c] = int(cell.ID)

    return T_array, dP_array, material_ID.astype(int), s_array  # , gas_array


def add_slice(T, dP, vV, m_ID, this_slice):
    """
    adding another layer in 3D to the solution arrays, by copy the last slice.
    returning the same set of arrays but now in 3d d- dimension (rows,cols,depth)
    """
    T = np.dstack([T, np.copy(T[:, :, this_slice])])
    dP = np.dstack([dP, np.copy(dP[:, :, this_slice])])
    vV = np.dstack([vV, np.copy(vV[:, :, this_slice])])
    m_ID = np.dstack([m_ID, np.copy(m_ID[:, :, this_slice])])

    return T, dP, vV, m_ID


@njit
def solve_heat(T_array, dP_array, massCp_array, dt=1 / 100):
    rows, cols = T_array.shape

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            T_array[r, c] += dP_array[r, c] * dt / massCp_array[r, c]


@njit
def solve_cond_with_v(
    T_array,
    dP_array,
    v_array,
    m_ID,
    massCp_array,
    Rth_array,
    gas_array,
    dx,
    dt=1 / 100,
    g=9.81,
):
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

            if gas_array[m_ID[r, c]]:
                v_array[r, c] += g * (((T_array[r, c] + 35) / 35) - 1) * dt
            else:
                v_array[r, c] = 0


@njit
def solve_3d_cond_with_v(
    T_array: np.array,
    dP_array: np.array,
    v_array: np.array,
    m_ID: np.array,
    massCp_array: np.array,
    Rth_array: np.array,
    gas_array: np.array,
    dx,
    dt=1 / 100,
    g=9.81,
):
    # T, dP, m_ID, m_massCp, m_Rth, dt
    # checking if we got the arrays in 3D
    if T_array.ndim > 2:
        rows, cols, slices = T_array.shape
    else:
        rows, cols = T_array.shape
        slices = 1

    for s in range(slices):
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                # heat generation temp rise
                T_array[r, c, s] += dP_array[r, c, s] * dt / massCp_array[m_ID[r, c, s]]

                # Thermal conduction
                # to the left
                DT = T_array[r, c, s] - T_array[r, c - 1, s]
                heatSigma = 1 / (
                    Rth_array[m_ID[r, c, s]] + Rth_array[m_ID[r, c - 1, s]]
                )
                dP = DT * heatSigma
                dQ = dP * dt
                T_array[r, c, s] -= dQ / massCp_array[m_ID[r, c, s]]
                T_array[r, c - 1, s] += dQ / massCp_array[m_ID[r, c - 1, s]]

                # to the right
                DT = T_array[r, c, s] - T_array[r, c + 1, s]
                heatSigma = 1 / (
                    Rth_array[m_ID[r, c, s]] + Rth_array[m_ID[r, c + 1, s]]
                )
                dP = DT * heatSigma
                dQ = dP * dt
                T_array[r, c, s] -= dQ / massCp_array[m_ID[r, c, s]]
                T_array[r, c + 1, s] += dQ / massCp_array[m_ID[r, c + 1, s]]

                # to the top
                DT = T_array[r, c, s] - T_array[r - 1, c, s]
                heatSigma = 1 / (
                    Rth_array[m_ID[r, c, s]] + Rth_array[m_ID[r - 1, c, s]]
                )
                dP = DT * heatSigma
                dQ = dP * dt
                T_array[r, c, s] -= dQ / massCp_array[m_ID[r, c, s]]
                T_array[r - 1, c, s] += dQ / massCp_array[m_ID[r - 1, c, s]]

                # to the bottom
                DT = T_array[r, c, s] - T_array[r + 1, c, s]
                heatSigma = 1 / (
                    Rth_array[m_ID[r, c, s]] + Rth_array[m_ID[r + 1, c, s]]
                )
                dP = DT * heatSigma
                dQ = dP * dt
                T_array[r, c, s] -= dQ / massCp_array[m_ID[r, c, s]]
                T_array[r + 1, c, s] += dQ / massCp_array[m_ID[r + 1, c, s]]

                if gas_array[m_ID[r, c, s]]:
                    v_array[r, c, s] += g * (((T_array[r, c, s] + 35) / 35) - 1) * dt
                else:
                    v_array[r, c, s] = 0


def solve_conv_3d():
    # how to make it?
    # it's need to be made out of full 3D arrays - thats it ....
    # lot of work... but should be fun :)

    pass


@njit
def solve_conv(T_array, m_ID, vV, gas_array, dx, N=1, dt=1 / 100):

    rows, cols = T_array.shape

    for n in range(N):
        this_s = n * dx

        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                s = vV[r, c] * dt
                if s >= this_s:

                    if gas_array[m_ID[r, c]] and (
                        T_array[r, c] > T_array[r, c - 1] or T_array[r, c + 1]
                    ):
                        # if this is a gas cell and it's hotter then the adjacted ones (L or R)
                        # up
                        if (T_array[r, c] > T_array[r - 1, c]) and m_ID[r, c] == m_ID[
                            r - 1, c
                        ]:
                            T_array[r - 1, c], T_array[r, c] = (
                                T_array[r, c],
                                T_array[r - 1, c],
                            )
                            vV[r - 1, c], vV[r, c] = (
                                vV[r, c],
                                vV[r - 1, c],
                            )
                            # vV[r, c] = 0

                        # below is a tricky path for some kind of evaporate
                        # elif (T_array[r, c] > 100) and m_ID[r - 1, c] == 0 and m_ID[r, c] == 3:
                        #     # if it's a water cell, and hot, and above is air - lets evaporate
                        #     m_ID[r, c] = 0

                        # up-left
                        elif (
                            T_array[r, c] > T_array[r - 1, c - 1]
                            and m_ID[r, c] == m_ID[r - 1, c - 1]
                        ):
                            T_array[r - 1, c - 1], T_array[r, c] = (
                                T_array[r, c],
                                T_array[r - 1, c - 1],
                            )
                            vV[r - 1, c - 1], vV[r, c] = (
                                vV[r, c],
                                vV[r - 1, c - 1],
                            )
                            # vV[r, c] = 0
                        # up-right
                        elif (
                            T_array[r, c] > T_array[r - 1, c + 1]
                            and m_ID[r, c] == m_ID[r - 1, c + 1]
                        ):
                            T_array[r - 1, c + 1], T_array[r, c] = (
                                T_array[r, c],
                                T_array[r - 1, c + 1],
                            )
                            vV[r - 1, c + 1], vV[r, c] = (
                                vV[r, c],
                                vV[r - 1, c + 1],
                            )
                            # vV[r, c] = 0
                        # -left
                        elif (
                            T_array[r, c] > T_array[r, c - 1]
                            and m_ID[r, c] == m_ID[r, c - 1]
                        ):
                            T_array[r, c - 1], T_array[r, c] = (
                                T_array[r, c],
                                T_array[r, c - 1],
                            )
                            vV[r, c - 1], vV[r, c] = (
                                vV[r, c],
                                vV[r, c - 1],
                            )
                            # vV[r, c] = 0
                        # -right
                        elif (
                            T_array[r, c] > T_array[r, c + 1]
                            and m_ID[r, c] == m_ID[r, c + 1]
                        ):
                            T_array[r, c + 1], T_array[r, c] = (
                                T_array[r, c],
                                T_array[r, c + 1],
                            )
                            vV[r, c + 1], vV[r, c] = (
                                vV[r, c],
                                vV[r, c + 1],
                            )
                            # vV[r, c] = 0


def open_air_boundary(T_array, vV):

    if T_array.ndim > 2:
        T_array[0, :, :] *= 0.25
        T_array[-1, :, :] = 0
        T_array[:, 0, :] = 0
        T_array[:, -1, :] = 0
        vV[0, :, :] = 0
    else:
        T_array[0, :] *= 0.25
        T_array[-1, :] = 0
        T_array[:, 0] = 0
        T_array[:, -1] = 0
        vV[0, :] = 0
