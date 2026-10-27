import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from parts import *

NAME = "ep05_intake"
CAPTION = """
Your engine breathes air just like you do. Here's the path it takes, from air filter to power 💨⚙️

#howitworks #carengine #intake #carmaintenance #cartok #cartips #learnontiktok #carfacts
"""
SCENES = [
 dict(badge="HOW IT WORKS", title=["YOUR ENGINE", "BREATHES AIR"], acc=CYAN, vis=intake(None, None), say=[
    "Your engine breathes air just like you do.",
    "Here's the path that air takes."]),
 dict(badge="PART 1 / 5", title=["AIR", "FILTER"], acc=CYAN, vis=intake(0, "CATCHES DIRT + BUGS"), say=[
    "First, air comes in and the air filter catches dirt and bugs."]),
 dict(badge="PART 2 / 5", title=["MAF", "SENSOR"], acc=LIME, vis=intake(1, "MEASURES THE AIR"), say=[
    "Next, the mass airflow sensor measures how much air is coming in."]),
 dict(badge="PART 3 / 5", title=["THROTTLE", "BODY"], acc=ORANGE, vis=intake(2, "THE AIR VALVE"), say=[
    "Then the throttle body opens and closes like a valve.",
    "Press the gas and it opens wider."]),
 dict(badge="PART 4 / 5", title=["INTAKE", "MANIFOLD"], acc=PINK, vis=intake(3, "SPLITS AIR TO EACH CYLINDER"), say=[
    "The intake manifold splits that air and sends it to every cylinder."]),
 dict(badge="PART 5 / 5", title=["BANG =", "POWER"], acc=PURPLE, vis=intake(4, "FUEL + AIR + SPARK = POWER", fire=True), say=[
    "Fuel joins in, the spark plug fires, and boom.",
    "That's your power."]),
 dict(badge="DONE!", title=["FOLLOW FOR", "MORE CAR HACKS"], acc=PINK, vis=make_cta("SPARK PLUGS"), say=[
    "That's it! Follow for more car hacks.",
    "Next up, how to change spark plugs."]),
]
