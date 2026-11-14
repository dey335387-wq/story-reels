"""Gemini TTS: python gemini_tts.py <in.gtts> <out.wav>
in.gtts: line1 voice (e.g. Charon), line2 style prompt, rest = text. Needs GEMINI_API_KEY env."""
import sys, os, json, base64, wave, time, urllib.request, urllib.error
src, out = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().split("\n")
voice, style, text = lines[0].strip(), lines[1].strip(), "\n".join(lines[2:]).strip()
model = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
body = {"contents": [{"parts": [{"text": f"{style}\n\n{text}"}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    data=json.dumps(body).encode(), headers={"Content-Type": "application/json",
    "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
pcm = None
for attempt in range(7):  # free tier: 429 rate limits + occasional empty candidates -> retry with backoff
    try:
        data = json.load(urllib.request.urlopen(req, timeout=300))
        pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
        break
    except (urllib.error.HTTPError, KeyError, IndexError) as e:
        print("retry", attempt, repr(e)[:200]); time.sleep(30 + 20 * attempt)
if pcm is None: sys.exit("TTS failed after retries")
with wave.open(out, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
print("ok", len(pcm) / 48000, "sec")
