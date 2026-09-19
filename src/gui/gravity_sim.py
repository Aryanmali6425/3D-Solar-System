"""
gravity_sim.py
A simplified, visually-driven (not physically rigorous) gravity slider
effect. Real N-body simulation is out of scope for a real-time demo; instead
we approximate the *visible consequences* of more/less gravity in a way
that reads clearly on screen, applied independently to whichever body the
person has selected:

  - multiplier > 1 ("stronger gravity"): this body's orbit speeds up, and if
    it orbits a parent (i.e. it's a planet or moon), it slowly spirals
    inward (orbit_radius shrinks) -- eventually "captured".
  - multiplier < 1 ("weaker gravity"): orbit slows down, and an orbiting
    body slowly drifts outward (orbit_radius grows) -- eventually "escapes".
  - multiplier == 1: behaves exactly like the original simulation.

Each body tracks its own gravity_multiplier independently (set via the UI's
Weather & Gravity tab when that body is selected), so adjusting a moon's
gravity does not require also touching its parent planet's.
"""

DRIFT_RATE = 0.35  # orbit_radius units per second at multiplier extremes


def apply_gravity(body, multiplier, dt):
    """Mutates one body's effective orbit_speed/spin_speed/orbit_radius for this frame."""
    body.gravity_multiplier = multiplier
    body.orbit_speed = body._base_orbit_speed * multiplier
    body.spin_speed = body._base_spin_speed * (0.5 + 0.5 * multiplier)

    if body.parent is not None:
        drift = (multiplier - 1.0) * DRIFT_RATE * dt
        # Stronger gravity (multiplier > 1) pulls the body inward (shrinks
        # radius); weaker gravity lets it drift outward.
        body.orbit_radius = max(0.05, body.orbit_radius - drift)


def reset_gravity(body):
    body.gravity_multiplier = 1.0
    body.orbit_speed = body._base_orbit_speed
    body.spin_speed = body._base_spin_speed
