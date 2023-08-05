"""
Immediate drawing without explicitely creating a context.
"""

from .context import Context

def display_faces(vertices, face_indices, normals=None, colors=None, uvs=None,
                  shading='flat', z_offset=0.5, texture=None, width=600, height=400,
                  background_color = '#dddddd', clipping_planes = [], show_bounds = False):
    Context(width, height, background_color).draw_faces(vertices, face_indices, normals, colors, uvs, shading, z_offset, texture, clipping_planes).set_bounds(show_bounds).display()

def display_edges(vertices, edge_indices=None, colors=None, uvs=None,
                  z_offset=0, texture=None, line_width=1, width=600, height=400,
                  background_color = '#dddddd', clipping_planes = [], show_bounds = False):
    Context(width, height, background_color).draw_edges(vertices, edge_indices, colors, uvs, z_offset, texture, line_width, clipping_planes).set_bounds(show_bounds).display()

def display_vertices(vertices, colors=None, uvs=None, point_size=1, z_offset=0, texture=None,
                     perspective=False, width=600, height=400,
                     background_color = '#dddddd', clipping_planes = [], show_bounds = False):
    Context(width, height, background_color).draw_vertices(vertices, colors, uvs, point_size, z_offset, texture, perspective, clipping_planes).set_bounds(show_bounds).display()

def display(obj, shading='flat', point_size=1, z_offset=0, texture=None,
            perspective=False, width=600, height=400,
            background_color = '#dddddd', clipping_planes = [], show_bounds = False):
    Context(width, height, background_color).draw(obj, shading= shading, point_size = point_size, z_offset= z_offset, texture = texture, perspective = perspective, clipping_planes = clipping_planes).set_bounds(show_bounds).display()