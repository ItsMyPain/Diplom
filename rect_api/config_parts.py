from pathlib import Path
from typing import Literal

import numpy as np

from .consts import *


def pprint(data):
    if isinstance(data, (list, tuple)):
        return ', '.join([str(i) for i in data])
    else:
        return str(data)


class Axe:
    size: int
    data: np.ndarray | None
    path: str | None

    def __init__(self, size: int, data: np.array = None):
        if len(data.shape) > 1:
            raise Exception(f"Неправильная размерность: {data.shape}")
        self.data = data
        self.size = size
        self.path = None

    def save(self, filename: str):
        if self.data is not None:
            self.path = filename
            self.data.astype('f').tofile(filename)


class Helper:
    commands: list[str]

    def __init__(self):
        self.commands = []

    def add_command(self, command: str):
        self.commands.append(command)

    def to_file(self, filename: str = PREPARE_FILE):
        with open(filename, 'w') as f:
            f.write('set -e\n')
            f.write('\n'.join(self.commands))
        print(PREPARE_ALL)


helper = Helper()


class Material:
    c1: float
    c2: float
    rho: float

    def __init__(self, c1: float, c2: float, rho: float):
        self.c1 = c1
        self.c2 = c2
        self.rho = rho

    def to_config(self) -> str:
        attrs = []
        for i in vars(self):
            attrs.append(f'{i} = {pprint(getattr(self, i))}')
        attrs = '\n        '.join(attrs)
        return f"""        [material]
            {attrs}
        [/material]"""


class Factory:
    name: str
    size: tuple[int, int, int]
    origin: tuple[float, float, float] | None
    spacing: tuple[float, float, float] | None
    path_x: str | None
    path_y: str | None
    path_z: str | None

    def __init__(self, name: str, x: Axe, y: Axe, z: Axe, origin: tuple[float, float, float] = None,
                 spacing: tuple[float, float, float] = None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name
        self.size = (x.size, y.size, z.size)
        if origin is not None:
            self.origin = origin
        if spacing is not None:
            self.spacing = spacing

    def to_config(self) -> str:
        attrs = []
        for i in vars(self):
            attrs.append(f'{i} = {pprint(getattr(self, i))}')
        attrs = '\n        '.join(attrs)
        return f"""        [factory]
            {attrs}
        [/factory]"""


class Schema:
    name: str

    def __init__(self, name: str):
        self.name = name

    def to_config(self) -> str:
        attrs = []
        for i in vars(self):
            attrs.append(f'{i} = {pprint(getattr(self, i))}')
        attrs = '\n        '.join(attrs)
        return f"""        [schema]
            {attrs}
        [/schema]"""


class Contact:
    name: str
    grid1: str
    grid2: str

    def __init__(self, name: str, grid1: str, grid2: str, interpolation_file: str = None, contact_file: str = None,
                 predictor_flag: bool = None, corrector_flag: bool = None, axis: int = None):
        """
        Класс контакта сеток.

        :param name: Название
        :param grid1:
        :param grid2:
        :param interpolation_file:
        :param contact_file:
        :param predictor_flag:
        :param corrector_flag:
        :param axis:
        """
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

    def to_config(self) -> str:
        attrs = []
        for i in vars(self):
            attrs.append(f'{i} = {pprint(getattr(self, i))}')
        attrs = '\n        '.join(attrs)
        return f"""    [contact]
        {attrs}
    [/contact]"""

    def __repr__(self):
        return str(vars(self))


class Impulse:
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


class Condition:
    name1: str
    name2: str
    nodes_file: str | None

    def __init__(self, name1: str, name2: str, nodes_file: str = None):
        self.name1 = name1
        self.name2 = name2
        self.nodes_file = nodes_file

    def from_contact(self, obj, contacts: list[Contact], direction: Literal['forward', 'backward'],
                     side: Literal['Z1', 'Z0'], directory=''):
        path = f"{BOUNDARY_DIR}/{directory}/{obj.filename}" if directory else f"{BOUNDARY_DIR}/{obj.filename}"
        Path(path).mkdir(parents=True, exist_ok=True)
        self.nodes_file = f"{path}/erased_nodes.txt"

        if side == 'Z1':
            z = (obj.data.z.size - 1, obj.data.z.size, obj.data.z.size + 1)
        else:
            z = (0, -1, -2)
        z = ' '.join(map(str, z))

        input_files = []
        for contact in contacts:
            if ((contact.grid1 == obj.filename and direction == 'backward') or (
                    contact.grid2 == obj.filename and direction == 'forward')) \
                    and hasattr(contact, 'interpolation_file'):
                input_files.append(contact.interpolation_file[1:-1])
        input_files = ' '.join(input_files)

        helper.add_command(f"python3 {BOUNDARY_CUTTER} {self.nodes_file} '{z}' '{input_files}'")

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


class Filler:
    name: str
    axis: int
    side: int

    def __init__(self, name: str, axis: int, side: int, condition: Condition | None = None):
        self.name = name
        self.axis = axis
        self.side = side
        self.condition = condition

    def to_config(self) -> str:
        if self.condition is not None:
            condition = '\n' + self.condition.to_config()
        else:
            condition = ''
        return f"""            [filler]
                name = {self.name}
                axis = {self.axis}
                side = {self.side}{condition}
            [/filler]"""


class Corrector:
    name: str
    axis: int
    side: int

    def __init__(self, name: str, axis: int, side: int, condition: Condition | None = None):
        self.name = name
        self.axis = axis
        self.side = side
        self.condition = condition

    def to_config(self) -> str:
        if self.condition is not None:
            condition = '\n' + self.condition.to_config()
        else:
            condition = ''
        return f"""            [corrector]
                name = {self.name}
                axis = {self.axis}
                side = {self.side}{condition}
            [/corrector]"""
