set -e
direction=1 interpolation=barycentric rect_new/rect/build/interpolation interpolation_configs/P3/P1/P1_P2.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation interpolation_configs/P3/P1/P1_P2.cfg
python3 boundary_cutter.py boundary/P3/P2/erased_nodes.txt '0 -1 -2' 'interpolation/P3/P1/forward_P1_P2.txt'
rect_new/rect/build/rect configs/P3.conf