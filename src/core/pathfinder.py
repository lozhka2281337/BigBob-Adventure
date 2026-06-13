import pygame
import heapq

import config as cfg

class PathFinder:
    @staticmethod
    def get_path(matrix: list[list[int]], start_pos: pygame.math.Vector2, target_pos: pygame.math.Vector2) -> list[pygame.math.Vector2]:
        start_node = (int(start_pos.x // cfg.TILE_SIZE), int(start_pos.y // cfg.TILE_SIZE))
        target_node = (int(target_pos.x // cfg.TILE_SIZE), int(target_pos.y // cfg.TILE_SIZE))

        if not PathFinder._is_walkable(matrix, target_node):
            target_node = PathFinder._find_nearest_walkable(matrix, target_node)
            if not target_node:
                return []

        open_set = []
        heapq.heappush(open_set, (0, start_node))
        
        came_from = {}
        g_score = {start_node: 0}

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == target_node:
                return PathFinder._reconstruct_path(came_from, current)

            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if not PathFinder._is_walkable(matrix, neighbor):
                    continue
                if dx != 0 and dy != 0:
                    if not PathFinder._is_walkable(matrix, (current[0] + dx, current[1])) or \
                       not PathFinder._is_walkable(matrix, (current[0], current[1] + dy)):
                        continue

                cost = 1.414 if dx != 0 and dy != 0 else 1
                tentative_g_score = g_score[current] + cost

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    
                    f_score = tentative_g_score + PathFinder._heuristic(neighbor, target_node)
                    heapq.heappush(open_set, (f_score, neighbor))

        return [] 

    @staticmethod
    def _heuristic(node: tuple, target: tuple) -> float:
        dx = abs(node[0] - target[0])
        dy = abs(node[1] - target[1])
        return max(dx, dy)

    @staticmethod
    def _is_walkable(matrix: list[list[int]], node: tuple) -> bool:
        x, y = node
        if 0 <= x < cfg.MAP_WIDTH and 0 <= y < cfg.MAP_HEIGHT:
            return matrix[y][x] == 0
        return False

    @staticmethod
    def _find_nearest_walkable(matrix: list[list[int]], node: tuple) -> tuple | None:
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (node[0] + dx, node[1] + dy)
            if PathFinder._is_walkable(matrix, neighbor):
                return neighbor
        return None

    @staticmethod
    def _reconstruct_path(came_from: dict, current: tuple) -> list[pygame.math.Vector2]:
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        
        pixel_path = []
        for node in path:
            px = node[0] * cfg.TILE_SIZE + cfg.TILE_SIZE // 2
            py = node[1] * cfg.TILE_SIZE + cfg.TILE_SIZE // 2
            pixel_path.append(pygame.math.Vector2(px, py))
            
        return pixel_path
