WINDOW_HEIGHT = 600
WINDOW_WIDTH = 900

class smartGrid:
    def __init__(self):
        # สร้างตารางเก็บค่าที่มีขนาดเท่ากับ WINDOW_WIDTH x WINDOW_HEIGHT
        self.grid = [[False for i in range(WINDOW_HEIGHT)] for j in range(WINDOW_WIDTH)]

    def __getitem__(self, coords):
        return self.grid[coords[0]][coords[1]]

    def __setitem__(self, coords, value):

        if 0 <= coords[0] < WINDOW_WIDTH and 0 <= coords[1] < WINDOW_HEIGHT:
            # ตรวจสอบว่าตำแหน่ง coords อยู่ในขอบเขตของตารางหรือไม่
            self.grid[coords[0]][coords[1]] = value
        else:
            # ถ้าตำแหน่ง coords ไม่อยู่ในขอบเขตของตาราง พิมพ์ข้อความ "Index out of range" พร้อมกับ coords
            print("Index out of range:", coords)