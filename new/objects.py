from .kernel import *


class ParCyl(Base):
    par: Parallelepiped
    cyl: Cylinder

    def __init__(self, id: str, par: Parallelepiped, cyl: Cylinder):
        super().__init__(id)
        self.par = par
        self.cyl = cyl

    def save(self, directory: str):
        self.par.configure(directory)
        self.cyl.configure(directory)

        if self.par.z0 > self.cyl.z0:
            contacts = helper.sew_par_cyl(self.par, self.cyl, 'Z0', 'Z1', (1, 1), directory)
        else:
            contacts = helper.sew_par_cyl(self.cyl, self.par, 'Z1', 'Z0', (1, 1), directory)

        self.par.add_filler(RectNoReflectFiller, ['X', 'Y', 'Z1'])
        self.par.add_corrector(ForceRectElasticBoundary, ['X', 'Y', 'Z1'])
        self.cyl.add_filler(RectNoReflectFiller, ['XY', 'Z0'])
        self.cyl.add_corrector(ForceRectElasticBoundary, ['XY', 'Z0'])

        cond = helper.cut_boundary(self.par.grid, contacts, direction='forward', side='Z0', directory=directory)
        self.par.add_filler(RectNoReflectFillerConditional, ['Z0'], cond)
        self.par.add_corrector(ForceRectElasticBoundary, ['Z0'], cond)

        self.par.reconfigure()
        self.cyl.reconfigure()

        self.contacts = Contacts(contacts, include_contacts=IncludeContacts([self.par.path, self.cyl.path]))
        self.grids = Grids(include_grids=IncludeGrids([self.par.path, self.cyl.path]))


class Column(Base):
    cyl_d: Cylinder
    cyl_u: Cylinder

    def __init__(self, id: str, cyl_d: Cylinder, cyl_u: Cylinder):
        super().__init__(id)
        if cyl_d.z0 >= cyl_u.z0:
            raise ValueError('Неправильное расположение цилиндров')
        self.cyl_d = cyl_d
        self.cyl_u = cyl_u

    def save(self, directory: str):
        self.cyl_d.configure(directory)
        self.cyl_u.configure(directory)

        contacts = helper.sew_cyl_cyl(self.cyl_d, self.cyl_u, 'Z1', 'Z0', (1, 1), directory)

        self.cyl_d.add_filler(RectNoReflectFiller, ['XY'])
        self.cyl_d.add_corrector(ForceRectElasticBoundary, ['XY'])
        self.cyl_u.add_filler(RectNoReflectFiller, ['XY'])
        self.cyl_u.add_corrector(ForceRectElasticBoundary, ['XY'])

        self.cyl_d.reconfigure()
        self.cyl_u.reconfigure()

        self.contacts = Contacts(contacts, include_contacts=IncludeContacts([self.cyl_d.path, self.cyl_u.path]))
        self.grids = Grids(include_grids=IncludeGrids([self.cyl_d.path, self.cyl_u.path]))

    def reconfigure(self):
        self.cyl_d.reconfigure()
        self.cyl_u.reconfigure()
        super().reconfigure()


class Platform(Base):
    p_d: Parallelepiped
    p_u: Parallelepiped
    columns: list[Column]

    def __init__(self, id: str, p_d: Parallelepiped, p_u: Parallelepiped, columns: list[Column]):
        super().__init__(id)
        self.p_d = p_d
        self.p_u = p_u
        self.columns = columns

    def save(self, directory: str):
        self.p_d.configure(directory)
        self.p_u.configure(directory)

        for i in self.columns:
            i.configure(directory)

        sews1 = []
        sews2 = []

        for column in self.columns:
            sews1.extend(helper.sew_par_cyl(self.p_d, column.cyl_d, 'Z1', 'Z0', (1, 1), directory))
            sews2.extend(helper.sew_par_cyl(self.p_u, column.cyl_u, 'Z0', 'Z1', (1, 1), directory))

        self.p_d.add_filler(RectNoReflectFiller, ['X', 'Y', 'Z0'])
        self.p_d.add_corrector(ForceRectElasticBoundary, ['X', 'Y', 'Z0'])
        cond1 = helper.cut_boundary(self.p_d.grid, sews1, direction='backward', side='Z1', directory=directory)
        self.p_d.add_filler(RectNoReflectFillerConditional, ['Z1'], cond1)
        self.p_d.add_corrector(ForceRectElasticBoundary, ['Z1'], cond1)

        self.p_u.add_filler(RectNoReflectFiller, ['X', 'Y', 'Z1'])
        self.p_u.add_corrector(ForceRectElasticBoundary, ['X', 'Y', 'Z1'])
        cond2 = helper.cut_boundary(self.p_u.grid, sews2, direction='backward', side='Z0', directory=directory)
        self.p_u.add_filler(RectNoReflectFillerConditional, ['Z0'], cond2)
        self.p_u.add_corrector(ForceRectElasticBoundary, ['Z0'], cond2)

        self.p_d.reconfigure()
        self.p_u.reconfigure()

        for i in self.columns:
            i.reconfigure()

        self.contacts = Contacts(sews1 + sews2,
                                 include_contacts=IncludeContacts(
                                     [self.p_d.path, self.p_u.path, *[i.path for i in self.columns]]))
        self.grids = Grids(include_grids=IncludeGrids([self.p_d.path, self.p_u.path, *[i.path for i in self.columns]]))

    def reconfigure(self):
        self.p_d.reconfigure()
        self.p_u.reconfigure()
        for i in self.columns:
            i.reconfigure()
        super().reconfigure()
