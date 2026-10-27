#!/usr/bin/env python3
"""Render one episode:  render.py [preview|full] episodes/ep02_air_filter.py"""
import os, sys, importlib.util, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine
from PIL import Image

def load(path):
    spec = importlib.util.spec_from_file_location("episode", path)
    m = importlib.util.module_from_spec(spec); sys.modules["episode"] = m; spec.loader.exec_module(m)
    return m

if __name__ == "__main__":
    mode, path = sys.argv[1], sys.argv[2]
    ep = load(path); engine.SCENES = ep.SCENES
    W, H, FPS = engine.W, engine.H, engine.FPS
    out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True)
    total = engine.init(); TL = engine.TL
    print(ep.NAME, "total %.1fs" % total, [(round(s["start"], 1), round(s["end"], 1)) for s in TL], flush=True)
    if mode == "preview":
        tiles = []
        for sc in TL:
            for f in (.25, .8):
                tt = sc["start"] + max(.9, sc["dur"] * f) if f < .5 else sc["start"] + sc["dur"] * f
                tiles.append(Image.frombytes("RGB", (W, H), engine.render_frame(int(tt * FPS))).resize((270, 480)))
        for part in range(0, len(tiles), 8):
            sheet = Image.new("RGB", (270 * min(8, len(tiles) - part), 480))
            for k, im in enumerate(tiles[part:part + 8]): sheet.paste(im, (k * 270, 0))
            sheet.save(os.path.join(engine.BUILD, f"sheet_{ep.NAME}_{part // 8}.png"))
        sys.exit()
    audio = engine.make_audio(TL, total)
    nframes = int(total * FPS)
    mp4 = os.path.join(out, ep.NAME + ".mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", f"{nframes / FPS:.3f}", mp4], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, fr in enumerate(pool.imap(engine.render_frame, range(nframes), chunksize=6)):
            ff.stdin.write(fr)
    ff.stdin.close(); ff.wait()
    Image.frombytes("RGB", (W, H), engine.render_frame(int(1.0 * FPS))).save(os.path.join(out, ep.NAME + "_cover.png"))
    open(os.path.join(out, ep.NAME + "_caption.txt"), "w").write(ep.CAPTION.strip() + "\n")
    print("wrote", mp4, flush=True)
