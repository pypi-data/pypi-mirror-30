from .indexed_attribute import FaceAttribute, PointAttribute, resolve_attributes, stretch_vertices
import numpy as np


def calculate_normal_edges(vertices, face_indices, normals, length):

    resolved_normals = None

    if isinstance(normals, FaceAttribute):
        resolved_normals = normals.values
        face_centers = []
        for face in face_indices:
            face_centers.append(np.average(vertices[face], axis=0, weights=face!=-1))
        vertices = face_centers
    elif face_indices is not None:
        resolved_normals = resolve_attributes(face_indices, [normals])[0]
        vertices, face_indices = stretch_vertices(vertices, face_indices)
    else:
        resolved_normals = normals

    edge_vertices = []
    edge_indices = []
    for i, vert in enumerate(vertices):

        norm = np.array(resolved_normals[i])
        vert = np.array(vert)

        edge_vertices.append(vert)
        edge_vertices.append(np.add(norm*length, vert))

        edge_indices.append([i*2, i*2 + 1])

    return edge_vertices, edge_indices

def calculate_face_normals(vertices, face_indices):
    values = []
    for face in face_indices:
        # Assuming face is planar
        v1 = np.array(vertices[face[0]])
        v2 = np.array(vertices[face[1]])
        v3 = np.array(vertices[face[2]])

        v12 = np.subtract(v2, v1)
        v13 = np.subtract(v3, v1)

        norm = np.cross(v12, v13)
        norm = norm / np.linalg.norm(norm)
        values.append(norm)

    return FaceAttribute(values)

def calculate_point_normals(vertices, face_indices):
    normals = np.zeros_like(vertices)
    counts = np.zeros(vertices.shape[0])

    for face in face_indices:
        # Assuming face is planar
        v1 = np.array(vertices[face[0]])
        v2 = np.array(vertices[face[1]])
        v3 = np.array(vertices[face[2]])

        v12 = np.subtract(v2, v1)
        v13 = np.subtract(v3, v1)

        norm = np.cross(v12, v13)

        filtered_face = face[np.where(face != -1)]
        normals[filtered_face] += norm
        counts[filtered_face] += 1

    normals /= counts.reshape(-1, 1)
    normals /= np.linalg.norm(normals, axis=1).reshape(-1, 1)
    return PointAttribute(normals)