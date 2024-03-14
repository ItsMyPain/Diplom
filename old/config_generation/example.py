from objects import *

DT = 0.01
STEPS = 1


class GeomConfig(Config):
    def __init__(self, id: str, size: tuple[int, int, int], path_x: str, path_y: str, path_z: str):
        global DT, STEPS
        super().__init__(DT, STEPS, Grids([
            Grid(id=id,
                 node=Node('ElasticMetaNode3D'),
                 material_node=MaterialNode(),
                 material=Material(2850.0, 1650.0, 2400.0),
                 factory=Factory("BINGridFactory", size, path_x, path_y, path_z),
                 schema=Schema('ElasticCurveSchema3DRusanov3'),
                 fillers=Fillers(
                     [Filler('RectPeriodFiller', i, j) for i in range(3) for j in range(2)]
                 ),
                 correctors=Correctors(
                     [Corrector('ForceRectElasticBoundary2D', i, j) for i in range(3) for j in range(2)]
                 )
                 )
        ]))


class Impulse(Corrector):
    @property
    def class_name(self):
        return 'corrector'


a = GeomConfig('test', (1, 1, 1), 'path_x', 'path_y', 'path_z')
a.to_file('test.conf')
