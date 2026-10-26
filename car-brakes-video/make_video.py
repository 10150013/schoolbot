"""Builds how_to_change_car_brakes.mp4 from slides drawn with Pillow,
narrated with espeak-ng and assembled with ffmpeg."""
import os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
OUT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(OUT, "build")
os.makedirs(WORK, exist_ok=True)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG, FG, ACC, WARN = (18, 24, 38), (240, 244, 250), (255, 170, 40), (240, 80, 70)

def font(p, s): return ImageFont.truetype(p, s)

def diagram(d, stage):
    """Draw a side view of a brake: rotor, caliper, pads, wheel depending on stage."""
    cx, cy = 900, 400
    if stage in ("wheel", "jack"):
        d.ellipse([cx-210, cy-210, cx+210, cy+210], fill=(30, 30, 34), outline=(90, 90, 100), width=6)
        d.ellipse([cx-150, cy-150, cx+150, cy+150], fill=(150, 155, 165))
        for i in range(5):
            import math
            a = i * 2 * math.pi / 5
            x, y = cx + 70*math.cos(a), cy + 70*math.sin(a)
            d.ellipse([x-14, y-14, x+14, y+14], fill=ACC if stage == "wheel" else (90, 90, 100))
        d.ellipse([cx-25, cy-25, cx+25, cy+25], fill=(60, 60, 70))
        if stage == "jack":
            d.rectangle([cx-120, cy+250, cx+120, cy+275], fill=WARN)
            d.rectangle([cx-30, cy+215, cx+30, cy+250], fill=(200, 60, 55))
        return
    d.ellipse([cx-190, cy-190, cx+190, cy+190], fill=(120, 125, 135), outline=(200, 205, 215), width=4)
    for r in (60, 130):
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(90, 95, 105), width=3)
    d.ellipse([cx-45, cy-45, cx+45, cy+45], fill=(60, 62, 70))
    if stage == "rotor_only":
        return
    off = 70 if stage == "caliper_off" else 0
    if stage in ("pads", "compress"):
        off = 0
    px = cx + 120 - off // 2
    if stage != "caliper_off":
        d.rounded_rectangle([cx+90, cy-120, cx+210, cy+120], 18, fill=(200, 50, 45), outline=(255, 120, 110), width=3)
    else:
        d.rounded_rectangle([cx+140, cy+90, cx+260, cy+300], 18, fill=(200, 50, 45), outline=(255, 120, 110), width=3)
        d.line([cx+200, cy+90, cx+160, cy+20], fill=(180, 180, 190), width=8)  # hanger wire
    pad = (255, 190, 90)
    if stage in ("pads", "compress", "new"):
        d.rectangle([cx+60, cy-100, cx+80, cy+100], fill=pad)
        d.rectangle([cx+215, cy-100, cx+235, cy+100], fill=pad)
    if stage == "compress":
        d.rectangle([cx+235, cy-18, cx+330, cy+18], fill=(190, 190, 200))
        d.rectangle([cx+330, cy-40, cx+350, cy+40], fill=(190, 190, 200))

SLIDES = [
 ("How to Change Car Brakes", ["Disc brake pads: the most common job", "Takes 1 to 2 hours per axle", "Always do both wheels on an axle"], None,
  "In this video you will learn how to change the brake pads on almost any car. We will cover disc brakes, which are on the front of nearly every vehicle and on the back of most. Always replace pads on both wheels of an axle at the same time."),
 ("Tools and Parts", ["Jack and 2 jack stands", "Lug wrench and torque wrench", "Socket set and C-clamp", "Brake cleaner and brake grease", "New pads, plus rotors if worn"], None,
  "Gather your tools. You need a jack, two jack stands, a lug wrench, a socket set, a C clamp or brake piston tool, brake cleaner, and high temperature brake grease. Buy the pads that match your exact make, model, and year."),
 ("Safety First", ["Park on flat, solid ground", "Chock the wheels, handbrake on", "NEVER work under a car held only by a jack", "Wear gloves and eye protection", "Never blow brake dust with your mouth or air"], "jack",
  "Safety first. Park on flat, level ground and chock the wheels that stay on the ground. Never rely on a jack alone. Always support the car on jack stands. Brake dust is harmful, so wear gloves and a mask, and clean it with brake cleaner, not compressed air."),
 ("1. Loosen and Lift", ["Loosen lug nuts a half turn", "Jack at the manufacturer's lift point", "Place jack stands under the frame", "Remove the lug nuts and the wheel"], "wheel",
  "Step one. With the car on the ground, break the lug nuts loose about half a turn. Then lift the car at the jacking point shown in your owner's manual, set it on jack stands, and take the wheel off."),
 ("2. Remove the Caliper", ["Find the two caliper slide bolts", "Remove them and lift the caliper off", "Hang it with a wire or hook", "NEVER let it dangle by the brake hose"], "caliper_off",
  "Step two. Locate the two bolts on the back of the caliper and remove them. Slide the caliper off the rotor. Hang it from the suspension with a wire or bungee cord. Never let it hang from the rubber brake hose, because that can damage it."),
 ("3. Remove the Old Pads", ["Slide out the old pads", "Note how the clips and shims sit", "Check the rotor for grooves or warping", "Replace the rotor if worn or below minimum thickness"], "pads",
  "Step three. Slide the old pads out and take a photo of how the clips and shims are arranged. Inspect the rotor. If it has deep grooves, a lip, or is thinner than the minimum marked on it, replace it."),
 ("4. Compress the Piston", ["Open the brake fluid cap to avoid overflow", "Use a C-clamp against the old pad", "Press the piston slowly all the way in", "Clean the bracket and add brake grease"], "compress",
  "Step four. The piston must be pushed back to make room for the thicker new pads. Place the old pad against the piston and slowly tighten a C clamp. Watch the fluid reservoir so it does not overflow. Then clean the bracket and apply a little brake grease to the contact points. Keep grease off the pad surface and the rotor."),
 ("5. Install New Pads", ["Fit new clips and pads", "Pad friction material faces the rotor", "Refit the caliper over the pads", "Tighten slide bolts to spec"], "new",
  "Step five. Fit the new clips and pads, with the friction material facing the rotor. Slide the caliper back over the pads and tighten the bolts to the torque listed in your repair manual. If you changed the rotor, clean it with brake cleaner first."),
 ("6. Wheel On and Test", ["Mount the wheel, hand-tighten the nuts", "Lower the car, then torque in a star pattern", "Pump the brake pedal until it feels firm", "Top up brake fluid if needed"], "wheel",
  "Step six. Put the wheel on, lower the car, and tighten the lug nuts to specification in a star pattern. Before moving, pump the brake pedal several times until it feels firm. The first presses will go to the floor because the piston needs to seat. Check the fluid level and top up if needed."),
 ("7. Bed In the Brakes", ["Do 5 to 6 moderate stops from 35 mph", "Avoid hard stops for the first 200 miles", "Listen for grinding or squealing", "Re-check lug nut torque after 50 miles"], None,
  "Finally, bed in your new pads. Make five or six moderate stops from about thirty five miles per hour, without coming to a complete halt. Avoid hard braking for the first couple hundred miles, and re-check your lug nuts after fifty miles."),
 ("Rear Drum Brakes?", ["Same safety steps and wheel removal", "Remove the drum, then springs and shoes", "Take photos before disassembly", "If unsure, have a professional do it"], None,
  "Some cars have drum brakes on the rear. The process is similar, but you remove the drum and swap out the shoes and springs. Take lots of photos first. If you are ever unsure, let a professional handle it, because brakes are critical to your safety."),
 ("Thanks for Watching", ["Always check your manual for specs", "Brakes are a safety system: no shortcuts", "Drive safe!"], None,
  "That is how to change your car's brakes. Always follow your vehicle's manual for torque values and procedures. Brakes are a safety system, so never cut corners. Thanks for watching, and drive safe."),
]

def render(i, title, bullets, stage, n):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=ACC)
    d.rectangle([0, 0, int(W * (i + 1) / n), 10], fill=WARN)
    big = font(FB, 52 if i not in (0, n-1) else 68)
    d.text((60, 60), title, font=big, fill=ACC)
    x_text_w = 640 if stage else 1100
    y = 190
    bf = font(FR, 31)
    for b in bullets:
        lines = textwrap.wrap(b, width=34 if stage else 60)
        d.ellipse([60, y+12, 76, y+28], fill=ACC)
        for ln in lines:
            d.text((95, y), ln, font=bf, fill=FG)
            y += 44
        y += 20
    if stage:
        diagram(d, stage)
    d.text((60, H - 50), "Car brake pad replacement guide", font=font(FR, 20), fill=(120, 130, 150))
    p = os.path.join(WORK, f"s{i:02d}.png")
    img.save(p)
    return p

def run(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

clips = []
for i, (t, b, st, narr) in enumerate(SLIDES):
    png = render(i, t, b, st, len(SLIDES))
    wav = os.path.join(WORK, f"s{i:02d}.wav")
    run("espeak-ng", "-v", "en-us", "-s", "150", "-w", wav, narr)
    mp4 = os.path.join(WORK, f"s{i:02d}.mp4")
    run("ffmpeg", "-y", "-loop", "1", "-i", png, "-i", wav, "-af", "apad=pad_dur=0.8",
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "24",
        "-c:a", "aac", "-b:a", "128k", "-shortest", mp4)
    clips.append(mp4)

lst = os.path.join(WORK, "list.txt")
with open(lst, "w") as f:
    f.writelines(f"file '{c}'\n" for c in clips)
final = os.path.join(OUT, "how_to_change_car_brakes.mp4")
run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final)
print(final)
