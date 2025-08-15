const API = import.meta.env.VITE_API || "http://localhost:8000";

export async function fetchDiverse(limit = 15, maxRating = 2100) {
  const r = await fetch(`${API}/puzzles?limit=${limit}&max_rating=${maxRating}`);
  return r.json();
}

export function prefetchSimilar(id, topK = 15, maxRating = 2100) {
  fetch(`${API}/prefetch/${id}?top_k=${topK}&max_rating=${maxRating}`, { method: "POST" }).catch(()=>{});
}

export async function fetchSimilar(id, topK = 15, maxRating = 2100) {
  const r = await fetch(`${API}/similar?puzzle_id=${id}&top_k=${topK}&max_rating=${maxRating}`);
  return r.json();
}

export async function fetchPuzzleById(id) {
  const r = await fetch(`${API}/puzzle/${id}`);
  return r.json();
}
