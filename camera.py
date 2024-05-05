import pygame

def em():
    pass

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # r = random.randint(1,100)
        # if r <= 5:
        #     self.alive = 1
        # else:
        #     self.alive = 0
        self.alive = 1
        self.last = 1
        self.upd_col()
    
    def upd_col(self):
        if self.alive == 0:
            self.color = (0, 0, 0)
        else:
            self.color = (255, 255, 255)
    
    def draw(self, s, rx, ry, surf):
        if self.alive == 0: return
        pygame.draw.rect(surf, self.color, pygame.Rect(rx, ry, s, s))
    
    def copy(self):
        new = Cell(self.x, self.y)
        new.alive = self.alive
        new.last = self.color
        new.upd_col()
        return new
        

class Row:
    def __init__(self, y, items):
        self.y=y
        self.i=items

class Button:
    def __init__(self, size, pos):
        self.size = size
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.on = em
    def render(self, scr):
        pygame.draw.rect(scr, (210, 210, 210), self.rect)
    
    def update(self, pos):
        if self.rect.collidepoint(pos):
            self.on()


class Camera:
    def __init__(self, sizes):
        self.x = 0
        self.y = 0
        self.size = sizes
        self.cell_s = 20
        self.holding = False
        self.hold_start = [0,0]
    
    def ch_scale(self, s):
        self.cell_s += s
        if self.cell_s <= 0:
            self.cell_s = 1
#        ncx = self.size[0]//self.cell_s
#        self.x += ncx//4
#        ncy = self.size[1]//self.cell_s
#        self.y += ncy//4
        

        
    def hold_s(self, pos):
        self.holding = True
        self.hold_start = pos
        
    def hold_e(self, pos):
        self.holding = False
    def update(self, pos):
        if self.holding:
            dx = pos[0]//self.cell_s - self.hold_start[0]//self.cell_s
            dy = pos[1]//self.cell_s - self.hold_start[1]//self.cell_s
            self.x -= dx
            self.y -= dy
            self.hold_start = pos

class Drawer:
    def __init__(self, cam: Camera) -> None:
        self.cam = cam
        self.holding = False
        self.hold_start = [0,0]
        self.mode = 0 # 0 not drawing; 1 drawing; 2 deleting
    
    def hold_s(self, pos):
        self.holding = True
        self.hold_start = pos
        
    def hold_e(self, pos):
        self.holding = False
    
    def get_line(self, start: list[int], end: list[int]):
        x1, y1 = start
        x2, y2 = end

        line = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while x1 != x2 or y1 != y2:
            line.append((x1, y1))
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        line.append((x1, y1))
        return line


    def update(self, pos, world):
        if self.mode == 0: return
        if self.holding:
            x = self.hold_start[0]//self.cam.cell_s+self.cam.x
            y = self.hold_start[1]//self.cam.cell_s+self.cam.y
            ex = pos[0]//self.cam.cell_s+self.cam.x
            ey = pos[1]//self.cam.cell_s+self.cam.y
            for cord in self.get_line([x, y], [ex, ey]):
                alive = world.is_alive(cord)
                if not alive and self.mode == 1:
                    world.new(cord)
                    continue
                if self.mode == 2:
                    world.delete(cord)
            self.hold_start = pos

class World:
    def __init__(self, surf, size):
        self.surf = surf
        self.size = size
        self.step = 0
        self.alive_cells = set()
        self.render_grid = True
        self.grid_col = (15, 15, 15)
    
    def delete(self, pos):
         try:
             self.alive_cells.remove(tuple(pos))
         except:
             pass
     
    def new(self, pos):
        x,y = pos
        if self.size is not None:
            if x > self.size[0] or x < 0 or y > self.size[1] or y < 0:
                return
        self.alive_cells.add(tuple(pos))
     
    def is_alive(self, pos):
         return tuple(pos) in self.alive_cells
     
    def update(self):
        self.step += 1
        next_generation = set()
        candidates = set()

        # Step 1: Generate a set of candidate cells to consider for the next generation
        for cell in self.alive_cells:
            candidates.add(cell)
            for neighbor in self.get_neighbors(cell):
                candidates.add(neighbor)

        # Step 2: Update the alive state of cells based on the candidate cells
        for candidate in candidates:
            live_neighbor_count = self.count_live_neighbors(candidate)
            if candidate in self.alive_cells:
                if live_neighbor_count == 2 or live_neighbor_count == 3:
                    next_generation.add(candidate)
            else:
                if live_neighbor_count == 3:
                    next_generation.add(candidate)

        # Step 3: Replace the live cells with the next generation cells
        self.alive_cells = next_generation
        
    def get_neighbors(self, cell):
        x, y = cell
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                rx = x+dx
                ry = y+dy
                if self.size is not None:
                    w = self.size[0]
                    h = self.size[1]
                    if rx >= 0 and rx < w and ry >= 0 and ry < h:
                        neighbors.append((rx, ry))
                else:
                    neighbors.append((rx, ry))
        return neighbors

    def count_live_neighbors(self, cell):
        count = 0
        for neighbor in self.get_neighbors(cell):
            if neighbor in self.alive_cells:
                count += 1
        return count
        
    
    def render(self, cam):
        size = cam.cell_s
        for cell in self.alive_cells:
            x, y = cell
            if y < cam.y:
                continue
            ry = y*size-cam.y*size
            if ry > cam.size[1]:
                continue
            if x < cam.x:
                continue
            rx = x*size-cam.x*size
            if rx > cam.size[0]:
                 continue
            pygame.draw.rect(self.surf, (255, 255, 255), pygame.Rect(rx, ry, size, size))
       
        if self.render_grid:
            
            numrows = cam.size[1]//size
            for i in range(numrows):
                ry = i*size
                pygame.draw.line(self.surf, self.grid_col, [0, ry], [cam.size[0], ry])
            numcols = cam.size[0]//size
            for i in range(numcols):
                rx = i*size
                pygame.draw.line(self.surf, self.grid_col, [rx, 0], [rx, cam.size[1]])
        if self.size is None:
            return
        border = pygame.Rect(-cam.x*size, -cam.y*size, self.size[0]*size+size, self.size[1]*size+size)
        pygame.draw.rect(self.surf, (66, 135, 245), border, 2)