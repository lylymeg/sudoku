import random

class SudokuEngine:
    def __init__(self):
        self.grid = [[0] * 9 for _ in range(9)]

    def is_valid(self, grid, row, col, num):
        """Vérifie si placer 'num' à (row, col) respecte les règles du Sudoku."""
        for i in range(9):
            if grid[row][i] == num or grid[i][col] == num:
                return False

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[start_row + i][start_col + j] == num:
                    return False

        return True

    def solve(self, grid):
        """Résout la grille par Backtracking (modifie la grille sur place)."""
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(grid, row, col, num):
                            grid[row][col] = num
                            if self.solve(grid):
                                return True
                            grid[row][col] = 0
                    return False
        return True

    def count_solutions(self, grid, count=0):
        """Compte le nombre de solutions possibles (s'arrête à 2 pour l'unicité)."""
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(grid, row, col, num):
                            grid[row][col] = num
                            count = self.count_solutions(grid, count)
                            grid[row][col] = 0
                            if count >= 2:
                                return count
                    return count
        return count + 1

    def generate(self, difficulty="Moyen"):
        """Génère une nouvelle grille jouable selon la difficulté."""
        # 1. Remplir une grille vide complète
        self.grid = [[0] * 9 for _ in range(9)]
        self._fill_grid(self.grid)

        solution = [row[:] for row in self.grid]

        # 2. Définir le nombre de cases à retirer selon la difficulté
        removals_map = {"Facile": 30, "Moyen": 42, "Difficile": 52}
        removals = removals_map.get(difficulty, 42)

        # 3. Retirer des cases tout en garantissant une solution unique
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)

        removed = 0
        for r, c in cells:
            if removed >= removals:
                break

            temp = self.grid[r][c]
            self.grid[r][c] = 0

            # Vérifier que la grille conserve une solution unique
            temp_grid = [row[:] for row in self.grid]
            if self.count_solutions(temp_grid) != 1:
                self.grid[r][c] = temp
            else:
                removed += 1

        return self.grid, solution

    def _fill_grid(self, grid):
        """Remplit la grille de façon aléatoire et valide."""
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if self.is_valid(grid, row, col, num):
                            grid[row][col] = num
                            if self._fill_grid(grid):
                                return True
                            grid[row][col] = 0
                    return False
        return True