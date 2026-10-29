"""
saturn_ring.py
Generates a flat annulus (ring) mesh in the XZ plane for Saturn's rings.
The fragment shader fades opacity from inner to outer edge procedurally,
so no ring texture image is required.
"""

import numpy as np


def create_ring(inner_radius, outer_radius, segments=96):
    """
    Returns (vertices, indices).
    vertices: [x, y, z, u(=radial fraction 0..1), v(unused)] per vertex,
    two rings of points (inner edge, outer edge) triangulated into a strip.
    """
    vertices = []
    angles = np.linspace(0.0, 2.0 * np.pi, segments, endpoint=True)

    for angle in angles:
        cx, cz = np.cos(angle), np.sin(angle)
        # inner vertex: u = 0.0 (fully transparent edge)
        vertices.extend([inner_radius * cx, 0.0, inner_radius * cz, 0.0, 0.0])
        # outer vertex: u = 1.0
        vertices.extend([outer_radius * cx, 0.0, outer_radius * cz, 1.0, 0.0])

    indices = []
    for i in range(segments - 1):
        base = i * 2
        indices.extend([base, base + 1, base + 2])
        indices.extend([base + 1, base + 3, base + 2])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)
