import chess
import chess.svg
import cairosvg
from PIL import Image
import io

def fen_to_image(fen: str, size=(224, 224)) -> Image.Image:
    board = chess.Board(fen)
    svg = chess.svg.board(board)
    png_bytes = cairosvg.svg2png(bytestring=svg)
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    return img.resize(size)
