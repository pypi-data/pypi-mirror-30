import numpy as np

def stretch_vertices(vertices, face_indices):
    stretched_verts = []

    for face in face_indices:
        for vidx in face:
            if vidx != -1:
                stretched_verts.append(vertices[vidx])

    return np.array(stretched_verts), np.arange(0, len(stretched_verts))


def resolve_attributes(face_indices, attribs):
    final_attributes = []

    for attrib in attribs:
        if attrib is None:
            final_attributes.append(None)
            continue

        resolved_attrib = attrib.resolve(face_indices)
        final_attributes.append(stretch_attribute(face_indices, resolved_attrib))

    return final_attributes

def stretch_attribute(face_indices, resolved_attrib):
    face_valence = (face_indices != -1).sum(1)
    totalVertexCount = face_valence.sum()
    flattened_face_start = np.cumsum(face_valence) - face_valence

    stretched_attrib = [None] * totalVertexCount

    for val in resolved_attrib:
        stretched_attrib[ flattened_face_start[val[0]] + val[1]] = val[2]

    return np.array(stretched_attrib)

def find(element, list_element):
    index_element = np.where(list_element==element)
    if len(index_element[0]) > 0: return index_element[0][0]
    return None


class UniformAttribute(object):
    def __init__(self, value):
        self.value = value


    def resolve(self, face_indices):
        result = []
        for f_idx, face in enumerate(face_indices):
            for idx_in_face, _ in enumerate(face):
                result.append((f_idx, idx_in_face, self.value))

        return result

class IndexedAttribute(object):
    def __init__(self, values):
        self.values = values
        self.face_remap = None
        self.halfedge_remap = None

class PointAttribute(IndexedAttribute):
    def __init__(self, values):
        super(PointAttribute, self).__init__(values)

    def resolve(self, face_indices):
        result = []
        vertex_to_face = dict()
        for fidx, face in enumerate(face_indices):
            for index_in_face, vidx in enumerate(face):
                if vidx not in vertex_to_face:
                    vertex_to_face[vidx] = []
                vertex_to_face[vidx].append((fidx, index_in_face))

        for idx, val in enumerate(self.values):
            if idx in vertex_to_face:
                for occurence in vertex_to_face[idx]:
                    result.append((occurence[0], occurence[1], val))

        return result

class FaceAttribute(IndexedAttribute):
    def __init__(self, values):
        super(FaceAttribute, self).__init__(values)

    def resolve(self, face_indices):
        result = []
        if self.face_remap is None:
            self.face_remap = range(len(face_indices))

        for i, fidx in enumerate(self.face_remap):
            val = self.values[fidx]

            # Add value for all vertices in the face
            for f_vidx in range(len(face_indices[i])):
                result.append((i, f_vidx, val))

        return result

class HalfEdgeAttribute(IndexedAttribute):
    def __init__(self, values, halfedge_vertex_indices, halfedge_face_indices):
        self.halfedge_vertex_indices = halfedge_vertex_indices
        self.halfedge_face_indices = halfedge_face_indices
        self.halfedge_remap = None
        super(HalfEdgeAttribute, self).__init__(values)

    def resolve(self, face_indices):
        result = []

        if self.halfedge_remap is None:
            self.halfedge_remap = []
            for i, f in enumerate(face_indices):
                self.halfedge_remap.append( {f[0]: [(i,0)], f[1]: [(i,1)], f[2]: [(i,2)]} )


        for i, edge in enumerate(self.halfedge_vertex_indices):
            face = self.halfedge_face_indices[i]
            val = self.values[i]

            if face == -1:
                continue
                
            for fv_idx in self.halfedge_remap[face][edge[1]]:
                result.append((fv_idx[0], fv_idx[1], val))



        return result