import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tiktok"))
import engine
from hf_vis_brakes import EP01
NAME = "ep01_brakes"
SCENES = engine.SCENES            # same script as the first cut
VIS_NAMES = EP01
NEXT = None
