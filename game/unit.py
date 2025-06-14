import pygame
from .constants import *

class Unit:
    def __init__(self, unit_type, grid_position, size=1):
        self.unit_type = unit_type
        self.grid_position = grid_position
        self.size = size
        self.selected = False
        self.owner = None

    def render(self, screen, offset_x=0, offset_y=0, zoom_level=1.0):
        x, y = self.grid_position
        scaled_size = int(GRID_SIZE * self.size * zoom_level)
        rect = pygame.Rect(
            x * GRID_SIZE * zoom_level + offset_x,
            y * GRID_SIZE * zoom_level + offset_y,
            scaled_size,
            scaled_size
        )
        # Draw unit
        pygame.draw.rect(screen, self.get_color(), rect)
        # Draw selection highlight
        if self.selected:
            pygame.draw.rect(screen, WHITE, rect, 2)
        # Draw label if available
        if hasattr(self, 'label'):
            font = pygame.font.Font(None, int(16 * zoom_level))
            label_text = font.render(self.label, True, WHITE)
            # Draw a dark background for the label
            label_bg_rect = pygame.Rect(rect.x + 1, rect.y + 1, label_text.get_width() + 4, label_text.get_height() + 2)
            pygame.draw.rect(screen, (20, 20, 20), label_bg_rect)
            # Top-left corner with a small margin
            screen.blit(label_text, (rect.x + 3, rect.y + 2))

    def get_color(self):
        return WHITE  # Base color, override in subclasses

    def is_at_position(self, grid_pos):
        return self.grid_position == grid_pos

    def occupies_position(self, grid_pos):
        x, y = grid_pos
        unit_x, unit_y = self.grid_position
        return (unit_x <= x < unit_x + self.size and 
                unit_y <= y < unit_y + self.size)

    def set_selected(self, selected):
        self.selected = selected

    def update(self):
        pass  # Base update method, override in subclasses

    def render_tooltip(self, screen, offset_x=0, offset_y=0):
        if not self.selected:
            return
        from .constants import GRID_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
        x, y = self.grid_position
        font = pygame.font.Font(None, 18)
        lines = [
            f"{self.full_name}",
            f"Move: {self.move_range}",
            f"Actions Left: {self.actions_left}",
            f"Ability: {self.ability}"
        ]
        width = max(font.size(line)[0] for line in lines) + 12
        height = len(lines) * 22 + 8
        # Calculate scaled grid size (try to get from parent if possible, else fallback)
        try:
            scaled_grid_size = screen.get_width() // 25  # fallback guess
            if hasattr(screen, 'scaled_grid_size_hint'):
                scaled_grid_size = screen.scaled_grid_size_hint
        except Exception:
            scaled_grid_size = GRID_SIZE
        # Calculate unit's screen position
        screen_x = x * scaled_grid_size + offset_x
        screen_y = y * scaled_grid_size + offset_y
        # Tooltip offset (fixed pixel distance)
        tooltip_offset_x = screen_x + scaled_grid_size + 12
        tooltip_offset_y = screen_y
        tooltip_rect = pygame.Rect(
            tooltip_offset_x,
            tooltip_offset_y,
            width,
            height
        )
        # Clamp tooltip to screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        if tooltip_rect.right > screen_width:
            tooltip_rect.x = max(0, screen_width - tooltip_rect.width - 8)
        if tooltip_rect.bottom > screen_height:
            tooltip_rect.y = max(0, screen_height - tooltip_rect.height - 8)
        pygame.draw.rect(screen, (30, 30, 30), tooltip_rect)
        pygame.draw.rect(screen, WHITE, tooltip_rect, 1)
        for i, line in enumerate(lines):
            text = font.render(line, True, WHITE)
            screen.blit(text, (tooltip_rect.x + 6, tooltip_rect.y + 4 + i * 22))

class Ship(Unit):
    full_name = 'Corvette'
    ability = '—'
    def __init__(self, grid_position, move_range=5, owner=0):
        super().__init__('SHIP', grid_position, size=1)
        self.move_range = move_range
        self.label = 'COR'  # Corvette
        self.actions_left = 6
        self.owner = owner

    def get_color(self):
        # Player 1: blue shades, Player 2: red shades
        if self.owner == 0:
            return (80, 160, 255)  # Default blue
        else:
            return (255, 100, 100)  # Default red

    def reset_actions(self):
        self.actions_left = 6

    def render_tooltip(self, screen, offset_x=0, offset_y=0):
        if not self.selected:
            return
        x, y = self.grid_position
        font = pygame.font.Font(None, 18)
        lines = [
            f"{self.full_name}",
            f"Move: {self.move_range}",
            f"Actions Left: {self.actions_left}",
            f"Ability: {self.ability}"
        ]
        width = max(font.size(line)[0] for line in lines) + 12
        height = len(lines) * 22 + 8
        tooltip_rect = pygame.Rect(
            x * GRID_SIZE + offset_x + GRID_SIZE + 6,
            y * GRID_SIZE + offset_y,
            width,
            height
        )
        # Clamp tooltip to screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        if tooltip_rect.right > screen_width:
            tooltip_rect.x = max(0, screen_width - tooltip_rect.width - 8)
        if tooltip_rect.bottom > screen_height:
            tooltip_rect.y = max(0, screen_height - tooltip_rect.height - 8)
        pygame.draw.rect(screen, (30, 30, 30), tooltip_rect)
        pygame.draw.rect(screen, WHITE, tooltip_rect, 1)
        for i, line in enumerate(lines):
            text = font.render(line, True, WHITE)
            screen.blit(text, (tooltip_rect.x + 6, tooltip_rect.y + 4 + i * 22))

class Frigate(Ship):
    full_name = 'Frigate'
    ability = '—'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=3, owner=owner)
        self.label = 'FRG'
        self.actions_left = 4

    def reset_actions(self):
        self.actions_left = 4

    def get_color(self):
        if self.owner == 0:
            return (60, 200, 255)  # Lighter blue
        else:
            return (255, 60, 60)  # Lighter red

class Destroyer(Ship):
    full_name = 'Destroyer'
    ability = '—'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=2, owner=owner)
        self.label = 'DST'
        self.actions_left = 3

    def reset_actions(self):
        self.actions_left = 3

    def get_color(self):
        if self.owner == 0:
            return (0, 120, 255)  # Deep blue
        else:
            return (200, 0, 0)  # Deep red

class Cruiser(Ship):
    full_name = 'Cruiser'
    ability = '—'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=1, owner=owner)
        self.label = 'CRU'
        self.actions_left = 2

    def reset_actions(self):
        self.actions_left = 2

    def get_color(self):
        if self.owner == 0:
            return (0, 80, 200)  # Navy blue
        else:
            return (160, 0, 0)  # Dark red

class Battleship(Ship):
    full_name = 'Battleship'
    ability = '—'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=1, owner=owner)
        self.label = 'BAT'
        self.actions_left = 2

    def reset_actions(self):
        self.actions_left = 2

    def get_color(self):
        if self.owner == 0:
            return (0, 40, 120)  # Very dark blue
        else:
            return (120, 0, 0)  # Very dark red

class Carrier(Ship):
    full_name = 'Carrier'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=1, owner=owner)
        self.label = 'CAR'
        self.deployed = False
        self.hangar = {'Fighter': 0, 'Bomber': 0}
        self.actions_left = 3
        self.docked_units = []  # List of docked Fighter/Bomber objects
        self.max_dock_slots = 4
    @property
    def ability(self):
        if self.docked_units:
            return f"Deploy {len([u for u in self.docked_units if u.label == 'FIG'])} Fighter(s), {len([u for u in self.docked_units if u.label == 'BOM'])} Bomber(s)"
        elif not self.deployed:
            return 'Deploys docked Fighters/Bombers'
        else:
            return 'Ability: Used'
    def reset_actions(self):
        self.actions_left = 3
    def get_color(self):
        if self.owner == 0:
            return (0, 200, 255)  # Bright blue
        else:
            return (255, 0, 0)  # Bright red
    def can_dock(self, unit):
        return len(self.docked_units) < self.max_dock_slots and unit.label in ('FIG', 'BOM')
    def dock_unit(self, unit):
        if self.can_dock(unit):
            self.docked_units.append(unit)
            print(f"DEBUG: {unit.label} docked in Carrier at {self.grid_position}")
            return True
        return False
    def deploy_units(self, galaxy):
        if not self.docked_units:
            print("DEBUG: No docked units to deploy.")
            return False
        # Find all open adjacent tiles
        x, y = self.grid_position
        adjacent = [(x+dx, y+dy) for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]]
        open_tiles = []
        for tx, ty in adjacent:
            if 0 <= tx < GALAXY_SIZE and 0 <= ty < GALAXY_SIZE:
                occupied = False
                for ship in galaxy.ships:
                    if ship.grid_position == (tx, ty):
                        occupied = True
                        break
                for planet in galaxy.planets:
                    px, py = planet.grid_position
                    if px <= tx < px + planet.size and py <= ty < py + planet.size:
                        occupied = True
                        break
                if not occupied:
                    open_tiles.append((tx, ty))
        deployed = 0
        for unit in list(self.docked_units):
            if not open_tiles:
                break
            pos = open_tiles.pop(0)
            unit.grid_position = pos
            unit.owner = self.owner
            galaxy.ships.append(unit)
            self.docked_units.remove(unit)
            print(f"DEBUG: Deployed {unit.label} to {pos}")
            deployed += 1
        if deployed:
            self.actions_left -= 1
            print(f"DEBUG: Carrier at {self.grid_position} deployed {deployed} units.")
            return True
        print("DEBUG: No open tiles to deploy units.")
        return False

class Fighter(Ship):
    full_name = 'Fighter'
    ability = 'Can dock to nearest friendly Carrier (Q)'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=7, owner=owner)
        self.label = 'FIG'
        self.actions_left = 8

    def reset_actions(self):
        self.actions_left = 8

    def get_color(self):
        if self.owner == 0:
            return (120, 220, 255)  # Very light blue
        else:
            return (255, 180, 180)  # Very light red

class Bomber(Ship):
    full_name = 'Bomber'
    ability = 'Can dock to nearest friendly Carrier (Q)'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=6, owner=owner)
        self.label = 'BOM'
        self.actions_left = 6

    def reset_actions(self):
        self.actions_left = 6

    def get_color(self):
        if self.owner == 0:
            return (180, 220, 255)  # Pale blue
        else:
            return (255, 120, 180)  # Pale red

class BuilderShip(Ship):
    full_name = 'Builder Ship'
    ability = 'Can build stations/colonies (future)'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=4, owner=owner)
        self.label = 'BLD'
        self.actions_left = 5

    def reset_actions(self):
        self.actions_left = 5

    def get_color(self):
        if self.owner == 0:
            return (0, 255, 200)  # Aqua for player 1
        else:
            return (255, 180, 0)  # Orange-yellow for player 2

class Corvette(Ship):
    full_name = 'Corvette'
    ability = '—'
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=5, owner=owner)
        self.label = 'COR'
        self.actions_left = 6

    def reset_actions(self):
        self.actions_left = 6

    def get_color(self):
        if self.owner == 0:
            return (80, 160, 255)  # Default blue (same as base Ship)
        else:
            return (255, 100, 100)  # Default red (same as base Ship) 