import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from hf_build import tiktok_scenes
NAME = "ep07_battery"
SCENES = tiktok_scenes("ep07_battery")
VIS_NAMES = ['hook_batt', 'batt_safe', 'batt_neg', 'batt_pos', 'batt_lift', 'batt_new', 'batt_back', "cta"]
NEXT = "WIPER BLADES"
