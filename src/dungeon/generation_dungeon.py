import random
import pygame

from config import TILE_SIZE, ROWS, COLS

# ГЕНЕРАЦИЯ УРОВНЯ 

def generate_walls(grid: list):
    walls = []
    for i in range(ROWS):
        for j in range(COLS):
            if grid[i][j] == 1:
                walls.append(pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    return walls

def room_is_correct(rooms: list, new_room: pygame.Rect):
    for other_room in rooms:
            if new_room.colliderect(other_room.inflate(4, 4)): 
                return False
    return True

def grid_init(x: int, y: int, h: int, w: int, grid: list):
     for i in range(y, y + h):
        for j in range(x, x + w):
            grid[i][j] = 0

def generate_dungeon():    
    while True:
        grid = [[1 for _ in range(COLS)] for _ in range(ROWS)] 
        rooms = []
        
        for _ in range(15):
            w = random.randint(10, 18) 
            h = random.randint(10, 18) 
            x = random.randint(2, COLS - w - 2)
            y = random.randint(2, ROWS - h - 2)
            
            new_room = pygame.Rect(x, y, w, h)
            
            # проверяем новую комнату на коллизии с уже существующими комнатами
            ok = room_is_correct(rooms, new_room)        
            if not ok: continue

            grid_init(x, y, h, w, grid)
            
            if len(rooms) > 0:
                prev_room = rooms[-1]
                c1_x, c1_y = new_room.centerx, new_room.centery
                c2_x, c2_y = prev_room.centerx, prev_room.centery
                
                def dig_wide_tunnel(start, end, fixed, horizontal=True):
                    for val in range(min(start, end), max(start, end) + 1):
                        if horizontal:
                            grid[fixed][val] = 0
                            if fixed + 1 < ROWS: grid[fixed + 1][val] = 0
                            if fixed - 1 >= 0: grid[fixed - 1][val] = 0
                        else:
                            grid[val][fixed] = 0
                            if fixed + 1 < COLS: grid[val][fixed + 1] = 0
                            if fixed - 1 >= 0: grid[val][fixed - 1] = 0

                if random.randint(0, 1) == 1:
                    dig_wide_tunnel(c1_x, c2_x, c1_y, True)
                    dig_wide_tunnel(c1_y, c2_y, c2_x, False)
                else:
                    dig_wide_tunnel(c1_y, c2_y, c1_x, False)
                    dig_wide_tunnel(c1_x, c2_x, c2_y, True)
                    
            rooms.append(new_room)
                
        walls = generate_walls(grid)

        # если получилось создать комнаты - успех
        if rooms:            
            start_x = rooms[0].centerx * TILE_SIZE
            start_y = rooms[0].centery * TILE_SIZE
            
            return walls, start_x, start_y
