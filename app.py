from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import faiss
import numpy as np
import pandas as pd
import os
import json
import random
from time import time
from typing import Any, Dict, List, Optional

INDEX_PATH = os.environ.get("INDEX_PATH", "./db/index.faiss")
META_PATH  = os.environ.get("META_PATH",  "./db/metadata.json")  # or .json/.jsonl/.parquet
EMB_PATH   = os.environ.get("EMB_PATH",   "./db/vectors_merged.npy")  # optional

print("Loading FAISS index (mmap)…")
index = faiss.read_index(INDEX_PATH, faiss.IO_FLAG_MMAP)
d = index.d  # vector dim

# Optional: mmap embeddings.npy as fallback
EMB = None
if EMB_PATH and os.path.exists(EMB_PATH):
    print("Memory-mapping embeddings for fallback:", EMB_PATH)
    EMB = np.load(EMB_PATH, mmap_mode="r")  # shape (N, d), float32

# Load metadata (supports .json/.jsonl/.parquet)
def _load_meta(path: str):
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
        # ensure themes is list[str]
        df["themes"] = df["themes"].apply(lambda t: t if isinstance(t, list) else ([] if pd.isna(t) else [str(t)]))
        return df.to_dict(orient="records")
    elif path.endswith(".jsonl"):
        rows = []
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
        for r in rows:
            r["themes"] = r.get("themes") if isinstance(r.get("themes"), list) else ([] if r.get("themes") in (None, float("nan")) else [str(r.get("themes"))])
        return rows
    else:
        with open(path, "r") as f:
            rows = json.load(f)
        for r in rows:
            r["themes"] = r.get("themes") if isinstance(r.get("themes"), list) else ([] if r.get("themes") in (None, float("nan")) else [str(r.get("themes"))])
        return rows

raw_meta = _load_meta(META_PATH)

# Map FAISS row index → metadata
meta_map = {i: m for i, m in enumerate(raw_meta)}

# Helper: map string puzzle_id to FAISS row index
id_to_row = {m["id"]: i for i, m in enumerate(raw_meta)}

def get_meta(row_id: int):
    return meta_map.get(row_id)

def get_vector_for_row(row_id: int) -> np.ndarray:
    """Get vector for FAISS row index."""
    try:
        vec = index.reconstruct(int(row_id))
        if vec is not None and len(vec) == d:
            return np.asarray(vec, dtype="float32").reshape(1, -1)
    except Exception:
        pass
    if EMB is not None:
        return np.asarray(EMB[int(row_id)], dtype="float32").reshape(1, -1)
    raise RuntimeError(f"Cannot reconstruct vector for row={row_id}")

app = FastAPI(title="Puzzle API")

# --- CORS (React dev, etc.) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simple in-memory cache for /similar prefetch ---
SIM_CACHE: Dict[str, Dict[str, Any]] = {}
SIM_TTL_SEC = int(os.environ.get("SIM_TTL_SEC", "300"))

def cache_put(key: str, value: Any):
    SIM_CACHE[key] = {"value": value, "ts": time()}

def cache_get(key: str) -> Optional[Any]:
    v = SIM_CACHE.get(key)
    if not v:
        return None
    if time() - v["ts"] > SIM_TTL_SEC:
        SIM_CACHE.pop(key, None)
        return None
    return v["value"]

# ---------------- Home (kept) ----------------
@app.get("/", response_class=HTMLResponse)
def form():
    return """
    <html>
        <head><title>Puzzle Similarity Search</title></head>
        <body>
            <h2>Find Similar Puzzles</h2>
            <form action="/similar" method="get">
                <label for="puzzle_id">Puzzle ID:</label>
                <input type="text" id="puzzle_id" name="puzzle_id" required>
                <input type="number" name="top_k" value="10" min="1" max="100">
                <button type="submit">Search</button>
            </form>
        </body>
    </html>
    """

# ---------------- Diverse 15 (new) ----------------
def _pick_diverse_puzzles(limit: int, max_rating: int) -> List[Dict[str, Any]]:
    pool = [m for m in raw_meta if isinstance(m.get("rating"), (int, float)) and m["rating"] < max_rating]
    random.shuffle(pool)  # randomize each call
    seen = set()
    out: List[Dict[str, Any]] = []

    for r in pool:
        themes = r.get("themes") or []
        primary = themes[0] if themes else "Other"
        if primary in seen:
            continue
        seen.add(primary)
        out.append(r)
        if len(out) >= limit:
            break

    if len(out) < limit:
        # top up ignoring theme uniqueness
        needed = limit - len(out)
        # exclude already chosen ids
        chosen_ids = {o["id"] for o in out}
        tail = [m for m in pool if m["id"] not in chosen_ids][:needed]
        out.extend(tail)

    # return minimal payload
    return [{
        "id": r["id"],
        "fen": r["fen"],
        "moves": r.get("moves", []),
        "rating": int(r.get("rating", 0)),
        "themes": r.get("themes", []),
    } for r in out]

@app.get("/puzzles")
def get_diverse_puzzles(limit: int = Query(15, ge=1, le=50),
                        max_rating: int = Query(2100, ge=300, le=4000)):
    puzzles = _pick_diverse_puzzles(limit, max_rating)
    return {"puzzles": puzzles}

# ---------------- Similar (kept, with optional rating filter + cache) ----------------
@app.get("/similar")
def similar(
    puzzle_id: str = Query(..., description="string puzzle_id from dataset"),
    top_k: int = Query(15, ge=1, le=100),
    exclude_self: bool = Query(True),
    max_rating: int = Query(2100, ge=300, le=4000)  # keep results in user range
):
    # cache key
    key = f"sim:{puzzle_id}:{top_k}:{exclude_self}:{max_rating}"
    cached = cache_get(key)
    if cached is not None:
        return cached

    if puzzle_id not in id_to_row:
        raise HTTPException(status_code=404, detail=f"Puzzle ID {puzzle_id} not found in metadata")
    row_id = id_to_row[puzzle_id]

    try:
        q = get_vector_for_row(row_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Search (oversample a bit for filtering)
    D, I = index.search(q.astype("float32"), min(top_k + 32, top_k + 128))
    ids, dists = I[0].tolist(), D[0].tolist()

    results = []
    for rid, dist in zip(ids, dists):
        if rid == -1:
            continue
        if exclude_self and rid == row_id:
            continue
        md = get_meta(rid)
        if not md:
            continue
        if isinstance(md.get("rating"), (int, float)) and md["rating"] >= max_rating:
            continue
        results.append({
            "puzzle_id": md["id"],
            "score": float(dist),
            "fen": md.get("fen"),
            "moves": md.get("moves", []),
            "rating": int(md.get("rating", 0)),
            "themes": md.get("themes", []),
        })
        if len(results) >= top_k:
            break

    payload = {"query_puzzle_id": puzzle_id, "results": results}
    cache_put(key, payload)
    return payload

# ---------------- Prefetch similar (new) ----------------
@app.post("/prefetch/{puzzle_id}")
def prefetch_similar(puzzle_id: str, top_k: int = 15, exclude_self: bool = True, max_rating: int = 2100, bg: BackgroundTasks = None):
    def _job():
        try:
            _ = similar(puzzle_id=puzzle_id, top_k=top_k, exclude_self=exclude_self, max_rating=max_rating)
        except Exception:
            pass
    if bg is not None:
        bg.add_task(_job)
    return {"status": "ok"}

@app.get("/puzzle/{puzzle_id}")
def get_puzzle(puzzle_id: str):
    if puzzle_id not in id_to_row:
        raise HTTPException(status_code=404, detail="puzzle not found")
    row = id_to_row[puzzle_id]
    md = get_meta(row)
    return {"puzzle": {
        "id": md.get("id"),
        "fen": md.get("fen"),
        "moves": md.get("moves", []),  # ensure these are UCI strings
        "rating": int(md.get("rating", 0)),
        "themes": md.get("themes", []),
    }}
