// src/components/PuzzleCard.jsx
import React from "react";
import MiniBoard from "./MiniBoard";

export default function PuzzleCard({ puzzle, onClick }) {
  return (
    <div className="puzzle-card" onClick={() => onClick(puzzle)} role="button">
      <MiniBoard fen={puzzle.fen} />
      <div style={{ padding: 10, fontSize: 13 }}>
        <div style={{ fontWeight: 700 }}>{puzzle.id}</div>
        <div style={{ marginTop: 6 }}>Rating: {puzzle.rating}</div>
        <div style={{ marginTop: 6, color: "#666", fontSize: 12 }}>
          Theme: {Array.isArray(puzzle.themes) ? puzzle.themes.join(", ") : puzzle.themes}
        </div>
      </div>
    </div>
  );
}
