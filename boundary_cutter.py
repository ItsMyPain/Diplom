import argparse

parser = argparse.ArgumentParser("boundary_cutter")
parser.add_argument("output_file", type=str)
parser.add_argument("z", type=str)
parser.add_argument("input_files", type=str)
args = parser.parse_args()

input_files = args.input_files.split()
z = args.z.split()
output_file = args.output_file

xx, yy, zz = [], [], []

for input_file in input_files:
    with open(input_file, 'r') as input_f:
        input_f.readline()
        input_f.readline()
        input_f.readline()
        for line in input_f:
            x_i, y_i = map(int, line.split()[:2])
            for z_i in z:
                xx.append(x_i)
                yy.append(y_i)
                zz.append(z_i)

with open(output_file, 'w') as output_f:
    output_f.write(f'{len(xx)}\n')
    for i in range(len(xx)):
        output_f.write(f'{xx[i]} {yy[i]} {zz[i]}\n')
