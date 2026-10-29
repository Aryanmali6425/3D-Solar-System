"""
starfield.py
Generates a large shell of randomly placed points to act as a procedural
"galaxy" background -- thousands of stars with varying brightness and a
faint color tint (white/blue/warm), no texture file required.
"""

import numpy as np


def create_starfield(num_stars=6000, min_radius=150.0, max_radius=400.0, seed=42):
    """
    Returns a flat float32 array of [x, y, z, brightness, r, g, b] per star,
    scattered uniformly over a spherical shell around the origin so they're
    always "behind" the solar system regardless of camera position.
    """
    rng = np.random.default_rng(seed)

    # Uniform points on a sphere shell (rejection-free method)
    phi = rng.uniform(0.0, 2.0 * np.pi, num_stars)
    costheta = rng.uniform(-1.0, 1.0, num_stars)
    theta = np.arccos(costheta)
    radius = rng.uniform(min_radius, max_radius, num_stars)

    x = radius * np.sin(theta) * np.cos(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(theta)

    brightness = rng.uniform(0.3, 1.0, num_stars) ** 2  # bias toward dimmer stars

    # Star color tint: mostly white, some cool blue, some warm amber -- gives
    # a more "galaxy photo" feel than flat white dots.
    tint_roll = rng.uniform(0.0, 1.0, num_stars)
    colors = np.ones((num_stars, 3), dtype=np.float32)
    blue_mask = tint_roll < 0.15
    warm_mask = tint_roll > 0.90
    colors[blue_mask] = [0.7, 0.8, 1.0]
    colors[warm_mask] = [1.0, 0.85, 0.6]

    data = np.column_stack([x, y, z, brightness, colors]).astype(np.float32)
    return data.flatten()
