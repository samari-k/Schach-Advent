import py_cui
import json
from datetime import date


"""
Aufgaben von https://www.schach-tipps.de/schachtraining/taktik/matt-in-1-zug
Verkürzte algebraische Notation: https://de.wikipedia.org/wiki/Schachnotation#Verk%C3%BCrzte_algebraische_Notation
"""


class AdventCalendar:

    def __init__(self, master):
        self.master = master

        self.focus_border_color = py_cui.CYAN_ON_BLACK

        self.current_date = date.today().strftime("%d") if date.today() >= date(2021, 12, 1) else "00"
        self.closed = ['0'+str(i) for i in range(1, 10) if i > int(self.current_date)] + \
                      [str(i) for i in range(10, 25) if i > int(self.current_date)]
        self.opened = ['0'+str(i) for i in range(1, 10) if '0'+str(i) not in self.closed] + \
                      [str(i) for i in range(10, 25) if str(i) not in self.closed]

        self.pieces = {'--': '   ',
                       'sT': ' ♜ ', 'sS': ' ♞ ', 'sL': ' ♝ ', 'sD': ' ♛ ', 'sK': ' ♚ ', 'sB': ' ♟ ',
                       'wT': ' ♖ ', 'wS': ' ♘ ', 'wL': ' ♗ ', 'wD': ' ♕ ', 'wK': ' ♔ ', 'wB': ' ♙ '}

        self.solution = ""

        self.puzzles_scroll_menu = self.master.add_scroll_menu('Rätsel', 0, 0, column_span=1, row_span=6)
        self.puzzles_scroll_menu.add_key_command(py_cui.keys.KEY_ENTER, self.select_puzzle)
        self.puzzles_scroll_menu.set_focus_border_color(self.focus_border_color)
        with open("puzzles.json", "r") as puzzles_file:
            self.puzzles = json.load(puzzles_file)
        self.puzzles_scroll_menu.add_text_color_rule(self.current_date, py_cui.CYAN_ON_BLACK, 'contains')
        for c in self.closed:
            self.puzzles_scroll_menu.add_text_color_rule(c, py_cui.YELLOW_ON_BLACK, 'contains')
        for o in self.opened:
            self.puzzles_scroll_menu.add_text_color_rule(o, py_cui.GREEN_ON_BLACK, 'contains')

        self.puzzle_text_block = self.master.add_text_block('Advent, Advent!', 0, 1, column_span=3, row_span=5)
        self.puzzle_text_block.set_selectable(False)
        self.puzzle_text_block.add_text_color_rule(r'(\|.*)|(\+.*)|(a\s+b.*)|(h\s+g.*)', py_cui.BLACK_ON_WHITE,
                                                   'contains', match_type='region', region=[1, 37])

        self.answer_text_box = self.master.add_text_box('Antwort', 5, 1, column_span=3)
        self.answer_text_box.add_key_command(py_cui.keys.KEY_ENTER, self.check_solution)
        self.answer_text_box.set_selectable(False)
        self.answer_text_box.set_focus_border_color(self.focus_border_color)

        self.manual_button = self.master.add_button('Anleitung', 0, 4, command=self.show_manual)
        self.reset_button = self.master.add_button('reset', 1, 4, command=self.show_reset_popup)
        self.hint_button = self.master.add_button('Hinweis', 5, 4, command=self.show_hint)

        self.load_scroll_menu()
        self.disable_hint()
        self.show_manual()

    def save(self):
        with open("puzzles.json", "w") as puzzles_file:
            json.dump(self.puzzles, puzzles_file)

    def board_to_string(self, board, flip: bool = False):
        # flip Board if it's black's turn

        border = "   +-------------------------------+\n"

        if not flip:
            letter_row = "     a   b   c   d   e   f   g   h \n"
            board_string = letter_row + border
            i = 8
        else:
            letter_row = "     h   g   f   e   d   c   b   a \n"
            board_string = border
            i = 1

        for row in board:
            board_string += f"  {int(i)}|"
            for field in row:
                board_string += self.pieces[field] + '|'
            board_string += "\n"

            if (i > 1 and not flip) or (i < 8 and flip):
                board_string += "   |---+---+---+---+---+---+---+---|\n"

            i = i-1 if not flip else i+1

        if not flip:
            board_string += border
        else:
            board_string += (border + letter_row)
        return board_string

    def load_scroll_menu(self):
        self.puzzles_scroll_menu.clear()
        for puzzle in self.puzzles:
            self.puzzles_scroll_menu.add_item(puzzle)

    def select_puzzle(self):
        self.answer_text_box._text_color_rules.clear()
        puzzle_name = self.puzzles_scroll_menu.get()
        if puzzle_name[-2:] not in self.closed:
            self.puzzle_text_block.clear()
            puzzle = self.puzzles.get(puzzle_name)
            flip = True if puzzle["turn"] == "schwarz" else False
            self.puzzle_text_block.set_text(self.board_to_string(puzzle.get("board"), flip) +
                                            "\n Matt in einem Zug." +
                                            "\n " + puzzle.get("turn").capitalize() + " am Zug.")
            self.puzzle_text_block.set_title(puzzle_name)
            self.solution = puzzle.get("solution")
            if puzzle["solved"]:
                self.color_solved()
                self.answer_text_box.set_text(puzzle["solution"])
                self.disable_hint()
            else:
                self.answer_text_box.set_color(py_cui.WHITE_ON_BLACK)
                self.answer_text_box.clear()
                self.master.move_focus(self.answer_text_box)
                self.enable_hint()
                self.answer_text_box.set_selectable(True)
        else:
            self.master.show_message_popup(title="STOP", text="Hierfür musst du noch warten.",
                                           color=py_cui.YELLOW_ON_BLACK)

    def color_solved(self):
        self.answer_text_box.add_text_color_rule(self.solution, py_cui.BLACK_ON_GREEN, 'startswith')
        self.answer_text_box.set_selectable(False)

    def check_solution(self):
        answer = self.answer_text_box.get()
        if answer == self.solution:
            self.master.show_message_popup(title="Super!", text="Das war richtig.", color=py_cui.WHITE_ON_GREEN)
            self.color_solved()
            puzzle_name = self.puzzles_scroll_menu.get()
            puzzle = self.puzzles.get(puzzle_name)
            puzzle["solved"] = 1
            self.rename_puzzle(puzzle_name)
            self.master.move_focus(self.puzzles_scroll_menu)
            self.disable_hint()
        else:
            self.master.show_message_popup(title="Leider falsch..", text="Versuch es noch einmal.",
                                           color=py_cui.WHITE_ON_RED)
            self.master.move_focus(self.answer_text_box)

    def rename_puzzle(self, puzzle_name):
        if puzzle_name[-1] == "*":
            new_name = puzzle_name[:-1]
        else:
            new_name = puzzle_name+"*"
        new_puzzles_dict = {new_name if k == puzzle_name else k: v for k, v in self.puzzles.items()}
        self.puzzles = new_puzzles_dict
        self.save()
        self.load_scroll_menu()

    def show_reset_popup(self):
        self.master.show_yes_no_popup("Spielstand zurücksetzen?", command=self.reset)

    def reset(self, reset_value):
        if reset_value:
            for puzzle_name in self.puzzles:
                puzzle = self.puzzles.get(puzzle_name)
                if puzzle['solved'] == 1:
                    puzzle['solved'] = 0
                    self.rename_puzzle(puzzle_name)
            self.answer_text_box.clear()
        self.select_puzzle()

    def show_hint(self):
        self.answer_text_box.set_text(self.solution[0])
        self.master.move_focus(self.answer_text_box)
        self.disable_hint()

    def disable_hint(self):
        self.hint_button.set_color(py_cui.WHITE_ON_BLACK)
        self.hint_button.set_selectable(False)

    def enable_hint(self):
        self.hint_button.set_color(py_cui.BLUE_ON_BLACK)
        self.hint_button.set_selectable(True)

    def show_manual(self):
        text = "\n" \
               "Navigation:\n" \
               "-----------\n" \
               "  Benutze die Pfeiltasten um zwischen den Feldern\n" \
               "  und den Rätseln zu navigieren. Enter wählt ein \n" \
               "  Feld, Button oder Rätsel aus. Mit Escape lässt \n" \
               "  sich die Auswahl eines Feldes beenden.\n\n" \
               "Notation:\n" \
               "---------\n" \
               "  Die Antwort wird in der verkürzten algebraischen\n" \
               "  Notation angegeben, wobei hier auch der Bauer ein \n" \
               "  voran gestelltes 'B' erwartet. \n\n" \
               "  Beispiel: Dg6# wenn die Dame auf das Feld g6 zieht.\n" \
               "  und den gegnerischen König Matt setzt.\n" \
               "  Wenn bei dem Zug eine gegnerische Figur geschlagen\n" \
               "  wird, kommt zwischen Figur und Zielfeld ein x: \n" \
               "  Sxc4# bedeutet also: Springer zieht nach c4, schlägt \n" \
               "  dort eine gegnerische Figur und setzt den König matt.\n\n" \
               "  Mehr Infos: de.wikipedia.org/wiki/Schachnotation"
        self.puzzle_text_block.set_text(text)
        self.puzzle_text_block.set_title("Spielanleitung")
        self.disable_hint()


if __name__ == '__main__':
    root = py_cui.PyCUI(12, 5)
    root.toggle_unicode_borders()
    root.set_title('Advent, Advent!')
    calendar = AdventCalendar(root)

    root.start()
