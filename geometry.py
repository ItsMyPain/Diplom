from pathlib import Path
from typing import Literal

import numpy as np

STDOUT = None  # subprocess.DEVNULL
STDERR = None  # subprocess.DEVNULL

BINS_DIR = 'bins'
CONFIGS_DIR = 'configs'
INTERP_CFG_DIR = 'interpolation_configs'
INTERP_DIR = 'interpolation'
CONTACT_CFG_DIR = 'contact_configs'
CONTACT_DIR = 'contact'
BOUNDARY_DIR = 'boundary'

DIMS = 3

BASE_CONF = f'template{DIMS}D.conf'
INTERP_CFG = f'template{DIMS}D.cfg'
CONTACT_CFG = f'template{DIMS}D.cfg'
MAIN_CONF = f'main_template{DIMS}D.conf'

RECT_DIR = 'rect_new'
BUILD_COMM = f'{RECT_DIR}/rect/build/rect'
PREPARE_FILE = 'prepare.sh'
PREPARE_ALL = f'bash ./{PREPARE_FILE}'

INTERP_COMM1 = f'direction=1 interpolation=barycentric {RECT_DIR}/rect/build/interpolation'
INTERP_COMM2 = f'direction=2 interpolation=barycentric {RECT_DIR}/rect/build/interpolation'
CONTACT_COMM = f'{RECT_DIR}/rect/build/contact_finder'

BOUNDARY_CUTTER = 'boundary_cutter.py'

AXES = {'X': 0, 'Y': 1, 'Z': 2}

RectGridInterpolationCorrector = 'RectGridInterpolationCorrector'
GlueRectElasticContact = f'GlueRectElasticContact{DIMS}D'
RectNoReflectFiller = 'RectNoReflectFiller'


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


class NewContact:
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
            attrs.append(f'{i} = {getattr(self, i)}')
        attrs = '\n        '.join(attrs)
        return f"""    [contact]
        {attrs}
    [/contact]"""


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

    def from_contact(self, obj, contacts: list[NewContact], direction: Literal['forward', 'backward'],
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
            if hasattr(contact, 'interpolation_file'):
                if direction == 'forward':
                    input_files.append(contact.interpolation_file[1:-1])
                else:
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

    def configure(self, directory='', reconfigure=False):
        if not reconfigure:
            self.save(f"{directory}/{self.filename}" if directory else self.filename)

        args = [
            self.filename,
            self.x.size, self.y.size, self.z.size,
            self.x.path, self.y.path, self.z.path,
            '\n'.join([i.to_config() for i in self.fillers])
        ]

        correctors = [i.to_config() for i in self.correctors]

        if self.impulse is not None:
            correctors.append(self.impulse.to_config())

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

    def reconfigure(self, directory=''):
        if not self.configured:
            raise Exception("Геометрия не сконфигурирована")
        self.configure(directory=directory)

    def sew(self, obj: 'Geometry', ghost_from: str, ghost_to: str, ghosts: tuple[int, int],
            directory='') -> list[NewContact]:
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
        # print(comm1)
        # proc = subprocess.run(comm1, shell=True, stdout=STDOUT, stderr=STDERR, check=True)
        helper.add_command(comm1)

        comm2 = f"{INTERP_COMM2} {config_filename}"
        # print(comm2)
        # proc = subprocess.run(comm2, shell=True, stdout=STDOUT, stderr=STDERR, check=True)
        helper.add_command(comm2)

        # return Contact(self, obj, output1, output2)

        return [NewContact(RectGridInterpolationCorrector, self.filename, obj.filename, interpolation_file=output1,
                           predictor_flag=True, corrector_flag=False, axis=1),
                NewContact(RectGridInterpolationCorrector, obj.filename, self.filename, interpolation_file=output2,
                           predictor_flag=False, corrector_flag=True, axis=1)]

    def contact(self, obj: 'Geometry', directory=''):
        if not isinstance(obj, Geometry):
            raise Exception("Неверный тип данных")
        if not self.configured or not obj.configured:
            raise Exception("Геометрия не сконфигурирована")
        direct = f"{directory}/" if directory else ""
        output = f'"{CONTACT_DIR}/{direct}{self.filename}_{obj.filename}.txt"'

        with open(f'{CONTACT_CFG_DIR}/{CONTACT_CFG}') as f:
            config = f.read()

        config = config.format(self.filename, obj.filename, output,
                               self.x.size, self.y.size, self.z.size,
                               self.x.path, self.y.path, self.z.path,
                               obj.x.size, obj.y.size, obj.z.size,
                               obj.x.path, obj.y.path, obj.z.path)

        path = f"{CONTACT_CFG_DIR}/{directory}" if directory else CONTACT_CFG_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        config_filename = f"{path}/{self.filename}_{obj.filename}.cfg"

        with open(config_filename, 'w') as f:
            f.write(config)

        out_path = f"{CONTACT_DIR}/{directory}" if directory else CONTACT_DIR
        Path(out_path).mkdir(parents=True, exist_ok=True)

        comm = f"{CONTACT_COMM} {config_filename}"
        helper.add_command(comm)

        return NewContact(GlueRectElasticContact, self.filename, obj.filename, contact_file=output)
