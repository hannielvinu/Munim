# Rebuild narration and video
Install requirements, run the local app at http://127.0.0.1:8000, then run:
`python scripts/make_video.py`

Uses edge-tts en-IN-NeerjaNeural at -5% rate, sentence audio cache, natural pauses, section timing and loudness-normalised audio. No API key is needed. ffmpeg comes from imageio-ffmpeg; ffprobe is discovered or installed into ignored tmp/media through npm. Never use a formant fallback. A failed neural voice build emits a clearly documented captioned silent fallback and can be retried later.

