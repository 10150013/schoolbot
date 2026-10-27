import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from parts import *

NAME = "ep03_cabin_filter"
CAPTION = """
A/C smells like old gym socks? Blame the cabin air filter. Swap it in 5 steps 🤢➡️😮‍💨

Glove box and filter cover layouts vary, so check your owner's manual.

#cabinairfilter #carmaintenance #diy #cartok #cartips #howto #carhacks #learnontiktok
"""
SCENES = [
 dict(badge="FRESH AIR FIX", title=["SMELLY A/C?", "BLAME THIS"], acc=LIME, vis=v_hook_vent, say=[
    "Does your air conditioning smell like old gym socks?",
    "Blame this filter. Here's the fix."]),
 dict(badge="STEP 1 / 5", title=["OPEN THE", "GLOVE BOX"], acc=CYAN, vis=v_glove1, say=[
    "Step one. Empty the glove box."]),
 dict(badge="STEP 2 / 5", title=["DROP IT", "DOWN"], acc=PINK, vis=v_glove2, say=[
    "Step two. On most cars, squeeze the sides so it swings all the way down."]),
 dict(badge="STEP 3 / 5", title=["SLIDE THE", "FILTER OUT"], acc=YELLOW, vis=v_glove3, say=[
    "Step three. Pop off the filter cover and slide the old filter out."]),
 dict(badge="STEP 4 / 5", title=["CHECK THE", "ARROW"], acc=ORANGE, vis=v_glove4, say=[
    "Step four. Check the arrow on the new filter.",
    "It should point the way the air flows, usually down."], sticker=("FOLLOW THE AIRFLOW ARROW", "💨", 1)),
 dict(badge="STEP 5 / 5", title=["NEW FILTER", "IN"], acc=LIME, vis=v_glove5, say=[
    "Step five. Slide the new filter in, snap the cover on, and close the glove box. Fresh air!"]),
 dict(badge="DONE!", title=["FOLLOW FOR", "MORE CAR HACKS"], acc=PINK, vis=make_cta("OIL CHANGE"), say=[
    "That's it! Follow for more car hacks.",
    "Next up, how to change your oil."]),
]
