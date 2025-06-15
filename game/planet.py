import pygame
import numpy as np
from .unit import Unit
from .constants import *
from .shipyard import ShipyardMixin

PLANET_TYPES = {
    'ROCKY': {'label': 'R', 'color': (139, 69, 19)},
    'GAS': {'label': 'G', 'color': (255, 215, 0)},
    'ICE': {'label': 'I', 'color': (173, 216, 230)},
    'DESERT': {'label': 'D', 'color': (237, 201, 175)},
    'TERRAN': {'label': 'T', 'color': (34, 139, 34)},
    'OCEAN': {'label': 'O', 'color': (0, 105, 148)},
    'VOLCANIC': {'label': 'V', 'color': (255, 69, 0)},
    'TOXIC': {'label': 'X', 'color': (110, 255, 110)},
}

SUN_TYPES = {
    # Original stars
    'RED_DWARF': {'label': 'RD', 'color': (255, 80, 80), 'size': 5},
    'YELLOW_STAR': {'label': 'YS', 'color': (255, 215, 0), 'size': 9},
    'BLUE_GIANT': {'label': 'BG', 'color': (80, 160, 255), 'size': 13},
    'WHITE_DWARF': {'label': 'WD', 'color': (240, 240, 255), 'size': 3},
    'NEUTRON_STAR': {'label': 'NS', 'color': (180, 180, 255), 'size': 2},
    
    # Expanded star types
    'RED_GIANT': {'label': 'RG', 'color': (255, 120, 60), 'size': 16},      # Massive, dying red star
    'ORANGE_STAR': {'label': 'OS', 'color': (255, 165, 0), 'size': 7},      # K-type main sequence star
    'BLUE_SUPERGIANT': {'label': 'BS', 'color': (100, 200, 255), 'size': 20}, # Extremely massive blue star
    'BROWN_DWARF': {'label': 'BD', 'color': (139, 69, 19), 'size': 4},      # Failed star, dim brown
    'VARIABLE_STAR': {'label': 'VS', 'color': (255, 100, 255), 'size': 8},  # Pulsating star, magenta
    'CARBON_STAR': {'label': 'CS', 'color': (200, 50, 50), 'size': 11},     # Carbon-rich red star
    'WOLF_RAYET': {'label': 'WR', 'color': (255, 255, 150), 'size': 6},     # Hot, luminous star
    'T_TAURI': {'label': 'TT', 'color': (255, 200, 100), 'size': 6},        # Young, pre-main sequence star
    
    # Exotic stellar objects
    'BINARY_STAR': {'label': 'BI', 'color': (255, 150, 100), 'size': 12},   # Two stars orbiting each other
    'TRIPLE_STAR': {'label': 'TR', 'color': (200, 150, 255), 'size': 15},   # Three-star system
    'MAGNETAR': {'label': 'MG', 'color': (100, 200, 255), 'size': 2},       # Ultra-magnetic neutron star
    'QUASAR': {'label': 'QS', 'color': (255, 255, 255), 'size': 8},         # Supermassive object with energy jets
    'DARK_STAR': {'label': 'DS', 'color': (40, 40, 60), 'size': 7},         # Theoretical dark matter star
    'HYPERGIANT': {'label': 'HG', 'color': (255, 100, 0), 'size': 25},      # Largest possible star
    'PREON_STAR': {'label': 'PR', 'color': (200, 220, 255), 'size': 1},     # Theoretical ultra-dense star
    'HELIUM_STAR': {'label': 'HE', 'color': (255, 255, 200), 'size': 4},    # Pure helium burning star
    'OXYGEN_STAR': {'label': 'OX', 'color': (200, 255, 200), 'size': 5},    # Oxygen-burning stellar remnant
    
    # Ultra-exotic stellar objects
    'QUASI_STAR': {'label': 'QU', 'color': (255, 50, 255), 'size': 30},     # Hypothetical supermassive early universe star
    'BOSON_STAR': {'label': 'BO', 'color': (150, 255, 150), 'size': 6},     # Theoretical exotic matter star
    'STRANGE_STAR': {'label': 'ST', 'color': (255, 100, 200), 'size': 3},   # Strange quark matter star
    'ELECTROWEAK_STAR': {'label': 'EW', 'color': (100, 255, 255), 'size': 4}, # Theoretical electroweak matter star
    'PLANCK_STAR': {'label': 'PL', 'color': (255, 255, 100), 'size': 1},    # Quantum gravity effects star
    'FUZZBALL': {'label': 'FB', 'color': (200, 100, 255), 'size': 5},       # String theory alternative to black holes
    'GRAVASTARS': {'label': 'GR', 'color': (100, 100, 255), 'size': 4},     # Gravitational vacuum condensate stars
    'Q_STAR': {'label': 'Q*', 'color': (255, 200, 255), 'size': 2},         # Theoretical ultra-compact object
}

class Planet(Unit, ShipyardMixin):
    def __init__(self, planet_type, grid_position, size=3, system_label=None):
        Unit.__init__(self, 'PLANET', grid_position, size=size)
        ShipyardMixin.__init__(self)
        self.planet_type = planet_type
        self.resources = self._generate_resources()
        self.show_tooltip = False
        self.color = PLANET_TYPES.get(planet_type, {'color': (255, 255, 255)})['color']
        self.type_label = PLANET_TYPES.get(planet_type, {'label': '?'})['label']
        self.system_label = system_label
        self.planet_grid = [[None for _ in range(self.size)] for _ in range(self.size)]  # NxN grid

    def _generate_resources(self):
        # Generate random resources based on planet type
        resources = {
            'ROCK': {'minerals': np.random.randint(50, 100)},
            'GAS': {'gas': np.random.randint(50, 100)},
            'ICE': {'water': np.random.randint(50, 100)},
            'SUN': {'energy': np.random.randint(50, 100)}
        }
        return resources.get(self.planet_type, {})

    def get_color(self):
        return self.color

    def render(self, screen, offset_x, offset_y, zoom_level=1.0):
        scaled_grid_size = max(1, round(GRID_SIZE * zoom_level))
        
        # Ensure planets are always visible with minimum size based on zoom level
        if zoom_level <= 0.05:
            # At extreme zoom out, use a larger minimum size
            scaled_size = max(4, int(self.size * 1.5))  # Smaller than stars but still visible
        else:
            scaled_size = max(4, int(self.size * scaled_grid_size))
        
        px = self.grid_position[0] * scaled_grid_size + offset_x
        py = self.grid_position[1] * scaled_grid_size + offset_y
        rect = pygame.Rect(px, py, scaled_size, scaled_size)
        # Draw main square
        pygame.draw.rect(screen, self.color, rect)
        # Draw darker border for all planets
        border_color = tuple(max(0, c - 60) for c in self.color)
        pygame.draw.rect(screen, border_color, rect, max(1, scaled_size // 10))
        
        # Only draw buildings when zoomed in enough to see them
        if zoom_level > 0.25 and scaled_grid_size > 8:
            # Draw buildings on the grid (colored by type)
            from .constants import BUILDING_COLORS
            for gy in range(self.size):
                for gx in range(self.size):
                    cell = self.planet_grid[gy][gx]
                    if cell is not None:
                        btype = cell.get('type', None)
                        color = BUILDING_COLORS.get(btype, (0, 120, 255))
                        cell_x = (self.grid_position[0] + gx) * scaled_grid_size + offset_x
                        cell_y = (self.grid_position[1] + gy) * scaled_grid_size + offset_y
                        rect = pygame.Rect(cell_x, cell_y, scaled_grid_size, scaled_grid_size)
                        pygame.draw.rect(screen, color, rect.inflate(-scaled_grid_size//3, -scaled_grid_size//3))
        elif zoom_level > 0.1:
            # When moderately zoomed out, just show a dot if planet has any buildings
            has_buildings = any(cell is not None for row in self.planet_grid for cell in row)
            if has_buildings:
                center_x = px + scaled_size // 2
                center_y = py + scaled_size // 2
                pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), max(2, scaled_size // 8))
        
        # Draw label when zoomed in enough to read it
        if self.system_label and zoom_level > 0.2:
            font_size = max(12, min(24, scaled_size // 2))
            font = pygame.font.Font(None, font_size)
            label_text = font.render(f"{self.system_label}-{self.type_label}", True, (255, 255, 255))
            screen.blit(label_text, (px + 2, py + 2))

    def can_build(self, player_id):
        # You cannot build if any cell is occupied by an enemy building
        for row in self.planet_grid:
            for cell in row:
                if cell is not None and cell['owner'] != player_id:
                    return False
        return True

    def place_building(self, grid_x, grid_y, player_id, building_type=None):
        if 0 <= grid_x < self.size and 0 <= grid_y < self.size and self.planet_grid[grid_y][grid_x] is None:
            self.planet_grid[grid_y][grid_x] = {'owner': player_id, 'type': building_type or 'BUILDING'}
            return True
        return False

    def build(self, building_type, grid_x, grid_y):
        if self.can_build(building_type, grid_x, grid_y):
            self.planet_grid[grid_y, grid_x] = 1
            self.buildings.append({
                'type': building_type,
                'position': (grid_x, grid_y),
                'level': 1
            })
            return True
        return False

    def upgrade_building(self, grid_x, grid_y):
        for building in self.buildings:
            if building['position'] == (grid_x, grid_y):
                # Check if player can afford upgrade
                upgrade_cost = {
                    resource: amount * 1.5  # 50% more expensive than original
                    for resource, amount in BUILDING_COSTS[building['type']].items()
                }
                if self.owner.can_afford(upgrade_cost):
                    # Spend resources
                    for resource, amount in upgrade_cost.items():
                        self.owner.spend_resource(resource, amount)
                    building['level'] += 1
                    return True
        return False

    def get_resource_production(self):
        # Base planet resources plus building production
        from .constants import BUILDING_PRODUCTION
        production = self.resources.copy()
        
        # Add production from buildings
        for row in self.planet_grid:
            for cell in row:
                if cell is not None:
                    building_type = cell.get('type')
                    if building_type in BUILDING_PRODUCTION:
                        building_production = BUILDING_PRODUCTION[building_type]
                        for resource, amount in building_production.items():
                            if resource in production:
                                production[resource] += amount
                            else:
                                production[resource] = amount
        
        return production

    def can_build_type(self, building_type):
        """Check if this building type can be built on this planet type"""
        from .constants import PLANET_BUILDING_RESTRICTIONS
        allowed_buildings = PLANET_BUILDING_RESTRICTIONS.get(self.planet_type, [])
        return building_type in allowed_buildings

    def get_allowed_buildings(self):
        """Get list of building types allowed on this planet"""
        from .constants import PLANET_BUILDING_RESTRICTIONS
        return PLANET_BUILDING_RESTRICTIONS.get(self.planet_type, [])

    def update(self):
        if self.owner:
            production = self.get_resource_production()
            for resource, amount in production.items():
                self.owner.add_resource(resource, amount)

    def _render_grid(self, screen):
        # Calculate grid position
        grid_x = self.screen_position[0] - (PLANET_GRID_WIDTH * PLANET_GRID_SIZE) // 2
        grid_y = self.screen_position[1] - (PLANET_GRID_HEIGHT * PLANET_GRID_SIZE) // 2

        # Draw grid lines
        for x in range(PLANET_GRID_WIDTH + 1):
            pygame.draw.line(
                screen,
                GRAY,
                (grid_x + x * PLANET_GRID_SIZE, grid_y),
                (grid_x + x * PLANET_GRID_SIZE, grid_y + PLANET_GRID_HEIGHT * PLANET_GRID_SIZE),
                1
            )
        for y in range(PLANET_GRID_HEIGHT + 1):
            pygame.draw.line(
                screen,
                GRAY,
                (grid_x, grid_y + y * PLANET_GRID_SIZE),
                (grid_x + PLANET_GRID_WIDTH * PLANET_GRID_SIZE, grid_y + y * PLANET_GRID_SIZE),
                1
            )

        # Draw buildings
        for building in self.buildings:
            x, y = building['position']
            building_rect = pygame.Rect(
                grid_x + x * PLANET_GRID_SIZE,
                grid_y + y * PLANET_GRID_SIZE,
                PLANET_GRID_SIZE,
                PLANET_GRID_SIZE
            )
            pygame.draw.rect(screen, WHITE, building_rect, 1)
            
            # Draw building level
            level_font = pygame.font.Font(None, 20)
            level_text = level_font.render(str(building['level']), True, WHITE)
            screen.blit(level_text, (building_rect.centerx - 5, building_rect.centery - 5))

    def render_tooltip(self, screen, offset_x=0, offset_y=0, mouse_pos=None):
        # If this planet has a shipyard, use the shipyard tooltip
        if self.has_shipyard():
            return self.render_shipyard_tooltip(screen, offset_x, offset_y, mouse_pos)
        
        # Otherwise, use the regular planet tooltip
        font = pygame.font.Font(None, 18)
        lines = [
            f"{self.system_label}-{self.type_label} ({self.planet_type.title()})",
            f"Size: {self.size}x{self.size}"
        ]
        # Add base resources if any
        if hasattr(self, 'resources') and self.resources:
            lines.append("Base Resources:")
            for k, v in self.resources.items():
                lines.append(f"  {k.title()}: {v}")
        
        # Add resource production from buildings
        production = self.get_resource_production()
        if production:
            lines.append("Total Production/Turn:")
            for resource, amount in production.items():
                lines.append(f"  {resource}: +{amount}")
        
        # Add allowed buildings for this planet type
        allowed_buildings = self.get_allowed_buildings()
        if allowed_buildings:
            lines.append("Allowed Buildings:")
            for building in allowed_buildings:
                lines.append(f"  {building}")
        
        width = max(font.size(line)[0] for line in lines) + 12
        height = len(lines) * 22 + 8
        tooltip_rect = pygame.Rect(
            offset_x,
            offset_y,
            width,
            height
        )
        pygame.draw.rect(screen, (30, 30, 30), tooltip_rect)
        pygame.draw.rect(screen, (255, 255, 255), tooltip_rect, 1)
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (tooltip_rect.x + 6, tooltip_rect.y + 4 + i * 22))
        
        return None  # No interactive buttons for regular planets

class Sun(Planet):
    def __init__(self, sun_type, grid_position, system_label):
        sun_info = SUN_TYPES[sun_type]
        super().__init__('SUN', grid_position, size=sun_info['size'], system_label=system_label)
        self.sun_type = sun_type
        self.color = sun_info['color']
        self.type_label = sun_info['label']
        self.sun_type_name = sun_type.replace('_', ' ').title()

    def render(self, screen, offset_x, offset_y, zoom_level=1.0):
        scaled_grid_size = max(1, round(GRID_SIZE * zoom_level))
        
        # Ensure stars are always visible with minimum size based on zoom level
        if zoom_level <= 0.05:
            # At extreme zoom out, use a larger minimum size
            scaled_size = max(8, int(self.size * 2))  # Larger minimum for extreme zoom
        else:
            scaled_size = max(6, int(self.size * scaled_grid_size))
        
        px = self.grid_position[0] * scaled_grid_size + offset_x
        py = self.grid_position[1] * scaled_grid_size + offset_y
        
        # Special rendering for multi-star systems
        if self.sun_type == 'BINARY_STAR':
            # Draw two overlapping stars for binary system
            star_size = max(4, scaled_size // 2)
            offset = max(2, scaled_size // 4)
            
            # First star (slightly left and up)
            rect1 = pygame.Rect(px - offset, py - offset, star_size, star_size)
            pygame.draw.rect(screen, self.color, rect1)
            border_color = tuple(max(0, c - 60) for c in self.color)
            pygame.draw.rect(screen, border_color, rect1, max(1, star_size // 8))
            
            # Second star (slightly right and down) - slightly different color
            second_color = tuple(min(255, c + 30) for c in self.color)
            rect2 = pygame.Rect(px + offset, py + offset, star_size, star_size)
            pygame.draw.rect(screen, second_color, rect2)
            border_color2 = tuple(max(0, c - 60) for c in second_color)
            pygame.draw.rect(screen, border_color2, rect2, max(1, star_size // 8))
            
        elif self.sun_type == 'TRIPLE_STAR':
            # Draw three stars in a triangle formation
            star_size = max(3, scaled_size // 3)
            offset = max(2, scaled_size // 4)
            
            # First star (center-left)
            rect1 = pygame.Rect(px - offset, py, star_size, star_size)
            pygame.draw.rect(screen, self.color, rect1)
            
            # Second star (top-right)
            second_color = tuple(min(255, c + 20) for c in self.color)
            rect2 = pygame.Rect(px + offset//2, py - offset, star_size, star_size)
            pygame.draw.rect(screen, second_color, rect2)
            
            # Third star (bottom-right)
            third_color = tuple(max(0, c - 20) for c in self.color)
            rect3 = pygame.Rect(px + offset//2, py + offset, star_size, star_size)
            pygame.draw.rect(screen, third_color, rect3)
            
            # Draw borders for all three
            border_color = tuple(max(0, c - 60) for c in self.color)
            pygame.draw.rect(screen, border_color, rect1, max(1, star_size // 8))
            pygame.draw.rect(screen, border_color, rect2, max(1, star_size // 8))
            pygame.draw.rect(screen, border_color, rect3, max(1, star_size // 8))
            
        else:
            # Draw single star normally
            rect = pygame.Rect(px, py, scaled_size, scaled_size)
            pygame.draw.rect(screen, self.color, rect)
            border_color = tuple(max(0, c - 60) for c in self.color)
            pygame.draw.rect(screen, border_color, rect, max(1, scaled_size // 10))
        
        # Only draw label when zoomed in enough to read it
        if zoom_level > 0.1:
            font = pygame.font.Font(None, max(12, scaled_size // 2))
            label_text = font.render(f"{self.system_label}-{self.type_label}", True, (255, 255, 255))
            screen.blit(label_text, (px + 2, py + 2))

    def render_tooltip(self, screen, offset_x=0, offset_y=0, mouse_pos=None):
        font = pygame.font.Font(None, 18)
        lines = [
            f"{self.system_label}-{self.type_label} ({self.sun_type_name})",
            f"Size: {self.size}x{self.size}"
        ]
        width = max(font.size(line)[0] for line in lines) + 12
        height = len(lines) * 22 + 8
        tooltip_rect = pygame.Rect(
            offset_x,
            offset_y,
            width,
            height
        )
        pygame.draw.rect(screen, (30, 30, 30), tooltip_rect)
        pygame.draw.rect(screen, (255, 255, 255), tooltip_rect, 1)
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (tooltip_rect.x + 6, tooltip_rect.y + 4 + i * 22))

class Moon(Unit):
    def __init__(self, grid_position, parent_planet=None):
        super().__init__('MOON', grid_position, size=1)
        self.parent_planet = parent_planet
        self.resources = {'Minerals': np.random.randint(2, 10)}
    def get_color(self):
        return (200, 200, 200)  # Light gray
    def render(self, screen, offset_x=0, offset_y=0):
        super().render(screen, offset_x, offset_y)
        font = pygame.font.Font(None, 16)
        label_text = font.render('M', True, WHITE)
        screen.blit(label_text, (self.grid_position[0] * GRID_SIZE + offset_x + 2, self.grid_position[1] * GRID_SIZE + offset_y + 2))

class Asteroid(Unit):
    def __init__(self, grid_position):
        super().__init__('ASTEROID', grid_position, size=1)
        self.resources = {'Minerals': np.random.randint(1, 6)}
    def get_color(self):
        return (120, 120, 120)  # Dark gray
    def render(self, screen, offset_x=0, offset_y=0):
        super().render(screen, offset_x, offset_y)
        font = pygame.font.Font(None, 16)
        label_text = font.render('A', True, WHITE)
        screen.blit(label_text, (self.grid_position[0] * GRID_SIZE + offset_x + 2, self.grid_position[1] * GRID_SIZE + offset_y + 2)) 