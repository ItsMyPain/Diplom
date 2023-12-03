from base import String, Structure, List, Page


class Node(String):
    name: str

    def __init__(self, name=""):
        self.name = name


class MaterialNode(String):
    pass


class Material(String):
    c1: float
    c2: float
    rho: float

    def __init__(self, c1=0.0, c2=0.0, rho=0.0):
        self.c1 = c1
        self.c2 = c2
        self.rho = rho


class Factory(String):
    name: str
    size: str
    path_x: str
    path_y: str
    path_z: str

    def __init__(self, name="", size=(0, 0, 0), path_x="", path_y="", path_z=""):
        self.name = name
        self.size = "{}, {}, {}".format(*size)
        self.path_x = path_x
        self.path_y = path_y
        self.path_z = path_z


class Schema(String):
    name: str

    def __init__(self, name=""):
        self.name = name


class Filler(String):
    name: str
    axis: int
    side: int

    def __init__(self, name="", axis=0, side=0):
        self.name = name
        self.axis = axis
        self.side = side


class Corrector(String):
    name: str
    axis: int
    side: int

    def __init__(self, name="", axis=0, side=0):
        self.name = name
        self.axis = axis
        self.side = side


class Fillers(List):
    data: list[Filler]

    def __init__(self, data: list[Filler] = None):
        self.data = data or []


class Correctors(List):
    data: list[Corrector]

    def __init__(self, data: list[Corrector] = None):
        self.data = data or []


class Grid(Structure):
    id: str
    node: Node
    material_node: MaterialNode
    material: Material
    factory: Factory
    schema: Schema
    fillers: Fillers
    correctors: Correctors

    def __init__(self, id="", node: Node = None, material_node: MaterialNode = None, material: Material = None,
                 factory: Factory = None, schema: Schema = None, fillers: Fillers = None,
                 correctors: Correctors = None):
        self.id = id
        self.node = node or Node()
        self.material_node = material_node or MaterialNode()
        self.material = material or Material()
        self.factory = factory or Factory()
        self.schema = schema or Schema()
        self.fillers = fillers or Fillers()
        self.correctors = correctors or Correctors()


class Contact(Structure):
    pass


class Initial(Structure):
    pass


class Saver(Structure):
    pass


class Grids(List):
    data: list[Grid]

    def __init__(self, data: list[Grid] = None):
        self.data = data or []


class Contacts(List):
    data: list[Contact]

    def __init__(self, data: list[Contact] = None):
        self.data = data or []


class Initials(List):
    data: list[Initial]

    def __init__(self, data: list[Initial] = None):
        self.data = data or []


class Savers(List):
    data: list[Saver]

    def __init__(self, data: list[Saver] = None):
        self.data = data or []


class Config(Page):
    verbose: bool
    dt: float
    steps: int
    grids: Grids
    contacts: Contacts
    initials: Initials
    savers: Savers

    def __init__(self, dt=0.0, steps=0, grids: Grids = None, contacts: Contacts = None, initials: Initials = None,
                 savers: Savers = None, verbose=True):
        self.verbose = verbose
        self.dt = dt
        self.steps = steps
        self.grids = grids or Grids()
        self.contacts = contacts or Contacts()
        self.initials = initials or Initials()
        self.savers = savers or Savers()

    def to_file(self, path):
        with open(path, "w") as f:
            f.write(self.print())

    def from_file(self, path):
        with open(path, "r") as f:
            self.load(f.read())


if __name__ == '__main__':
    a = Config()
    a.from_file("test.conf")
    print(a.print())
