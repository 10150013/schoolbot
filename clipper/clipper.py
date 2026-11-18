#!/usr/bin/env python3
"""Clipper AI: turn a stream/VOD into finished vertical clips.

  python clipper.py <youtube-url-or-local-video> [--game "Kai playing Elden Ring"]
                    [--credit "@streamer"] [--count 5] [--out clips]

Pipeline: download -> transcript (YouTube captions, else Whisper) ->
Claude picks moments -> ffmpeg cuts 9:16 clips with burned captions ->
clips.md with hook titles and post text.

Needs: ffmpeg on PATH, ANTHROPIC_API_KEY set, `pip install -r requirements.txt`.
Only clip streams you own or have permission to clip, and credit the streamer.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

MODEL = "claude-sonnet-5-5"

PROMPT = """You're an editor for a short-form clipping channel. Below is a livestream transcript, one segment per line as [seconds] text. Find the {n} best moments to post as vertical clips on TikTok, Reels and Shorts.

A good moment works on its own with no context: a reaction with a clear cause, a punchline, a fail, a clutch play, a story with an ending, or a hot take. Loud isn't the same as good. Skip anything that needs earlier context. Start a few seconds before the setup and end just after the payoff; 15 to 45 seconds. Never overlap moments.

{context}
Return ONLY a JSON array, strongest first, each item:
{{"start": seconds, "end": seconds, "summary": "one line", "why": "one line", "title": "2-6 WORDS IN CAPITALS, a hook that doesn't spoil or overclaim", "caption": "post text under 150 chars, hooks differently from the title, no promises the clip doesn't deliver", "hashtags": ["3 to 5"]}}

Transcript:
{transcript}"""


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def download(src, work):
    if Path(src).exists():
        return Path(src), None
    work.mkdir(parents=True, exist_ok=True)
    run(["yt-dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4",
         "--write-auto-subs", "--sub-langs", "en.*", "--sub-format", "json3",
         "-o", str(work / "video.%(ext)s"), src])
    subs = next(work.glob("video*.json3"), None)
    return work / "video.mp4", subs


def segs_from_json3(path):
    data = json.loads(Path(path).read_text())
    out = []
    for ev in data.get("events", []):
        text = "".join(s.get("utf8", "") for s in ev.get("segs", [])).replace("\n", " ").strip()
        if text:
            t = ev["tStartMs"] / 1000
            out.append({"start": t, "end": t + ev.get("dDurationMs", 2000) / 1000, "text": text})
    return out


def segs_from_whisper(video):
    from faster_whisper import WhisperModel
    model = WhisperModel("small", compute_type="int8")
    segs, _ = model.transcribe(str(video), vad_filter=True)
    return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segs]


def find_moments(segs, n, game):
    import anthropic
    lines = "\n".join(f"[{int(s['start'])}] {s['text']}" for s in segs)
    ctx = f"Context: {game}\n" if game else ""
    # Long streams: ask per chunk, then take the best overall.
    chunk, chunks, size = [], [], 0
    for ln in lines.split("\n"):
        chunk.append(ln); size += len(ln)
        if size > 150_000:
            chunks.append("\n".join(chunk)); chunk, size = [], 0
    if chunk:
        chunks.append("\n".join(chunk))
    client = anthropic.Anthropic()
    found = []
    for part in chunks:
        msg = client.messages.create(model=MODEL, max_tokens=4000, messages=[
            {"role": "user", "content": PROMPT.format(n=n, context=ctx, transcript=part)}])
        text = msg.content[0].text
        found += json.loads(text[text.index("["): text.rindex("]") + 1])
    if len(chunks) > 1:
        msg = client.messages.create(model=MODEL, max_tokens=4000, messages=[{"role": "user", "content":
            f"Of these clip candidates, return the {n} strongest as the same JSON array, nothing else.\n"
            + json.dumps(found)}])
        text = msg.content[0].text
        found = json.loads(text[text.index("["): text.rindex("]") + 1])
    return found[:n]


def srt_time(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s % 1) * 1000):03}"


def write_srt(segs, start, end, path):
    rows, i = [], 1
    for s in segs:
        if s["end"] > start and s["start"] < end:
            a, b = max(s["start"], start) - start, min(s["end"], end) - start
            rows.append(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{s['text']}\n")
            i += 1
    Path(path).write_text("\n".join(rows))
    return bool(rows)


def cut(video, m, segs, out_dir, idx):
    start, end = float(m["start"]), float(m["end"])
    base = out_dir / f"{idx:02}_{re.sub(r'[^A-Za-z0-9]+', '-', m['title']).strip('-')[:40]}"
    srt = base.with_suffix(".srt")
    has_subs = write_srt(segs, start, end, srt)
    # 9:16: blurred full frame behind, sharp frame centered on top.
    vf = ("[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920,boxblur=30[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
    if has_subs:
        style = "Alignment=2,MarginV=260,FontSize=14,Bold=1,Outline=2"
        vf += f",subtitles={srt.name}:force_style='{style}'"
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-to", str(end), "-i", str(video),
         "-filter_complex", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "20",
         "-c:a", "aac", str(base.with_suffix(".mp4").name)], cwd=out_dir)
    return base.with_suffix(".mp4")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--game", default="")
    ap.add_argument("--credit", default="")
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--out", default="clips")
    a = ap.parse_args()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY first.")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    video, subs = download(a.source, out / "_work")
    video = video.resolve()
    print("Transcript...")
    segs = segs_from_json3(subs) if subs else segs_from_whisper(video)
    print(f"Finding moments in {len(segs)} segments...")
    moments = find_moments(segs, a.count, a.game)
    report = ["# Clips\n"]
    for i, m in enumerate(moments, 1):
        print(f"Cutting {i}/{len(moments)}: {m['title']}")
        f = cut(video, m, segs, out.resolve(), i)
        credit = f"Clip from {a.credit}'s stream" if a.credit else ""
        tags = " ".join("#" + h.lstrip("#") for h in m.get("hashtags", []))
        report.append(f"## {i}. {m['title']}\n`{f.name}` ({m['start']:.0f}s to {m['end']:.0f}s)\n\n"
                      f"- What: {m['summary']}\n- Why: {m['why']}\n\n"
                      f"Post text:\n\n{m['caption']}\n{credit}\n{tags}\n")
    (out / "clips.md").write_text("\n".join(report))
    print(f"Done. Watch each clip before posting. See {out / 'clips.md'}")


if __name__ == "__main__":
    main()
