import tkinter as tk

# Unicode chess symbols
pieces_symbols = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
    '.': ' '
}

class ChessGame:
    def __init__(self):
        self.board = [
            list("rnbqkbnr"),
            list("pppppppp"),
            list("........"),
            list("........"),
            list("........"),
            list("........"),
            list("PPPPPPPP"),
            list("RNBQKBNR")
        ]
        self.turn = 'white'
        self.white_can_castle_kingside = True
        self.white_can_castle_queenside = True
        self.black_can_castle_kingside = True
        self.black_can_castle_queenside = True
        self.en_passant = None
        self.selected = None
        self.move_history = []
        self.promotion_choice = None

    def inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def get_piece(self, r, c):
        return self.board[r][c]

    def is_white(self, piece):
        return piece.isupper()

    def is_black(self, piece):
        return piece.islower()

    def color_turn(self, piece):
        return (self.turn == 'white' and self.is_white(piece)) or (self.turn == 'black' and self.is_black(piece))

    def make_move(self, r1, c1, r2, c2):
        piece = self.board[r1][c1]
        target = self.board[r2][c2]
        move_str = f"{piece}{r1}{c1}->{r2}{c2}"

        # handle en passant
        if piece.lower() == 'p' and self.en_passant == (r2, c2):
            if self.turn == 'white':
                self.board[r2 + 1][c2] = '.'
            else:
                self.board[r2 - 1][c2] = '.'

        # handle castling
        if piece.lower() == 'k':
            if self.turn == 'white':
                self.white_can_castle_kingside = self.white_can_castle_queenside = False
                if (r2, c2) == (7, 6):  # kingside
                    self.board[7][5], self.board[7][7] = self.board[7][7], '.'
                elif (r2, c2) == (7, 2):  # queenside
                    self.board[7][3], self.board[7][0] = self.board[7][0], '.'
            else:
                self.black_can_castle_kingside = self.black_can_castle_queenside = False
                if (r2, c2) == (0, 6):
                    self.board[0][5], self.board[0][7] = self.board[0][7], '.'
                elif (r2, c2) == (0, 2):
                    self.board[0][3], self.board[0][0] = self.board[0][0], '.'

        # move piece
        self.board[r2][c2] = piece
        self.board[r1][c1] = '.'

        # pawn promotion
        if piece.lower() == 'p' and (r2 == 0 or r2 == 7):
            promoted_piece = self.promotion_choice or ('Q' if piece.isupper() else 'q')
            self.board[r2][c2] = promoted_piece

        # set en passant
        self.en_passant = None
        if piece.lower() == 'p' and abs(r2 - r1) == 2:
            ep_row = (r1 + r2) // 2
            self.en_passant = (ep_row, c1)

        # switch turn
        self.turn = 'black' if self.turn == 'white' else 'white'
        self.move_history.append(move_str)

    def valid_moves(self, r, c):
        piece = self.board[r][c]
        if piece == '.':
            return []

        moves = []
        directions = {
            'P': [(-1, 0)], 'p': [(1, 0)],
            'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
            'N': [(-2, -1), (-2, 1), (2, -1), (2, 1),
                  (-1, -2), (-1, 2), (1, -2), (1, 2)],
            'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            'Q': [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)],
            'K': [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)],
        }

        color = 'white' if self.is_white(piece) else 'black'

        # Pawn moves
        if piece.lower() == 'p':
            direction = -1 if self.is_white(piece) else 1
            start_row = 6 if self.is_white(piece) else 1
            if self.inside(r + direction, c) and self.board[r + direction][c] == '.':
                moves.append((r + direction, c))
                if r == start_row and self.board[r + 2 * direction][c] == '.':
                    moves.append((r + 2 * direction, c))
            for dc in [-1, 1]:
                if self.inside(r + direction, c + dc):
                    target = self.board[r + direction][c + dc]
                    if target != '.' and ((self.is_white(piece) and self.is_black(target)) or (self.is_black(piece) and self.is_white(target))):
                        moves.append((r + direction, c + dc))
                    if (r + direction, c + dc) == self.en_passant:
                        moves.append((r + direction, c + dc))

        # Knights
        elif piece.lower() == 'n':
            for dr, dc in directions['N']:
                nr, nc = r + dr, c + dc
                if self.inside(nr, nc):
                    target = self.board[nr][nc]
                    if target == '.' or (self.is_white(piece) and self.is_black(target)) or (self.is_black(piece) and self.is_white(target)):
                        moves.append((nr, nc))

        # Rook, Bishop, Queen
        elif piece.lower() in ['r', 'b', 'q']:
            dirs = directions[piece.upper()]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while self.inside(nr, nc):
                    target = self.board[nr][nc]
                    if target == '.':
                        moves.append((nr, nc))
                    elif (self.is_white(piece) and self.is_black(target)) or (self.is_black(piece) and self.is_white(target)):
                        moves.append((nr, nc))
                        break
                    else:
                        break
                    nr += dr
                    nc += dc

        # King (with castling)
        elif piece.lower() == 'k':
            for dr, dc in directions['K']:
                nr, nc = r + dr, c + dc
                if self.inside(nr, nc):
                    target = self.board[nr][nc]
                    if target == '.' or (self.is_white(piece) and self.is_black(target)) or (self.is_black(piece) and self.is_white(target)):
                        moves.append((nr, nc))
            # castling
            if color == 'white' and r == 7 and c == 4:
                if self.white_can_castle_kingside and self.board[7][5] == '.' and self.board[7][6] == '.':
                    moves.append((7, 6))
                if self.white_can_castle_queenside and self.board[7][1] == '.' and self.board[7][2] == '.' and self.board[7][3] == '.':
                    moves.append((7, 2))
            if color == 'black' and r == 0 and c == 4:
                if self.black_can_castle_kingside and self.board[0][5] == '.' and self.board[0][6] == '.':
                    moves.append((0, 6))
                if self.black_can_castle_queenside and self.board[0][1] == '.' and self.board[0][2] == '.' and self.board[0][3] == '.':
                    moves.append((0, 2))
        return moves


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess - Tkinter with Timer")
        self.game = ChessGame()
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        self.flipped = False

        # Timers: 10 minutes each
        self.white_time = 10 * 60
        self.black_time = 10 * 60
        self.timer_running = True

        self.create_timer_labels()
        self.create_board()
        self.draw_board()
        self.update_timer()

    def create_timer_labels(self):
        self.white_label = tk.Label(self.root, text="White: 10:00", font=("Arial", 14))
        self.white_label.pack()
        self.black_label = tk.Label(self.root, text="Black: 10:00", font=("Arial", 14))
        self.black_label.pack()

    def create_board(self):
        frame = tk.Frame(self.root)
        frame.pack()
        for r in range(8):
            for c in range(8):
                btn = tk.Button(frame, width=4, height=2, font=("Arial", 24),
                                command=lambda r=r, c=c: self.on_click(r, c))
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

    def get_display_coords(self, r, c):
        return (7 - r, 7 - c) if self.flipped else (r, c)

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                dr, dc = self.get_display_coords(r, c)
                piece = self.game.get_piece(r, c)
                symbol = pieces_symbols.get(piece, ' ')
                color = '#f0d9b5' if (dr + dc) % 2 == 0 else '#b58863'
                self.buttons[dr][dc].config(text=symbol, bg=color)

    def ask_promotion(self, color):
        win = tk.Toplevel(self.root)
        win.title("Choose Promotion Piece")
        tk.Label(win, text="Promote to:", font=("Arial", 14)).pack(pady=5)
        choice = tk.StringVar(value='Q' if color == 'white' else 'q')

        def select(piece):
            choice.set(piece)
            win.destroy()

        for piece in ['Q', 'R', 'B', 'N']:
            symbol = pieces_symbols[piece if color == 'white' else piece.lower()]
            tk.Button(win, text=symbol, font=("Arial", 20),
                      command=lambda p=piece: select(p if color == 'white' else p.lower())).pack(pady=3)
        win.wait_window()
        return choice.get()

    def on_click(self, dr, dc):
        if not self.timer_running:
            return

        if self.flipped:
            r, c = 7 - dr, 7 - dc
        else:
            r, c = dr, dc

        if self.game.selected:
            r1, c1 = self.game.selected
            valid = self.game.valid_moves(r1, c1)
            if (r, c) in valid:
                piece = self.game.get_piece(r1, c1)
                if piece.lower() == 'p' and (r == 0 or r == 7):
                    color = 'white' if self.game.is_white(piece) else 'black'
                    promo_choice = self.ask_promotion(color)
                    self.game.promotion_choice = promo_choice
                else:
                    self.game.promotion_choice = None

                self.game.make_move(r1, c1, r, c)
                self.flipped = not self.flipped
            self.game.selected = None
            self.draw_board()
        else:
            piece = self.game.get_piece(r, c)
            if piece != '.' and self.game.color_turn(piece):
                self.game.selected = (r, c)
                sr, sc = self.get_display_coords(r, c)
                self.buttons[sr][sc].config(bg='yellow')

    def update_timer(self):
        if self.timer_running:
            if self.game.turn == 'white':
                self.white_time -= 1
            else:
                self.black_time -= 1

            self.white_label.config(text=f"White: {self.format_time(self.white_time)}")
            self.black_label.config(text=f"Black: {self.format_time(self.black_time)}")

            if self.white_time <= 0:
                self.timer_running = False
                self.white_label.config(text="White: Time Over!")
                tk.messagebox.showinfo("Time Over", "Black wins on time!")
            elif self.black_time <= 0:
                self.timer_running = False
                self.black_label.config(text="Black: Time Over!")
                tk.messagebox.showinfo("Time Over", "White wins on time!")
            else:
                self.root.after(1000, self.update_timer)

    def format_time(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02}:{s:02}"


if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()
