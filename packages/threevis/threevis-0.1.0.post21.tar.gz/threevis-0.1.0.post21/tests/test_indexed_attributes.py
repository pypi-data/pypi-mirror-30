import unittest
import threevis
import numpy as np

class IndexedAttributes(unittest.TestCase):
    
    quad_verts = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    quad_faces_tri = np.array([[0, 1, 2], [0, 2, 3]])

    def test_point_attribute_tri(self):
        attrib = threevis.PointAttribute(['a', 'b', 'c', 'd'])
        resolved_attrib = threevis.resolve_attributes(self.quad_faces_tri, [attrib])[0]
        self.assertEqual(len(resolved_attrib), 6)
        np.testing.assert_array_equal(resolved_attrib, ['a', 'b', 'c', 'a', 'c', 'd'])

    def test_face_attribute_tri(self):
        attrib = threevis.FaceAttribute(['a', 'b'])
        resolved_attrib = threevis.resolve_attributes(self.quad_faces_tri, [attrib])[0]
        self.assertEqual(len(resolved_attrib), 6)
        np.testing.assert_array_equal(resolved_attrib, ['a', 'a', 'a', 'b', 'b', 'b'])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(IndexedAttributes)
    unittest.TextTestRunner(verbosity=2).run(suite)
