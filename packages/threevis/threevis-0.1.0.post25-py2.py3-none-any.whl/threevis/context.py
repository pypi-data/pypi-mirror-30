import pythreejs as three
import numpy as np
from ipywidgets import HTML, Text
from traitlets import link, dlink, Bool
from IPython.display import display
from .indexed_attribute import *
from .mesh_helper import calculate_face_normals, calculate_point_normals
from .mesh import *
import math

class Context(object):
    """
    The Context represents everything that's drawn in one output window. 
    The output of any draw* call gets added to the window. This allows you to draw multiple models in one output window.
    """

    def __init__(self, width=600, height=400, background_color = '#dddddd'):    
        """
        Initialize a new Context.
        """

        self.camera = three.PerspectiveCamera(position=[1,1,1], fov=20,
                children=[three.DirectionalLight(color='#ffffff', position=[-30, 50, 10], intensity=1.0)])

        self.camera.aspect = width/float(height)

        self.minCorner = np.array([ 100000.0,  100000.0,  100000.0])
        self.maxCorner = np.array([-100000.0, -100000.0, -100000.0])

        self.scene = three.Scene(children=[three.AmbientLight(color='#aaaaaa'), self.camera])
        self.scene.background = background_color

        self.orbit_controls = three.OrbitControls(controlling=self.camera)
        self.click_picker = three.Picker(controlling=self.scene, root=self.scene, event='dblclick')

        self.renderer = three.Renderer(camera=self.camera,  background=background_color, background_opacity=1,
                                       scene=self.scene, controls=[self.orbit_controls, self.click_picker],
                                       width=width, height=height, antialias=True, localClippingEnabled=True )

        def on_picked(change):
            self.orbit_controls.target = change['new']

        self.click_picker.observe(on_picked, names=['point'])

        self.bounds_enabled = False

    def draw(self, obj, shading='flat', z_offset=0.5, texture=None, point_size = 1, perspective = False, line_width = 1, clipping_planes = []):
        """
        Draw the given object. Not all named parameters are relevant for all object types.
        """

        obj.prepare_render()

        if isinstance(obj, Mesh):
            return self.draw_faces(obj.vertices, obj.tri_face_indices, obj.normals, obj.colors, obj.uvs, shading, z_offset, texture, clipping_planes)
        elif isinstance(obj, EdgeList):
            return self.draw_edges(obj.vertices, obj.edge_indices, obj.colors, obj.uvs, z_offset, texture, line_width, clipping_planes)
        elif isinstance(obj, PointList):
            return self.draw_vertices(obj.vertices, obj.colors, obj.uvs, point_size, z_offset, texture, perspective, clipping_planes)

        return self
            


    def draw_faces(self, vertices, face_indices, normals=None, colors=None, uvs=None,
                   shading='flat', z_offset=0.5, texture=None, clipping_planes = []):
        """
        Draw a triangle mesh described by a list of vertex positions and face indices.
        face_indices is expected to be a n x 3 matrix.
        """

        assert(len(face_indices) > 0 and len(vertices) > 0)


        vertices = np.array(vertices)
        face_indices = np.array(face_indices)

        mat = None
        # Setup Material
        if shading == 'flat' or shading == 'hidden' or shading == 'wireframe':
            mat = three.MeshLambertMaterial(color='#dddddd', colorWrite=shading is not 'hidden')
        elif shading == 'phong':
            mat = three.MeshPhongMaterial(color='#dddddd')
        elif shading == 'none':
            mat = three.MeshBasicMaterial(color='#FFFFFF')

        if len(clipping_planes) != 0:
            mat.clipShadows = True
            mat.clippingPlanes = tuple(clipping_planes)

        mat.wireframe = shading is 'wireframe'
        mat.map = texture

        if z_offset is not 0:
            mat.polygonOffset = True
            mat.polygonOffsetFactor = z_offset
            mat.polygonOffsetUnits = 0.1

        if normals is 'vertex':
            normals = calculate_point_normals(vertices, face_indices)
        elif normals is 'face':
            normals = calculate_face_normals(vertices, face_indices)

        # Resolve the given attributes, it's ok if they are None
        resolved_attribs = resolve_attributes(face_indices, [normals, colors, uvs])
        resolved_normals    = resolved_attribs[0]
        resolved_colors     = resolved_attribs[1]
        resolved_uvs        = resolved_attribs[2]

        # De-index our vertices
        vertices, face_indices = stretch_vertices(vertices, face_indices)

        # Create attributes dictionary, always use at least position and index
        attributes=dict(
            position = three.BufferAttribute(np.asarray(vertices, dtype=np.float32), normalized=False),
            index =    three.BufferAttribute(np.asarray(face_indices, dtype=np.uint32).ravel(), normalized=False),
        )

        if resolved_colors is not None:
            mat.vertexColors = 'VertexColors'
            mat.color = 'white'
            attributes['color'] = three.BufferAttribute(np.asarray(resolved_colors, dtype=np.float32))

        if resolved_normals is not None:
            attributes['normal'] = three.BufferAttribute(np.asarray(resolved_normals, dtype=np.float32))

        if resolved_uvs is not None:
            attributes['uv'] = three.BufferAttribute(np.asarray(resolved_uvs, dtype=np.float32))

        mesh_geom = three.BufferGeometry(attributes=attributes)

        mesh_obj = three.Mesh(geometry=mesh_geom, material=mat)
        self.minCorner = np.minimum(self.minCorner, vertices.min(axis=0))
        self.maxCorner = np.maximum(self.maxCorner, vertices.max(axis=0))

        self.scene.add(mesh_obj)
        return self

    def draw_edges(self, vertices, edge_indices=None, colors=None, uvs=None, z_offset=0, texture=None, line_width=1, clipping_planes = []):
        """
        Draw a list of edges described by a list of vertex positions and edge indices.
        edge_indices is expected to be a n x 2 matrix. If no indices are given, a continous line is connecting the vertices is drawn.
        """

        mat = three.LineBasicMaterial(color='#000000')
        mat.linewidth = line_width
        mat.map = texture

        if len(clipping_planes) != 0:
            mat.clipShadows = True
            mat.clippingPlanes = clipping_planes

        if z_offset is not 0:
            mat.polygonOffset = True
            mat.polygonOffsetFactor = z_offset
            mat.polygonOffsetUnits = 0.1

        if edge_indices is None:
            edge_indices = list(zip(np.arange(0, len(vertices)-1),
                                    np.arange(1, len(vertices))))

        assert(len(edge_indices) > 0 and len(vertices) > 0)

        vertices = np.array(vertices)
        edge_indices = np.array(edge_indices)

        resolved_attribs = resolve_attributes(edge_indices, [colors, uvs])
        resolved_colors = resolved_attribs[0]
        resolved_uvs    = resolved_attribs[1]

        vertices, edge_indices = stretch_vertices(vertices, edge_indices)

        attributes=dict(
            position = three.BufferAttribute(np.asarray(vertices, dtype=np.float32), normalized=False),
            index =    three.BufferAttribute(np.asarray(edge_indices, dtype=np.uint32).ravel(), normalized=False),
        )

        if resolved_colors is not None:
            mat.vertexColors = 'VertexColors'
            mat.color = 'white'
            attributes['color'] = three.BufferAttribute(np.asarray(resolved_colors, dtype=np.float32))

        if resolved_uvs is not None:
            attributes['uv'] = three.BufferAttribute(np.asarray(resolved_uvs, dtype=np.float32))

        geom = three.BufferGeometry(attributes = attributes)

        mesh_obj = three.LineSegments(geometry=geom, material=mat)

        self.minCorner = np.minimum(self.minCorner, vertices.min(axis=0))
        self.maxCorner = np.maximum(self.maxCorner, vertices.max(axis=0))

        self.scene.add(mesh_obj)
        return self

    def draw_vertices(self, vertices, colors=None, uvs=None, point_size=1, z_offset=0, texture=None, perspective=False, clipping_planes = []):
        """
        Draw a list of unconnected vertices.
        """

        vertices = np.array(vertices)
        matColor = colors

        if colors is None:
            matColor = 'black'
        elif isinstance(colors, PointAttribute):
            colors = colors.values
            matColor = '#ffffff'
        elif hasattr(colors, '__len__') and (not isinstance(colors, str)):
            matColor = '#ffffff'
        else:
            colors = None



        attributes = dict(
            position = three.BufferAttribute(np.asarray(vertices, dtype=np.float32), normalized=False),
        )

        mat = three.PointsMaterial(color=matColor, sizeAttenuation=perspective, size=point_size)
        mat.map = texture

        if len(clipping_planes) != 0:
            mat.clipShadows = True
            mat.clippingPlanes = clipping_planes

        if z_offset is not 0:
            mat.polygonOffset = True
            mat.polygonOffsetFactor = z_offset
            mat.polygonOffsetUnits = 0.1

        if colors is not None:
            attributes['color'] = three.BufferAttribute(np.asarray(colors, dtype=np.float32))
            mat.vertexColors = 'VertexColors'
        
        if uvs is not None:
            attributes['uv'] = three.BufferAttribute(np.asarray(uvs, dtype=np.float32))

        geom = three.BufferGeometry(attributes=attributes)
        mesh_obj = three.Points(geometry=geom, material=mat)

        self.minCorner = np.minimum(self.minCorner, vertices.min(axis=0))
        self.maxCorner = np.maximum(self.maxCorner, vertices.max(axis=0))

        self.scene.add(mesh_obj)
        return self

    def set_camera_position(self, position):
        self.camera.position = tuple(position)

    def get_camera_position(self):
        return self.camera.position

    def set_camera_rotation(self, rotation):
        self.camera.rotation = ( math.radians(rotation[0]), math.radians(rotation[1]), math.radians(rotation[2]), 'XYZ')

    def get_camera_rotation(self):
        return math.degrees(self.camera.rotation[0]), math.degrees(self.camera.rotation[1]), math.degrees(self.camera.rotation[2])

    def set_camera(self, transform):
        self.set_camera_position(transform[0])
        self.set_camera_rotation(transform[1])
    
    def get_camera(self):
        return self.get_camera_position(), self.get_camera_rotation()

    def show_bounds(self):
        self.bounds_enabled = True
        return self
    
    def hide_bounds(self):
        self.bounds_enabled = False
        return self

    def set_bounds(self, val):
        self.bounds_enabled = val
        return self
        
    def draw_text(self, text, position=(0, 0, 0), color='white', size=100, height=1):
        """
        Draw a text object at the specified location with a given height
        """
        height *= len(text)
        sm = three.SpriteMaterial(map=three.TextTexture(string=text, color=color, size=size, squareTexture=True))
        sprite = three.Sprite(material=sm, position=tuple(position), scaleToTexture=True, scale=[height, height, 1])
        self.scene.add(sprite)

    def display(self):
        """
        Display a window containing all the previous draw calls.
        """

        center = (self.minCorner + self.maxCorner) * 0.5
        distance = max(np.linalg.norm(center-self.minCorner), np.linalg.norm(center-self.maxCorner))
        self.camera.position = tuple( np.array(self.camera.position) * distance * 5)
        self.orbit_controls.target = tuple(center)

        

        if self.bounds_enabled:
            extends = self.maxCorner - self.minCorner
            boxEdges = [self.minCorner, 
                        self.minCorner + [extends[0], 0, 0], 
                        self.minCorner + [0, extends[1], 0],
                        self.minCorner + [0, 0, extends[2]]]

            self.draw_edges(boxEdges, [[0, 1], [0, 2], [0, 3]], FaceAttribute([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
            self.draw_text(str([round(v,3) for v in self.minCorner]), self.minCorner - [0, extends[1]*0.1, 0], color = 'black', height=extends[1]/25)
            
            self.draw_text(str(round(extends[0], 3)), (boxEdges[0] * 0.25 + boxEdges[1] * 0.75), color = 'black', height=extends[1]/20)
            self.draw_text(str(round(extends[1], 3)), (boxEdges[0] * 0.25 + boxEdges[2] * 0.75), color = 'black', height=extends[1]/20)
            self.draw_text(str(round(extends[2], 3)), (boxEdges[0] * 0.25 + boxEdges[3] * 0.75), color = 'black', height=extends[1]/20)

        self.orbit_controls.enabled = False

        # Manually calling update on the controls to make sure they are all set up
        self.orbit_controls.exec_three_obj_method("update")

        display(self.renderer)
