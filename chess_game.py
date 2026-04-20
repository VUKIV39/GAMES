from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

FILES = "abcdefgh"
RANKS = "12345678"


@dataclass(frozen=True)
class Piece:
    color: str  # 'w' or 'b'
    kind: str   # 'P', 'N', 'B', 'R', 'Q', 'K'

    def symbol(self) -> str:
        return self.kind if self.color == "w" else self.kind.lower()


Square = str
Move = Tuple[Square, Square, Optional[str]]


class ChessGame:
    """Console chess game with legal moves, check and checkmate detection.

    Supported: normal piece movement, capture, promotion to Q/R/B/N, check/checkmate/stalemate.
    Not implemented: castling and en passant.
    """

    def __init__(self) -> None:
        self.board: Dict[Square, Piece] = {}
        self.turn = "w"
        self.setup_board()

    def setup_board(self) -> None:
        self.board.clear()
        back = "RNBQKBNR"
        for i, f in enumerate(FILES):
            self.board[f + "2"] = Piece("w", "P")
            self.board[f + "7"] = Piece("b", "P")
            self.board[f + "1"] = Piece("w", back[i])
            self.board[f + "8"] = Piece("b", back[i])

    # ---------- Utilities ----------
    @staticmethod
    def in_bounds(file_idx: int, rank_idx: int) -> bool:
        return 0 <= file_idx < 8 and 0 <= rank_idx < 8

    @staticmethod
    def to_square(file_idx: int, rank_idx: int) -> Square:
        return FILES[file_idx] + RANKS[rank_idx]

    @staticmethod
    def from_square(square: Square) -> Tuple[int, int]:
        return FILES.index(square[0]), RANKS.index(square[1])

    def piece_at(self, square: Square) -> Optional[Piece]:
        return self.board.get(square)

    def king_square(self, color: str) -> Optional[Square]:
        for sq, piece in self.board.items():
            if piece.color == color and piece.kind == "K":
                return sq
        return None

    def opposite(self, color: str) -> str:
        return "b" if color == "w" else "w"

    # ---------- Move generation ----------
    def pseudo_moves_for_piece(self, square: Square, piece: Piece) -> List[Move]:
        f, r = self.from_square(square)
        moves: List[Move] = []

        if piece.kind == "P":
            dir_rank = 1 if piece.color == "w" else -1
            start_rank = 1 if piece.color == "w" else 6
            promo_rank = 7 if piece.color == "w" else 0

            # one step forward
            nr = r + dir_rank
            if self.in_bounds(f, nr):
                front = self.to_square(f, nr)
                if self.piece_at(front) is None:
                    if nr == promo_rank:
                        for promo in "QRBN":
                            moves.append((square, front, promo))
                    else:
                        moves.append((square, front, None))

                    # two steps from start
                    if r == start_rank:
                        nr2 = r + 2 * dir_rank
                        front2 = self.to_square(f, nr2)
                        if self.piece_at(front2) is None:
                            moves.append((square, front2, None))

            # captures
            for df in (-1, 1):
                nf, nr = f + df, r + dir_rank
                if self.in_bounds(nf, nr):
                    target = self.to_square(nf, nr)
                    victim = self.piece_at(target)
                    if victim is not None and victim.color != piece.color:
                        if nr == promo_rank:
                            for promo in "QRBN":
                                moves.append((square, target, promo))
                        else:
                            moves.append((square, target, None))

        elif piece.kind == "N":
            for df, dr in [
                (1, 2), (2, 1), (2, -1), (1, -2),
                (-1, -2), (-2, -1), (-2, 1), (-1, 2),
            ]:
                nf, nr = f + df, r + dr
                if not self.in_bounds(nf, nr):
                    continue
                target = self.to_square(nf, nr)
                occ = self.piece_at(target)
                if occ is None or occ.color != piece.color:
                    moves.append((square, target, None))

        elif piece.kind in ("B", "R", "Q"):
            directions = []
            if piece.kind in ("B", "Q"):
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            if piece.kind in ("R", "Q"):
                directions.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])

            for df, dr in directions:
                nf, nr = f + df, r + dr
                while self.in_bounds(nf, nr):
                    target = self.to_square(nf, nr)
                    occ = self.piece_at(target)
                    if occ is None:
                        moves.append((square, target, None))
                    else:
                        if occ.color != piece.color:
                            moves.append((square, target, None))
                        break
                    nf += df
                    nr += dr

        elif piece.kind == "K":
            for df in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    if df == 0 and dr == 0:
                        continue
                    nf, nr = f + df, r + dr
                    if not self.in_bounds(nf, nr):
                        continue
                    target = self.to_square(nf, nr)
                    occ = self.piece_at(target)
                    if occ is None or occ.color != piece.color:
                        moves.append((square, target, None))

        return moves

    def all_pseudo_moves(self, color: str) -> List[Move]:
        moves: List[Move] = []
        for sq, piece in self.board.items():
            if piece.color == color:
                moves.extend(self.pseudo_moves_for_piece(sq, piece))
        return moves

    def apply_move(self, move: Move) -> None:
        src, dst, promo = move
        piece = self.board.pop(src)
        self.board.pop(dst, None)
        if piece.kind == "P" and promo is not None:
            self.board[dst] = Piece(piece.color, promo)
        else:
            self.board[dst] = piece

    def legal_moves(self, color: str) -> List[Move]:
        legal: List[Move] = []
        for move in self.all_pseudo_moves(color):
            snapshot = dict(self.board)
            self.apply_move(move)
            if not self.in_check(color):
                legal.append(move)
            self.board = snapshot
        return legal

    # ---------- Check logic ----------
    def square_attacked_by(self, square: Square, attacker_color: str) -> bool:
        for move in self.all_pseudo_moves(attacker_color):
            _, dst, _ = move
            if dst == square:
                return True
        return False

    def in_check(self, color: str) -> bool:
        king = self.king_square(color)
        if king is None:
            return False
        return self.square_attacked_by(king, self.opposite(color))

    def game_state(self) -> str:
        moves = self.legal_moves(self.turn)
        if moves:
            return "check" if self.in_check(self.turn) else "ongoing"
        if self.in_check(self.turn):
            return "checkmate"
        return "stalemate"

    # ---------- I/O ----------
    def print_board(self) -> None:
        print("\n    a b c d e f g h")
        for rank in reversed(RANKS):
            row = [rank]
            for file in FILES:
                piece = self.piece_at(file + rank)
                row.append(piece.symbol() if piece else ".")
            print(" ".join(row))
        print()

    @staticmethod
    def parse_move(text: str) -> Optional[Move]:
        s = text.strip().lower()
        if len(s) not in (4, 5):
            return None
        src, dst = s[:2], s[2:4]
        if src[0] not in FILES or src[1] not in RANKS:
            return None
        if dst[0] not in FILES or dst[1] not in RANKS:
            return None
        promo = None
        if len(s) == 5:
            p = s[4].upper()
            if p not in "QRBN":
                return None
            promo = p
        return src, dst, promo

    def move_to_text(self, move: Move) -> str:
        src, dst, promo = move
        return f"{src}{dst}{promo.lower() if promo else ''}"

    def play(self) -> None:
        print("Chess Game")
        print("Enter moves as: e2e4 or e7e8q (promotion)")
        print("Type 'quit' to exit.\n")

        while True:
            self.print_board()
            state = self.game_state()
            if state == "checkmate":
                winner = "White" if self.turn == "b" else "Black"
                print(f"Checkmate! {winner} wins.")
                return
            if state == "stalemate":
                print("Stalemate! Draw.")
                return
            if state == "check":
                print(f"{('White' if self.turn == 'w' else 'Black')} is in check.")

            side = "White" if self.turn == "w" else "Black"
            raw = input(f"{side} to move: ").strip()
            if raw.lower() in {"quit", "exit"}:
                print("Game ended.")
                return

            parsed = self.parse_move(raw)
            if not parsed:
                print("Invalid format. Use e2e4 or e7e8q.")
                continue

            legal = self.legal_moves(self.turn)
            if parsed not in legal:
                # allow auto-queen if user omits promotion letter
                src, dst, promo = parsed
                if promo is None and (src, dst, "Q") in legal:
                    parsed = (src, dst, "Q")
                else:
                    preview = ", ".join(self.move_to_text(m) for m in legal[:12])
                    more = "..." if len(legal) > 12 else ""
                    print(f"Illegal move. Examples of legal moves: {preview}{more}")
                    continue

            self.apply_move(parsed)
            self.turn = self.opposite(self.turn)


if __name__ == "__main__":
    ChessGame().play()
