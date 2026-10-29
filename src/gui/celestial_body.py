"""
celestial_body.py
Represents the Sun, a planet, or a moon: its geometry, orbit parameters,
and per-frame transform update.
"""

import math
import numpy as np
from pyrr import matrix44


class CelestialBody:
    def __init__(self, name, radius, orbit_radius, orbit_speed,
                 spin_speed, texture_path=None, parent=None, color=(1.0, 1.0, 1.0),
                 axial_tilt=0.0, has_rings=False):
        """
        name: display name (e.g. "Earth")
        radius: visual radius of the sphere (scaled, not real km)
        orbit_radius: distance from parent body (scaled)
        orbit_speed: degrees per second around parent
        spin_speed: degrees per second around own axis
        texture_path: path to a texture image (None -> flat color)
        parent: CelestialBody this orbits (None for the Sun)
        color: fallback RGB if no texture is used
        axial_tilt: tilt of the spin axis in degrees (visual realism, e.g. Earth ~23.4, Uranus ~97.8)
        has_rings: whether this body should render a Saturn-style ring
        """
        self.name = name
        self.radius = radius
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed
        self.spin_speed = spin_speed
        self.texture_path = texture_path
        self.parent = parent
        self.color = color
        self.axial_tilt = axial_tilt
        self.has_rings = has_rings

        self.orbit_angle = 0.0
        self.spin_angle = 0.0
        self.moons = []

        self.texture_id = None  # populated by renderer when texture is loaded

        # --- Elite-feature state (gravity slider, destroy button, time travel) ---
        self._base_orbit_speed = orbit_speed  # restore point for the gravity slider
        self._base_spin_speed = spin_speed
        self.gravity_multiplier = 1.0

        self.destroyed = False        # True once the destroy sequence has been triggered
        self.destroy_timer = 0.0      # seconds since destruction was triggered
        self.pre_destroy_scale = 1.0  # planet shrinks briefly before the burst

        self.time_travel_years = 0.0  # slider value, -100..+100, purely cosmetic tint/shape shift

        self.rain_enabled = False     # weather toggle from the info panel

    def add_moon(self, moon):
        self.moons.append(moon)

    def update(self, dt):
        """Advance orbit and spin angles by dt seconds."""
        if self.destroyed:
            self.destroy_timer += dt
            # Orbit/spin freeze in place once destroyed -- the explosion
            # particle system takes over visual motion from here.
            for moon in self.moons:
                moon.update(dt)
            return

        self.orbit_angle = (self.orbit_angle + self.orbit_speed * dt) % 360.0
        self.spin_angle = (self.spin_angle + self.spin_speed * dt) % 360.0
        for moon in self.moons:
            moon.update(dt)

    def trigger_destruction(self):
        """Marks this body (and its moons) for the destroy-planet sequence."""
        if self.destroyed:
            return
        self.destroyed = True
        self.destroy_timer = 0.0

    def reset_destruction(self):
        """Restores the body after a destroy sequence (e.g. 'Rebuild' button)."""
        self.destroyed = False
        self.destroy_timer = 0.0
        self.pre_destroy_scale = 1.0

    def get_time_travel_tint(self):
        """
        Returns an RGB multiplier applied on top of base_color/texture to give
        a stylized "what this planet may look like" push toward the past
        (cooler/dimmer) or future (warmer/brighter), driven by time_travel_years
        in [-100, 100]. Purely an artistic visualization, see planet_facts.py
        future_note for the per-planet framing shown in the UI.
        """
        t = max(-100.0, min(100.0, self.time_travel_years)) / 100.0  # -1..1
        if t >= 0.0:
            # Future: warmer, slightly brighter
            return (1.0 + 0.18 * t, 1.0 + 0.05 * t, 1.0 - 0.12 * t)
        # Past: cooler, slightly dimmer
        return (1.0 + 0.10 * t, 1.0 + 0.08 * t, 1.0 - 0.15 * t)

    def get_world_position(self):
        """World-space (x, y, z) position, accounting for parent's position."""
        rad = math.radians(self.orbit_angle)
        local_x = self.orbit_radius * math.cos(rad)
        local_z = self.orbit_radius * math.sin(rad)

        if self.parent is not None:
            px, py, pz = self.parent.get_world_position()
            return (px + local_x, py, pz + local_z)
        return (local_x, 0.0, local_z)

    def get_model_matrix(self, scale_override=None):
        """Model matrix = translate(orbit position) * tilt * rotate(spin) * scale(radius)."""
        x, y, z = self.get_world_position()

        r = self.radius if scale_override is None else scale_override
        translate = matrix44.create_from_translation([x, y, z])
        spin = matrix44.create_from_y_rotation(math.radians(self.spin_angle))
        tilt = matrix44.create_from_z_rotation(math.radians(self.axial_tilt))
        scale = matrix44.create_from_scale([r, r, r])

        model = matrix44.multiply(scale, spin)
        model = matrix44.multiply(model, tilt)
        model = matrix44.multiply(model, translate)
        return model.astype(np.float32)

    def get_ring_model_matrix(self, ring_scale=2.3):
        """Model matrix for a ring mesh: positioned at this body, tilted, scaled by radius."""
        x, y, z = self.get_world_position()
        translate = matrix44.create_from_translation([x, y, z])
        tilt = matrix44.create_from_z_rotation(math.radians(self.axial_tilt + 5.0))
        scale = matrix44.create_from_scale([self.radius * ring_scale, 1.0, self.radius * ring_scale])

        model = matrix44.multiply(scale, tilt)
        model = matrix44.multiply(model, translate)
        return model.astype(np.float32)
