"""
texture_loader.py
Loads an image file into an OpenGL 2D texture. Returns None (and prints a
warning) if the file is missing, so the renderer can fall back to a flat
base_color instead of crashing -- useful during early development before
you've sourced planet textures.
"""

import os
from OpenGL.GL import *
from PIL import Image


def load_texture(path):
    if not path or not os.path.isfile(path):
        print(f"[texture_loader] Warning: texture not found: {path} (using flat color fallback)")
        return None

    image = Image.open(path).convert("RGBA")
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = image.tobytes()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)

    return tex_id
