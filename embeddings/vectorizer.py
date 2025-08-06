import numpy as np
import chess

PIECE_MAP = {
    'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
    'p': -1, 'n': -2, 'b': -3, 'r': -4, 'q': -5, 'k': -6,
}

def fen_to_array(fen):
    board = chess.Board(fen)
    arr = np.zeros(64, dtype=int)
    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            arr[i] = PIECE_MAP.get(piece.symbol(), 0)
    return arr

def embed_board(fen):
    arr = fen_to_array(fen)
    return arr.astype('float32')


#r6k/pp2r2p/4Rp1Q/3p4/8/1N1P2R1/PqP2bPP/7K b - - 0 24