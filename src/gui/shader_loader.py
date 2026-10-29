"""
shader_loader.py
Reads GLSL source files and compiles/links them into an OpenGL program.
"""

from OpenGL.GL import *


def _compile(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        log = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Shader compile error:\n{log}")
    return shader


def load_shader_program(vert_path, frag_path):
    with open(vert_path, "r") as f:
        vert_src = f.read()
    with open(frag_path, "r") as f:
        frag_src = f.read()

    vert_shader = _compile(vert_src, GL_VERTEX_SHADER)
    frag_shader = _compile(frag_src, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vert_shader)
    glAttachShader(program, frag_shader)
    glLinkProgram(program)

    if not glGetProgramiv(program, GL_LINK_STATUS):
        log = glGetProgramInfoLog(program).decode()
        raise RuntimeError(f"Shader link error:\n{log}")

    glDeleteShader(vert_shader)
    glDeleteShader(frag_shader)
    return program
