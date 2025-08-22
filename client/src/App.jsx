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
    navigate(`/puzzle/${normalized.id}`, { replace: true });
  };

  const openPuzzle = (p) => goToPuzzle(p);

  return (
    <div style={{ padding: 8 }}>
      <h2 style={{ textAlign: "center" }}>15 Diverse Puzzles (≤2100)</h2>
      <PuzzlesGrid puzzles={puzzles} onOpen={openPuzzle} />
      
    </div>
  );
}

function PuzzleRouteWrapper() {
  const { id } = useParams();
  const [puzzle, setPuzzle] = useState(null);
  const [index, setIndex] = useState(null);
  const [similarList, setSimilarList] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const { puzzle } = await fetchPuzzleById(id);
        if (puzzle) {
          console.log("Loaded puzzle:", puzzle);
          setPuzzle(puzzle);
          const { results } = await fetchSimilar(puzzle.id, 15, 3000);
          
          if (results?.length > 0) {
            setSimilarList(results);
            setIndex(0); // start at first result
          }
        }
      } catch (err) {
        console.error(err);
      }
    })();
  }, [id]);

  const handleNextSimilar = async () => {
    if (!similarList.length) return;

    const nextIndex = index + 1;
    if (nextIndex < similarList.length) {
      const next = similarList[nextIndex];
      const normalized = {
        id: next.puzzle_id || next.id,
        fen: next.fen,
        moves: next.moves || [],
        rating: next.rating,
        themes: next.themes || [],
      };
      setPuzzle(normalized);
      setIndex(nextIndex); // move pointer forward
    } else {
      console.warn("No more similar puzzles available");
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
