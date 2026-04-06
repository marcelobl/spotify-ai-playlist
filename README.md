# Spotify Liked Songs Classifier

A Python-based tool for organizing Spotify "Liked Songs" into cohesive, thematic playlists using hybrid genre-embedding and audio-feature clustering. 

## Overview

This project analyzes a user's Spotify library (fetched directly via the API) and automatically groups tracks into meaningful playlists. Unlike simple genre-based sorting, it uses a hybrid approach:
- **Genre Semantics:** High-dimensional embeddings capture the relationship between musical genres.
- **Audio Features:** Technical attributes like danceability, energy, and acousticness ensure a consistent "vibe" within each playlist.

The system handles large libraries (10k+ tracks) and creates distinct, named playlists. It provides both a traditional CLI and a modern Web UI for real-time progress tracking.

## Features

- **Direct Spotify Integration:** Fetch your Liked Songs directly from the Spotify API—no manual export needed.
- **Advanced Clustering Pipeline:** Uses **UMAP** for dimensionality reduction and **HDBSCAN** for density-based clustering to handle outliers and effectively cluster tracks.
- **Intelligent Naming Engine:** Maps genre signatures to evocative, thematic names (e.g., "Tarde no Rio" for Bossa Nova/Samba, "Deep Cuts" for Lo-fi House).
- **Web UI:** A FastAPI-powered web interface with real-time SSE streaming for progress visualization.
- **Spotify Sync:** Automatically creates or updates playlists on your Spotify account.

## Prerequisites

- **Python 3.12** or higher.
- A **Spotify Developer Account** to create an App and obtain credentials.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/marcelobl/spotify-ai-playlist.git
   cd spotify-ai-playlist
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy the example environment file and fill in your Spotify API credentials.
   ```bash
   cp .env.example .env
   ```
   Open `.env` and configure:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_WEB_REDIRECT_URI` (Defaults to `http://127.0.0.1:5000/api/auth/callback` for the Web UI)

## Usage

### Web Interface (Recommended)

The Web UI provides a visual representation of the processing pipeline, streaming progress in real-time. It handles Spotify authentication and fetches your tracks automatically.

1. Start the FastAPI server:
   ```bash
   uvicorn app:app --port 5000 --reload
   ```
2. Open your browser and navigate to `http://127.0.0.1:5000/`.
3. Authenticate with Spotify when prompted and start the classification/sync process.

### Command Line Interface (CLI)

You can also run the pipeline manually using the CLI scripts.

1. **Generate clusters and playlists:**
   ```bash
   python classify_songs.py
   ```
   The script will prompt you to authenticate with Spotify to fetch your liked songs directly. This produces `output/playlists.json`, `output/playlists_summary.csv`, and an interactive `output/diagnostics.html`.

2. **Sync to your Spotify account:**
   ```bash
   python sync_to_spotify.py
   ```
   This script reads `output/playlists.json`, authenticates with your Spotify account, and creates or updates the playlists.

## Architecture

- **`app.py`**: FastAPI web interface serving static files and API routes.
- **`pipeline.py`**: Contains the core logic for the Web UI's data processing stream.
- **`classify_songs.py`**: CLI script containing the machine learning pipeline (StandardScaler, UMAP, HDBSCAN).
- **`sync_to_spotify.py`**: CLI script managing Spotify OAuth and playlist creation.
- **`playlist_names.py`**: Naming dictionary to map thematic signatures to playlist names.
- **`.cache/`**: (Generated) Stores pre-computed embeddings and Spotify tokens.
- **`output/`**: (Generated) Contains the output JSON/CSV reports and HTML diagnostics.

## License

This project is open-sourced under the MIT License.
