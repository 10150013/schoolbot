import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from hf_build import tiktok_scenes
NAME = "ep04_oil_change"
SCENES = tiktok_scenes("ep04_oil_change")
VIS_NAMES = ['hook_oil', 'car_lift', 'drain', 'ofilter', 'plug_back', 'pour', 'dipstick', "cta"]
NEXT = "HOW YOUR ENGINE BREATHES"
