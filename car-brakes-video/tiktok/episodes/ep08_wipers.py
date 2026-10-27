import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from parts import *

NAME = "ep08_wipers"
CAPTION = """
Streaky wipers? Fix them in 60 seconds. No tools needed 🌧️🚗

Hold the arm so it can't snap back onto the glass. Blade types and clips vary, so check the package.

#wiperblades #carmaintenance #diy #cartok #cartips #howto #carhacks #learnontiktok
"""
SCENES = [
 dict(badge="60-SECOND FIX", title=["STREAKY", "WIPERS?"], acc=CYAN, vis=v_hook_wiper, say=[
    "Streaky wipers? Fix them in sixty seconds.",
    "No tools needed."]),
 dict(badge="STEP 1 / 5", title=["LIFT THE", "ARM"], acc=PINK, vis=v_wipe1, say=[
    "Step one. Lift the wiper arm away from the glass.",
    "Hold it, don't let it snap back."], sticker=("DON'T LET IT SNAP BACK", "⚠", 1)),
 dict(badge="STEP 2 / 5", title=["FIND THE", "TAB"], acc=YELLOW, vis=v_wipe2, say=[
    "Step two. Find the little tab where the blade meets the arm."]),
 dict(badge="STEP 3 / 5", title=["SLIDE THE", "BLADE OFF"], acc=ORANGE, vis=v_wipe3, say=[
    "Step three. Press the tab and slide the old blade off."]),
 dict(badge="STEP 4 / 5", title=["CLICK THE", "NEW ONE ON"], acc=LIME, vis=v_wipe4, say=[
    "Step four. Slide the new blade on until it clicks."]),
 dict(badge="STEP 5 / 5", title=["LOWER IT", "GENTLY"], acc=PURPLE, vis=v_wipe5, say=[
    "Step five. Lower the arm gently and test it with washer fluid."]),
 dict(badge="DONE!", title=["FOLLOW FOR", "MORE CAR HACKS"], acc=PINK, vis=make_cta("BRAKE FLUID CHECK"), say=[
    "That's it! Follow for more car hacks.",
    "Next up, how to check your brake fluid."]),
]
