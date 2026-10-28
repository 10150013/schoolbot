import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from hf_build import tiktok_scenes
NAME = "ep05_intake"
SCENES = tiktok_scenes("ep05_intake")
VIS_NAMES = ['intake_all', 'intake0', 'intake1', 'intake2', 'intake3', 'intake4', "cta"]
NEXT = "SPARK PLUGS"
