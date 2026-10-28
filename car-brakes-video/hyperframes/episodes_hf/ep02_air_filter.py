import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from hf_build import tiktok_scenes
NAME = "ep02_air_filter"
SCENES = tiktok_scenes("ep02_air_filter")
VIS_NAMES = [("hook", dict(old="$80", new="$15", lab_old="SOME SHOP PRICES", lab_new="THE FILTER COSTS ABOUT")), 'air_open', 'air_pull', 'air_light', 'air_new', 'air_close', "cta"]
NEXT = "CABIN AIR FILTER"
