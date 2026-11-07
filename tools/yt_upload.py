"""Upload a video to YouTube with the Data API v3 (free; no Metricool needed).
Job file inbox/<name>.yt (JSON): {"file": "out/x.mp4", "title": "...", "description": "...", "tags": [...],
  "categoryId": "25", "publishAt": "2026-11-08T13:00:00Z" (optional -> scheduled, else public now)}
Secrets: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (OAuth, scope youtube.upload).
Writes result JSON to media/yt/<name>.json (videoId, url, status)."""
import sys, os, json, requests
job = json.load(open(sys.argv[1])); out = sys.argv[2]
tok = requests.post("https://oauth2.googleapis.com/token", data={
    "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
    "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}, timeout=60).json()
if "access_token" not in tok:
    json.dump({"error": tok}, open(out, "w")); print("token error", tok); sys.exit(1)
H = {"Authorization": "Bearer " + tok["access_token"]}
status = {"privacyStatus": job.get("privacy") or ("private" if job.get("publishAt") else "public"), "selfDeclaredMadeForKids": False}
if job.get("publishAt"): status["publishAt"] = job["publishAt"]
meta = {"snippet": {"title": job["title"][:100], "description": job.get("description", "")[:4900],
                    "tags": job.get("tags", []), "categoryId": job.get("categoryId", "25")}, "status": status}
data = open(job["file"], "rb").read()
r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                  headers={**H, "Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Type": "video/mp4",
                           "X-Upload-Content-Length": str(len(data))}, data=json.dumps(meta), timeout=60)
if r.status_code != 200:
    json.dump({"error": r.text}, open(out, "w")); print("init error", r.status_code, r.text); sys.exit(1)
up = requests.put(r.headers["Location"], headers={**H, "Content-Type": "video/mp4"}, data=data, timeout=900)
res = up.json()
vid = res.get("id")
json.dump({"videoId": vid, "url": f"https://www.youtube.com/shorts/{vid}" if vid else None,
           "status": res.get("status"), "error": None if vid else res}, open(out, "w"), indent=1)
print("ok" if vid else "upload error", vid)
sys.exit(0 if vid else 1)
