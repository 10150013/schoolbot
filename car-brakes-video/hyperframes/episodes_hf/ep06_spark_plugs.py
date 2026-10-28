import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from hf_build import tiktok_scenes
NAME = "ep06_spark_plugs"
SCENES = tiktok_scenes("ep06_spark_plugs")
VIS_NAMES = ['hook_plug', 'plug_coil', 'plug_blow', 'plug_socket', 'plug_gap', 'plug_in', 'plug_coilback', "cta"]
NEXT = "SWAP A BATTERY"
