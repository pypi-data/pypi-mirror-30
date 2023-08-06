import json
import os
from pyrr import matrix44  # Matrix44
from demosys import resources


class GLTF2:
    """
    Represents a GLTF 2.0 file
    """
    def __init__(self, file_path):
        """
        Parse the json file and validate its contents.
        No actual data loading will happen.

        Supported formats:
        - gltf json format with external resources
        - gltf embedded buffers
        - glb Binary format
        """
        self.scenes = []
        self.nodes = []
        self.json = None
        self.file = file_path
        self.path = os.path.dirname(file_path)
        self.load()

    def load(self):
        print("Loading", self.file)

        # Load gltf json file
        if self.file.endswith('.gltf'):
            self.load_gltf()

        # Load binary gltf file
        if self.file.endswith('.glb'):
            self.load_glb()

        self.check_version()
        print(self.json)

        self.buffers_exist()
        self.images_exist()

    def process_gltf(self):
        """Go through gltf json and create objects"""
        pass

    def create_nodes(self):
        pass

    def load_gltf(self):
        """Loads a gltf json file"""
        with open(self.file) as fd:
            self.json = json.load(fd)

    def load_glb(self):
        """Loads a binary gltf file"""
        pass

    def load_images(self):
        for i in self.json['images']:
            test = resources.textures.get()
            print(test)

    def check_version(self):
        if not self.json['asset']['version'] == "2.0":
            msg = "Format version is not 2.0. Version states '{}' in file {}".format(
                self.json['asset']['version'],
                self.file
            )
            raise ValueError(msg)

    def buffers_exist(self):
        """Checks if the bin files referenced exist"""
        for e in self.json['buffers']:
            path = os.path.join(self.path, e['uri'])
            if not os.path.exists(path):
                raise FileNotFoundError("Buffer %s referenced in %s not found", path, self.file)

    def images_exist(self):
        """checks if the images references in textures exist"""
        pass


class GLTFScene:
    def __init__(self, root=None):
        self.root = root


class GLTFNode:
    """
    Nodes define the hierarchy of the scene
    """
    def __init__(self, name="", mesh=None, camera=None):
        self.name = name
        self.camera = camera
        self.mesh = mesh
        self.matrix = matrix44.create_identity()
        self.children = []


class GLTFMaterial:
    """Represents a gltf material"""
    pass


class GLTFSampler:
    """
    Describes the wrapping and scaling of a texture
    minFilter
    magFilter
    wrapS
    wrapT
    """
    pass


if __name__ == '__main__':
    gltf = GLTF2('/Users/einarforselv/Documents/projects/contraz/'
                 'glTF-Sample-Models/2.0/BoxTextured/glTF/BoxTextured.gltf')
