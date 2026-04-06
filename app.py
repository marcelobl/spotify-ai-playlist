"""
Web interface for Spotify Playlist Classifier.
FastAPI server with SSE streaming for real-time progress.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from pipeline import PipelineRunner, SyncRunner

load_dotenv()

app = FastAPI(title="Spotify Playlist Classifier")

STATIC_DIR = Path(__file__).parent / "static"
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
TOKEN_PATH = CACHE_DIR / ".spotify_token"

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
WEB_REDIRECT_URI = os.getenv("SPOTIFY_WEB_REDIRECT_URI", "http://127.0.0.1:5000/api/auth/callback")

SCOPES = [
    "playlist-modify-public",
    "playlist-modify-private",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-read-private",
    "user-library-read",
]

# Single-user state
_pipeline_runner: PipelineRunner | None = None
_sync_runner: SyncRunner | None = None
_last_results: list | None = None


def _get_auth_manager():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=WEB_REDIRECT_URI,
        scope=" ".join(SCOPES),
        cache_path=str(TOKEN_PATH),
        open_browser=False,
    )


def _get_spotify_client():
    auth = _get_auth_manager()
    token_info = auth.get_cached_token()
    if not token_info:
        return None
    return spotipy.Spotify(auth_manager=auth)


# ─── Static ─────────────────────────────────────────────────────

@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


# ─── Auth ────────────────────────────────────────────────────────

@app.get("/api/auth/status")
async def auth_status():
    sp = _get_spotify_client()
    if sp:
        try:
            user = sp.current_user()
            return {"authenticated": True, "user": user.get("display_name", user["id"])}
        except Exception:
            pass
    return {"authenticated": False, "user": None}


@app.get("/api/auth/login")
async def auth_login():
    auth = _get_auth_manager()
    url = auth.get_authorize_url()
    return RedirectResponse(url)


@app.get("/api/auth/callback")
async def auth_callback(code: str):
    auth = _get_auth_manager()
    auth.get_access_token(code)
    return RedirectResponse("/#authenticated")


@app.post("/api/auth/logout")
async def auth_logout():
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()
    return {"ok": True}


# ─── Classify ────────────────────────────────────────────────────

@app.post("/api/classify")
async def classify(request: Request):
    global _pipeline_runner, _last_results
    body = await request.json()
    naming_mode = body.get("naming_mode", "descriptive")

    _pipeline_runner = PipelineRunner()
    _pipeline_runner.start(naming_mode=naming_mode)
    _last_results = None
    return JSONResponse({"status": "started"}, status_code=202)


@app.get("/api/classify/stream")
async def classify_stream():
    if not _pipeline_runner:
        return JSONResponse({"error": "No pipeline running"}, status_code=404)

    def _generate():
        global _last_results
        for event in _pipeline_runner.events():
            yield event
        if _pipeline_runner.result:
            _last_results = _pipeline_runner.result

    return StreamingResponse(_generate(), media_type="text/event-stream")


# ─── Sync ────────────────────────────────────────────────────────

@app.post("/api/sync")
async def sync(request: Request):
    global _sync_runner
    body = await request.json()
    selected_names = body.get("playlist_names", [])

    if not _last_results:
        return JSONResponse({"error": "No classification results available"}, status_code=400)

    sp = _get_spotify_client()
    if not sp:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    # Build playlists data in the format sync_selected expects
    playlists_data = []
    for p in _last_results:
        playlists_data.append({
            "name": p["name"],
            "description": p.get("description", ""),
            "track_uris": p["track_uris"],
        })

    _sync_runner = SyncRunner()
    _sync_runner.start(playlists_data, selected_names, sp)
    return JSONResponse({"status": "started"}, status_code=202)


@app.get("/api/sync/stream")
async def sync_stream():
    if not _sync_runner:
        return JSONResponse({"error": "No sync running"}, status_code=404)

    return StreamingResponse(_sync_runner.events(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
