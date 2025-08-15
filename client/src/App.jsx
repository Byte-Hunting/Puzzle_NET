// src/App.jsx
import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useParams } from "react-router-dom";
import { fetchDiverse, prefetchSimilar, fetchPuzzleById } from "./api"; // see api changes below
import PuzzlesGrid from "./components/PuzzlesGrid";
import PuzzleModal from "./components/PuzzleModal";

function Home() {
  const [puzzles, setPuzzles] = useState([]);
  const [current, setCurrent] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      const { puzzles } = await fetchDiverse(15, 2100);
      setPuzzles(puzzles);
    })();
  }, []);

  const openPuzzle = (p) => {
    setCurrent(p);
    prefetchSimilar(p.id, 15, 2100);
    navigate(`/puzzle/${p.id}`);
  };

  const nextSimilar = async () => {
    if (!current) return;
    const { results } = await fetchSimilar(current.id, 15, 2100); // keep your existing fetchSimilar
    const next = results?.[0];
    if (next) {
      const normalized = {
        id: next.puzzle_id,
        fen: next.fen,
        moves: next.moves || [],
        rating: next.rating,
        themes: next.themes || [],
      };
      setCurrent(normalized);
      prefetchSimilar(normalized.id, 15, 2100);
      navigate(`/puzzle/${normalized.id}`, { replace: true });
    }
  };

  return (
    <div style={{ padding: 8 }}>
      <h2 style={{ textAlign: "center" }}>15 Diverse Puzzles (≤2100)</h2>
      <PuzzlesGrid puzzles={puzzles} onOpen={openPuzzle} />
      <PuzzleModal puzzle={current} onClose={() => { setCurrent(null); navigate("/"); }} onSolvedNext={nextSimilar} />
    </div>
  );
}

function PuzzleRouteWrapper() {
  // If the user enters /puzzle/:id directly, this component loads the puzzle from the API
  const { id } = useParams();
  const [puzzle, setPuzzle] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const { puzzle } = await fetchPuzzleById(id);
        if (puzzle) setPuzzle(puzzle);
      } catch (err) {
        console.error(err);
      }
    })();
  }, [id]);

  return (
    <>
      <PuzzleModal puzzle={puzzle} onClose={() => navigate("/")} onSolvedNext={() => navigate("/")} />
    </>
  );
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/puzzle/:id" element={<PuzzleRouteWrapper />} />
      </Routes>
    </BrowserRouter>
  );
}
