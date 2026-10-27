import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from parts import *

NAME = "ep07_battery"
CAPTION = """
Car won't start? Don't pay for a tow. Swap the battery yourself in 6 steps 🔋⚡

Wear gloves and eye protection. Negative off first, positive on first. Check your manual, some cars need a computer reset or have the battery in the trunk.

#carbattery #carmaintenance #diy #cartok #cartips #howto #mechanic #learnontiktok
"""
SCENES = [
 dict(badge="DEAD BATTERY?", title=["CAR WON'T", "START?"], acc=YELLOW, vis=v_hook_batt, say=[
    "Car won't start? Don't pay for a tow.",
    "You can swap the battery yourself in six steps."]),
 dict(badge="STEP 1 / 6", title=["SAFETY", "FIRST"], acc=CYAN, vis=v_batt_safe, say=[
    "Step one. Turn everything off.",
    "Wear gloves and eye protection."]),
 dict(badge="STEP 2 / 6", title=["NEGATIVE", "OFF FIRST"], acc=PINK, vis=v_batt_neg, say=[
    "Step two. Disconnect the negative cable first. That's the black one."], sticker=("NEGATIVE OFF FIRST", "⚡", 0)),
 dict(badge="STEP 3 / 6", title=["POSITIVE", "OFF NEXT"], acc=ORANGE, vis=v_batt_pos, say=[
    "Step three. Then take off the red positive cable."]),
 dict(badge="STEP 4 / 6", title=["LIFT IT", "OUT"], acc=PURPLE, vis=v_batt_lift, say=[
    "Step four. Remove the hold down and lift the battery out.",
    "It's heavy, so lift with your legs."]),
 dict(badge="STEP 5 / 6", title=["NEW BATTERY", "IN"], acc=LIME, vis=v_batt_new, say=[
    "Step five. Clean the cable clamps, set in the new battery, and secure the hold down."]),
 dict(badge="STEP 6 / 6", title=["RECONNECT", "POSITIVE FIRST"], acc=YELLOW, vis=v_batt_back, say=[
    "Step six. Connect positive first, then negative last."], sticker=("POSITIVE FIRST, NEGATIVE LAST", "⚡", 0)),
 dict(badge="DONE!", title=["FOLLOW FOR", "MORE CAR HACKS"], acc=PINK, vis=make_cta("WIPER BLADES"), say=[
    "That's it! Follow for more car hacks.",
    "Next up, how to change your wiper blades."]),
]
