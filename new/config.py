from typing import Literal

from .consts import *

directions_boundary = Literal['X', 'X0', 'X1', 'Y', 'Y0', 'Y1', 'Z', 'Z0', 'Z1']
AXES = {'X': 0, 'Y': 1, 'Z': 2}


class BaseConfig:
    indent: int = 0

    @staticmethod
    def _print(data):
        if isinstance(data, (list, tuple)):
            return
        else:
            return str(data)

    def to_config(self) -> str:
        attrs = []
        for i, j in vars(self).items():
            if isinstance(j, (list, tuple)):
                if len(j) == 0:
                    continue
                if issubclass(j[0].__class__, BaseConfig):
                    for k in j:
                        txt = k.to_config()
                        if txt:
                            attrs.append(txt)
                else:
                    attrs.append(f"{'    ' * (self.indent + 1)}{i} = {', '.join([str(k) for k in j])}")
            else:
                if issubclass(j.__class__, BaseConfig):
                    txt = j.to_config()
                    if txt:
                        attrs.append(txt)
                elif isinstance(j, bool):
                    attrs.append(f"{'    ' * (self.indent + 1)}{i} = {str(j).lower()}")
                else:
                    attrs.append(f"{'    ' * (self.indent + 1)}{i} = {j}")
        attrs = '\n'.join(attrs)
        attrs = '\n' + attrs if attrs else ''
        return f"""{'    ' * self.indent}[{self.__class__.__name__.lower()}]{attrs}
{'    ' * self.indent}[/{self.__class__.__name__.lower()}]"""


class Node(BaseConfig):
    indent = 2
    name: str

    def __init__(self, name: str):
        self.name = name


class Material(BaseConfig):
    indent = 2
    c1: float
    c2: float
    rho: float

    def __init__(self, c1: float, c2: float, rho: float):
        self.c1 = c1
        self.c2 = c2
        self.rho = rho


class Material_Node(BaseConfig):
    indent = 2

    def __init__(self):
        pass


class Factory(BaseConfig):
    indent = 2
    name: str
    size: tuple[int, int, int]
    origin: tuple[float, float, float] | None
    spacing: tuple[float, float, float] | None
    path_x: str | None
    path_y: str | None
    path_z: str | None

    def __init__(self, name: str, size: tuple[int, int, int], origin: tuple[float, float, float] = None,
                 spacing: tuple[float, float, float] = None, path_x: str | None = None, path_y: str | None = None,
                 path_z: str | None = None):
        self.name = name
        self.size = size
        if origin is not None:
            self.origin = origin
        if spacing is not None:
            self.spacing = spacing
        if path_x is not None:
            self.path_x = path_x
        if path_y is not None:
            self.path_y = path_y
        if path_z is not None:
            self.path_z = path_z


class Schema(BaseConfig):
    indent = 2
    name: str

    def __init__(self, name: str):
        self.name = name


class Condition(BaseConfig):
    name1: str
    name2: str
    nodes_file: str

    def __init__(self, name1: str, name2: str, nodes_file: str):
        self.name1 = name1
        self.name2 = name2
        self.nodes_file = nodes_file

    def to_config(self) -> str:
        return f"""                [condition]
                    name = {self.name1}
                    [conditions]
                        [condition]
                            name = {self.name2}
                            nodes_file = {self.nodes_file}
                        [/condition]
                    [/conditions]
                [/condition]"""


class Filler(BaseConfig):
    indent = 3
    name: str
    axis: int
    side: int

    def __init__(self, name: str, axis: int, side: int, condition: Condition | None = None):
        self.name = name
        self.axis = axis
        self.side = side
        if condition is not None:
            self.condition = condition


class Fillers(BaseConfig):
    indent = 2
    fillers: list[Filler]

    def __init__(self, fillers: list[Filler] = None):
        if fillers is None:
            fillers = []
        self.fillers = fillers


class Corrector(BaseConfig):
    indent = 3
    name: str
    axis: int
    side: int

    def __init__(self, name: str, axis: int, side: int, condition: Condition | None = None):
        self.name = name
        self.axis = axis
        self.side = side
        if condition is not None:
            self.condition = condition


class Impulse(BaseConfig):
    indent = 3
    x: int
    y: int
    z: int
    filename: str

    def __init__(self, x, y, z, filename):
        self.x = x
        self.y = y
        self.z = z
        self.filename = filename

    def to_config(self) -> str:
        return f"""            [corrector]
                name = PointSourceCorrector{DIMS}D
                compression = 1.0
                gauss_w = 3
                index = {self.x}, {self.y}, {self.z}
                axis = 0
                [impulse]
                    name = FileInterpolationImpulse
                    [interpolator]
                        name = PiceWiceInterpolator1D
                        file = {self.filename}
                    [/interpolator]
                [/impulse]
            [/corrector]"""


class Correctors(BaseConfig):
    indent = 2
    correctors: list[Corrector | Impulse]

    def __init__(self, correctors: list[Corrector] = None):
        if correctors is None:
            correctors = []
        self.correctors = correctors


class Grid(BaseConfig):
    indent = 1
    id: str
    node: Node
    material_node: Material_Node
    material: Material
    factory: Factory
    schema: Schema
    fillers: Fillers
    correctors: Correctors

    def __init__(self, id: str, node: Node, material: Material, factory: Factory, schema: Schema,
                 fillers: Fillers = None, correctors: Correctors = None):
        self.id = id
        self.node = node
        self.material_node = Material_Node()
        self.material = material
        self.factory = factory
        self.schema = schema
        if fillers is None:
            fillers = Fillers()
        self.fillers = fillers
        if correctors is None:
            correctors = Correctors()
        self.correctors = correctors

    def add_impulse(self, filename: str, x: int | float = None, y: int | float = None, z: int | float = None):
        base = self.factory.size
        old = [x, y, z]
        new = []
        for i, j in zip(base, old):
            if j is None:
                new.append(int(i / 2))
            elif isinstance(j, float):
                new.append(int(j * i))
            else:
                new.append(j)

        for i in zip(base, new):
            if i[0] < i[1]:
                raise Exception(f"Неправильная размерность: {i}")
        self.correctors.correctors.append(Impulse(*new, filename))

    def add_filler(self, name: str, where: directions_boundary | list[directions_boundary],
                   condition: Condition | None = None):
        if isinstance(where, str):
            where = [where]
        for direction in where:
            if direction in AXES:
                self.fillers.fillers.append(Filler(name, AXES[direction], 0))
                self.fillers.fillers.append(Filler(name, AXES[direction], 1))
            else:
                self.fillers.fillers.append(Filler(name, AXES[direction[0]], int(direction[1]), condition))

    def add_corrector(self, name: str, where: directions_boundary | list[directions_boundary],
                      condition: Condition | None = None):
        if isinstance(where, str):
            where = [where]
        for direction in where:
            if direction in AXES:
                self.correctors.correctors.append(Corrector(name, AXES[direction], 0))
                self.correctors.correctors.append(Corrector(name, AXES[direction], 1))
            else:
                self.correctors.correctors.append(
                    Corrector(name, AXES[direction[0]], int(direction[1]), condition))


class IncludeGrids(BaseConfig):
    paths: list[str]

    def __init__(self, paths: list[str] = None):
        if paths is None:
            paths = []
        self.paths = paths

    def to_config(self) -> str:
        return '\n'.join([f'    @include("{path}", "grids")' for path in self.paths])


class Grids(BaseConfig):
    indent = 0
    include_grids: IncludeGrids
    grids: list[Grid]

    def __init__(self, grids: list[Grid] = None, include_grids: IncludeGrids = None):
        if include_grids is None:
            include_grids = IncludeGrids()
        self.include_grids = include_grids
        if grids is None:
            grids = []
        self.grids = grids


class Contact(BaseConfig):
    indent = 1
    name: str
    grid1: str
    grid2: str
    interpolation_file: str | None
    contact_file: str | None
    predictor_flag: bool | None
    corrector_flag: bool | None
    axis: int | None

    def __init__(self, name: str, grid1: str, grid2: str, interpolation_file: str = None, contact_file: str = None,
                 predictor_flag: bool = None, corrector_flag: bool = None, axis: int = None):
        self.name = name
        self.grid1 = grid1
        self.grid2 = grid2
        if interpolation_file is not None:
            self.interpolation_file = interpolation_file
        if contact_file is not None:
            self.contact_file = contact_file
        if predictor_flag is not None:
            self.predictor_flag = predictor_flag
        if corrector_flag is not None:
            self.corrector_flag = corrector_flag
        if axis is not None:
            self.axis = axis


class IncludeContacts(BaseConfig):
    paths: list[str]

    def __init__(self, paths: list[str] = None):
        if paths is None:
            paths = []
        self.paths = paths

    def to_config(self) -> str:
        return '\n'.join([f'    @include("{path}", "contacts")' for path in self.paths])


class Contacts(BaseConfig):
    indent = 0
    include_contacts: IncludeContacts
    contacts: list[Contact]

    def __init__(self, contacts: list[Contact] = None, include_contacts: IncludeContacts = None):
        if include_contacts is None:
            include_contacts = IncludeContacts()
        self.include_contacts = include_contacts
        if contacts is None:
            contacts = []
        self.contacts = contacts
