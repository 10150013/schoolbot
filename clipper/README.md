# Clipper AI

Give it a stream or VOD, get finished vertical clips plus titles and post text.

```
pip install -r requirements.txt   # also needs ffmpeg
export ANTHROPIC_API_KEY=...
python clipper.py "https://youtube.com/watch?v=..." --length 45 --game "Kai playing Elden Ring" --credit "@kai"
```

Output goes to `clips/`: one 1080x1920 mp4 per moment (blurred background, captions burned in)
and `clips.md` with hook titles, post text, credit line and hashtags.

- Works on YouTube links or a local video file. No YouTube captions? It transcribes with Whisper.
- Long streams are read in chunks, then the best moments overall are picked.
- It can't see or hear the video, only read the transcript. Watch every clip before posting.
- Only clip streams you own or have permission to clip, and credit the streamer.
