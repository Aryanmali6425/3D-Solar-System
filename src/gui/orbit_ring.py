"""
orbit_ring.py
Generates a flat circle (line loop) in the XZ plane to visualize a
planet's orbit path around its parent.
"""

import numpy as np


def create_orbit_ring(radius, segments=128):
    """Returns a flat float32 array of [x, y, z] points forming a circle."""
    angles = np.linspace(0.0, 2.0 * np.pi, segments, endpoint=True)
    x = radius * np.cos(angles)
    z = radius * np.sin(angles)
    y = np.zeros_like(x)
    return np.column_stack([x, y, z]).astype(np.float32).flatten()
