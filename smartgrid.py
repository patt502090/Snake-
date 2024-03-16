WINDOW_HEIGHT = 600
WINDOW_WIDTH = 900

class smartGrid:
    def __init__(self):
        self.grid = [[False for i in range(WINDOW_HEIGHT)] for j in range(WINDOW_WIDTH)]

    def __getitem__(self, coords):
        return self.grid[coords[0]][coords[1]]

    def __setitem__(self, coords, value):
        if 0 <= coords[0] < WINDOW_WIDTH and 0 <= coords[1] < WINDOW_HEIGHT:
            self.grid[coords[0]][coords[1]] = value
        else:
            print("Index out of range:", coords)