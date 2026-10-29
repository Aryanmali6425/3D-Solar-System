"""
sphere.py
Generates vertex/normal/texcoord/index data for a UV sphere.
Used to build the mesh for the Sun, planets, and moons.
"""

import numpy as np
import math


def create_sphere(radius=1.0, sectors=36, stacks=18):
    """
    Returns (vertices, indices) for a UV sphere.
    vertices: flat float32 array of [x,y,z, nx,ny,nz, u,v] per vertex
    indices: uint32 array of triangle indices
    """
    vertices = []
    for i in range(stacks + 1):
        stack_angle = math.pi / 2 - i * (math.pi / stacks)  # from +pi/2 to -pi/2
        xy = radius * math.cos(stack_angle)
        z = radius * math.sin(stack_angle)

        for j in range(sectors + 1):
            sector_angle = j * (2 * math.pi / sectors)

            x = xy * math.cos(sector_angle)
            y = xy * math.sin(sector_angle)

            nx, ny, nz = x / radius, y / radius, z / radius
            u = j / sectors
            v = i / stacks

            vertices.extend([x, y, z, nx, ny, nz, u, v])

    indices = []
    for i in range(stacks):
        k1 = i * (sectors + 1)
        k2 = k1 + sectors + 1

        for j in range(sectors):
            if i != 0:
                indices.extend([k1 + j, k2 + j, k1 + j + 1])
            if i != (stacks - 1):
                indices.extend([k1 + j + 1, k2 + j, k2 + j + 1])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)
