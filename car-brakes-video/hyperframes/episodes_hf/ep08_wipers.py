import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from hf_build import tiktok_scenes
NAME = "ep08_wipers"
SCENES = tiktok_scenes("ep08_wipers")
VIS_NAMES = ['hook_wiper', 'wipe1', 'wipe2', 'wipe3', 'wipe4', 'wipe5', "cta"]
NEXT = "BRAKE FLUID CHECK"
