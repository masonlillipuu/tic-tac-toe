"""Tic-Tac-Toe vs AI (tkinter). Eestikeelne kasutajaliides.

Raskusaste määrab mängulaua suuruse:
  Kerge    -> klassikaline 3x3, 3 järjest võidab
  Keskmine -> 4x4, 4 järjest võidab
  Raske    -> 5x5, 4 järjest võidab
"""

import json
import math
import random
import resource
import sys
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from functools import lru_cache
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "game_history.json"

RESULT_LABELS = {"win": "Võit", "loss": "Kaotus", "draw": "Viik"}

HUMAN = "X"
AI = "O"
EMPTY = " "

LEVELS = {
    "Kerge": {"size": 3, "win_len": 3, "depth": 9, "label": "Kerge — klassikaline 3×3"},
    "Keskmine": {"size": 4, "win_len": 4, "depth": 5, "label": "Keskmine — 4×4"},
    "Raske": {"size": 5, "win_len": 4, "depth": 4, "label": "Raske — 5×5"},
}

CELL_STYLE = {
    3: {"font": 28, "width": 3},
    4: {"font": 20, "width": 3},
    5: {"font": 16, "width": 2},
}


def get_memory_mb():
    """Protsessi kasutatud mälu (tipphetk) megabaitides."""
    peak_kb_or_b = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return peak_kb_or_b / (1024 * 1024)
    return peak_kb_or_b / 1024


@lru_cache(maxsize=None)
def generate_lines(size, win_len):
    lines = []
    for r in range(size):
        for c in range(size - win_len + 1):
            lines.append(tuple(r * size + c + k for k in range(win_len)))
    for c in range(size):
        for r in range(size - win_len + 1):
            lines.append(tuple((r + k) * size + c for k in range(win_len)))
    for r in range(size - win_len + 1):
        for c in range(size - win_len + 1):
            lines.append(tuple((r + k) * size + c + k for k in range(win_len)))
    for r in range(size - win_len + 1):
        for c in range(win_len - 1, size):
            lines.append(tuple((r + k) * size + c - k for k in range(win_len)))
    return tuple(lines)


def check_winner(board, size, win_len):
    for line in generate_lines(size, win_len):
        first = board[line[0]]
        if first != EMPTY and all(board[i] == first for i in line):
            return first
    if EMPTY not in board:
        return "Draw"
    return None


def evaluate_board(board, size, win_len, mark, opponent):
    score = 0
    for line in generate_lines(size, win_len):
        cells = [board[i] for i in line]
        if opponent not in cells:
            cnt = cells.count(mark)
            if cnt:
                score += 10 ** cnt
        if mark not in cells:
            cnt = cells.count(opponent)
            if cnt:
                score -= 10 ** cnt
    return score


def win_probability_pct(board, size, win_len):
    """Umbkaudne hinnang sinu (X) võiduvõimalusele praeguse seisu põhjal."""
    winner = check_winner(board, size, win_len)
    if winner == HUMAN:
        return 100.0
    if winner == AI:
        return 0.0
    if winner == "Draw":
        return 50.0

    score = evaluate_board(board, size, win_len, HUMAN, AI)
    temperature = 150.0
    pct = 100.0 / (1.0 + math.exp(-score / temperature))
    return min(98.0, max(2.0, pct))


def minimax_ab(board, depth, alpha, beta, maximizing, size, win_len):
    winner = check_winner(board, size, win_len)
    if winner == AI:
        return 1_000_000 + depth
    if winner == HUMAN:
        return -1_000_000 - depth
    if winner == "Draw":
        return 0
    if depth == 0:
        return evaluate_board(board, size, win_len, AI, HUMAN)

    empties = [i for i, v in enumerate(board) if v == EMPTY]
    if maximizing:
        value = -math.inf
        for i in empties:
            board[i] = AI
            value = max(value, minimax_ab(board, depth - 1, alpha, beta, False, size, win_len))
            board[i] = EMPTY
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = math.inf
        for i in empties:
            board[i] = HUMAN
            value = min(value, minimax_ab(board, depth - 1, alpha, beta, True, size, win_len))
            board[i] = EMPTY
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def best_move(board, size, win_len, depth):
    empties = [i for i, v in enumerate(board) if v == EMPTY]
    random.shuffle(empties)
    best_score = -math.inf
    move = empties[0]
    alpha, beta = -math.inf, math.inf
    for i in empties:
        board[i] = AI
        score = minimax_ab(board, depth - 1, alpha, beta, False, size, win_len)
        board[i] = EMPTY
        if score > best_score:
            best_score = score
            move = i
        alpha = max(alpha, score)
    return move


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe vs AI")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # macOS'i natiivne "aqua" teema eirab tk.Button'i bg/fg värve,
        # mistõttu nupud renderdusid valgena. "clam" teema austab värve.
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._configure_button_styles()

        self.buttons = []
        self.difficulty = tk.StringVar(value="Kerge")

        self.history = self.load_history()

        self._build_stats_section()
        self._build_difficulty_section()
        self._build_board_container()
        self._build_status()
        self._build_controls()
        self._build_history_section()

        self.start_new_level()
        self.refresh_stats()
        self.update_memory_label()

    # ---------- Stiil ----------
    def _configure_button_styles(self):
        for name, fg in (
            ("Cell.TButton", "#cdd6f4"),
            ("CellX.TButton", "#89b4fa"),
            ("CellO.TButton", "#f38ba8"),
        ):
            self.style.configure(
                name, background="#313244", foreground=fg,
                borderwidth=0, focuscolor="", relief="flat",
            )
            self.style.map(
                name,
                background=[("active", "#45475a"), ("disabled", "#313244")],
                foreground=[("disabled", fg)],
            )

        self.style.configure(
            "Primary.TButton",
            background="#89b4fa", foreground="#1e1e2e",
            borderwidth=0, focuscolor="", relief="flat",
        )
        self.style.map("Primary.TButton", background=[("active", "#74a8f5")])

        self.style.configure(
            "Danger.TButton",
            background="#f38ba8", foreground="#1e1e2e",
            borderwidth=0, focuscolor="", relief="flat",
        )
        self.style.map("Danger.TButton", background=[("active", "#e57a98")])

    # ---------- Statistika ----------
    def load_history(self):
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text())
            except Exception:
                pass
        return []

    def save_history(self):
        HISTORY_FILE.write_text(json.dumps(self.history, indent=2))

    def compute_stats(self):
        wins = sum(1 for g in self.history if g["result"] == "win")
        losses = sum(1 for g in self.history if g["result"] == "loss")
        draws = sum(1 for g in self.history if g["result"] == "draw")
        return {"wins": wins, "losses": losses, "draws": draws}

    def _build_stats_section(self):
        frame = tk.Frame(self.root, bg="#1e1e2e", padx=16, pady=12)
        frame.pack(fill="x")

        self.verdict_label = tk.Label(
            frame, text="", font=("Helvetica", 15, "bold"), bg="#1e1e2e"
        )
        self.verdict_label.pack()

        self.pct_label = tk.Label(
            frame, text="", font=("Helvetica", 11), fg="#cdd6f4", bg="#1e1e2e"
        )
        self.pct_label.pack(pady=(2, 8))

        self.bar_canvas = tk.Canvas(
            frame, width=320, height=16, bg="#313244", highlightthickness=0
        )
        self.bar_canvas.pack()

        score_frame = tk.Frame(frame, bg="#1e1e2e", pady=10)
        score_frame.pack(fill="x")

        self.wins_label = tk.Label(
            score_frame, text="", font=("Helvetica", 12, "bold"),
            fg="#a6e3a1", bg="#1e1e2e"
        )
        self.wins_label.pack(side="left", expand=True)

        self.draws_label = tk.Label(
            score_frame, text="", font=("Helvetica", 12, "bold"),
            fg="#f9e2af", bg="#1e1e2e"
        )
        self.draws_label.pack(side="left", expand=True)

        self.losses_label = tk.Label(
            score_frame, text="", font=("Helvetica", 12, "bold"),
            fg="#f38ba8", bg="#1e1e2e"
        )
        self.losses_label.pack(side="left", expand=True)

        self.memory_label = tk.Label(
            frame, text="", font=("Helvetica", 9), fg="#6c7086", bg="#1e1e2e"
        )
        self.memory_label.pack(pady=(6, 0))

    def update_memory_label(self):
        self.memory_label.config(text=f"AI mälukasutus: {get_memory_mb():.2f} MB")
        self.root.after(1000, self.update_memory_label)

    def refresh_stats(self):
        stats = self.compute_stats()
        wins = stats["wins"]
        losses = stats["losses"]
        draws = stats["draws"]
        total = wins + losses + draws

        win_pct = (wins / total * 100) if total else 0.0
        loss_pct = (losses / total * 100) if total else 0.0
        draw_pct = (draws / total * 100) if total else 0.0

        if total == 0:
            verdict, color = "Alusta mängu!", "#cdd6f4"
        elif win_pct > loss_pct:
            verdict, color = "Sa oled hetkel VÕITMAS", "#a6e3a1"
        elif win_pct < loss_pct:
            verdict, color = "Sa oled hetkel KAOTAMAS", "#f38ba8"
        else:
            verdict, color = "Hetkel viigis", "#f9e2af"

        self.verdict_label.config(text=verdict, fg=color)
        self.pct_label.config(
            text=f"Võite: {win_pct:.1f}%   Viike: {draw_pct:.1f}%   Kaotusi: {loss_pct:.1f}%"
        )

        self.wins_label.config(text=f"Võidud\n{wins}")
        self.draws_label.config(text=f"Viigid\n{draws}")
        self.losses_label.config(text=f"Kaotused\n{losses}")

        self.bar_canvas.delete("all")
        width = 320
        w_w = width * win_pct / 100
        d_w = width * draw_pct / 100
        l_w = width * loss_pct / 100
        x = 0
        if w_w:
            self.bar_canvas.create_rectangle(x, 0, x + w_w, 16, fill="#a6e3a1", width=0)
            x += w_w
        if d_w:
            self.bar_canvas.create_rectangle(x, 0, x + d_w, 16, fill="#f9e2af", width=0)
            x += d_w
        if l_w:
            self.bar_canvas.create_rectangle(x, 0, x + l_w, 16, fill="#f38ba8", width=0)

    # ---------- Raskusaste ----------
    def _build_difficulty_section(self):
        frame = tk.Frame(self.root, bg="#1e1e2e", padx=16, pady=4)
        frame.pack(fill="x")

        tk.Label(
            frame, text="Raskusaste:", font=("Helvetica", 10),
            fg="#cdd6f4", bg="#1e1e2e"
        ).pack(anchor="w")

        radio_frame = tk.Frame(frame, bg="#1e1e2e")
        radio_frame.pack(anchor="w")

        for key, cfg in LEVELS.items():
            tk.Radiobutton(
                radio_frame, text=cfg["label"], value=key, variable=self.difficulty,
                command=self.on_difficulty_change,
                bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                activebackground="#1e1e2e", activeforeground="#cdd6f4",
                font=("Helvetica", 10)
            ).pack(side="left", padx=4)

    def on_difficulty_change(self):
        self.start_new_level()

    # ---------- Mängulaud ----------
    def _build_board_container(self):
        self.board_container = tk.Frame(self.root, bg="#1e1e2e", padx=16, pady=8)
        self.board_container.pack()

    def rebuild_board_widgets(self):
        for widget in self.board_container.winfo_children():
            widget.destroy()

        self.buttons = []
        style = CELL_STYLE[self.size]
        for name in ("Cell.TButton", "CellX.TButton", "CellO.TButton"):
            self.style.configure(
                name,
                font=("Helvetica", style["font"], "bold"),
                padding=(0, style["font"] // 2 + 6),
            )
        for i in range(self.size * self.size):
            btn = ttk.Button(
                self.board_container, text=" ", width=style["width"],
                style="Cell.TButton",
                command=lambda i=i: self.on_cell_click(i)
            )
            btn.grid(row=i // self.size, column=i % self.size, padx=3, pady=3)
            self.buttons.append(btn)

    def _build_status(self):
        self.status_label = tk.Label(
            self.root, text="Sinu käik (X)", font=("Helvetica", 12),
            fg="#89b4fa", bg="#1e1e2e", pady=6
        )
        self.status_label.pack()

        winprob_frame = tk.Frame(self.root, bg="#1e1e2e")
        winprob_frame.pack(pady=(0, 4))

        self.winprob_label = tk.Label(
            winprob_frame, text="", font=("Helvetica", 11, "bold"), bg="#1e1e2e"
        )
        self.winprob_label.pack()

        self.winprob_canvas = tk.Canvas(
            winprob_frame, width=220, height=10, bg="#313244", highlightthickness=0
        )
        self.winprob_canvas.pack(pady=(2, 0))

    def update_win_probability(self):
        pct = win_probability_pct(self.board, self.size, self.win_len)
        if pct >= 60:
            color = "#a6e3a1"
        elif pct <= 40:
            color = "#f38ba8"
        else:
            color = "#f9e2af"
        self.winprob_label.config(
            text=f"Sinu võiduvõimalus praegu: {pct:.0f}%", fg=color
        )
        self.winprob_canvas.delete("all")
        width = 220
        fill_w = width * pct / 100
        self.winprob_canvas.create_rectangle(0, 0, width, 10, fill="#313244", width=0)
        self.winprob_canvas.create_rectangle(0, 0, fill_w, 10, fill=color, width=0)

    def _build_controls(self):
        frame = tk.Frame(self.root, bg="#1e1e2e", pady=10)
        frame.pack()

        self.style.configure("Primary.TButton", font=("Helvetica", 11), padding=(10, 6))
        self.style.configure("Danger.TButton", font=("Helvetica", 11), padding=(10, 6))

        ttk.Button(
            frame, text="Uus mäng", style="Primary.TButton",
            command=self.start_new_level,
        ).pack(side="left", padx=6)

        ttk.Button(
            frame, text="Lähtesta skoor", style="Danger.TButton",
            command=self.reset_stats,
        ).pack(side="left", padx=6)

    # ---------- Mängude ajalugu ----------
    def _build_history_section(self):
        frame = tk.Frame(self.root, bg="#1e1e2e", padx=16)
        frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            frame, text="Viimased mängud:", font=("Helvetica", 10, "bold"),
            fg="#cdd6f4", bg="#1e1e2e"
        ).pack(anchor="w")

        self.history_list = tk.Listbox(
            frame, height=5, font=("Helvetica", 10), bg="#313244",
            fg="#cdd6f4", highlightthickness=0, borderwidth=0,
            selectbackground="#45475a"
        )
        self.history_list.pack(fill="x", pady=(4, 0))
        self.refresh_history_list()

    def refresh_history_list(self):
        self.history_list.delete(0, tk.END)
        for game in reversed(self.history[-20:]):
            label = RESULT_LABELS.get(game["result"], game["result"])
            self.history_list.insert(
                tk.END, f"{game['timestamp']}  •  {label}  •  {game['difficulty']}"
            )

    # ---------- Mängu loogika ----------
    def start_new_level(self):
        cfg = LEVELS[self.difficulty.get()]
        self.size = cfg["size"]
        self.win_len = cfg["win_len"]
        self.depth = cfg["depth"]
        self.board = [EMPTY] * (self.size * self.size)
        self.game_over = False
        self.rebuild_board_widgets()
        self.status_label.config(text="Sinu käik (X)")
        self.update_win_probability()

    def on_cell_click(self, i):
        if self.game_over or self.board[i] != EMPTY:
            return

        self.board[i] = HUMAN
        self.buttons[i].config(text=HUMAN, style="CellX.TButton")
        self.update_win_probability()

        winner = check_winner(self.board, self.size, self.win_len)
        if winner:
            self.finish_round(winner)
            return

        self.status_label.config(text="AI mõtleb...")
        self.root.after(200, self.do_ai_move)

    def do_ai_move(self):
        move = best_move(self.board, self.size, self.win_len, self.depth)
        if move is not None:
            self.board[move] = AI
            self.buttons[move].config(text=AI, style="CellO.TButton")

        self.update_win_probability()

        winner = check_winner(self.board, self.size, self.win_len)
        if winner:
            self.finish_round(winner)
        else:
            self.status_label.config(text="Sinu käik (X)")

    def finish_round(self, winner):
        self.game_over = True
        for i, val in enumerate(self.board):
            if val == EMPTY:
                self.buttons[i].config(state="disabled")

        if winner == HUMAN:
            self.status_label.config(text="Sina võitsid! 🎉")
            result = "win"
        elif winner == AI:
            self.status_label.config(text="AI võitis.")
            result = "loss"
        else:
            self.status_label.config(text="Viik!")
            result = "draw"

        self.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": result,
            "difficulty": self.difficulty.get(),
        })
        self.save_history()
        self.refresh_stats()
        self.refresh_history_list()

    def reset_stats(self):
        self.history = []
        self.save_history()
        self.refresh_stats()
        self.refresh_history_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
