import os
import shutil

from orm.kernel import *


class TestKernel:
    test_conf_dir = 'configs'

    def test_helper(self):
        helper1 = Helper()

        helper1.add_command('command1')
        helper1.add_command('command2')

        helper1.to_file('helper.sh')

        need = "set -e\ncommand1\ncommand2"

        with open('helper.sh') as f:
            conf = f.read()

        assert conf == need

        os.remove('helper.sh')

    def test_bins(self):
        bins = Bins('B1', (np.linspace(0, 1), np.arange(2, 3, 0.5), np.ones(3)))
        paths = bins.save('B1')

        for i, j in zip(paths, (f"bins/B1_{i}.bin" for i in 'xyz')):
            with open(i, 'rb') as f:
                conf = f.read()

            with open(j, 'rb') as f:
                template = f.read()

            assert conf == template

        shutil.rmtree('B1')

    def test_base(self):
        base = Base('B1')

        base.configure('.')

        base.reconfigure()

        with open(base.path) as f:
            conf = f.read()

        with open(f'{self.test_conf_dir}/B1.conf') as f:
            template = f.read()

        assert conf == template

        shutil.rmtree('B1')

    def test_parallelepiped(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        par = Parallelepiped('P1', mat, lg=10, w=10, h=20, h_lg=0.5, h_w=0.5, h_h=0.5)

        par.configure('.')

        par.add_filler('RectNoReflectFiller', ['X', 'Y', 'Z0'])
        par.add_corrector('ForceRectElasticBoundary3D', ['X', 'Y', 'Z0'])

        par.grid.add_impulse('test_impulse.txt', x=0.5, y=0.5, z=0.5)

        par.reconfigure()

        with open(par.path) as f:
            conf = f.read()

        with open(f'{self.test_conf_dir}/P1.conf') as f:
            template = f.read()

        assert conf == template

        shutil.rmtree('P1')

    def test_prism(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        prism = Prism('P2', mat, lg_d=20, w_d=20, lg_u=10, w_u=10, h=20, h_lg=0.5, h_w=0.5, h_h=0.5)

        prism.configure('.')

        prism.add_filler('RectNoReflectFiller', ['X', 'Y', 'Z0'])
        prism.add_corrector('ForceRectElasticBoundary3D', ['X', 'Y', 'Z0'])

        prism.grid.add_impulse('test_impulse.txt', x=0.5, y=0.5, z=0.5)

        prism.reconfigure()

        with open(prism.path) as f:
            conf = f.read()

        with open(f'{self.test_conf_dir}/P2.conf') as f:
            template = f.read()

        assert conf == template

        shutil.rmtree('P2')

    def test_cylinder(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        cyl = Cylinder('C1', mat, r_d=10, r_u=10, h=20, h_r=0.5, h_h=0.5)

        cyl.configure('.')

        cyl.add_filler('RectNoReflectFiller', ['XY', 'Z0'])
        cyl.add_corrector('ForceRectElasticBoundary3D', ['XY', 'Z0'])

        cyl.reconfigure()

        with open(cyl.path) as f:
            conf = f.read()

        with open(f'{self.test_conf_dir}/C1.conf') as f:
            template = f.read()

        assert conf == template

        shutil.rmtree('C1')

    def test_sew(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        par1 = Parallelepiped('P1', mat, lg=10, w=10, h=10, h_lg=0.5, h_w=0.5, h_h=0.5)
        par2 = Parallelepiped('P2', mat, lg=10, w=10, h=10, h_lg=0.5, h_w=0.5, h_h=0.5, z0=10)

        par1.configure('sew')
        par2.configure('sew')

        helper1 = Helper()
        contacts = helper1.sew(par1.grid, par1.path, par2.grid, par2.path, 'Z1', 'Z0', (1, 1), 'sew')
        helper1.to_file('sew/sew.sh')

        need = """set -e
direction=1 interpolation=barycentric rect_new/rect/build/interpolation sew/interpolation_configs/P1_P2.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation sew/interpolation_configs/P1_P2.cfg"""

        with open('sew/sew.sh') as f:
            conf = f.read()

        assert conf == need

        with open("sew/interpolation_configs/P1_P2.cfg") as f:
            conf = f.read()

        with open(f"{self.test_conf_dir}/P1_P2.cfg") as f:
            need = f.read()

        assert conf == need

        need = """    [contact]
        name = RectGridInterpolationCorrector
        grid1 = P1
        grid2 = P2
        interpolation_file = "sew/interpolation/forward_P1_P2.txt"
        predictor_flag = true
        corrector_flag = false
        axis = 1
    [/contact]"""

        assert contacts[0].to_config() == need

        need = """    [contact]
        name = RectGridInterpolationCorrector
        grid1 = P2
        grid2 = P1
        interpolation_file = "sew/interpolation/backward_P1_P2.txt"
        predictor_flag = false
        corrector_flag = true
        axis = 1
    [/contact]"""

        assert contacts[1].to_config() == need

        shutil.rmtree('sew')

    def test_cut_boundary(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        par1 = Parallelepiped('P1', mat, lg=20, w=20, h=10, h_lg=0.5, h_w=0.5, h_h=0.5)
        par2 = Parallelepiped('P2', mat, lg=10, w=10, h=10, h_lg=0.5, h_w=0.5, h_h=0.5, z0=10)

        par1.configure('cut_boundary')
        par2.configure('cut_boundary')

        helper1 = Helper()
        contacts = helper1.sew(par1.grid, par1.path, par2.grid, par2.path, 'Z1', 'Z0', (1, 1), 'cut_boundary')
        cond = helper1.cut_boundary(par1.grid, contacts, direction='forward', side='Z0', directory='cut_boundary')

        helper1.to_file('cut_boundary/cut_boundary.sh')

        need = """set -e
direction=1 interpolation=barycentric rect_new/rect/build/interpolation cut_boundary/interpolation_configs/P1_P2.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation cut_boundary/interpolation_configs/P1_P2.cfg
python3 boundary_cutter.py cut_boundary/P1/boundary_configs/P1.cfg"""

        with open('cut_boundary/cut_boundary.sh') as f:
            conf = f.read()

        assert conf == need

        need = """                [condition]
                    name = RectNodeMatchConditionNoneOf
                    [conditions]
                        [condition]
                            name = RectNodeMatchConditionInFixedSet
                            nodes_file = cut_boundary/P1/boundary/erased_nodes.txt
                        [/condition]
                    [/conditions]
                [/condition]"""

        assert cond.to_config() == need

        shutil.rmtree('cut_boundary')

    def test_contact(self):
        mat = Material(2850.0, 1650.0, 2400.0)
        par1 = Parallelepiped('P1', mat, lg=20, w=20, h=10, h_lg=0.5, h_w=0.5, h_h=0.5)
        par2 = Parallelepiped('P2', mat, lg=10, w=10, h=10, h_lg=0.5, h_w=0.5, h_h=0.5, z0=10)

        par1.configure('contact')
        par2.configure('contact')

        helper1 = Helper()
        contact = helper1.contact(par1.grid, par2.grid, 'contact')
        helper1.to_file('contact/contact.sh')

        need = """set -e
rect_new/rect/build/contact_finder contact/contact_configs/P1_P2.cfg"""

        with open('contact/contact.sh') as f:
            conf = f.read()

        assert conf == need

        need = """    [contact]
        name = GlueRectElasticContact3D
        grid1 = P1
        grid2 = P2
        contact_file = "contact/contact/P1_P2.txt"
    [/contact]"""

        assert contact.to_config() == need

        shutil.rmtree('contact')