"""
picking.py
Mouse-click "select a planet" support via ray casting: unprojects the mouse
position into a world-space ray, then tests that ray against every body's
world-space bounding sphere and returns the closest hit.
"""

import numpy as np
from pyrr import matrix44


def screen_to_world_ray(mouse_x, mouse_y, screen_w, screen_h, view, projection):
    """
    Converts a 2D mouse position (pixels, origin top-left) into a world-space
    ray (origin, direction) using the classic NDC -> clip -> eye -> world
    unprojection chain.
    """
    # Normalized device coordinates in [-1, 1], y flipped (screen y grows downward)
    ndc_x = (2.0 * mouse_x) / screen_w - 1.0
    ndc_y = 1.0 - (2.0 * mouse_y) / screen_h

    clip_near = np.array([ndc_x, ndc_y, -1.0, 1.0], dtype=np.float32)
    clip_far = np.array([ndc_x, ndc_y, 1.0, 1.0], dtype=np.float32)

    # NOTE: pyrr matrices here follow a row-vector convention (v @ M), matching
    # how model/view/projection matrices are built and uploaded elsewhere in
    # this project (see the comment in main.py's post-process composite step).
    # For a vector v and matrix M this means v @ M == M.T @ v, so unprojection
    # (which is naturally a M^-1 @ v operation) is written here as v @ M^-1.
    inv_proj = np.linalg.inv(np.array(projection))
    inv_view = np.linalg.inv(np.array(view))

    eye_near = clip_near.dot(inv_proj)
    eye_near /= eye_near[3]
    eye_far = clip_far.dot(inv_proj)
    eye_far /= eye_far[3]

    world_near = eye_near.dot(inv_view)
    world_far = eye_far.dot(inv_view)

    origin = world_near[:3]
    direction = world_far[:3] - world_near[:3]
    norm = np.linalg.norm(direction)
    if norm > 1e-8:
        direction = direction / norm
    return origin.astype(np.float32), direction.astype(np.float32)


def ray_sphere_intersect(ray_origin, ray_dir, sphere_center, sphere_radius):
    """
    Returns the distance along the ray to the nearest intersection with a
    sphere, or None if the ray misses it.
    """
    oc = ray_origin - np.array(sphere_center, dtype=np.float32)
    b = np.dot(oc, ray_dir)
    c = np.dot(oc, oc) - sphere_radius * sphere_radius
    discriminant = b * b - c
    if discriminant < 0.0:
        return None
    sqrt_disc = np.sqrt(discriminant)
    t0 = -b - sqrt_disc
    t1 = -b + sqrt_disc
    t = t0 if t0 > 0.0 else t1
    if t < 0.0:
        return None
    return float(t)


def pick_body(mouse_x, mouse_y, screen_w, screen_h, view, projection, bodies,
              pick_radius_scale=1.6):
    """
    bodies: iterable of objects with .get_world_position() and .radius
    pick_radius_scale: inflates the hit sphere a little so small/far planets
    are easier to click (a common "generous hitbox" UX trick).
    Returns the closest hit body, or None.
    """
    origin, direction = screen_to_world_ray(mouse_x, mouse_y, screen_w, screen_h, view, projection)

    best_body = None
    best_t = float("inf")
    for body in bodies:
        if getattr(body, "destroyed", False):
            continue
        center = body.get_world_position()
        radius = body.radius * pick_radius_scale
        t = ray_sphere_intersect(origin, direction, center, radius)
        if t is not None and t < best_t:
            best_t = t
            best_body = body
    return best_body
