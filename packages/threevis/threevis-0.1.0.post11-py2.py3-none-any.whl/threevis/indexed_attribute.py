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
    def __init__(self, values, indices):
        assert(len(values) == len(indices))
        self.values = values
        self.indices = indices
        self.face_remap = None

class PointAttribute(IndexedAttribute):
    def __init__(self, values, indices = None):
        if indices is None:
            indices = range(0, len(values))
        super(PointAttribute, self).__init__(values, indices)

    def resolve(self, face_indices):
        result = []
        vertex_to_face = dict()
        for fidx, face in enumerate(face_indices):
            for index_in_face, vidx in enumerate(face):
                if vidx not in vertex_to_face:
                    vertex_to_face[vidx] = []
                vertex_to_face[vidx].append((fidx, index_in_face))

        for i, val in enumerate(self.values):
            idx = self.indices[i]
            if idx in vertex_to_face:
                for occurence in vertex_to_face[idx]:
                    result.append((occurence[0], occurence[1], val))

        return result

class FaceAttribute(IndexedAttribute):
    def __init__(self, values, indices = None):
        if indices is None:
            indices = range(0, len(values))
        super(FaceAttribute, self).__init__(values, indices)

    def resolve(self, face_indices):
        result = []
        if self.face_remap is None:
            self.face_remap = range(len(self.indices))

        for i, fidx in enumerate(self.face_remap):
            idx = self.indices[fidx]
            val = self.values[idx]

            # Add value for all vertices in the face
            for f_vidx in range(len(face_indices[i])):
                result.append((i, f_vidx, val))

        return result

class HalfEdgeAttribute(IndexedAttribute):
    def __init__(self, values, indices):
        super(HalfEdgeAttribute, self).__init__(values, indices)

    def resolve(self, face_indices):
        result = []
        for i, val in enumerate(self.values):
            idx = self.indices[i]

            # find all faces that contain the vertex
            for f_idx, face in enumerate(face_indices):
                # check if edge is in face
                start_idx_in_face = find(idx[0], face)
                end_idx_in_face = find(idx[1], face)

                # both ends need to be in the face
                if start_idx_in_face is None or end_idx_in_face is None:
                    continue

                # and the edge needs to point in the right direction
                if (start_idx_in_face + 1) % len(face) is not end_idx_in_face:
                    continue

                # value of half edge counts as value of the vertex that's pointed towards
                result.append((f_idx, end_idx_in_face, val))

        return result