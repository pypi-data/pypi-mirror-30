import numpy as np
from .mesh_helper import calculate_face_normals, calculate_point_normals

class Mesh():
    """
    A polygonal mesh. Faces can have varying valence.
    """
    
    def __init__(self, vertices, face_indices, normals=None, colors=None, uvs=None):
        self.normals = normals
        self.colors = colors
        self.uvs = uvs
        
        self.face_valence = (face_indices != -1).sum(1)

        minValence = self.face_valence.min(axis = 0)
        maxValuence = self.face_valence.max(axis = 0)
        self.uniform_valence = minValence == maxValuence
        
        self.is_triangulated = self.uniform_valence and self.face_valence[0] == 3

        self.vertices = vertices
        self.face_indices = face_indices

    def prepare_render(self):
        if not self.normals:
            self.calculate_normals()

        self.triangulate()

        if self.normals: 
            self.normals.face_remap = self.triangulate_face_to_attribute_face
            self.normals.halfedge_remap = self.attribute_face_vertex_to_triangulate_face_vertex
        
        if self.colors:
            self.colors.face_remap = self.triangulate_face_to_attribute_face
            self.colors.halfedge_remap = self.attribute_face_vertex_to_triangulate_face_vertex
        
        if self.uvs:
            self.uvs.face_remap = self.triangulate_face_to_attribute_face
            self.uvs.halfedge_remap = self.attribute_face_vertex_to_triangulate_face_vertex

    def calculate_normals(self, normal_element = 'face'):
        assert(normal_element is 'face' or normal_element is 'point')
        
        if normal_element is 'face':
            self.normals = calculate_face_normals(self.vertices, self.face_indices)
        else:
            self.normals = calculate_point_normals(self.vertices, self.face_indices)

    def triangulate(self):
        if self.is_triangulated:
            self.tri_face_indices = self.face_indices
            self.triangulate_face_to_attribute_face = np.arange(len(self.face_indices))
            self.attribute_face_vertex_to_triangulate_face_vertex = None
            return
        
        new_faces = []

        triangulate_face_to_attribute_face = []
        self.attribute_face_vertex_to_triangulate_face_vertex = []

        halfedge_index = 0
        for fid, face in enumerate(self.face_indices):
            originVertex = face[0]

            face_to_face = { originVertex: [], face[1]: [] }

            for in_face_idx in range(2, self.face_valence[fid]):
                triangulate_face_to_attribute_face.append(fid)
                
                face_to_face[originVertex].append((len(new_faces), 0))
                face_to_face[face[in_face_idx-1]].append((len(new_faces), 1))
                face_to_face[face[in_face_idx]] = [(len(new_faces), 2)]
                
                new_faces.append([originVertex, face[in_face_idx-1], face[in_face_idx]])
            
            self.attribute_face_vertex_to_triangulate_face_vertex.append(face_to_face)
            halfedge_index += self.face_valence[fid]

        self.triangulate_face_to_attribute_face = np.array(triangulate_face_to_attribute_face)
        self.tri_face_indices = np.array(new_faces)
        
        self.is_triangulated = True
        
        

class PointList():
    def __init__(self, vertices, colors = None, uvs = None):
        self.vertices = vertices
        self.colors = colors
        self.uvs = uvs

    def prepare_render(self):
        pass


class EdgeList():

    def __init__(self, vertices, edge_indices, colors=None, uvs=None):
        self.vertices = vertices
        self.edge_indices = edge_indices
        self.colors = colors
        self.uvs = uvs

    def prepare_render(self):
        pass
