from objects import *

R1 = 10
R2 = 15
H1 = 20
H2 = 40
H_R = 0.35
H_H = 0.35

# p1 = Parallelepiped('p1', lg=10, w=10, h=10, h_l=H_R, h_w=H_R, h_h=H_H)
# p1.configure()
# p1.build()

c1 = Cylinder('C1', r1=R1, r2=R2, h=H1, z0=0, h_r=H_R, h_h=H_H)
c1.center.data.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.1)
c1.configure()
c1.build()
