import re
import subprocess
from pathlib import Path

import numpy as np

STDOUT = subprocess.DEVNULL
STDERR = subprocess.DEVNULL

BINS_DIR = 'bins'
CONFIGS_DIR = 'configs'
INTERP_CFG_DIR = 'interpolation_configs'
INTERP_DIR = 'interpolation'
BOUNDARY_DIR = 'boundary'

DIMS = 3

BASE_CONF = f'template{DIMS}D.conf'
INTERP_CFG = f'template{DIMS}D.cfg'
MAIN_CONF = f'main_template{DIMS}D.conf'

INTERP_COMM1 = 'direction=1 interpolation=barycentric rect/rect/build/interpolation'
INTERP_COMM2 = 'direction=2 interpolation=barycentric rect/rect/build/interpolation'
BUILD_COMM = 'rect_new/rect/build/rect'

AXES = {'X': 0, 'Y': 1, 'Z': 2}


class Axe:
    data: np.array
    size: int
    path: str | None

    def __init__(self, data: np.array, size: int):
        if len(data.shape) > 1:
            raise Exception(f"Неправильная размерность: {data.shape}")
        self.data = data
        self.size = size
        self.path = None

    def save(self, filename: str):
        self.path = filename
        self.data.astype('f').tofile(filename)


class Contact:
    first_geom: 'Geometry'
    second_geom: 'Geometry'
    forward_output: str
    backward_output: str

    def __init__(self, first_geom: 'Geometry', second_geom: 'Geometry', forward_output: str, backward_output: str):
        self.first_geom = first_geom
        self.second_geom = second_geom
        self.forward_output = forward_output
        self.backward_output = backward_output

    def to_config(self) -> str:
        return f"""    [contact]
        name = RectGridInterpolationCorrector
        interpolation_file = {self.forward_output}
        grid1 = {self.first_geom.filename}
        grid2 = {self.second_geom.filename}
        predictor_flag = true
        corrector_flag = false
        axis = 1
    [/contact]
    [contact]
        name = RectGridInterpolationCorrector
        interpolation_file = {self.backward_output}
        grid1 = {self.second_geom.filename}
        grid2 = {self.first_geom.filename}
        predictor_flag = false
        corrector_flag = true
        axis = 1
    [/contact]"""


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


class Condition:
    name1: str
    name2: str
    nodes_file: str | None

    def __init__(self, name1: str, name2: str, nodes_file: str = None):
        self.name1 = name1
        self.name2 = name2
        self.nodes_file = nodes_file

    def from_contact(self, contact: Contact, z=(0, -1, -2), directory=''):
        path = f"{BOUNDARY_DIR}/{directory}/{contact.first_geom.filename}" if directory else f"{BOUNDARY_DIR}/{contact.first_geom.filename}"
        Path(path).mkdir(parents=True, exist_ok=True)
        self.nodes_file = f"{path}/erased_nodes.txt"
        with open(contact.forward_output[1:-1], 'r') as input_f:
            with open(self.nodes_file, 'w') as output_f:
                input_f.readline()
                input_f.readline()
                n = int(input_f.readline()) // 2
                output_f.write(f'{len(z) * n}\n')
                for i in range(n):
                    x, y = map(int, input_f.readline().split()[:2])
                    for z_i in z:
                        output_f.write(f'{x} {y} {z_i}\n')

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


class Geometry:
    x: Axe
    y: Axe
    z: Axe
    filename: str
    path: str | None
    configured: bool
    impulse: None | Impulse
    fillers: list[Filler]
    correctors: list[Corrector]
    sewed: set[tuple[int, int]]

    def __init__(self, x: Axe, y: Axe, z: Axe, filename: str, impulse=None, fillers=None, correctors=None):
        if x.data.shape != y.data.shape or z.data.shape != y.data.shape:
            raise Exception("Не согласующиеся длины")
        self.x = x
        self.y = y
        self.z = z
        self.filename = filename
        self.path = None
        self.configured = False
        self.impulse = impulse
        self.sewed = set()
        if fillers is None:
            fillers = []
        if correctors is None:
            correctors = []
        self.fillers = fillers
        self.correctors = correctors

    def add_impulse(self, filename: str, x: int | float = None, y: int | float = None, z: int | float = None):
        base = (self.x.size, self.y.size, self.z.size)
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
        self.impulse = Impulse(*new, filename)

    def add_property(self, cls, name: str, where: str | list[str], condition: Condition | None = None):
        if isinstance(where, str):
            where = [where]
        if cls is Filler:
            data = self.fillers
        else:
            data = self.correctors
        for i in where:
            if i in AXES:
                data.append(cls(name, AXES[i], 0, condition))
                data.append(cls(name, AXES[i], 1, condition))
            else:
                data.append(cls(name, AXES[i[0]], int(i[1]), condition))

    def save(self, directory=''):
        path = f'{BINS_DIR}/{directory}'
        Path(path).mkdir(parents=True, exist_ok=True)
        self.x.save(f'{path}/{self.filename}_x.bin')
        self.y.save(f'{path}/{self.filename}_y.bin')
        self.z.save(f'{path}/{self.filename}_z.bin')

    def configure(self, directory=''):
        self.save(f"{directory}/{self.filename}" if directory else self.filename)

        args = [
            self.filename,
            self.x.size, self.y.size, self.z.size,
            self.x.path, self.y.path, self.z.path,
            '\n'.join([i.to_config() for i in self.fillers])
        ]

        correctors = [i.to_config() for i in self.correctors]

        if self.impulse is not None:
            correctors.append(f"""            [corrector]
                name = PointSourceCorrector{DIMS}D
                compression = 1.0
                gauss_w = 3
                index = {self.impulse.x}, {self.impulse.y}, {self.impulse.z}
                axis = 0
                [impulse]
                    name = FileInterpolationImpulse
                    [interpolator]
                        name = PiceWiceInterpolator1D
                        file = {self.impulse.filename}
                    [/interpolator]
                [/impulse]
            [/corrector]""")

        args.append('\n'.join(correctors))

        with open(f'{CONFIGS_DIR}/{BASE_CONF}') as f:
            config = f.read()

        config = config.format(*args)

        path = f"{CONFIGS_DIR}/{directory}" if directory else CONFIGS_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        self.path = f"{path}/{self.filename}.conf"

        with open(self.path, 'w') as f:
            f.write(config)

        self.configured = True

    def sew(self, obj: 'Geometry', ghost_from: str, ghost_to: str, ghosts: tuple[int, int],
            directory='') -> Contact:
        if not isinstance(obj, Geometry):
            raise Exception("Неверный тип данных")
        if not self.configured or not obj.configured:
            raise Exception("Геометрия не сконфигурирована")

        direct = f"{directory}/" if directory else ""
        main_config = f'"{self.path}"'
        obj_config = f'"{obj.path}"'
        output1 = f'"{INTERP_DIR}/{direct}forward_{self.filename}_{obj.filename}.txt"'
        output2 = f'"{INTERP_DIR}/{direct}backward_{self.filename}_{obj.filename}.txt"'

        with open(f'{INTERP_CFG_DIR}/{INTERP_CFG}') as f:
            config = f.read()

        config = config.format(self.filename, obj.filename, main_config, obj_config,
                               output1, output2, ghost_to, ghost_from, ghosts[0], ghosts[1])

        path = f"{INTERP_CFG_DIR}/{directory}" if directory else CONFIGS_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        config_filename = f"{path}/{self.filename}_{obj.filename}.cfg"

        with open(config_filename, 'w') as f:
            f.write(config)

        out_path = f"{INTERP_DIR}/{directory}" if directory else INTERP_DIR
        Path(out_path).mkdir(parents=True, exist_ok=True)

        comm1 = f"{INTERP_COMM1} {config_filename}"
        print(comm1)
        proc = subprocess.run(comm1, shell=True, stdout=STDOUT, stderr=STDERR)
        if proc.returncode != 0:
            raise Exception(comm1)

        comm2 = f"{INTERP_COMM2} {config_filename}"
        print(comm2)
        proc = subprocess.run(comm2, shell=True, stdout=STDOUT, stderr=STDERR)
        if proc.returncode != 0:
            raise Exception(comm2)

        # self.sewed.add((AXES[ghost_from[0]], int(ghost_from[-1])))
        # obj.sewed.add((AXES[ghost_to[0]], int(ghost_to[-1])))

        return Contact(self, obj, output1, output2)

    def update_config(self):
        with open(self.path) as f:
            config = f.read()

        connectors = {(i, j) for i in range(DIMS) for j in range(2)} - self.sewed
        fillers = '\n'.join([f"""            [filler]
                name = RectNoReflectFiller
                axis = {i}
                side = {j}
            [/filler]""" for i, j in connectors])

        config = re.sub(r"\[fillers].*\[/fillers]",
                        f"[fillers]\n{fillers}\n        [/fillers]",
                        config,
                        flags=re.DOTALL)

        correctors = [f"""            [corrector]
                name = ForceRectElasticBoundary{DIMS}D
                axis = {i}
                side = {j}
           [/corrector]""" for i, j in connectors]

        if self.impulse is not None:
            correctors.append(f"""            [corrector]
                name = PointSourceCorrector{DIMS}D
                compression = 1.0
                gauss_w = 3
                index = {self.impulse.x}, {self.impulse.y}, {self.impulse.z}
                axis = 0
                [impulse]
                    name = FileInterpolationImpulse
                    [interpolator]
                        name = PiceWiceInterpolator1D
                        file = {self.impulse.filename}
                    [/interpolator]
                [/impulse]
            [/corrector]""")

        correctors = '\n'.join(correctors)

        config = re.sub(r"\[correctors].*\[/correctors]",
                        f"[correctors]\n{correctors}\n        [/correctors]",
                        config,
                        flags=re.DOTALL)

        with open(self.path, 'w') as f:
            f.write(config)
