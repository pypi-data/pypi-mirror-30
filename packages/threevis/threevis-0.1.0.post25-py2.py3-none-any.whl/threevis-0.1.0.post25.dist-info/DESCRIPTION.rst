![](https://www.graphics.rwth-aachen.de:9000/threevis/threevis/raw/master/docs/images/logo-90.png)

# threevis

[![](https://www.graphics.rwth-aachen.de:9000/threevis/threevis/badges/master/pipeline.svg)](https://www.graphics.rwth-aachen.de:9000/threevis/threevis/commits/master)

A Python library for visualizing meshes, point clouds, and other geometry in Jupyter notebooks

## Installation
`pip install threevis`

## Examples

### Quick Mesh Inspection

```python
import threevis
import openmesh as om

m = om.read_trimesh('examples/models/bunny.obj')

threevis.display_openmesh(m)
```

### Custom Rendering

```python
import threevis
import openmesh as om
import numpy as np

# Load Mesh
m = om.read_trimesh('mouse.obj')

# Create Context
ctx = threevis.Context(width=640, height=480)

# Get vertices and faces from the mesh
vertices = m.points()
faces = m.face_vertex_indices()

# We don't have normals, calculate them
normals = threevis.calculateFaceNormals(m.points(), m.face_vertex_indices())

# Choose a random color for each face
colors = threevis.FaceAttribute(np.random.rand(len(faces), 3))

# Draw the mesh with flat shading
ctx.draw_faces(vertices, faces, 
               normals = normals,
               colors = colors,
               shading = 'flat')

# Draw edges on top with random colors
ctx.draw_edges(vertices, m.ev_indices(), 
               colors = threevis.FaceAttribute(np.random.rand(len(m.ev_indices()), 3)),
               linewidth=3)

# Calculate data to display normals as edges
normal_vis_verts, normal_vis_edges = threevis.calculateNormalEdges(vertices, faces, normals, length=0.05)

# Draw the normals in
ctx.draw_edges(normal_vis_verts, normal_vis_edges, colors = colors)

# Draw a point for each vertex
ctx.draw_vertices(vertices, point_size=4, colors='red')

# Finally display it
ctx.display()
```

![](https://www.graphics.rwth-aachen.de:9000/threevis/threevis/raw/master/docs/images/mouse.PNG)

## Development Setup

- Install dependencies
- Clone the repository
- `pip install -e .`

## Dependencies

- [pythreejs](https://github.com/jovyan/pythreejs/) >= 1.0.0

### Optional
- [openmesh-python](https://graphics.rwth-aachen.de:9000/adielen/openmesh-python) latest



