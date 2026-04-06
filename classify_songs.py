#!/usr/bin/env python3
"""
Spotify Liked Songs Classifier
Analyzes and classifies songs into thematic playlists using hybrid
genre-embedding + audio-feature clustering.
"""

import json
import os
import hashlib
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score

# ─── Configuration ───────────────────────────────────────────────
INPUT_CSV = Path(__file__).parent / "Liked_Songs.csv"
OUTPUT_DIR = Path(__file__).parent / "output"
CACHE_DIR = Path(__file__).parent / ".cache"

GENRE_WEIGHT = 0.65
AUDIO_WEIGHT = 0.35
UMAP_COMPONENTS = 15
UMAP_NEIGHBORS = 30
MIN_CLUSTER_SIZE = 15
MIN_SAMPLES = 5
MIN_PLAYLIST_SIZE = 15
TARGET_MIN_PLAYLISTS = 50
KNN_K = 7
MEMBERSHIP_THRESHOLD = 0.1  # HDBSCAN soft clustering threshold

AUDIO_FEATURES = [
    "Danceability", "Energy", "Loudness", "Speechiness",
    "Acousticness", "Instrumentalness", "Liveness", "Valence", "Tempo"
]


def run_pipeline(naming_mode="descriptive", progress_callback=None):
    """
    Run the full classification pipeline.

    Args:
        naming_mode: "descriptive" (match signatures first) or "creative" (generate names)
        progress_callback: optional callable(step, total_steps, label, detail)

    Returns:
        list of named playlist dicts
    """
    def _progress(step, label, detail=""):
        if progress_callback:
            progress_callback(step, 10, label, detail)

    # Step 1: Load data
    _progress(1, "Loading data")
    df = load_data()
    _progress(1, "Loading data", f"Loaded {len(df)} tracks, {df['has_genre'].sum()} with genres")

    # Step 2: Artist genre backfill
    _progress(2, "Backfilling genres from same-artist tracks")
    backfill_count = backfill_genres(df)
    _progress(2, "Backfilling genres", f"Backfilled {backfill_count} tracks. Now {df['has_genre'].sum()} with genres")

    # Step 3: Genre embeddings
    _progress(3, "Computing genre embeddings")
    genre_embeddings = embed_genres(df)
    _progress(3, "Computing genre embeddings", f"Embeddings shape: {genre_embeddings.shape}")

    # Step 4: Build hybrid features
    _progress(4, "Building hybrid feature matrix")
    audio_scaled, scaler = scale_audio(df)
    hybrid_features, hybrid_idx = build_hybrid_features(df, genre_embeddings, audio_scaled)
    _progress(4, "Building hybrid feature matrix", f"Hybrid matrix: {hybrid_features.shape} for {len(hybrid_idx)} tracks")

    # Step 5: UMAP
    _progress(5, "Reducing dimensions with UMAP")
    reduced, reduced_2d = reduce_dims(hybrid_features)
    _progress(5, "Reducing dimensions with UMAP", f"Reduced to {reduced.shape[1]} dims")

    # Step 6: HDBSCAN
    _progress(6, "Clustering with HDBSCAN")
    labels, probabilities, soft_labels = cluster(reduced)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    noise_count = (labels == -1).sum()
    _progress(6, "Clustering with HDBSCAN", f"Found {n_clusters} clusters, {noise_count} noise points")

    # Step 7: Assign no-genre tracks
    _progress(7, "Assigning tracks without genres")
    all_labels = assign_all_tracks(df, hybrid_idx, labels, probabilities, audio_scaled)
    assigned = sum(1 for v in all_labels.values() if v >= 0)
    _progress(7, "Assigning tracks without genres", f"{assigned}/{len(df)} tracks assigned")

    # Step 8: Multi-assignment & sub-clustering
    _progress(8, "Building playlists")
    playlists = build_playlists(df, all_labels, hybrid_idx, soft_labels, reduced, audio_scaled)
    _progress(8, "Building playlists", f"Created {len(playlists)} playlists")

    # Step 9: Name playlists
    _progress(9, "Naming playlists")
    named_playlists = name_playlists(playlists, df, naming_mode=naming_mode)
    _progress(9, "Naming playlists", f"Named {len(named_playlists)} playlists")

    # Step 10: Export
    _progress(10, "Exporting results")
    export(named_playlists, df, hybrid_idx, reduced_2d, labels)
    _progress(10, "Exporting results", "Done")

    return named_playlists


def main():
    print("=" * 60)
    print("SPOTIFY LIKED SONGS CLASSIFIER")
    print("=" * 60)

    def cli_progress(step, total, label, detail):
        print(f"\n[{step}/{total}] {label}...")
        if detail:
            print(f"  {detail}")

    named_playlists = run_pipeline(progress_callback=cli_progress)

    all_uris = set()
    for p in named_playlists:
        all_uris.update(p["track_uris"])
    print(f"\n{'=' * 60}")
    print(f"DONE! {len(named_playlists)} playlists created")
    print(f"  Total unique tracks in playlists: {len(all_uris)}")
    print(f"  Output: {OUTPUT_DIR}/")
    print(f"{'=' * 60}")


# ─── Step 1: Load Data ──────────────────────────────────────────
def load_data():
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")

    # Parse genres
    df["genre_list"] = df["Genres"].fillna("").apply(
        lambda x: [g.strip() for g in x.split(",") if g.strip()]
    )
    df["genre_string"] = df["genre_list"].apply(lambda x: ", ".join(x))
    df["has_genre"] = df["genre_list"].apply(lambda x: len(x) > 0)

    # Ensure audio features are numeric
    for feat in AUDIO_FEATURES:
        df[feat] = pd.to_numeric(df[feat], errors="coerce").fillna(0)

    return df


# ─── Step 2: Artist Genre Backfill ──────────────────────────────
def backfill_genres(df):
    count = 0
    no_genre_mask = ~df["has_genre"]
    artist_genres = {}

    for _, row in df[df["has_genre"]].iterrows():
        artist = row["Artist Name(s)"]
        if artist not in artist_genres:
            artist_genres[artist] = Counter()
        for g in row["genre_list"]:
            artist_genres[artist][g] += 1

    for idx in df[no_genre_mask].index:
        artist = df.at[idx, "Artist Name(s)"]
        if artist in artist_genres and artist_genres[artist]:
            top_genres = [g for g, _ in artist_genres[artist].most_common(5)]
            df.at[idx, "genre_list"] = top_genres
            df.at[idx, "genre_string"] = ", ".join(top_genres)
            df.at[idx, "has_genre"] = True
            count += 1

    return count


# ─── Step 3: Genre Embeddings ───────────────────────────────────
def embed_genres(df):
    from sentence_transformers import SentenceTransformer

    CACHE_DIR.mkdir(exist_ok=True)

    # Get unique genre strings for efficient embedding
    genre_strings = df[df["has_genre"]]["genre_string"].unique().tolist()

    # Cache key based on content
    cache_key = hashlib.md5(",".join(sorted(genre_strings)).encode()).hexdigest()[:12]
    cache_file = CACHE_DIR / f"genre_embeddings_{cache_key}.npy"
    cache_keys_file = CACHE_DIR / f"genre_keys_{cache_key}.json"

    if cache_file.exists() and cache_keys_file.exists():
        print("  Using cached embeddings")
        embeddings_array = np.load(cache_file)
        with open(cache_keys_file) as f:
            cached_keys = json.load(f)
        embedding_map = dict(zip(cached_keys, embeddings_array))
    else:
        print(f"  Embedding {len(genre_strings)} unique genre strings...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings_array = model.encode(genre_strings, show_progress_bar=True, batch_size=256)
        embedding_map = dict(zip(genre_strings, embeddings_array))

        np.save(cache_file, embeddings_array)
        with open(cache_keys_file, "w") as f:
            json.dump(genre_strings, f)

    # Map back to dataframe rows
    dim = next(iter(embedding_map.values())).shape[0]
    result = np.zeros((len(df), dim))
    for i, row in df.iterrows():
        gs = row["genre_string"]
        if gs in embedding_map:
            result[i] = embedding_map[gs]

    return result


# ─── Step 4: Scale Audio Features ───────────────────────────────
def scale_audio(df):
    scaler = StandardScaler()
    audio_data = df[AUDIO_FEATURES].values
    audio_scaled = scaler.fit_transform(audio_data)
    return audio_scaled, scaler


def build_hybrid_features(df, genre_embeddings, audio_scaled):
    """Build hybrid features for tracks with genres."""
    has_genre_idx = df[df["has_genre"]].index.tolist()

    genre_part = genre_embeddings[has_genre_idx] * GENRE_WEIGHT
    audio_part = audio_scaled[has_genre_idx] * AUDIO_WEIGHT

    hybrid = np.hstack([genre_part, audio_part])
    return hybrid, has_genre_idx


# ─── Step 5: UMAP ───────────────────────────────────────────────
def reduce_dims(features):
    import umap

    reducer = umap.UMAP(
        n_components=UMAP_COMPONENTS,
        n_neighbors=UMAP_NEIGHBORS,
        min_dist=0.0,
        metric="euclidean",
        random_state=42,
        n_jobs=-1,
    )
    reduced = reducer.fit_transform(features)

    reducer_2d = umap.UMAP(
        n_components=2,
        n_neighbors=UMAP_NEIGHBORS,
        min_dist=0.1,
        metric="euclidean",
        random_state=42,
        n_jobs=-1,
    )
    reduced_2d = reducer_2d.fit_transform(features)

    return reduced, reduced_2d


# ─── Step 6: HDBSCAN ────────────────────────────────────────────
def cluster(reduced):
    import hdbscan

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=MIN_CLUSTER_SIZE,
        min_samples=MIN_SAMPLES,
        cluster_selection_method="eom",
        prediction_data=True,
    )
    clusterer.fit(reduced)

    labels = clusterer.labels_
    probabilities = clusterer.probabilities_

    # Soft clustering: get membership vectors for multi-assignment
    soft_labels = hdbscan.all_points_membership_vectors(clusterer)

    return labels, probabilities, soft_labels


# ─── Step 7: Assign All Tracks ──────────────────────────────────
def assign_all_tracks(df, hybrid_idx, labels, probabilities, audio_scaled):
    """Assign every track a primary cluster label using KNN for ungenred tracks."""
    all_labels = {}

    # Map hybrid_idx tracks to their cluster labels
    for i, df_idx in enumerate(hybrid_idx):
        all_labels[df_idx] = int(labels[i])

    # For tracks without genres, use KNN on audio features
    no_genre_idx = df[~df["has_genre"]].index.tolist()
    if not no_genre_idx:
        return all_labels

    # Train KNN on clustered tracks (excluding noise)
    clustered_mask = labels >= 0
    if clustered_mask.sum() < KNN_K:
        for idx in no_genre_idx:
            all_labels[idx] = -1
        return all_labels

    clustered_hybrid_idx = [hybrid_idx[i] for i in range(len(hybrid_idx)) if clustered_mask[i]]
    clustered_labels_clean = labels[clustered_mask]
    train_audio = audio_scaled[clustered_hybrid_idx]

    nn = NearestNeighbors(n_neighbors=KNN_K, metric="euclidean")
    nn.fit(train_audio)

    # Compute intra-cluster distance threshold
    train_dists, _ = nn.kneighbors(train_audio)
    dist_threshold = np.percentile(train_dists[:, -1], 85)

    query_audio = audio_scaled[no_genre_idx]
    dists, indices = nn.kneighbors(query_audio)

    for i, df_idx in enumerate(no_genre_idx):
        if dists[i, -1] <= dist_threshold:
            # Majority vote
            neighbor_labels = clustered_labels_clean[indices[i]]
            counts = Counter(neighbor_labels)
            all_labels[df_idx] = counts.most_common(1)[0][0]
        else:
            all_labels[df_idx] = -1

    return all_labels


# ─── Step 8: Build Playlists ────────────────────────────────────
def build_playlists(df, all_labels, hybrid_idx, soft_labels, reduced, audio_scaled):
    """
    Build playlists with multi-assignment, sub-clustering, and
    genre-based playlists to reach 50+ playlists with high coverage.
    """
    playlists = []

    # --- Phase 1: Primary clusters from HDBSCAN ---
    cluster_ids = sorted(set(v for v in all_labels.values() if v >= 0))
    primary_clusters = {}
    for cluster_id in cluster_ids:
        track_indices = [idx for idx, lbl in all_labels.items() if lbl == cluster_id]
        primary_clusters[cluster_id] = track_indices

    # --- Phase 2: Multi-assignment using soft clustering ---
    # For each track in hybrid_idx, check if it has significant membership in other clusters
    hybrid_idx_to_pos = {idx: i for i, idx in enumerate(hybrid_idx)}
    n_clusters_soft = soft_labels.shape[1] if soft_labels.ndim > 1 else 0

    for cluster_id in cluster_ids:
        additional = []
        for df_idx, pos in hybrid_idx_to_pos.items():
            if all_labels.get(df_idx) == cluster_id:
                continue  # Already in this cluster
            if cluster_id < n_clusters_soft and soft_labels[pos, cluster_id] > MEMBERSHIP_THRESHOLD:
                additional.append(df_idx)
        if additional:
            primary_clusters[cluster_id] = primary_clusters[cluster_id] + additional

    for cluster_id, track_indices in primary_clusters.items():
        if len(track_indices) >= MIN_PLAYLIST_SIZE:
            playlists.append({
                "source": f"hdbscan_{cluster_id}",
                "track_indices": track_indices,
            })

    # --- Phase 3: Sub-cluster large playlists ---
    new_playlists = []
    for p in playlists:
        if len(p["track_indices"]) > 400:
            subs = sub_cluster(p["track_indices"], audio_scaled, df)
            if len(subs) > 1:
                for i, sub_indices in enumerate(subs):
                    if len(sub_indices) >= MIN_PLAYLIST_SIZE:
                        new_playlists.append({
                            "source": f"{p['source']}_sub{i}",
                            "track_indices": sub_indices,
                        })
            else:
                new_playlists.append(p)
        else:
            new_playlists.append(p)
    playlists = new_playlists

    # --- Phase 4: Genre-based playlists for coverage & diversity ---
    covered = set()
    for p in playlists:
        covered.update(p["track_indices"])

    genre_playlists = build_genre_playlists(df, covered, all_labels)
    playlists.extend(genre_playlists)

    # --- Phase 5: Audio-vibe playlists for uncovered tracks ---
    for p in playlists:
        covered.update(p["track_indices"])

    uncovered = [i for i in range(len(df)) if i not in covered]
    if len(uncovered) >= MIN_PLAYLIST_SIZE:
        vibe_playlists = build_vibe_playlists(df, uncovered, audio_scaled)
        playlists.extend(vibe_playlists)

    # --- Phase 6: Decade playlists for extra coverage ---
    for p in playlists:
        covered.update(p["track_indices"])

    decade_playlists = build_decade_playlists(df, covered)
    playlists.extend(decade_playlists)

    # --- Phase 7: If still < 50 playlists, create more genre-specific ones ---
    if len(playlists) < TARGET_MIN_PLAYLISTS:
        extra = build_extra_genre_playlists(df, playlists)
        playlists.extend(extra)

    # Deduplicate playlists (remove if >80% overlap with another)
    playlists = deduplicate_playlists(playlists)

    return playlists


def sub_cluster(track_indices, audio_scaled, df, n_sub=3):
    """Sub-cluster a large playlist using KMeans on audio features."""
    from sklearn.cluster import KMeans

    features = audio_scaled[track_indices]
    n_sub = min(n_sub, max(2, len(track_indices) // MIN_PLAYLIST_SIZE))

    km = KMeans(n_clusters=n_sub, random_state=42, n_init=10)
    sub_labels = km.fit_predict(features)

    result = []
    for lbl in range(n_sub):
        mask = sub_labels == lbl
        result.append([track_indices[i] for i in range(len(track_indices)) if mask[i]])
    return result


def build_genre_playlists(df, already_covered, all_labels):
    """Create playlists for well-defined genre groups not fully covered."""
    genre_groups = {
        "mpb": ["mpb", "new mpb", "tropicalia"],
        "bossa_samba": ["bossa nova", "samba", "brazilian jazz"],
        "psych_rock": ["psychedelic rock", "acid rock", "neo-psychedelic", "space rock"],
        "prog_rock": ["progressive rock", "art rock", "krautrock", "canterbury scene"],
        "classic_rock": ["classic rock", "rock", "hard rock"],
        "blues": ["blues", "blues rock", "electric blues", "delta blues"],
        "trip_hop": ["trip hop", "downtempo", "electronica"],
        "reggae_dub": ["reggae", "roots reggae", "dub", "rocksteady"],
        "hip_hop_us": ["hip hop", "east coast hip hop", "boom bap", "old school hip hop", "west coast hip hop"],
        "br_hiphop": ["brazilian hip hop", "brazilian funk", "funk carioca", "jazz rap"],
        "jazz_core": ["jazz", "jazz fusion", "free jazz", "bebop", "hard bop"],
        "jazz_funk": ["jazz funk", "acid jazz", "soul jazz"],
        "nu_jazz": ["nu jazz", "indie jazz", "jazz house"],
        "soul_funk": ["funk", "classic soul", "retro soul", "motown"],
        "neo_soul": ["neo soul", "indie soul", "retro soul"],
        "afrobeat": ["afrobeat", "afropop", "highlife", "afro soul"],
        "disco_house": ["french house", "disco house", "nu disco", "disco", "post-disco"],
        "deep_house": ["deep house", "lo-fi house", "house", "tech house"],
        "grunge_alt": ["grunge", "alternative rock", "indie rock"],
        "garage_punk": ["garage rock", "punk rock", "post-punk"],
        "stoner_doom": ["stoner rock", "doom metal", "sludge metal"],
        "britpop": ["britpop", "indie", "madchester"],
        "dnb": ["drum and bass", "jungle", "liquid funk", "breakbeat"],
        "yacht_soft": ["yacht rock", "soft rock", "adult contemporary"],
        "surf": ["surf rock", "garage rock"],
        "glam_wave": ["glam rock", "new wave", "post-punk", "synth-pop"],
        "folk_acoustic": ["folk", "folk rock", "singer-songwriter"],
        "idm_ambient": ["idm", "ambient", "electronica", "glitch"],
        "baroque_pop": ["baroque pop", "chamber pop", "art pop"],
        "world_ethio": ["world music", "ethio-jazz", "desert blues"],
        "lofi_beats": ["lo-fi beats", "jazz beats", "chillhop"],
        "funk_rock": ["funk rock", "funk metal"],
        "samba_pagode": ["samba", "pagode", "samba rock"],
        "spoken_word": ["spoken word", "poetry"],
    }

    playlists = []
    for group_name, genres in genre_groups.items():
        genre_set = set(genres)
        matching = []
        for i, row in df.iterrows():
            if any(g in genre_set for g in row["genre_list"]):
                matching.append(i)

        if len(matching) >= MIN_PLAYLIST_SIZE:
            playlists.append({
                "source": f"genre_{group_name}",
                "track_indices": matching,
            })

    return playlists


def build_vibe_playlists(df, uncovered, audio_scaled):
    """Create playlists for uncovered tracks based on audio vibes."""
    from sklearn.cluster import KMeans

    if len(uncovered) < MIN_PLAYLIST_SIZE:
        return []

    features = audio_scaled[uncovered]
    n_clusters = max(2, len(uncovered) // 50)
    n_clusters = min(n_clusters, 8)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(features)

    playlists = []
    for lbl in range(n_clusters):
        mask = labels == lbl
        indices = [uncovered[i] for i in range(len(uncovered)) if mask[i]]
        if len(indices) >= MIN_PLAYLIST_SIZE:
            playlists.append({
                "source": f"vibe_{lbl}",
                "track_indices": indices,
            })
    return playlists


def build_decade_playlists(df, already_covered):
    """Create decade-based playlists for tracks not yet well covered."""
    df["year"] = pd.to_numeric(
        df["Release Date"].str[:4], errors="coerce"
    ).fillna(0).astype(int)

    decade_ranges = [
        (1960, 1969, "Anos 60"),
        (1970, 1979, "Anos 70"),
        (1980, 1989, "Anos 80"),
        (1990, 1999, "Anos 90"),
        (2000, 2009, "Anos 2000"),
        (2010, 2019, "Anos 2010"),
        (2020, 2030, "Contemporaneo"),
    ]

    playlists = []
    for start, end, name in decade_ranges:
        mask = (df["year"] >= start) & (df["year"] <= end)
        indices = df[mask].index.tolist()
        # Only create if enough uncovered tracks
        uncovered_in_decade = [i for i in indices if i not in already_covered]
        if len(uncovered_in_decade) >= MIN_PLAYLIST_SIZE and len(indices) >= 30:
            playlists.append({
                "source": f"decade_{start}",
                "track_indices": indices,
            })

    return playlists


def build_extra_genre_playlists(df, existing_playlists):
    """If we still don't have 50 playlists, mine for more genre-specific ones."""
    # Count all genres
    genre_counter = Counter()
    for _, row in df.iterrows():
        for g in row["genre_list"]:
            genre_counter[g] += 1

    existing_sources = {p["source"] for p in existing_playlists}
    playlists = []

    for genre, count in genre_counter.most_common(100):
        if count < MIN_PLAYLIST_SIZE:
            break
        source = f"single_genre_{genre.replace(' ', '_')}"
        if source in existing_sources:
            continue

        indices = [i for i, row in df.iterrows() if genre in row["genre_list"]]
        if len(indices) >= MIN_PLAYLIST_SIZE:
            playlists.append({
                "source": source,
                "track_indices": indices,
            })
            existing_sources.add(source)

        if len(existing_playlists) + len(playlists) >= TARGET_MIN_PLAYLISTS:
            break

    return playlists


def deduplicate_playlists(playlists):
    """Remove playlists that overlap >80% with a larger playlist."""
    # Sort by size descending
    playlists.sort(key=lambda p: len(p["track_indices"]), reverse=True)

    keep = []
    kept_sets = []

    for p in playlists:
        p_set = set(p["track_indices"])
        is_duplicate = False

        for k_set in kept_sets:
            if not p_set:
                break
            overlap = len(p_set & k_set) / len(p_set)
            if overlap > 0.80:
                is_duplicate = True
                break

        if not is_duplicate and len(p["track_indices"]) >= MIN_PLAYLIST_SIZE:
            keep.append(p)
            kept_sets.append(p_set)

    return keep


# ─── Step 9: Name Playlists ─────────────────────────────────────
def name_playlists(playlists, df, naming_mode="descriptive"):
    from playlist_names import match_playlist_name, differentiate_name

    # First pass: compute metadata for all playlists
    playlist_meta = []
    for p in playlists:
        indices = p["track_indices"]
        track_uris = df.iloc[indices]["Track URI"].tolist()

        genre_counter = Counter()
        for idx in indices:
            for g in df.iloc[idx]["genre_list"]:
                genre_counter[g] += 1
        top_genres = genre_counter.most_common(10)

        audio_profile = {}
        for feat in AUDIO_FEATURES:
            audio_profile[feat] = float(df.iloc[indices][feat].mean())

        base_name, name, description = match_playlist_name(top_genres, audio_profile, mode=naming_mode)

        playlist_meta.append({
            "base_name": base_name,
            "name": name,
            "description": description,
            "source": p["source"],
            "track_count": len(indices),
            "track_uris": track_uris,
            "top_genres": [(g, c) for g, c in top_genres[:5]],
            "audio_profile": audio_profile,
        })

    # Sort by track count descending so the largest playlist keeps the base name
    playlist_meta.sort(key=lambda x: x["track_count"], reverse=True)

    # Second pass: assign unique names, differentiating duplicates
    used_names = set()
    named = []

    for p in playlist_meta:
        name = p["name"]
        description = p["description"]

        if name in used_names:
            name, description = differentiate_name(
                p["base_name"], p["top_genres"], p["audio_profile"], used_names
            )

        used_names.add(name)
        p["name"] = name
        p["description"] = description
        named.append(p)

    return named


# ─── Step 10: Export ─────────────────────────────────────────────
def export(playlists, df, hybrid_idx, reduced_2d, labels):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # JSON output
    json_output = {
        "total_tracks": len(df),
        "total_playlists": len(playlists),
        "playlists": [],
    }

    all_uris = set()
    for p in playlists:
        all_uris.update(p["track_uris"])
        json_output["playlists"].append({
            "name": p["name"],
            "description": p["description"],
            "track_count": p["track_count"],
            "track_uris": p["track_uris"],
            "top_genres": [g for g, _ in p["top_genres"]],
            "audio_profile": {k: round(v, 3) for k, v in p["audio_profile"].items()},
        })

    json_output["coverage"] = {
        "tracks_in_playlists": len(all_uris),
        "coverage_pct": round(len(all_uris) / len(df) * 100, 1),
    }

    with open(OUTPUT_DIR / "playlists.json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)

    # CSV summary
    rows = []
    for p in playlists:
        rows.append({
            "Playlist": p["name"],
            "Description": p["description"],
            "Tracks": p["track_count"],
            "Top Genres": ", ".join(g for g, _ in p["top_genres"]),
            "Avg Energy": round(p["audio_profile"]["Energy"], 2),
            "Avg Danceability": round(p["audio_profile"]["Danceability"], 2),
            "Avg Valence": round(p["audio_profile"]["Valence"], 2),
        })
    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(OUTPUT_DIR / "playlists_summary.csv", index=False)

    # Diagnostics HTML (UMAP 2D)
    try:
        import plotly.express as px

        viz_data = pd.DataFrame({
            "UMAP_1": reduced_2d[:, 0],
            "UMAP_2": reduced_2d[:, 1],
            "Cluster": labels.astype(str),
            "Track": df.iloc[hybrid_idx]["Track Name"].values,
            "Artist": df.iloc[hybrid_idx]["Artist Name(s)"].values,
            "Genres": df.iloc[hybrid_idx]["genre_string"].values,
        })

        fig = px.scatter(
            viz_data, x="UMAP_1", y="UMAP_2", color="Cluster",
            hover_data=["Track", "Artist", "Genres"],
            title="UMAP 2D - Clusters de Musicas",
            width=1200, height=800,
            opacity=0.6,
        )
        fig.update_layout(showlegend=False)
        fig.write_html(OUTPUT_DIR / "diagnostics.html")
        print(f"  Visualization saved to {OUTPUT_DIR / 'diagnostics.html'}")
    except Exception as e:
        print(f"  Warning: Could not create visualization: {e}")

    print(f"  Playlists JSON: {OUTPUT_DIR / 'playlists.json'}")
    print(f"  Summary CSV: {OUTPUT_DIR / 'playlists_summary.csv'}")


if __name__ == "__main__":
    main()
