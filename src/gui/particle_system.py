"""
particle_system.py
A lightweight CPU-simulated, GPU-instanced-via-points particle system used
for two "elite feature" effects:

  - RainSystem: falling weather particles above a chosen planet.
  - ExplosionSystem: the "destroy planet" burst + debris + shockwave.

Particles are updated in Python/NumPy each frame (fine for a few thousand
points) and streamed to a dynamic VBO with glBufferSubData, then drawn as
GL_POINTS with the particle shader (see shaders/particle.vert/.frag), using
additive blending for a glowing look.

Layout per particle (7 floats): x, y, z, size, r, g, b   (alpha is derived
from remaining lifetime in the shader via a per-particle "life" field, so
we actually store 8 floats: x, y, z, size, r, g, b, life01)
"""

import ctypes
import numpy as np
from OpenGL.GL import *

FLOATS_PER_PARTICLE = 8  # x, y, z, size, r, g, b, life01(1.0=fresh, 0.0=dead)
MAX_PARTICLES = 4000


class ParticleSystem:
    """Base class: owns the GPU buffer and the generic update/draw plumbing."""

    def __init__(self, max_particles=MAX_PARTICLES):
        self.max_particles = max_particles
        self.positions = np.zeros((max_particles, 3), dtype=np.float32)
        self.velocities = np.zeros((max_particles, 3), dtype=np.float32)
        self.sizes = np.zeros(max_particles, dtype=np.float32)
        self.colors = np.ones((max_particles, 3), dtype=np.float32)
        self.lifetimes = np.zeros(max_particles, dtype=np.float32)   # seconds remaining
        self.max_lifetimes = np.ones(max_particles, dtype=np.float32)
        self.alive = np.zeros(max_particles, dtype=bool)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, max_particles * FLOATS_PER_PARTICLE * 4, None, GL_DYNAMIC_DRAW)
        stride = FLOATS_PER_PARTICLE * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))   # position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))  # size
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(4 * 4))  # color
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(7 * 4))  # life01
        glEnableVertexAttribArray(3)
        glBindVertexArray(0)

        self._live_count = 0

    def _find_free_slot(self):
        free = np.where(~self.alive)[0]
        return int(free[0]) if len(free) else None

    def spawn(self, position, velocity, size, color, lifetime):
        slot = self._find_free_slot()
        if slot is None:
            return
        self.positions[slot] = position
        self.velocities[slot] = velocity
        self.sizes[slot] = size
        self.colors[slot] = color
        self.lifetimes[slot] = lifetime
        self.max_lifetimes[slot] = max(lifetime, 1e-4)
        self.alive[slot] = True

    def update(self, dt):
        idx = np.where(self.alive)[0]
        if len(idx) == 0:
            self._live_count = 0
            return
        self.positions[idx] += self.velocities[idx] * dt
        self.lifetimes[idx] -= dt
        died = idx[self.lifetimes[idx] <= 0.0]
        self.alive[died] = False

    def upload_and_draw(self, shader):
        idx = np.where(self.alive)[0]
        count = len(idx)
        self._live_count = count
        if count == 0:
            return

        life01 = np.clip(self.lifetimes[idx] / self.max_lifetimes[idx], 0.0, 1.0)
        buf = np.empty((count, FLOATS_PER_PARTICLE), dtype=np.float32)
        buf[:, 0:3] = self.positions[idx]
        buf[:, 3] = self.sizes[idx]
        buf[:, 4:7] = self.colors[idx]
        buf[:, 7] = life01
        flat = buf.flatten()

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, flat.nbytes, flat)
        glUseProgram(shader)
        glDrawArrays(GL_POINTS, 0, count)
        glBindVertexArray(0)

    @property
    def live_count(self):
        return self._live_count


class RainSystem(ParticleSystem):
    """
    Continuous weather effect: spawns falling particles in a disc above the
    planet's "up" pole and lets them fall/slide across the surface before
    fading, then respawns. Purely visual -- not a climate simulation.
    """

    def __init__(self, max_particles=1500):
        super().__init__(max_particles)
        self.spawn_accumulator = 0.0
        self.spawn_rate = 500.0  # particles/sec while active

    def update_for_planet(self, body, dt, active):
        if active:
            self.spawn_accumulator += dt * self.spawn_rate
            spawn_count = int(self.spawn_accumulator)
            self.spawn_accumulator -= spawn_count
            cx, cy, cz = body.get_world_position()
            r = body.radius
            for _ in range(spawn_count):
                theta = np.random.uniform(0, 2 * np.pi)
                dist = np.random.uniform(0, r * 0.9)
                height = r * np.random.uniform(1.4, 1.9)
                pos = np.array([
                    cx + dist * np.cos(theta),
                    cy + height,
                    cz + dist * np.sin(theta),
                ], dtype=np.float32)
                vel = np.array([0.0, -r * np.random.uniform(1.8, 2.6), 0.0], dtype=np.float32)
                color = (0.55, 0.75, 1.0)
                self.spawn(pos, vel, size=max(2.0, r * 6.0), color=color,
                           lifetime=np.random.uniform(0.5, 0.9))
        self.update(dt)


class ExplosionSystem(ParticleSystem):
    """
    One-shot "destroy the planet" burst: a spherical shell of glowing debris
    flying outward from the planet's position with drag and a color ramp
    from white-hot -> orange -> ash-gray as each particle ages, plus a
    handful of larger tumbling "rock" particles for readability at a glance.
    """

    def __init__(self, max_particles=2500):
        super().__init__(max_particles)

    def detonate(self, center, base_radius, count=1200):
        center = np.array(center, dtype=np.float32)
        for _ in range(min(count, self.max_particles)):
            # Uniform direction on a sphere
            vec = np.random.normal(size=3).astype(np.float32)
            vec /= (np.linalg.norm(vec) + 1e-6)
            speed = base_radius * np.random.uniform(3.0, 9.0)
            vel = vec * speed
            size = np.random.uniform(0.06, 0.22) * (base_radius * 6.0 + 1.0)
            color = (1.0, np.random.uniform(0.55, 0.85), np.random.uniform(0.15, 0.4))
            lifetime = np.random.uniform(1.2, 2.6)
            self.spawn(center, vel, size=size, color=color, lifetime=lifetime)

    def update(self, dt):
        # Drag so the burst decelerates, plus a color shift toward ash-gray
        # as particles age (handled in-shader via life01, see particle.frag).
        idx = np.where(self.alive)[0]
        if len(idx):
            self.velocities[idx] *= max(0.0, 1.0 - 0.6 * dt)
        super().update(dt)
