
import openmesh as om
from .immediate import display_faces

def display_openmesh(mesh):
    display_faces(mesh.points(), mesh.face_vertex_indices())

def display_file(path):
    m = om.TriMesh()
    om.read_mesh(m, path)

    display_openmesh(m)
