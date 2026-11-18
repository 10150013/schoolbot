# Clipper AI

Give it a stream or VOD, get finished vertical clips plus titles and post text.

```
cd clipper && pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
python clipper.py "<url>" --credit "@streamer"
```

Output goes to `clips/`: one 1080x1920 mp4 per moment (blurred background, captions burned in)
and `clips.md` with hook titles, post text, credit line and hashtags.

- Works on YouTube links or a local video file. No YouTube captions? It transcribes with Whisper.
- Long streams are read in chunks, then the best moments overall are picked.
- It can't see or hear the video, only read the transcript. Watch every clip before posting.
- Only clip streams you own or have permission to clip, and credit the streamer.

## Live mode: clip when chat goes crazy

```
python live.py kaicenat xqc --game "GTA 6"
```

Watches Twitch channels live (needs `streamlink`, installed by requirements). For each one it keeps a
rolling 5-minute recording and reads chat. When chat's message rate jumps to 3x normal (hype words like
LUL, KEKW, POG and `??` count double), it saves the last 35s plus 10s after as a 1080x1920 clip in `clips/`,
and appends a title, post text and credit line (written from what chat said) to `clips/clips.md`.

Tune with `--factor`, `--min-msgs`, `--cooldown`, `--before`, `--after`. Leave it running; Ctrl+C stops it.
Titles need `ANTHROPIC_API_KEY`; without it clips still save with a generic title.
Big streamers' chats move fast, so the default `--min-msgs 25` suits them; lower it for smaller channels.
Check every clip before posting, and only clip streamers who allow it.

### Clip layout (live mode)

Facecam on top (his reaction), gameplay in the middle, live chat replaying at the bottom.
The facecam box is set with `--cam x,y,w,h` as fractions of the frame; the default fits CaseOh.
`--cam none` skips the facecam, and `--no-chat` leaves the chat off.
