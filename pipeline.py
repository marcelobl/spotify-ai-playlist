"""
Pipeline runners for web interface.
Wraps classify_songs and sync_to_spotify in background threads
with queue-based SSE event streaming.
"""

import json
import queue
import threading


class PipelineRunner:
    """Runs the classification pipeline in a background thread, yielding SSE events."""

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None
        self.result = None

    def start(self, naming_mode="descriptive", sp=None):
        def _run():
            try:
                from classify_songs import run_pipeline
                result = run_pipeline(
                    naming_mode=naming_mode,
                    progress_callback=self._on_progress,
                    sp=sp,
                )
                self.result = result
                self._queue.put({"type": "complete", "data": self._serialize(result)})
            except Exception as e:
                self._queue.put({"type": "error", "message": str(e)})
            finally:
                self._queue.put(None)  # sentinel

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def _on_progress(self, step, total_steps, label, detail):
        self._queue.put({
            "type": "progress",
            "step": step,
            "total_steps": total_steps,
            "label": label,
            "detail": detail or "",
        })

    def _serialize(self, playlists):
        """Convert playlists to JSON-safe format."""
        serialized = []
        for p in playlists:
            serialized.append({
                "name": p["name"],
                "description": p.get("description", ""),
                "track_count": p["track_count"],
                "track_uris": p["track_uris"],
                "top_genres": [(g, c) for g, c in p.get("top_genres", [])],
                "audio_profile": {k: round(v, 3) for k, v in p.get("audio_profile", {}).items()},
            })
        return serialized

    def events(self):
        """Generator that yields SSE-formatted events."""
        while True:
            item = self._queue.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"


class SyncRunner:
    """Runs Spotify sync in a background thread, yielding SSE events."""

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None

    def start(self, playlists_data, selected_names, sp):
        def _run():
            try:
                from sync_to_spotify import sync_selected
                sync_selected(
                    playlists_data=playlists_data,
                    selected_names=selected_names,
                    sp=sp,
                    progress_callback=self._on_progress,
                )
                self._queue.put({"type": "complete"})
            except Exception as e:
                self._queue.put({"type": "error", "message": str(e)})
            finally:
                self._queue.put(None)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def _on_progress(self, playlist_name, index, total):
        self._queue.put({
            "type": "progress",
            "playlist_name": playlist_name,
            "index": index,
            "total": total,
        })

    def events(self):
        while True:
            item = self._queue.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"
