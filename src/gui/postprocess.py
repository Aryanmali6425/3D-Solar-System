"""
postprocess.py
A small offscreen post-processing pipeline:

  scene FBO (color+depth)
      -> bright-pass extract (half-res)
      -> ping-pong gaussian blur (a few iterations)
      -> composite pass: scene + bloom + radial god-rays (reusing the blurred
         bright texture as the god-ray sample source) + vignette + chromatic
         aberration, drawn to the default framebuffer.

Kept deliberately simple (no HDR/exposure pipeline) so it stays robust across
GPUs/drivers for a course submission, while still reading as a "real"
post-processing stack rather than a single glow sprite.
"""

import os
from OpenGL.GL import *
from shader_loader import load_shader_program

SHADER_DIR = os.path.join(os.path.dirname(__file__), "..", "shaders")


def _make_color_fbo(width, height, with_depth=False):
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, width, height, 0, GL_RGB, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0)

    depth_rbo = None
    if with_depth:
        depth_rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, depth_rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_rbo)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError("Post-processing framebuffer is incomplete")

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    return fbo, tex, depth_rbo


class PostProcessPipeline:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.half_w, self.half_h = max(1, width // 2), max(1, height // 2)

        self.scene_fbo, self.scene_tex, self.scene_depth = _make_color_fbo(width, height, with_depth=True)
        self.bright_fbo, self.bright_tex, _ = _make_color_fbo(self.half_w, self.half_h)
        self.blur_fbo_a, self.blur_tex_a, _ = _make_color_fbo(self.half_w, self.half_h)
        self.blur_fbo_b, self.blur_tex_b, _ = _make_color_fbo(self.half_w, self.half_h)

        self.dummy_vao = glGenVertexArrays(1)  # fullscreen triangle needs no attributes

        self.brightpass_shader = load_shader_program(
            os.path.join(SHADER_DIR, "fullscreen.vert"), os.path.join(SHADER_DIR, "brightpass.frag"))
        self.blur_shader = load_shader_program(
            os.path.join(SHADER_DIR, "fullscreen.vert"), os.path.join(SHADER_DIR, "blur.frag"))
        self.composite_shader = load_shader_program(
            os.path.join(SHADER_DIR, "fullscreen.vert"), os.path.join(SHADER_DIR, "composite.frag"))

    def resize(self, width, height):
        self.__init__(width, height)  # simplest robust approach: recreate all FBOs

    def begin_scene(self):
        """Call before rendering the normal 3D scene."""
        glBindFramebuffer(GL_FRAMEBUFFER, self.scene_fbo)
        glViewport(0, 0, self.width, self.height)

    def _draw_fullscreen_triangle(self):
        glBindVertexArray(self.dummy_vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)

    def end_scene_and_composite(self, sun_screen_pos, sun_intensity, elapsed_time, blur_iterations=4):
        """
        Runs bright-pass -> blur -> composite, writing the final image to the
        default framebuffer (the visible window). sun_screen_pos is a
        (u, v) tuple in 0..1 UV space (can be outside [0,1] if off-screen).
        """
        glDisable(GL_DEPTH_TEST)

        # 1) Bright-pass extract, half resolution
        glBindFramebuffer(GL_FRAMEBUFFER, self.bright_fbo)
        glViewport(0, 0, self.half_w, self.half_h)
        glUseProgram(self.brightpass_shader)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.scene_tex)
        glUniform1i(glGetUniformLocation(self.brightpass_shader, "scene_tex"), 0)
        glUniform1f(glGetUniformLocation(self.brightpass_shader, "threshold"), 0.9)
        self._draw_fullscreen_triangle()

        # 2) Ping-pong gaussian blur
        read_tex = self.bright_tex
        for i in range(blur_iterations):
            # horizontal -> blur_fbo_a
            glBindFramebuffer(GL_FRAMEBUFFER, self.blur_fbo_a)
            glViewport(0, 0, self.half_w, self.half_h)
            glUseProgram(self.blur_shader)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, read_tex)
            glUniform1i(glGetUniformLocation(self.blur_shader, "image_tex"), 0)
            glUniform2f(glGetUniformLocation(self.blur_shader, "texel_size"), 1.0 / self.half_w, 1.0 / self.half_h)
            glUniform2f(glGetUniformLocation(self.blur_shader, "direction"), 1.0, 0.0)
            self._draw_fullscreen_triangle()

            # vertical -> blur_fbo_b
            glBindFramebuffer(GL_FRAMEBUFFER, self.blur_fbo_b)
            glViewport(0, 0, self.half_w, self.half_h)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.blur_tex_a)
            glUniform2f(glGetUniformLocation(self.blur_shader, "direction"), 0.0, 1.0)
            self._draw_fullscreen_triangle()

            read_tex = self.blur_tex_b

        # 3) Composite to the default framebuffer (the actual window)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.width, self.height)
        glUseProgram(self.composite_shader)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.scene_tex)
        glUniform1i(glGetUniformLocation(self.composite_shader, "scene_tex"), 0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, read_tex)
        glUniform1i(glGetUniformLocation(self.composite_shader, "bloom_tex"), 1)
        glUniform2f(glGetUniformLocation(self.composite_shader, "sun_screen_pos"), *sun_screen_pos)
        glUniform1f(glGetUniformLocation(self.composite_shader, "sun_intensity"), sun_intensity)
        glUniform1f(glGetUniformLocation(self.composite_shader, "time"), elapsed_time)
        self._draw_fullscreen_triangle()

        glEnable(GL_DEPTH_TEST)
