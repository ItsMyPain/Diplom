set -e
rect_new/rect/build/contact_finder ./PP_C/contact_configs/P2_P1.cfg
python3 boundary_cutter.py ./PP_C/P1/boundary_configs/P1.cfg
rect_new/rect/build/rect ./PP_C/PP_C.conf