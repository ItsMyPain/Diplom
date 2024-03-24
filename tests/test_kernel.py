import shutil

from new.kernel import *


class TestKernel:
    test_conf_dir = 'configs'

    def test_parallelepiped(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        par = Parallelepiped('P1', mat, lg=10, w=10, h=20, h_lg=0.5, h_w=0.5, h_h=0.5)

        par.configure(directory='P1')

        par.add_filler('RectNoReflectFiller', ['X', 'Y', 'Z0'])
        par.add_corrector('ForceRectElasticBoundary3D', ['X', 'Y', 'Z0'])

        par.reconfigure()

        with open('P1/P1.conf', 'r') as f:
            conf = f.read()

        with open(f'{self.test_conf_dir}/P1.conf', 'r') as f:
            template = f.read()

        assert conf == template

        shutil.rmtree('P1')

    def test_prism(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        prism = Prism('P2', mat, lg_d=20, w_d=20, lg_u=10, w_u=10, h=20, h_lg=0.5, h_w=0.5, h_h=0.5)

        prism.configure(directory='P2')

        prism.add_filler('RectNoReflectFiller', ['X', 'Y', 'Z0'])
        prism.add_corrector('ForceRectElasticBoundary3D', ['X', 'Y', 'Z0'])

        prism.reconfigure()

        with open('P2/P2.conf', 'r') as f:
            conf = f.read()

        with open(f'{self.test_conf_dir}/P2.conf', 'r') as f:
            template = f.read()

        assert conf == template

        shutil.rmtree('P2')

    def test_cylinder(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        cyl = Cylinder('C1', mat, r_d=10, r_u=10, h=20, h_r=0.5, h_h=0.5)

        cyl.configure(directory='C1')

        cyl.add_filler('RectNoReflectFiller', ['XY', 'Z0'])
        cyl.add_corrector('ForceRectElasticBoundary3D', ['XY', 'Z0'])

        cyl.reconfigure()

        with open('C1/C1.conf', 'r') as f:
            conf = f.read()

        with open(f'{self.test_conf_dir}/C1.conf', 'r') as f:
            template = f.read()

        assert conf == template

        shutil.rmtree('C1')
