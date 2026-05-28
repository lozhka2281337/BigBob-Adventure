import random
import pygame

from config import (MAP_HEIGHT, MAP_WIDTH, 
                    MIN_LEAF_SIZE, MIN_ROOM_SIZE, MAX_ROOM_SIZE, HALL_WIDTH,
                    PARTIES_RELATIONSHIP
                    )

class Leaf:
    def __init__(self, x=0, y=0, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.left_child = None
        self.right_child = None
        self.room = None
        self.halls = []

    def split(self) -> bool:
        if self.left_child is not None or self.right_child is not None:
            return False
        
        horizontal_split = random.random() > 0.5
        if self.width / self.height > PARTIES_RELATIONSHIP:
            horizontal_split = False
        elif self.height / self.width >= PARTIES_RELATIONSHIP:
            horizontal_split = True

        mx = self.width - MIN_LEAF_SIZE
        if horizontal_split: mx = self.height - MIN_LEAF_SIZE

        if mx < MIN_LEAF_SIZE: 
            return False

        spliter = random.randint(MIN_LEAF_SIZE, mx)

        if horizontal_split:
            self.left_child = Leaf(self.x, self.y, self.width, spliter)
            self.right_child = Leaf(self.x, self.y + spliter, self.width, self.height - spliter)
        else:
            self.left_child = Leaf(self.x, self.y, spliter, self.height)
            self.right_child = Leaf(self.x + spliter, self.y, self.width - spliter, self.height)

        return True
    
    def create_rooms(self):
        if self.left_child is not None or self.right_child is not None:
            if self.left_child is not None:
                self.left_child.create_rooms()
            
            if self.right_child is not None:
                self.right_child.create_rooms()

            if self.right_child is not None and self.left_child is not None:
                self.halls = self._create_hall(self.left_child._get_room(), self.right_child._get_room())
        else:
            # создаем комнату
            room_width = random.randint(MIN_ROOM_SIZE, max(MIN_ROOM_SIZE, min(MAX_ROOM_SIZE, self.width - 2)))
            room_height = random.randint(MIN_ROOM_SIZE, max(MIN_ROOM_SIZE, min(MAX_ROOM_SIZE, self.height - 2)))

            room_x = random.randint(1 , max(1, self.width - room_width - 1))
            room_y = random.randint(1, max(1, self.height - room_height - 1))

            self.room = pygame.Rect(self.x + room_x, self.y + room_y, room_width, room_height)
    
    def _get_room(self):
        if self.room is not None:
            return self.room
        
        l_room, r_room = None, None
        
        if self.left_child is not None:  l_room = self.left_child._get_room()
        if self.right_child is not None: r_room = self.right_child._get_room()

        if l_room is None and r_room is None: return None
        elif r_room is None:                  return l_room
        elif l_room is None:                  return r_room
        elif random.random() > 0.5:           return l_room
        return r_room
    
    def _create_hall(self, l, r):
        halls = []

        p1_x = l.centerx
        p1_y = l.centery

        p2_x = r.centerx
        p2_y = r.centery

        offset = HALL_WIDTH // 2

        # Сначала горизонтально, затем вертикально
        x = min(p1_x, p2_x) - offset
        width = abs(p2_x - p1_x) + HALL_WIDTH
        halls.append(pygame.Rect(x, p1_y - offset, width, HALL_WIDTH))

        y = min(p1_y, p2_y) - offset 
        height = abs(p2_y - p1_y) + HALL_WIDTH
        halls.append(pygame.Rect(p2_x - offset, y, HALL_WIDTH, height))
        
        return halls
