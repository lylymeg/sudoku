import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout,
    QHBoxLayout, QPushButton, QComboBox, QLabel, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator
from sudoku_engine import SudokuEngine

class SudokuCell(QLineEdit):
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.is_initial = False

        self.setMaxLength(1)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Consolas", 18, QFont.Bold))

        # Restreindre la saisie aux chiffres de 1 à 9
        validator = QRegExpValidator(QRegExp("[1-9]"))
        self.setValidator(validator)

class SudokuGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = SudokuEngine()
        self.cells = {}
        self.initial_grid = []
        self.solution_grid = []

        self.init_ui()
        self.new_game()

    def init_ui(self):
        self.setWindowTitle("Sudoku Solver & Generator")
        self.setFixedSize(520, 620)

        # Style Sombre
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #E0E0E0; font-size: 14px; font-weight: bold; }
            QComboBox { 
                background-color: #1E1E1E; color: #00FF9D; border: 1px solid #333; 
                padding: 5px; border-radius: 4px; font-weight: bold;
            }
            QPushButton {
                background-color: #1E1E1E; color: #00FF9D; border: 1px solid #00FF9D;
                padding: 8px 15px; border-radius: 6px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #00FF9D; color: #121212; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Zone des Contrôles (Haut)
        controls_layout = QHBoxLayout()
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Facile", "Moyen", "Difficile"])

        btn_new = QPushButton("Nouvelle Partie")
        btn_new.clicked.connect(self.new_game)

        controls_layout.addWidget(QLabel("Difficulté :"))
        controls_layout.addWidget(self.diff_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(btn_new)

        main_layout.addLayout(controls_layout)
        main_layout.addSpacing(10)

        # Grille 9x9 (Centre)
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(2)

        for r in range(9):
            for c in range(9):
                cell = SudokuCell(r, c)
                cell.textChanged.connect(lambda text, row=r, col=c: self.on_cell_changed(row, col, text))
                self.cells[(r, c)] = cell

                # Appliquer les bordures pour délimiter les blocs 3x3
                border_top = "3px solid #00FF9D" if r % 3 == 0 else "1px solid #2A2A2A"
                border_left = "3px solid #00FF9D" if c % 3 == 0 else "1px solid #2A2A2A"
                border_bottom = "3px solid #00FF9D" if r == 8 else "1px solid #2A2A2A"
                border_right = "3px solid #00FF9D" if c == 8 else "1px solid #2A2A2A"

                cell.setProperty("default_style", f"""
                    QLineEdit {{
                        background-color: #1E1E1E;
                        color: #FFFFFF;
                        border-top: {border_top};
                        border-left: {border_left};
                        border-bottom: {border_bottom};
                        border-right: {border_right};
                    }}
                """)
                cell.setStyleSheet(cell.property("default_style"))
                grid_layout.addWidget(cell, r, c)

        main_layout.addWidget(grid_container)
        main_layout.addSpacing(10)

        # Action Buttons (Bas)
        action_layout = QHBoxLayout()
        btn_check = QPushButton("Vérifier")
        btn_solve = QPushButton("Résoudre (Backtracking)")

        btn_check.clicked.connect(self.check_solution)
        btn_solve.clicked.connect(self.solve_automatically)

        action_layout.addWidget(btn_check)
        action_layout.addWidget(btn_solve)
        main_layout.addLayout(action_layout)

    def new_game(self):
        diff = self.diff_combo.currentText()
        self.initial_grid, self.solution_grid = self.engine.generate(diff)

        for (r, c), cell in self.cells.items():
            cell.blockSignals(True)
            val = self.initial_grid[r][c]
            base_style = cell.property("default_style")

            if val != 0:
                cell.setText(str(val))
                cell.setReadOnly(True)
                cell.is_initial = True
                cell.setStyleSheet(base_style + "QLineEdit { color: #00FF9D; font-weight: bold; }")
            else:
                cell.clear()
                cell.setReadOnly(False)
                cell.is_initial = False
                cell.setStyleSheet(base_style)
            cell.blockSignals(False)

    def on_cell_changed(self, row, col, text):
        cell = self.cells[(row, col)]
        if cell.is_initial or not text:
            return

        # Contrôle instantané de la validité locale
        val = int(text)
        temp_grid = self.get_current_grid()
        temp_grid[row][col] = 0  # Ignorer la case actuelle pour le test

        base_style = cell.property("default_style")
        if not self.engine.is_valid(temp_grid, row, col, val):
            cell.setStyleSheet(base_style + "QLineEdit { color: #FF5252; background-color: #2D1B1B; }")
        else:
            cell.setStyleSheet(base_style + "QLineEdit { color: #FFFFFF; }")

    def get_current_grid(self):
        grid = []
        for r in range(9):
            row = []
            for c in range(9):
                text = self.cells[(r, c)].text()
                row.append(int(text) if text.isdigit() else 0)
            grid.append(row)
        return grid

    def check_solution(self):
        current = self.get_current_grid()
        if current == self.solution_grid:
            QMessageBox.information(self, "Victoire !", "Félicitations, la grille est parfaitement résolue !")
        else:
            QMessageBox.warning(self, "Incomplet", "Il y a des erreurs ou la grille n'est pas encore terminée.")

    def solve_automatically(self):
        for (r, c), cell in self.cells.items():
            cell.blockSignals(True)
            cell.setText(str(self.solution_grid[r][c]))
            base_style = cell.property("default_style")
            if not cell.is_initial:
                cell.setStyleSheet(base_style + "QLineEdit { color: #FFB74D; }")
            cell.blockSignals(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SudokuGUI()
    window.show()
    sys.exit(app.exec_())