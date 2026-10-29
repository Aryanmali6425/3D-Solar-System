"""
glow_billboard.py
A single quad (two triangles) in local space, meant to be scaled and
always rotated to face the camera in the vertex shader (billboarding).
Used to fake a bright corona/bloom halo around the Sun without a full
post-processing bloom pipeline.
"""

import numpy as np


def create_billboard_quad():
    """Returns (vertices, indices) for a unit quad centered at origin, XY plane."""
    vertices = np.array([
        # x,    y,    u,   v
        -1.0, -1.0, 0.0, 0.0,
         1.0, -1.0, 1.0, 0.0,
         1.0,  1.0, 1.0, 1.0,
        -1.0,  1.0, 0.0, 1.0,
    ], dtype=np.float32)
    indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)
    return vertices, indices
