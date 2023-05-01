# Implements the Needleman-Wunsch algorithm for sequence alignment
import numpy as np
from operators import *

def NW(x, y, match = 1, mismatch = 1, gap = 1):
    nx = len(x)
    ny = len(y)
    digit_weight = 1
    # Optimal score at each possible pair of characters
    F = np.zeros((nx + 1, ny + 1))
    F[:,0] = np.linspace(0, -nx * gap, nx + 1)
    F[0,:] = np.linspace(0, -ny * gap, ny + 1)
    # Pointers to trace through an optimal alignment
    P = np.zeros((nx + 1, ny + 1))
    P[:,0] = 3
    P[0,:] = 4
    # Fill in the table for dynamic programming
    T = np.zeros(3)
    for i in range(nx):
        for j in range(ny):
            if x[i] == y[j]:
                T[0] = F[i,j] + match
            else:
                T[0] = F[i,j] - mismatch
            T[1] = F[i, j+1] - gap
            T[2] = F[i+1, j] - gap
            tmax = np.max(T)
            F[i+1, j+1] = tmax
            if T[0] == tmax:
                P[i+1, j+1] += 2
            if T[1] == tmax:
                P[i+1, j+1] += 3
            if T[2] == tmax:
                P[i+1, j+1] += 4

    # trace the optimal alignment
    i = nx
    j = ny
    rx = []
    ry = []
    while i > 0 or j > 0:
        if P[i,j] in [2,5,6,9]:
            rx.append(x[i-1])
            ry.append(y[j-1])
            i -= 1
            j -= 1
        elif P[i,j] in [3,5,7,9]:
            rx.append(x[i-1])
            ry.append(smallPsi)
            i -= 1
        elif P[i,j] in [4,6,7,9]:
            rx.append(smallPsi)
            ry.append(y[j-1])
            j -= 1

    # reverse the strings
    rx = ''.join(rx)[::-1]
    ry = ''.join(ry)[::-1]

    return rx, ry
