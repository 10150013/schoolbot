#!/usr/bin/env python3
"""Live Clipper: watch Twitch streamers live and clip when chat goes crazy.

  python live.py kaicenat xqc --game "GTA 6" --out clips

For each channel it (1) records the stream into a rolling 5-minute buffer,
(2) reads chat and watches the message rate, and (3) when chat spikes, saves
the last ~35s plus 10s after as a vertical 9:16 clip, with a title and post
text written from what chat said.

Needs ffmpeg, streamlink, and ANTHROPIC_API_KEY (optional: without it, titles
are generic). Only clip streamers who allow it, and credit them.
"""
import argparse, collections, json, os, re, socket, subprocess, threading, time
from pathlib import Path

MODEL = "claude-sonnet-5-5"
# Facecam boxes (x,y,w,h as fractions of the frame) for streamers whose layout is known.
CAM_PRESETS = {"caseoh_": "0,0.12,0.21,0.28"}
HYPE = re.compile(r"\b(LUL|OMEGALUL|KEKW|LMAO|POG\w*|W|WTF|NO WAY|CLIP IT|CLIP|\?\?+|HOLY|INSANE)\b", re.I)


class SpikeDetector:
    """Flags a spike when the last 10s of chat is well above the recent norm."""

    def __init__(self, factor=3.0, min_msgs=25, cooldown=90, bucket=10):
        self.factor, self.min_msgs, self.cooldown, self.bucket = factor, min_msgs, cooldown, bucket
        self.buckets = collections.deque(maxlen=30)  # last 5 minutes of 10s buckets
        self.cur, self.cur_start, self.last_fire = 0, None, 0

    def add(self, now, weight=1.0):
        """Feed one chat message; returns True if this should trigger a clip."""
        if self.cur_start is None:
            self.cur_start = now
        fired = False
        while now - self.cur_start >= self.bucket:
            fired = self._close() or fired
            self.cur_start += self.bucket
        self.cur += weight
        return fired

    def _close(self):
        count, self.cur = self.cur, 0
        base = sum(self.buckets) / len(self.buckets) if len(self.buckets) >= 6 else None
        self.buckets.append(count)
        now = self.cur_start + self.bucket
        if base is not None and count >= self.min_msgs and count >= self.factor * max(base, 1) \
                and now - self.last_fire > self.cooldown:
            self.last_fire = now
            return True
        return False


def chat_loop(channel, on_msg):
    while True:
        try:
            s = socket.create_connection(("irc.chat.twitch.tv", 6667), timeout=300)
            s.sendall(f"NICK justinfan{int(time.time()) % 90000 + 1000}\r\nJOIN #{channel}\r\n".encode())
            buf = ""
            while True:
                data = s.recv(4096).decode("utf8", "ignore")
                if not data:
                    break
                buf += data
                *lines, buf = buf.split("\r\n")
                for ln in lines:
                    if ln.startswith("PING"):
                        s.sendall(b"PONG :tmi.twitch.tv\r\n")
                    elif "PRIVMSG" in ln:
                        m = re.match(r"(?:@\S+ )?:(\w+)!", ln)
                        on_msg(m.group(1) if m else "chat", ln.split("PRIVMSG", 1)[1].split(":", 1)[1])
        except OSError:
            pass
        time.sleep(5)


def record(channel, buf_dir):
    """Rolling buffer: 5s .ts segments named by start epoch. Restarts if the stream drops."""
    buf_dir.mkdir(parents=True, exist_ok=True)
    while True:
        sl = subprocess.Popen(["streamlink", f"twitch.tv/{channel}", "best", "-O"],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-c", "copy", "-f", "segment",
                        "-segment_time", "5", "-strftime", "1", "-reset_timestamps", "1",
                        str(buf_dir / "%s.ts")], stdin=sl.stdout)
        sl.kill()
        time.sleep(15)  # offline or dropped; try again


def prune(buf_dir, keep=330):
    while True:
        time.sleep(30)
        for f in buf_dir.glob("*.ts"):
            if time.time() - int(f.stem) > keep:
                f.unlink(missing_ok=True)


def ass_escape(t):
    return t.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02}:{t % 60:05.2f}"


def chat_ass(log, start, length, path, lines=13):
    """Subtitle file that replays chat: each new message pushes the last few lines up."""
    msgs = [(ts - start, u, tx) for ts, u, tx in log if 0 <= ts - start <= length]
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
            "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,"
            "Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,"
            "MarginV,Encoding\nStyle: Chat,Arial,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,"
            "2,0,1,30,30,40,1\n\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n")
    palette = ["FF7F50", "1E90FF", "32CD32", "FF69B4", "FFD700", "9ACD32", "BA55D3", "00CED1"]
    nl = chr(92) + "N"

    def line(user, text):
        c = palette[sum(map(ord, user)) % len(palette)]
        bgr = c[4:6] + c[2:4] + c[0:2]  # ASS colours are BGR
        return "{%sc&H%s&%sb1}%s{%sc&HFFFFFF&%sb0}: %s" % (
            chr(92), bgr, chr(92), ass_escape(user), chr(92), chr(92), ass_escape(text[:48]))

    rows = []
    for i, (rt, _, _) in enumerate(msgs):
        end = msgs[i + 1][0] if i + 1 < len(msgs) else length
        body = nl.join(line(u, t) for _, u, t in msgs[max(0, i - lines + 1): i + 1])
        rows.append(f"Dialogue: 0,{ass_time(rt)},{ass_time(end)},Chat,,0,0,0,,{body}")
    Path(path).write_text(head + "\n".join(rows) + "\n")
    return bool(msgs)


def layout(cam):
    """Facecam (reaction) on top, gameplay in the middle, room for chat at the bottom."""
    if not cam:
        return ("[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,boxblur=30[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
    x, y, w, h = cam
    return (f"[0:v]split[g][c];[g]scale=1080:608[game];"
            f"[c]crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},scale=1080:640:force_original_aspect_ratio=increase,"
            f"crop=1080:640[cam];[cam][game]vstack=inputs=2,pad=1080:1920:0:0:black")


def make_clip(channel, t, buf_dir, out_dir, before, after, chatlog, game, credit, cam, show_chat):
    time.sleep(after + 6)  # let the payoff and the last segment finish writing
    segs = sorted(f for f in buf_dir.glob("*.ts") if t - before - 5 <= int(f.stem) <= t + after)
    segs = segs[:-1] if len(segs) > 1 and time.time() - int(segs[-1].stem) < 6 else segs
    if not segs:
        return print(f"[{channel}] no footage buffered, skipped")
    log = list(chatlog)
    window = [x for x in log if t - before <= x[0] <= t + after]
    texts = [x[2] for x in log if t - 30 <= x[0] <= t + 2]
    title, caption, tags = describe(channel, texts, game)
    slug = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")[:40]
    stamp = time.strftime("%H%M%S", time.localtime(t))
    name = out_dir / f"{channel}_{stamp}_{slug}.mp4"
    lst = buf_dir / f"concat_{t}.txt"
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in segs))
    vf = layout(cam)
    ass = buf_dir / f"chat_{t}.ass"
    if show_chat and chat_ass(window, t - before, before + after, ass):
        vf += f",subtitles={ass.name}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-filter_complex", vf, "-ss", str(max(0, t - before - int(segs[0].stem))),
                    "-t", str(before + after), "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                    "-c:a", "aac", str(name.resolve())], check=True, cwd=buf_dir)
    lst.unlink(missing_ok=True); ass.unlink(missing_ok=True)
    credit_line = f"Clip from {credit or '@' + channel}'s stream"
    with open(out_dir / "clips.md", "a") as f:
        f.write(f"## {title}\n`{name.name}` ({channel}, {time.strftime('%H:%M:%S', time.localtime(t))})\n\n"
                f"{caption}\n{credit_line}\n{tags}\n\nChat said: {' | '.join(texts[-8:])}\n\n")
    print(f"[{channel}] clip saved: {name.name}  <- {title}")


def describe(channel, msgs, game):
    fallback = ("CHAT WENT CRAZY", f"Chat lost it on {channel}'s stream", "#clips #gaming")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return fallback
    try:
        import anthropic
        prompt = (f"Chat on {channel}'s {game or 'stream'} exploded. Here are the chat messages from the moment:\n"
                  + "\n".join(msgs[-40:]) + "\n\nWrite a clip hook title (2-6 words, ALL CAPS, no spoilers, nothing the "
                  "chat doesn't support), a post caption under 150 chars, and 3-5 hashtags. Return only JSON: "
                  '{"title":"","caption":"","hashtags":""}')
        r = anthropic.Anthropic().messages.create(model=MODEL, max_tokens=500, messages=[
            {"role": "user", "content": prompt}]).content[0].text
        d = json.loads(r[r.index("{"): r.rindex("}") + 1])
        return d["title"], d["caption"], d["hashtags"]
    except Exception:
        return fallback


def watch(channel, a, out_dir, camspec):
    buf = Path(a.buffer) / channel
    det = SpikeDetector(a.factor, a.min_msgs, a.cooldown)
    chatlog = collections.deque(maxlen=8000)
    cam = None if camspec == "none" else tuple(float(v) for v in camspec.split(","))

    def on_msg(user, text):
        now = time.time()
        chatlog.append((now, user, text.strip()))
        if det.add(now, 2.0 if HYPE.search(text) else 1.0):
            print(f"[{channel}] chat spike!")
            threading.Thread(target=make_clip, daemon=True, args=(
                channel, int(now), buf, out_dir, a.before, a.after, chatlog, a.game, a.credit,
                cam, not a.no_chat)).start()

    threading.Thread(target=record, args=(channel, buf), daemon=True).start()
    threading.Thread(target=prune, args=(buf,), daemon=True).start()
    chat_loop(channel, on_msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("channels", nargs="+")
    ap.add_argument("--game", default="")
    ap.add_argument("--credit", default="", help="credit line name; defaults to @channel")
    ap.add_argument("--before", type=int, default=35, help="seconds before the spike")
    ap.add_argument("--after", type=int, default=10, help="seconds after the spike")
    ap.add_argument("--factor", type=float, default=3.0, help="spike = this many times normal chat rate")
    ap.add_argument("--min-msgs", type=float, default=25, help="minimum weighted msgs per 10s to count")
    ap.add_argument("--cooldown", type=int, default=90, help="seconds between clips per channel")
    ap.add_argument("--cam", default=None,
                    help="facecam box x,y,w,h as fractions of the frame, for all channels; 'none' = no facecam. "
                         "Per channel: name@x,y,w,h or name@none")
    ap.add_argument("--no-chat", action="store_true", help="don't burn the live chat into the clip")
    ap.add_argument("--buffer", default="_buffer")
    ap.add_argument("--out", default="clips")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    print("Watching:", ", ".join(a.channels), "(Ctrl+C to stop)")
    for ch in a.channels:
        name, _, spec = ch.lower().lstrip("#").partition("@")
        spec = spec or a.cam or CAM_PRESETS.get(name, "none")
        threading.Thread(target=watch, args=(name, a, out, spec), daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
