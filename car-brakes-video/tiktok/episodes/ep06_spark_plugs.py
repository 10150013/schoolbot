import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from parts import *

NAME = "ep06_spark_plugs"
CAPTION = """
Rough idle? Bad gas mileage? Worn spark plugs could be why. Change them in 6 steps ⚡🔧

Use the plug type, gap and torque from your owner's manual. Work on a cold engine.

#sparkplugs #carmaintenance #diy #cartok #cartips #howto #mechanic #learnontiktok
"""
SCENES = [
 dict(badge="TUNE-UP", title=["ROUGH IDLE?", "CHECK THIS"], acc=YELLOW, vis=v_hook_plug, say=[
    "Rough idle? Bad gas mileage?",
    "Worn spark plugs could be why."]),
 dict(badge="STEP 1 / 6", title=["PULL THE", "COIL"], acc=CYAN, vis=v_plug_coil, say=[
    "Step one. With the engine cold, pull the coil off the first plug.",
    "Do one at a time."]),
 dict(badge="STEP 2 / 6", title=["CLEAN THE", "WELL"], acc=PINK, vis=v_plug_blow, say=[
    "Step two. Blow away any dirt around the plug so nothing falls into the cylinder."]),
 dict(badge="STEP 3 / 6", title=["UNSCREW", "THE PLUG"], acc=ORANGE, vis=v_plug_socket, say=[
    "Step three. Use a spark plug socket to unscrew the old plug."]),
 dict(badge="STEP 4 / 6", title=["CHECK THE", "GAP"], acc=LIME, vis=v_plug_gap, say=[
    "Step four. Check the gap on the new plug with a gap gauge.",
    "Match your manual."]),
 dict(badge="STEP 5 / 6", title=["HAND-THREAD", "IT IN"], acc=PURPLE, vis=v_plug_in, say=[
    "Step five. Thread it in by hand first.",
    "Then snug it to the torque in your manual."], sticker=("HAND-THREAD FIRST", "✋", 0)),
 dict(badge="STEP 6 / 6", title=["COIL BACK", "ON"], acc=YELLOW, vis=v_plug_coilback, say=[
    "Step six. Put the coil back on, then repeat for every cylinder."]),
 dict(badge="DONE!", title=["FOLLOW FOR", "MORE CAR HACKS"], acc=PINK, vis=make_cta("SWAP A BATTERY"), say=[
    "That's it! Follow for more car hacks.",
    "Next up, how to swap a car battery."]),
]
