import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from parts import *

NAME = "ep02_air_filter"
CAPTION = """
Some shops charge $80 for this. The filter is about $15 and it takes 2 minutes. Engine air filter in 5 steps 🔧

Check your owner's manual for the right filter and how your air box opens.

#carmaintenance #airfilter #diy #cartok #cartips #howto #carhacks #learnontiktok
"""
SCENES = [
 dict(badge="DIY AIR FILTER", title=["$15 FIX SHOPS", "CHARGE $80 FOR"], acc=YELLOW, vis=hook_price("$80", "$15", "SOME SHOP PRICES", "THE FILTER COSTS ABOUT"), say=[
    "Some shops charge eighty dollars for this.",
    "It takes two minutes and a fifteen dollar filter."]),
 dict(badge="STEP 1 / 5", title=["OPEN THE", "AIR BOX"], acc=CYAN, vis=v_air_open, say=[
    "Step one. Open the air box. It's usually a couple of clips or a few screws."]),
 dict(badge="STEP 2 / 5", title=["PULL THE", "OLD FILTER"], acc=PINK, vis=v_air_pull, say=[
    "Step two. Lift the lid and pull the old filter straight out."]),
 dict(badge="STEP 3 / 5", title=["THE LIGHT", "TEST"], acc=YELLOW, vis=v_air_light, say=[
    "Step three. Hold it up to a light.",
    "If you can't see light through it, it's done."]),
 dict(badge="STEP 4 / 5", title=["DROP IN", "THE NEW ONE"], acc=LIME, vis=v_air_new, say=[
    "Step four. Wipe out any dust, then drop in the new filter. Same shape, same side up."]),
 dict(badge="STEP 5 / 5", title=["CLIP IT", "SHUT"], acc=ORANGE, vis=v_air_close, say=[
    "Step five. Close the lid and snap the clips. That's it."]),
 dict(badge="DONE!", title=["FOLLOW FOR", "MORE CAR HACKS"], acc=PINK, vis=make_cta("CABIN AIR FILTER"), say=[
    "That's it! Follow for more car hacks.",
    "Next up, the cabin air filter."]),
]
