import numpy as np

from topos.core.mesh import Mesh
from .widgets import ModelWidget


class PMesh(Mesh):
    """A Preview Mesh object

    This extends the core Mesh object by managing an instance of the
    ModelWidget to allow for in notebook previews of the Mesh's geometry
    """

    def __init__(self, verts=None, faces=None, name=None):
        super().__init__(verts, faces, name)

        self.widget = ModelWidget()
        self.widget.vertices = self.wverts
        self.widget.faces = self.wfaces

    @classmethod
    def frommesh(cls, mesh):
        """Create a PMesh from an existing mesh."""

        verts = mesh.vertices
        faces = mesh.faces
        name = mesh.name

        return cls(verts, faces, name)

    @property
    def wverts(self):
        """Return vertices formatted in a way compatible with the widget."""

        if self._verts is not None:
            verts = self.vertices.cartesian
            return [list(v) for v in verts]

        return []

    @property
    def wfaces(self):
        """Return faces formatted in a way compatible with the widget."""

        # Annoyingly three.js no longer support quads...
        # so we have to triangulate each face...
        # We represent each face as follows
        #
        # 4 -------- 3
        # |          |
        # |          |
        # |          |
        # |          |   face = [ 1, 2, 3, 4 ]
        # 1 -------- 2
        #
        # So for each face we will have to emit 2 triangles
        #
        # 4 -------- 3
        # | ⋱        |     ⋱ = U+22F1
        # |   ⋱      |
        # |     ⋱    |      lower = [1, 2, 4]
        # |       ⋱  |      upper = [4, 2, 3]
        # 1 -------- 2
        faces = []

        if self._faces is not None:
            fs = self.faces.data

            # We have to renumber the faces, this is due to threejs
            # starts numbering vertices at 0, whereas blender starts
            # at 1 :/
            #
            # We create a new array so that we don't mess with the one
            # we use internally
            FS = np.array(fs)
            FS = FS - 1

            for f in FS:

                # Lower triangle
                faces.append([f[0], f[1], f[3]])

                # Upper triangle
                faces.append([f[3], f[1], f[2]])

        return faces

    def show(self):
        return self.widget