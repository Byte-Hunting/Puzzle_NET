// src/components/PuzzlesGrid.jsx
import React from "react";
import PuzzleCard from "./PuzzleCard";

export default function PuzzlesGrid({ puzzles, onOpen }) {
  return (
    <div className="puzzles-grid">
      {puzzles.map((p) => (
        <PuzzleCard key={p.id} puzzle={p} onClick={onOpen} />
      ))}
    </div>
  );
}
