import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from hf_build import tiktok_scenes
NAME = "ep03_cabin_filter"
SCENES = tiktok_scenes("ep03_cabin_filter")
VIS_NAMES = ['hook_vent', 'glove1', 'glove2', 'glove3', 'glove4', 'glove5', "cta"]
NEXT = "OIL CHANGE"
