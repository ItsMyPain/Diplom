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
            contacts = helper.sew_parcyl(self.par, self.cyl, 'Z0', 'Z1', (1, 1), directory)
        else:
            contacts = helper.sew_parcyl(self.cyl, self.par, 'Z1', 'Z0', (1, 1), directory)

        self.par.add_filler(RectNoReflectFiller, ['X', 'Y', 'Z1'])
        self.par.add_corrector(ForceRectElasticBoundary, ['X', 'Y', 'Z1'])
        self.cyl.add_filler(RectNoReflectFiller, ['XY', 'Z0'])
        self.cyl.add_corrector(ForceRectElasticBoundary, ['XY', 'Z0'])

        cond = helper.cut_boundary(self.par, contacts, direction='forward', side='Z0', directory=directory)
        self.par.add_filler(RectNoReflectFillerConditional, ['Z0'], cond)
        self.par.add_corrector(ForceRectElasticBoundary, ['Z0'], cond)

        self.par.reconfigure()
        self.cyl.reconfigure()

        self.contacts = Contacts(contacts, include_contacts=IncludeContacts([self.par.path, self.cyl.path]))
        self.grids = Grids(include_grids=IncludeGrids([self.par.path, self.cyl.path]))
