import { useEffect, useRef, useState } from "react";
import { Chess } from "chess.js";
import { Chessground } from "chessground";
import "chessground/assets/chessground.base.css";
import "chessground/assets/chessground.brown.css";
import "chessground/assets/chessground.cburnett.css";

export default function PuzzleModal({ puzzle, onClose, onSolvedNext }) {
  const mount = useRef(null);
  const cgRef = useRef(null);
  const chessRef = useRef(null);

  const [moveIndex, setMoveIndex] = useState(0);
  const [msg, setMsg] = useState("");

  // Reset chess when puzzle changes
  useEffect(() => {
    if (!puzzle) return;
    chessRef.current = new Chess(puzzle.fen);
    setMoveIndex(0);
    setMsg("");
  }, [puzzle]);

  // Generate allowed move for current index
  const getDestsForPuzzle = () => {
    const dests = new Map();
    if (!chessRef.current) return dests;
    const moves = chessRef.current.moves({ verbose: true });
    moves.forEach(m => {
      const from = m.from;
      const to = m.to;
      if (!dests.has(from)) dests.set(from, []);
      dests.get(from).push(to);
    });
    return dests;
  };


  // Initialize / update Chessground
  useEffect(() => {
    if (!puzzle || !mount.current || !chessRef.current) return;

    if (cgRef.current) cgRef.current.destroy();

    const turnColor = chessRef.current.turn() === "w" ? "white" : "black";

    cgRef.current = Chessground(mount.current, {
      fen: chessRef.current.fen(),
      orientation: turnColor,
      turnColor,
      movable: {
        free: false,
        color: turnColor,
        dests: getDestsForPuzzle(),
        showDests: true,
        events: { after: handleMove },
      },
    });

    return () => cgRef.current && cgRef.current.destroy();
    // eslint-disable-next-line
  }, [puzzle, moveIndex]);

  const handleMove = (from, to) => {
    const chess = chessRef.current;
    if (!chess || !puzzle) return false;

    const expectedMove = puzzle.moves[moveIndex];
    const moveUCI = from + to;

    const move = chess.move({ from, to, promotion: "q" });
    if (!move) {
      setMsg("Illegal move!");
      return false;
    }

    if (moveUCI === expectedMove) {
      setMsg("✅ Correct move!");
      let nextIndex = moveIndex + 1;

      // Engine move
      if (puzzle.moves[nextIndex]) {
        const engineMove = puzzle.moves[nextIndex];
        chess.move({
          from: engineMove.slice(0, 2),
          to: engineMove.slice(2, 4),
          promotion: "q",
        });
        nextIndex += 1;
      }

      setMoveIndex(nextIndex);
      const turnColor = chess.turn() === "w" ? "white" : "black";

      cgRef.current.set({
        fen: chess.fen(),
        movableColor: turnColor,
        dests: getDestsForPuzzle(),
      });

      // Puzzle solved
      if (nextIndex >= puzzle.moves.length) {
        setMsg("🎉 Puzzle Solved!");
        onSolvedNext();
      }
    } else {
      // Wrong move: undo + feedback
      setMsg("❌ Try again");
      chess.undo(); // take back the bad move
    
      const turnColor = chess.turn() === "w" ? "white" : "black";
    
      cgRef.current.set({
        fen: chess.fen(),
        turnColor,
        movable: {
          free: false,
          color: turnColor,
          dests: getDestsForPuzzle(),   // ✅ recalc legal moves
          showDests: true,
          events: { after: handleMove },
        },
        highlight: {
          lastMove: [from, to], // optional: show wrong attempt
        },
      });
    }
    

    return true;
  };

  if (!puzzle) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          background: "#fff",
          padding: 16,
          width: "90%",
          maxWidth: 900,
          display: "grid",
          gridTemplateColumns: "minmax(320px,480px) 1fr",
          gap: 16,
        }}
      >
        <div ref={mount} style={{ width: "100%", aspectRatio: "1/1" }} />
        <div>
          <h3>{puzzle.id} · {puzzle.rating}</h3>
          <div>{(puzzle.themes || []).join(", ")}</div>
          <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
            <button onClick={onClose}>Close</button>
            <button onClick={onSolvedNext}>Next Puzzle</button>
          </div>
          <div style={{ marginTop: 12 }}>{msg}</div>
        </div>
      </div>
    </div>
  );
}
