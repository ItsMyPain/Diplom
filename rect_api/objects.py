from .bricks import *


class Platform(Base):
    p1: Parallelepiped
    p2: Parallelepiped
    columns: list[Column]

    def __init__(self, filename: str, p1: Parallelepiped, p2: Parallelepiped, columns: list[Column]):
        super().__init__(filename)
        self.p1 = p1
        self.p2 = p2
        self.columns = list(columns)

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        self.p1.configure(direct)
        self.p2.configure(direct)

        for i in self.columns:
            i.configure(direct)

        sews1 = []
        sews2 = []

        for i in self.columns:
            sews1.extend(i.sew_par(self.p1, 'Z0', 'Z1', (1, 1), direct))
            sews2.extend(i.sew_par(self.p2, 'Z1', 'Z0', (1, 1), direct))
            i.add_property(Filler, RectNoReflectFiller, ['XY'])
            i.add_property(Corrector, ForceRectElasticBoundary, ['XY'])

        self.p1.add_property(Filler, RectNoReflectFiller, ['X', 'Y', 'Z0'])
        self.p1.add_property(Corrector, ForceRectElasticBoundary, ['X', 'Y', 'Z0'])
        self.p2.add_property(Filler, RectNoReflectFiller, ['X', 'Y', 'Z1'])
        self.p2.add_property(Corrector, ForceRectElasticBoundary, ['X', 'Y', 'Z1'])

        cond1 = Condition("RectNodeMatchConditionNoneOf", "RectNodeMatchConditionInFixedSet")
        cond1.from_contact(self.p1, sews1, direction='forward', side='Z1', directory=direct)
        self.p1.add_property(Filler, RectNoReflectFillerConditional, 'Z1', cond1)
        self.p1.add_property(Corrector, ForceRectElasticBoundary, 'Z1', cond1)

        cond2 = Condition("RectNodeMatchConditionNoneOf", "RectNodeMatchConditionInFixedSet")
        cond2.from_contact(self.p2, sews2, direction='forward', side='Z0', directory=direct)
        self.p2.add_property(Filler, RectNoReflectFillerConditional, 'Z0', cond2)
        self.p2.add_property(Corrector, ForceRectElasticBoundary, 'Z0', cond2)

        self.p1.reconfigure(direct)
        self.p2.reconfigure(direct)

        for i in self.columns:
            i.reconfigure(direct)

        self.contacts = sews1 + sews2

        self._save_new_config((self.p1, self.p2, *self.columns), directory)

        self.configured = True


class ParallelepipedCylinder(Base):
    def __init__(self, filename: str, par: Parallelepiped, cyl: Cylinder):
        super().__init__(filename)
        self.par = par
        self.cyl = cyl

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        self.par.configure(direct)
        self.cyl.configure(direct)

        self.contacts = self.cyl.sew_par(self.par, 'Z1', 'Z0', (1, 1), direct)

        self.par.add_property(Filler, RectNoReflectFiller, ['X', 'Y', 'Z1'])
        self.par.add_property(Corrector, ForceRectElasticBoundary, ['X', 'Y', 'Z1'])
        self.cyl.add_property(Filler, RectNoReflectFiller, ['XY', 'Z0'])
        self.cyl.add_property(Corrector, ForceRectElasticBoundary, ['XY', 'Z0'])

        cond = Condition("RectNodeMatchConditionNoneOf", "RectNodeMatchConditionInFixedSet")
        cond.from_contact(self.par, self.contacts, direction='forward', side='Z0', directory=direct)
        self.par.add_property(Filler, RectNoReflectFillerConditional, 'Z0', cond)
        self.par.add_property(Corrector, ForceRectElasticBoundary, 'Z0', cond)

        self.par.reconfigure(direct)
        self.cyl.reconfigure(direct)

        self._save_new_config((self.par, self.cyl), directory)

        self.configured = True


class TwoParCut(Base):
    def __init__(self, filename: str, par1: Parallelepiped, par2: Parallelepiped):
        super().__init__(filename)
        self.par1 = par1
        self.par2 = par2

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        self.par1.configure(direct)
        self.par2.configure(direct)

        self.contacts = self.par1.sew_geom(self.par2.data, 'Z1', 'Z0', (1, 1), direct)

        self.par1.add_property(Filler, RectNoReflectFiller, ['X', 'Y', 'Z0'])
        self.par1.add_property(Corrector, ForceRectElasticBoundary, ['X', 'Y', 'Z0'])
        self.par2.add_property(Filler, RectNoReflectFiller, ['X', 'Y', 'Z1'])
        self.par2.add_property(Corrector, ForceRectElasticBoundary, ['X', 'Y', 'Z1'])

        if self.par1.data.x.size > self.par2.data.x.size or self.par1.data.y.size > self.par2.data.y.size:
            cond = Condition("RectNodeMatchConditionNoneOf", "RectNodeMatchConditionInFixedSet")
            cond.from_contact(self.par1, self.contacts, direction='backward', side='Z1', directory=direct)
            self.par1.add_property(Filler, RectNoReflectFillerConditional, 'Z1', cond)
            self.par1.add_property(Corrector, ForceRectElasticBoundary, 'Z1', cond)

        if self.par1.data.x.size < self.par2.data.x.size or self.par1.data.y.size < self.par2.data.y.size:
            cond = Condition("RectNodeMatchConditionNoneOf", "RectNodeMatchConditionInFixedSet")
            cond.from_contact(self.par2, self.contacts, direction='forward', side='Z0', directory=direct)
            self.par2.add_property(Filler, RectNoReflectFillerConditional, 'Z0', cond)
            self.par2.add_property(Corrector, ForceRectElasticBoundary, 'Z0', cond)

        self.par1.reconfigure(direct)
        self.par2.reconfigure(direct)

        self._save_new_config((self.par1, self.par2), directory)

        self.configured = True


class TwoParContact(Base):
    par1: Parallelepiped
    par2: Parallelepiped

    def __init__(self, filename: str, p1: Parallelepiped, p2: Parallelepiped):
        super().__init__(filename)
        self.par1 = p1
        self.par2 = p2

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        self.par1.configure(direct)
        self.par2.configure(direct)

        self.contacts = [self.par1.contact(self.par2.data, direct)]

        self.par1.add_property(Filler, RectNoReflectFiller, ['X', 'Y', 'Z'])
        self.par2.add_property(Filler, RectNoReflectFiller, ['X', 'Y', 'Z'])

        self.par1.reconfigure(direct)
        self.par2.reconfigure(direct)

        self._save_new_config((self.par1, self.par2), directory)
        self.configured = True
