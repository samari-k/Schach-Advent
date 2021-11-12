
"""
Matt in einem Zug, Aufgaben von https://www.schach-tipps.de/schachtraining/taktik/matt-in-1-zug
"""

import py_cui
import json
from datetime import date


class AdventCalendar:

    def __init__(self, master):
        self.master = master

        self.current_date = date.today().strftime("%d") if date.today() >= date(2021, 11, 1) else 0
        self.closed = ['0'+str(i) for i in range(1, 10) if i > int(self.current_date)] + \
                      [str(i) for i in range(10, 25) if i > int(self.current_date)]
        self.opened = ['0'+str(i) for i in range(1, 10) if '0'+str(i) not in self.closed] + \
                      [str(i) for i in range(10, 25) if str(i) not in self.closed]

        self.start_board = [['sT', 'sS', 'sL', 'sD', 'sK', 'sL', 'sS', 'sT'],
                            ['sB', 'sB', 'sB', 'sB', 'sB', 'sB', 'sB', 'sB'],
                            ['--', '--', '--', '--', '--', '--', '--', '--'],
                            ['--', '--', '--', '--', '--', '--', '--', '--'],
                            ['--', '--', '--', '--', '--', '--', '--', '--'],
                            ['--', '--', '--', '--', '--', '--', '--', '--'],
                            ['wB', 'wB', 'wB', 'wB', 'wB', 'wB', 'wB', 'wB'],
                            ['wT', 'wS', 'wL', 'wD', 'wK', 'wL', 'wS', 'wT']]

        self.pieces = {'--': '   ',
                       'sT': ' ♜ ', 'sS': ' ♞ ', 'sL': ' ♝ ', 'sD': ' ♛ ', 'sK': ' ♚ ', 'sB': ' ♟ ',
                       'wT': ' ♖ ', 'wS': ' ♘ ', 'wL': ' ♗ ', 'wD': ' ♕ ', 'wK': ' ♔ ', 'wB': ' ♙ '}

        self.solution = ""

        self.puzzles_scroll_menu = self.master.add_scroll_menu('Türchen', 0, 0, column_span=7, row_span=6)
        self.puzzles_scroll_menu.add_key_command(py_cui.keys.KEY_ENTER, self.select_puzzle)

        with open("puzzles.json", "r") as puzzles_file:
            self.puzzles = json.load(puzzles_file)
        for puzzle in self.puzzles:
            self.puzzles_scroll_menu.add_item(puzzle)

        self.puzzles_scroll_menu.add_text_color_rule(self.current_date, py_cui.GREEN_ON_BLACK, 'endswith')
        for c in self.closed:
            self.puzzles_scroll_menu.add_text_color_rule(c, py_cui.YELLOW_ON_BLACK, 'endswith')
        for o in self.opened:
            self.puzzles_scroll_menu.add_text_color_rule(o, py_cui.CYAN_ON_BLACK, 'endswith')
        self.master.move_focus(self.puzzles_scroll_menu)

        self.puzzle_text_block = self.master.add_text_block('Rätsel', 0, 7, column_span=10, row_span=5)
        self.puzzle_text_block.set_selectable(False)
        self.puzzle_text_block.set_text(self.board_to_string(self.start_board) +
                                        "Bitte wähle aus der Liste links ein Türchen aus.\n"
                                        "(Nutze die Pfeiltasten zum Navigieren und Enter\n"
                                        "zum Auswählen.")
        self.puzzle_text_block.add_text_color_rule('(\|.*)|(\+.*)|(a\s+b.*)', py_cui.BLACK_ON_WHITE, 'contains')

        self.answer_text_box = self.master.add_text_box('Antwort', 5, 7, column_span=7)
        self.answer_text_box.add_key_command(py_cui.keys.KEY_ENTER, self.check_solution)

        self.reset_button = self.master.add_button('reset', 5, 14, column_span=3, command=self.show_reset_popup)

    def save(self):
        with open("puzzles.json", "w") as puzzles_file:
            json.dump(self.puzzles, puzzles_file)

    def board_to_string(self, board):
        board_string = "     a   b   c   d   e   f   g   h \n" \
                       "   +-------------------------------+\n"
        i = 8
        for row in board:
            board_string += f"  {int(i)}|"
            for field in row:
                board_string += self.pieces[field] + '|'
            board_string += "\n"
            if i > 1:
                board_string += "   |---+---+---+---+---+---+---+---|\n"
            if i == 1:
                board_string += "   +-------------------------------+\n\n"
            i -= 1
        return board_string

    def select_puzzle(self):
        puzzle_name = self.puzzles_scroll_menu.get()
        if puzzle_name[-2:] not in self.closed:
            self.puzzle_text_block.clear()
            puzzle = self.puzzles.get(puzzle_name)
            self.puzzle_text_block.set_text(self.board_to_string(puzzle.get("board")) +
                                            puzzle.get("description"))
            self.solution = puzzle.get("solution")
            if puzzle["solved"]:
                self.answer_text_box.set_color(py_cui.BLACK_ON_GREEN)
                self.answer_text_box.set_text(puzzle["solution"])
                self.answer_text_box.set_selectable(False)
            else:
                self.answer_text_box.set_color(py_cui.WHITE_ON_BLACK)
                self.answer_text_box.clear()
                self.master.move_focus(self.answer_text_box)
        else:
            self.master.show_message_popup(title="STOP", text="Hierfür musst du noch warten.",
                                           color=py_cui.WHITE_ON_RED)

    def check_solution(self):
        answer = self.answer_text_box.get()
        if answer == self.solution:
            self.master.show_message_popup(title="Richtig", text="Super!", color=py_cui.BLACK_ON_GREEN)
            self.answer_text_box.set_color(py_cui.BLACK_ON_GREEN)
            puzzle_name = self.puzzles_scroll_menu.get()
            puzzle = self.puzzles.get(puzzle_name)
            puzzle["solved"] = 1
            self.save()
        else:
            self.master.show_message_popup(title="Falsch", text="Leider nein...", color=py_cui.WHITE_ON_RED)

    def show_reset_popup(self):
        self.master.show_yes_no_popup("Spielstand zurücksetzen?", command=self.reset)

    def reset(self, value):
        # TODO
        pass


if __name__ == '__main__':
    root = py_cui.PyCUI(12, 18)
    root.toggle_unicode_borders()
    root.set_title('Advent, Advent!')
    calendar = AdventCalendar(root)

    root.start()
