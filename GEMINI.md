# Spotify Liked Songs Classifier

A sophisticated Python-based tool for organizing Spotify "Liked Songs" into cohesive, thematic playlists using hybrid genre-embedding and audio-feature clustering.

## Project Overview

This project analyzes a user's Spotify library (fetched directly via API) and automatically groups tracks into playlists. Unlike simple genre-based sorting, it uses a hybrid approach:
- **Genre Semantics:** High-dimensional embeddings capture the relationship between musical genres.
- **Audio Features:** Technical attributes like danceability, energy, and acousticness ensure a consistent "vibe" within each playlist.

The system is designed to handle large libraries (10k+ tracks) and creates 50+ distinct, named playlists.

## Main Technologies

- **Python 3.12+**
- **Spotify API:** `spotipy` (OAuth2, Tracks, Audio Features, Artists)
- **Data Science:** `pandas`, `numpy`
- **Machine Learning:** `scikit-learn` (StandardScaler, NearestNeighbors)
- **Dimensionality Reduction:** `umap-learn`
- **Clustering:** `hdbscan`
- **Visualization:** `plotly` (interactive HTML diagnostics)

## Architecture & Workflow

1.  **Data Loading:** Fetches Liked Songs directly from Spotify (including audio features and artist genres).
2.  **Genre Backfilling:** Intelligently fills missing genre data by looking at other tracks from the same artist.
3.  **Hybrid Feature Engineering:**
    - Computes genre embeddings to understand musical proximity.
    - Scales technical audio features (Loudness, Tempo, etc.).
    - Combines them with configurable weights (`GENRE_WEIGHT=0.65`, `AUDIO_WEIGHT=0.35`).
4.  **Clustering Pipeline:**
    - Uses **UMAP** for dimensionality reduction.
    - Uses **HDBSCAN** for density-based clustering, effectively handling outliers ("noise").
    - Performs soft-clustering to allow tracks to belong to multiple related playlists.
5.  **Playlist Refinement:** Large clusters are recursively sub-clustered to maintain specific themes.
6.  **Naming Engine:** Uses `playlist_names.py` to map genre signatures to evocative names (e.g., "Tarde no Rio" for Bossa Nova/Samba, "Deep Cuts" for Lo-fi House).
7.  **Export:** Produces `output/playlists.json` (for API integration), `output/playlists_summary.csv`, and an interactive `output/diagnostics.html`.
8.  **Spotify Sync:** Uses `sync_to_spotify.py` to create or update playlists on your Spotify account using the February 2026 API endpoints.

## Getting Started

### Prerequisites
- Python 3.12 or higher.
- Spotify Developer Credentials (`CLIENT_ID`, `CLIENT_SECRET`).

### Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # And fill in your credentials
```

### Running the Classifier
```bash
# 1. Generate clusters and playlists (Web UI)
uvicorn app:app --port 5000

# 2. Generate clusters and playlists (CLI)
python3 classify_songs.py

# 3. Sync to your Spotify account
python3 sync_to_spotify.py
```

## Key Files

- `app.py`: FastAPI web interface.
- `classify_songs.py`: Main execution logic and machine learning pipeline.
- `sync_to_spotify.py`: Authenticates with Spotify and synchronizes generated playlists.
- `playlist_names.py`: Thematic mapping and naming dictionary for playlists.
- `.cache/`: Stores pre-computed genre embeddings and Spotify auth tokens.
- `output/`: Contains the generated playlists and diagnostic reports.

## Development Conventions

- **Modular Design:** Each step of the pipeline (loading, embedding, clustering, etc.) is isolated into distinct functions.
- **Caching:** Expensive operations (like computing genre embeddings) are cached in `.cache/`.
- **Diagnostics:** Always check `output/diagnostics.html` after a run to visualize the clusters and verify classification quality.
- **Naming Logic:** To add new playlist themes, modify the `PLAYLIST_SIGNATURES` list in `playlist_names.py`.
