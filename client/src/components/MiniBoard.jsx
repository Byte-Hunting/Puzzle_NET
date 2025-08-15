// src/components/MiniBoard.jsx
import React, { useEffect, useRef } from "react";
import { Chessground } from "chessground";
import "chessground/assets/chessground.base.css";
import "chessground/assets/chessground.brown.css";
import "chessground/assets/chessground.cburnett.css";

export default function MiniBoard({ fen }) {
  const mount = useRef(null);
  const cg = useRef(null);

  useEffect(() => {
    if (!fen || !mount.current) return;
    // destroy previous if any
    if (cg.current && typeof cg.current.destroy === "function") {
      cg.current.destroy();
      cg.current = null;
    }

    // orientation from FEN: second field is side to move
    const orientation = fen.split(" ")[1] === "b" ? "black" : "white";

    try {
      cg.current = Chessground(mount.current, {
        fen,
        orientation,
        viewOnly: true,
        coordinates: false,
        highlight: { lastMove: false, check: false },
      });
    } catch (err) {
      // fail silently but avoid crashing
      console.error("MiniBoard Chessground init failed:", err);
    }

    return () => {
      if (cg.current && typeof cg.current.destroy === "function") {
        cg.current.destroy();
        cg.current = null;
      }
    };
  }, [fen]);

  return <div className="mini-board" ref={mount} />;
}
