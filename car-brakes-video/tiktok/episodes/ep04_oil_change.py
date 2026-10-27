import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from parts import *

NAME = "ep04_oil_change"
CAPTION = """
Skip the quick lube. Change your own oil in 6 steps 🛢️🔧

Use the oil type, amount and drain plug torque from YOUR owner's manual. Jack stands only. Recycle old oil at an auto parts store.

#oilchange #carmaintenance #diy #cartok #cartips #howto #mechanic #learnontiktok
"""
SCENES = [
 dict(badge="OIL CHANGE", title=["SKIP THE", "QUICK LUBE"], acc=YELLOW, vis=v_hook_oil, say=[
    "Skip the quick lube. You can change your own oil in six steps.",
    "No special skills needed."]),
 dict(badge="STEP 1 / 6", title=["WARM UP", "& LIFT"], acc=PINK, vis=v_car_lift, say=[
    "Step one. Warm the engine for a few minutes, then lift the car safely on jack stands.",
    "Never trust a jack alone."], sticker=("JACK STANDS ONLY", "⚠", 1)),
 dict(badge="STEP 2 / 6", title=["DRAIN THE", "OIL"], acc=CYAN, vis=v_drain, say=[
    "Step two. Put a pan under the drain plug and loosen it.",
    "The oil is hot, so be careful."]),
 dict(badge="STEP 3 / 6", title=["SWAP THE", "FILTER"], acc=ORANGE, vis=v_ofilter, say=[
    "Step three. Let it drain, then spin off the old filter.",
    "Wipe a little fresh oil on the new gasket."]),
 dict(badge="STEP 4 / 6", title=["PLUG IT", "BACK"], acc=PURPLE, vis=v_plug_back, say=[
    "Step four. Put the drain plug back and tighten it to spec. Not gorilla tight."]),
 dict(badge="STEP 5 / 6", title=["POUR IN", "NEW OIL"], acc=YELLOW, vis=v_pour, say=[
    "Step five. Pour in the oil type and amount from your owner's manual."]),
 dict(badge="STEP 6 / 6", title=["CHECK THE", "DIPSTICK"], acc=LIME, vis=v_dipstick, say=[
    "Step six. Check the dipstick, run the engine, then check again.",
    "Recycle the old oil."]),
 dict(badge="DONE!", title=["FOLLOW FOR", "MORE CAR HACKS"], acc=PINK, vis=make_cta("HOW YOUR ENGINE BREATHES"), say=[
    "That's it! Follow for more car hacks.",
    "Next up, how your engine breathes."]),
]
