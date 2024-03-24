from new.config import *


class TestConfig:
    def test_material(self):
        mat = Material(1.21, 3.15, 5.55)
        conf = mat.to_config()
        need = """        [material]
            c1 = 1.21
            c2 = 3.15
            rho = 5.55
        [/material]"""

        assert conf == need

    def test_factory(self):
        fact = Factory('test_name', (11, 12, 13), (-4, 0.5, 0), (0.22, 0.33, 0.1))
        conf = fact.to_config()
        need = """        [factory]
            name = test_name
            size = 11, 12, 13
            origin = -4, 0.5, 0
            spacing = 0.22, 0.33, 0.1
        [/factory]"""

        assert conf == need

        fact = Factory('test_name2', (4, 8, 43), path_x='path_x.bin', path_y='path_y.bin', path_z='path_z.bin')
        conf = fact.to_config()
        need = """        [factory]
            name = test_name2
            size = 4, 8, 43
            path_x = path_x.bin
            path_y = path_y.bin
            path_z = path_z.bin
        [/factory]"""

        assert conf == need

    def test_schema(self):
        schema = Schema('test_schema')
        conf = schema.to_config()
        need = """        [schema]
            name = test_schema
        [/schema]"""

        assert conf == need

    def test_condition(self):
        cond = Condition('test_name1', 'test_name2', 'test_nodes')
        conf = cond.to_config()
        need = """                [condition]
                    name = test_name1
                    [conditions]
                        [condition]
                            name = test_name2
                            nodes_file = test_nodes
                        [/condition]
                    [/conditions]
                [/condition]"""

        assert conf == need

    def test_filler(self):
        fill = Filler('test_name', 0, 1)
        conf = fill.to_config()
        need = """            [filler]
                name = test_name
                axis = 0
                side = 1
            [/filler]"""

        assert conf == need

        cond = Condition('test_name1', 'test_name2', 'test_nodes')
        fill = Filler('test_name2', 1, 0, cond)
        conf = fill.to_config()
        need = """            [filler]
                name = test_name2
                axis = 1
                side = 0
                [condition]
                    name = test_name1
                    [conditions]
                        [condition]
                            name = test_name2
                            nodes_file = test_nodes
                        [/condition]
                    [/conditions]
                [/condition]
            [/filler]"""

        assert conf == need

    def test_fillers(self):
        fillers = Fillers([Filler('test_name', 0, 1), Filler('test_name2', 1, 0)])
        conf = fillers.to_config()
        need = """        [fillers]
            [filler]
                name = test_name
                axis = 0
                side = 1
            [/filler]
            [filler]
                name = test_name2
                axis = 1
                side = 0
            [/filler]
        [/fillers]"""

        assert conf == need

    def test_corrector(self):
        corr = Corrector('test_name', 0, 1)
        conf = corr.to_config()
        need = """            [corrector]
                name = test_name
                axis = 0
                side = 1
            [/corrector]"""

        assert conf == need

        cond = Condition('test_name1', 'test_name2', 'test_nodes')
        corr = Corrector('test_name2', 1, 0, cond)
        conf = corr.to_config()
        need = """            [corrector]
                name = test_name2
                axis = 1
                side = 0
                [condition]
                    name = test_name1
                    [conditions]
                        [condition]
                            name = test_name2
                            nodes_file = test_nodes
                        [/condition]
                    [/conditions]
                [/condition]
            [/corrector]"""

        assert conf == need

    def test_impulses(self):
        impulse = Impulse(8, 4, 20, 'test_name.txt')
        conf = impulse.to_config()
        need = """            [corrector]
                name = PointSourceCorrector3D
                compression = 1.0
                gauss_w = 3
                index = 8, 4, 20
                axis = 0
                [impulse]
                    name = FileInterpolationImpulse
                    [interpolator]
                        name = PiceWiceInterpolator1D
                        file = test_name.txt
                    [/interpolator]
                [/impulse]
            [/corrector]"""

        assert conf == need

    def test_correctors(self):
        correctors = Correctors([Corrector('test_name', 0, 1), Corrector('test_name2', 1, 0)])
        conf = correctors.to_config()
        need = """        [correctors]
            [corrector]
                name = test_name
                axis = 0
                side = 1
            [/corrector]
            [corrector]
                name = test_name2
                axis = 1
                side = 0
            [/corrector]
        [/correctors]"""

        assert conf == need

    def test_grid(self):
        node = Node('ElasticMetaNode3D')
        material = Material(2850.0, 1650.0, 2400.0)
        factory = Factory('BINGridFactory', (61, 61, 41), path_x='path_x.bin', path_y='path_y.bin', path_z='path_z.bin')
        schema = Schema('ElasticCurveSchema3DRusanov3')
        fillers = Fillers([Filler('RectNoReflectFiller', 0, 1), Filler('RectNoReflectFiller', 1, 0)])
        correctors = Correctors(
            [Corrector('ForceRectElasticBoundary3D', 0, 1), Corrector('ForceRectElasticBoundary3D', 1, 0)])
        grid = Grid('test_name', node, material, factory, schema, fillers, correctors)
        conf = grid.to_config()
        need = """    [grid]
        id = test_name
        [node]
            name = ElasticMetaNode3D
        [/node]
        [material_node]
        [/material_node]
        [material]
            c1 = 2850.0
            c2 = 1650.0
            rho = 2400.0
        [/material]
        [factory]
            name = BINGridFactory
            size = 61, 61, 41
            path_x = path_x.bin
            path_y = path_y.bin
            path_z = path_z.bin
        [/factory]
        [schema]
            name = ElasticCurveSchema3DRusanov3
        [/schema]
        [fillers]
            [filler]
                name = RectNoReflectFiller
                axis = 0
                side = 1
            [/filler]
            [filler]
                name = RectNoReflectFiller
                axis = 1
                side = 0
            [/filler]
        [/fillers]
        [correctors]
            [corrector]
                name = ForceRectElasticBoundary3D
                axis = 0
                side = 1
            [/corrector]
            [corrector]
                name = ForceRectElasticBoundary3D
                axis = 1
                side = 0
            [/corrector]
        [/correctors]
    [/grid]"""

        assert conf == need

    def test_grids(self):
        node1 = Node('ElasticMetaNode3D')
        material1 = Material(2850.0, 1650.0, 2400.0)
        factory1 = Factory('BINGridFactory', (61, 61, 41), path_x='path_x.bin', path_y='path_y.bin',
                           path_z='path_z.bin')
        schema1 = Schema('ElasticCurveSchema3DRusanov3')
        fillers1 = Fillers([Filler('RectNoReflectFiller', 0, 1), Filler('RectNoReflectFiller', 1, 0)])
        correctors1 = Correctors(
            [Corrector('ForceRectElasticBoundary3D', 0, 1), Corrector('ForceRectElasticBoundary3D', 1, 0)])
        grid1 = Grid('test_name', node1, material1, factory1, schema1, fillers1, correctors1)

        node2 = Node('ElasticMetaNode3D')
        material2 = Material(2850.0, 1650.0, 2400.0)
        factory2 = Factory('BINGridFactory', (61, 61, 41), path_x='path_x.bin', path_y='path_y.bin',
                           path_z='path_z.bin')
        schema2 = Schema('ElasticCurveSchema3DRusanov3')
        grid2 = Grid('test_name', node2, material2, factory2, schema2)

        grids = Grids([grid1, grid2])
        conf = grids.to_config()
        need = """[grids]
    [grid]
        id = test_name
        [node]
            name = ElasticMetaNode3D
        [/node]
        [material_node]
        [/material_node]
        [material]
            c1 = 2850.0
            c2 = 1650.0
            rho = 2400.0
        [/material]
        [factory]
            name = BINGridFactory
            size = 61, 61, 41
            path_x = path_x.bin
            path_y = path_y.bin
            path_z = path_z.bin
        [/factory]
        [schema]
            name = ElasticCurveSchema3DRusanov3
        [/schema]
        [fillers]
            [filler]
                name = RectNoReflectFiller
                axis = 0
                side = 1
            [/filler]
            [filler]
                name = RectNoReflectFiller
                axis = 1
                side = 0
            [/filler]
        [/fillers]
        [correctors]
            [corrector]
                name = ForceRectElasticBoundary3D
                axis = 0
                side = 1
            [/corrector]
            [corrector]
                name = ForceRectElasticBoundary3D
                axis = 1
                side = 0
            [/corrector]
        [/correctors]
    [/grid]
    [grid]
        id = test_name
        [node]
            name = ElasticMetaNode3D
        [/node]
        [material_node]
        [/material_node]
        [material]
            c1 = 2850.0
            c2 = 1650.0
            rho = 2400.0
        [/material]
        [factory]
            name = BINGridFactory
            size = 61, 61, 41
            path_x = path_x.bin
            path_y = path_y.bin
            path_z = path_z.bin
        [/factory]
        [schema]
            name = ElasticCurveSchema3DRusanov3
        [/schema]
        [fillers]
        [/fillers]
        [correctors]
        [/correctors]
    [/grid]
[/grids]"""

        assert conf == need

    def test_contact(self):
        cont = Contact('test_name', 'grid1', 'grid2', interpolation_file='interpolation_file',
                       predictor_flag=True, corrector_flag=False, axis=0, contact_file='contact_file')

        conf = cont.to_config()
        need = """    [contact]
        name = test_name
        grid1 = grid1
        grid2 = grid2
        interpolation_file = interpolation_file
        contact_file = contact_file
        predictor_flag = true
        corrector_flag = false
        axis = 0
    [/contact]"""

        assert conf == need

    def test_contacts(self):
        contacts = Contacts([
            Contact('test_name', 'grid1', 'grid2', interpolation_file='interpolation_file',
                    predictor_flag=True, corrector_flag=False, axis=0, contact_file='contact_file'),
            Contact('test_name', 'grid1', 'grid2', interpolation_file='interpolation_file',
                    predictor_flag=True, corrector_flag=False, axis=0, contact_file='contact_file')
        ])
        conf = contacts.to_config()
        need = """[contacts]
    [contact]
        name = test_name
        grid1 = grid1
        grid2 = grid2
        interpolation_file = interpolation_file
        contact_file = contact_file
        predictor_flag = true
        corrector_flag = false
        axis = 0
    [/contact]
    [contact]
        name = test_name
        grid1 = grid1
        grid2 = grid2
        interpolation_file = interpolation_file
        contact_file = contact_file
        predictor_flag = true
        corrector_flag = false
        axis = 0
    [/contact]
[/contacts]"""

        assert conf == need
