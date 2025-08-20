import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  useNavigate,
  useParams,
} from "react-router-dom";
import {
  fetchDiverse,
  fetchPuzzleById,
  fetchSimilar,
  prefetchSimilar,
} from "./api";
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

  const goToPuzzle = (p) => {
    const normalized = {
      id: p.puzzle_id || p.id,
      fen: p.fen,
      moves: p.moves || [],
      rating: p.rating,
      themes: p.themes || [],
    };
    console.log("Opening puzzle:", normalized);
    setCurrent(normalized);
    prefetchSimilar(normalized.id, 15, 2100);
    navigate(`/puzzle/${normalized.id}`, { replace: true });
  };

  const openPuzzle = (p) => goToPuzzle(p);

  const nextSimilar = async () => {
    if (!current) return;
    console.log("Fetching similar puzzles for:", current.id);
    const { results } = await fetchSimilar(current.id, 15, 2100);
    console.log("API returned:", results);
    const next = results?.[0];
    if (next) {
      const normalized = {
        id: next.puzzle_id || next.id,
        fen: next.fen,
        moves: next.moves || [],
        rating: next.rating,
        themes: next.themes || [],
      };
      console.log("👉 Switching to next similar puzzle:", normalized);
      setCurrent(normalized);
      prefetchSimilar(normalized.id, 15, 2100);
    } else {
      console.warn("No similar puzzles found for:", current.id);
    }
  };

  return (
    <div style={{ padding: 8 }}>
      <h2 style={{ textAlign: "center" }}>15 Diverse Puzzles (≤2100)</h2>
      <PuzzlesGrid puzzles={puzzles} onOpen={openPuzzle} />
      <PuzzleModal
        puzzle={current}
        onClose={() => {
          setCurrent(null);
          navigate("/");
        }}
        onSolvedNext={nextSimilar}
      />
    </div>
  );
}

function PuzzleRouteWrapper() {
  const { id } = useParams();
  const [puzzle, setPuzzle] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const { puzzle } = await fetchPuzzleById(id);
        if (puzzle) {
          console.log("Loaded puzzle:", puzzle);
          setPuzzle(puzzle);
        }
      } catch (err) {
        console.error(err);
      }
    })();
  }, [id]);

  const handleNextSimilar = async () => {
    if (!puzzle) return;
    console.log("Fetching similar puzzles for:", puzzle.id);
    const { results } = await fetchSimilar(puzzle.id, 15, puzzle.rating || 2100);
    console.log("API returned:", results);
    if (results?.length > 0) {
      const next = results[0];
      const normalized = {
        id: next.puzzle_id || next.id,
        fen: next.fen,
        moves: next.moves || [],
        rating: next.rating,
        themes: next.themes || [],
      };
      console.log("👉 Switching to next similar puzzle:", normalized);
      setPuzzle(normalized);
    } else {
      console.warn("No similar puzzles found for:", puzzle.id);
      navigate("/");
    }
  };

  return (
    <PuzzleModal
      puzzle={puzzle}
      onClose={() => navigate("/")}
      onSolvedNext={handleNextSimilar}
    />
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
