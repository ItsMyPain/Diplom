set -e
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_top_C1_left.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_top_C1_left.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_left_C1_bottom.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_left_C1_bottom.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_bottom_C1_right.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_bottom_C1_right.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_right_C1_top.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_right_C1_top.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_center_C1_top.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_center_C1_top.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_center_C1_left.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_center_C1_left.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_center_C1_bottom.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_center_C1_bottom.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_center_C1_right.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/C1/interpolation_configs/C1_center_C1_right.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_center.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_center.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_top.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_top.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_right.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_right.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_bottom.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_bottom.cfg
direction=1 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_left.cfg
direction=2 interpolation=barycentric rect_new/rect/build/interpolation ./PC1/interpolation_configs/P1_C1_left.cfg
python3 boundary_cutter.py ./PC1/P1/boundary/erased_nodes.txt '0 -1 -2' './PC1/interpolation/backward_P1_C1_center.txt ./PC1/interpolation/backward_P1_C1_top.txt ./PC1/interpolation/backward_P1_C1_right.txt ./PC1/interpolation/backward_P1_C1_bottom.txt ./PC1/interpolation/backward_P1_C1_left.txt'