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

    def render_tooltip(self, screen, offset_x=0, offset_y=0, zoom_level=1.0):
        """Compact tooltip for ships with health and combat stats"""
        font = pygame.font.Font(None, 14)  # Smaller font
        
        # Basic info - more compact
        lines = [
            f"{getattr(self, 'full_name', self.label)} (P{self.owner + 1})",  # Shorter player label
            f"Pos: ({self.grid_position[0]}, {self.grid_position[1]})",  # Shorter position label
            f"Act: {self.actions_left}/{self.max_actions} | Rng: {self.move_range}",  # Combined line
            f"HP: {self.health}/{self.max_health} ({self.get_health_percentage():.0f}%)"  # Shorter health label
        ]
        
        # Shield info if applicable - more compact
        if self.max_shield > 0:
            lines.append(f"Shield: {self.shield}/{self.max_shield} ({self.get_shield_percentage():.0f}%)")
        
        # Armor info if applicable - more compact
        if self.armor > 0:
            lines.append(f"Armor: {self.armor}")
        
        # Status effects - more compact
        if self.is_heavily_damaged():
            lines.append("DAMAGED!")
        
        # Special abilities - shortened to 1-2 words
        if hasattr(self, 'ability') and self.ability and self.ability != "—":
            # Map long abilities to short ones
            ability_map = {
                "Fast Attack": "Attack",
                "Anti-Ship": "Anti-Ship", 
                "Heavy Weapons": "Heavy",
                "Bombardment": "Bombard",
                "Launch Fighters": "Deploy",
                "Long Range Sensors": "Scout",
                "Carry Troops": "Transport",
                "Construct Buildings": "Build",
                "Establish Colony": "Colony",
                "Can dock to nearest friendly Carrier (Q)": "Dock",
                "Can build stations/colonies (future)": "Build",
                "Patrol Ship": "Patrol"
            }
            
            ability = ability_map.get(self.ability, self.ability)
            # If still too long, truncate
            if len(ability) > 8:
                ability = ability[:6] + ".."
            lines.append(f"Ability: {ability}")
        
        # Calculate tooltip size - more compact
        max_width = max(font.size(line)[0] for line in lines if line) + 8  # Less padding
        tooltip_height = len(lines) * 14 + 6  # Smaller line height and padding
        
        # Position tooltip to follow the ship - calculate ship's screen position
        from .constants import GRID_SIZE
        scaled_grid_size = max(1, round(GRID_SIZE * zoom_level))
        ship_screen_x = self.grid_position[0] * scaled_grid_size + offset_x
        ship_screen_y = self.grid_position[1] * scaled_grid_size + offset_y
        
        # Fixed offset from ship - more stable positioning
        tooltip_offset_x = 15  # Fixed pixel offset to the right
        tooltip_offset_y = -10  # Fixed pixel offset upward
        
        tooltip_x = ship_screen_x + tooltip_offset_x
        tooltip_y = ship_screen_y + tooltip_offset_y
        
        # Keep tooltip on screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Adjust if tooltip goes off screen
        if tooltip_x + max_width > screen_width:
            tooltip_x = ship_screen_x - max_width - 5  # Left of ship if no room on right
        if tooltip_y < 0:
            tooltip_y = ship_screen_y + scaled_grid_size + 5  # Below ship if no room above
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = screen_height - tooltip_height - 5
        
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, max_width, tooltip_height)
        
        # Draw tooltip background - semi-transparent
        tooltip_surface = pygame.Surface((max_width, tooltip_height))
        tooltip_surface.set_alpha(220)  # Semi-transparent
        tooltip_surface.fill((25, 25, 35))
        screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
        
        # Draw border
        pygame.draw.rect(screen, (80, 80, 120), tooltip_rect, 1)
        
        # Draw text - more compact
        for i, line in enumerate(lines):
            if line:  # Skip empty lines
                color = (255, 255, 255)
                if "DAMAGED" in line:
                    color = (255, 120, 120)
                elif "HP:" in line:
                    if self.get_health_percentage() < 25:
                        color = (255, 120, 120)
                    elif self.get_health_percentage() < 60:
                        color = (255, 255, 120)
                    else:
                        color = (120, 255, 120)
                
                text = font.render(line, True, color)
                screen.blit(text, (tooltip_x + 4, tooltip_y + 3 + i * 14))  # Smaller spacing

class Ship(Unit):
    full_name = 'Corvette'
    ability = '—'
    def __init__(self, grid_position, move_range=5, owner=0):
        super().__init__('SHIP', grid_position, size=1)
        self.move_range = move_range
        self.label = 'COR'  # Corvette
        self.actions_left = 6
        self.owner = owner
        
        # Health system - set default values, will be overridden by subclasses
        self.max_health = 100
        self.health = self.max_health
        
        # Combat stats
        self.armor = 0
        self.shield = 0
        self.max_shield = 0

    def take_damage(self, damage):
        """Apply damage to the ship, considering shields and armor"""
        # Shields absorb damage first
        if self.shield > 0:
            shield_damage = min(damage, self.shield)
            self.shield -= shield_damage
            damage -= shield_damage
        
        # Remaining damage goes to hull, reduced by armor
        if damage > 0:
            hull_damage = max(1, damage - self.armor)  # Minimum 1 damage
            self.health -= hull_damage
            
        # Ensure health doesn't go below 0
        self.health = max(0, self.health)
        
        return self.health <= 0  # Return True if ship is destroyed

    def repair(self, amount):
        """Repair the ship's hull"""
        self.health = min(self.max_health, self.health + amount)

    def recharge_shields(self, amount):
        """Recharge the ship's shields"""
        self.shield = min(self.max_shield, self.shield + amount)

    def get_health_percentage(self):
        """Get health as a percentage"""
        return (self.health / self.max_health) * 100

    def get_shield_percentage(self):
        """Get shield as a percentage"""
        if self.max_shield == 0:
            return 0
        return (self.shield / self.max_shield) * 100

    def is_heavily_damaged(self):
        """Check if ship is heavily damaged (below 25% health)"""
        return self.get_health_percentage() < 25

    def is_destroyed(self):
        """Check if ship is destroyed"""
        return self.health <= 0

    def get_color(self):
        # Player 1: blue shades, Player 2: red shades
        if self.owner == 0:
            return (80, 160, 255)  # Default blue
        else:
            return (255, 100, 100)  # Default red

    def render(self, screen, offset_x, offset_y, zoom_level=1.0):
        scaled_grid_size = max(1, round(GRID_SIZE * zoom_level))
        px = self.grid_position[0] * scaled_grid_size + offset_x
        py = self.grid_position[1] * scaled_grid_size + offset_y
        
        # Get ship color (may be modified for damage)
        base_color = self.get_color()
        
        # Modify color based on damage
        if self.is_heavily_damaged():
            # Darken and add red tint for heavily damaged ships
            base_color = tuple(max(0, min(255, int(c * 0.7 + 50))) if i == 0 else max(0, int(c * 0.7)) for i, c in enumerate(base_color))
        
        # Draw ship
        if not self.selected:
            pygame.draw.rect(screen, base_color, (px, py, scaled_grid_size, scaled_grid_size))
        else:
            # Draw selected ship with border
            pygame.draw.rect(screen, base_color, (px, py, scaled_grid_size, scaled_grid_size))
            pygame.draw.rect(screen, (255, 255, 0), (px, py, scaled_grid_size, scaled_grid_size), 3)
        
        # Draw health bar if damaged or if ship is selected
        if (self.health < self.max_health or self.selected) and zoom_level > 0.3:
            self._render_health_bar(screen, px, py, scaled_grid_size)
        
        # Draw shield bar if ship has shields
        if self.max_shield > 0 and zoom_level > 0.3:
            self._render_shield_bar(screen, px, py, scaled_grid_size)
        
        # Draw label if available
        if hasattr(self, 'label') and zoom_level > 0.4:
            font_size = max(8, min(16, scaled_grid_size // 3))
            font = pygame.font.Font(None, font_size)
            label_text = font.render(self.label, True, (255, 255, 255))
            label_rect = label_text.get_rect()
            label_rect.center = (px + scaled_grid_size // 2, py + scaled_grid_size // 2)
            screen.blit(label_text, label_rect)

    def _render_health_bar(self, screen, px, py, scaled_grid_size):
        """Render health bar above the ship"""
        bar_width = scaled_grid_size
        bar_height = max(2, scaled_grid_size // 8)
        bar_x = px
        bar_y = py - bar_height - 2
        
        # Background (red)
        health_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 0, 0), health_bg_rect)
        
        # Foreground (green to red based on health)
        health_ratio = self.health / self.max_health
        health_fg_width = int(bar_width * health_ratio)
        
        if health_fg_width > 0:
            # Color from green (high health) to red (low health)
            if health_ratio > 0.6:
                color = (0, 255, 0)  # Green
            elif health_ratio > 0.3:
                color = (255, 255, 0)  # Yellow
            else:
                color = (255, 0, 0)  # Red
                
            health_fg_rect = pygame.Rect(bar_x, bar_y, health_fg_width, bar_height)
            pygame.draw.rect(screen, color, health_fg_rect)

    def _render_shield_bar(self, screen, px, py, scaled_grid_size):
        """Render shield bar above the health bar"""
        bar_width = scaled_grid_size
        bar_height = max(1, scaled_grid_size // 12)
        bar_x = px
        bar_y = py - (max(2, scaled_grid_size // 8)) - bar_height - 3  # Above health bar
        
        # Background (dark blue)
        shield_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (0, 0, 50), shield_bg_rect)
        
        # Foreground (blue)
        shield_ratio = self.shield / self.max_shield if self.max_shield > 0 else 0
        shield_fg_width = int(bar_width * shield_ratio)
        
        if shield_fg_width > 0:
            shield_fg_rect = pygame.Rect(bar_x, bar_y, shield_fg_width, bar_height)
            pygame.draw.rect(screen, (0, 150, 255), shield_fg_rect)

    def reset_actions(self):
        """Reset ship actions at the start of a new turn"""
        self.actions_left = self.max_actions
        # Regenerate shields slightly each turn
        if self.max_shield > 0:
            self.recharge_shields(self.max_shield * 0.1)  # 10% shield regen per turn

class Frigate(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=4, owner=owner)
        self.full_name = "Frigate"
        self.label = "FRG"
        self.ability = "Fast Attack"
        self.max_actions = 4
        self.actions_left = self.max_actions
        
        # Light combat ship - fast but fragile
        self.max_health = 80
        self.health = self.max_health
        self.armor = 1
        self.max_shield = 40
        self.shield = self.max_shield

class Destroyer(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=3, owner=owner)
        self.full_name = "Destroyer"
        self.label = "DST"
        self.ability = "Anti-Ship"
        self.max_actions = 3
        self.actions_left = self.max_actions
        
        # Medium combat ship - balanced
        self.max_health = 120
        self.health = self.max_health
        self.armor = 2
        self.max_shield = 60
        self.shield = self.max_shield

class Cruiser(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=3, owner=owner)
        self.full_name = "Cruiser"
        self.label = "CRS"
        self.ability = "Heavy Weapons"
        self.max_actions = 2
        self.actions_left = self.max_actions
        
        # Heavy combat ship - tough and powerful
        self.max_health = 180
        self.health = self.max_health
        self.armor = 3
        self.max_shield = 90
        self.shield = self.max_shield

class Battleship(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=2, owner=owner)
        self.full_name = "Battleship"
        self.label = "BSH"
        self.ability = "Bombardment"
        self.max_actions = 2
        self.actions_left = self.max_actions
        
        # Capital ship - massive health and armor
        self.max_health = 300
        self.health = self.max_health
        self.armor = 5
        self.max_shield = 150
        self.shield = self.max_shield

class Carrier(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=2, owner=owner)
        self.full_name = "Carrier"
        self.label = "CAR"
        self.max_actions = 3
        self.actions_left = self.max_actions
        
        # Support capital ship - high health but less armor
        self.max_health = 250
        self.health = self.max_health
        self.armor = 2
        self.max_shield = 120
        self.shield = self.max_shield
        
        # Carrier-specific attributes
        self.deployed = False
        self.hangar = {'Fighter': 0, 'Bomber': 0}
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
            return True
        return False

    def deploy_units(self, galaxy):
        if not self.docked_units:
            return False
        
        # Find adjacent empty positions
        adjacent_positions = [
            (self.grid_position[0] + dx, self.grid_position[1] + dy)
            for dx in [-1, 0, 1] for dy in [-1, 0, 1]
            if (dx != 0 or dy != 0)
        ]
        
        deployed_count = 0
        for unit in self.docked_units[:]:
            for pos in adjacent_positions:
                if galaxy.is_position_empty(pos):
                    unit.grid_position = pos
                    galaxy.ships.append(unit)
                    self.docked_units.remove(unit)
                    deployed_count += 1
                    break
        
        if deployed_count > 0:
            self.deployed = True
            return True
        return False

class Fighter(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=7, owner=owner)
        self.full_name = 'Fighter'
        self.label = 'FIG'
        self.ability = 'Can dock to nearest friendly Carrier (Q)'
        self.max_actions = 8
        self.actions_left = self.max_actions
        
        # Light fighter - very fast but extremely fragile
        self.max_health = 40
        self.health = self.max_health
        self.armor = 0
        self.max_shield = 20
        self.shield = self.max_shield

class Bomber(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=6, owner=owner)
        self.full_name = 'Bomber'
        self.label = 'BOM'
        self.ability = 'Can dock to nearest friendly Carrier (Q)'
        self.max_actions = 6
        self.actions_left = self.max_actions
        
        # Attack bomber - fragile but more durable than fighter
        self.max_health = 60
        self.health = self.max_health
        self.armor = 1
        self.max_shield = 30
        self.shield = self.max_shield

class BuilderShip(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=4, owner=owner)
        self.full_name = 'Builder Ship'
        self.label = 'BLD'
        self.ability = 'Can build stations/colonies (future)'
        self.max_actions = 5
        self.actions_left = self.max_actions
        
        # Same as Builder class - construction ship
        self.max_health = 90
        self.health = self.max_health
        self.armor = 1
        self.max_shield = 30
        self.shield = self.max_shield

class Corvette(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=5, owner=owner)
        self.full_name = 'Corvette'
        self.label = 'COR'
        self.ability = 'Patrol Ship'
        self.max_actions = 6
        self.actions_left = self.max_actions
        
        # Small patrol ship - between frigate and scout
        self.max_health = 70
        self.health = self.max_health
        self.armor = 1
        self.max_shield = 35
        self.shield = self.max_shield

class Scout(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=6, owner=owner)
        self.full_name = "Scout"
        self.label = "SCT"
        self.ability = "Long Range Sensors"
        self.max_actions = 8
        self.actions_left = self.max_actions
        
        # Fast reconnaissance ship - very fragile
        self.max_health = 50
        self.health = self.max_health
        self.armor = 0
        self.max_shield = 25
        self.shield = self.max_shield

class Transport(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=3, owner=owner)
        self.full_name = "Transport"
        self.label = "TRP"
        self.ability = "Carry Troops"
        self.max_actions = 5
        self.actions_left = self.max_actions
        
        # Civilian ship - moderate health, no shields
        self.max_health = 100
        self.health = self.max_health
        self.armor = 1
        self.max_shield = 0
        self.shield = 0

class Builder(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=3, owner=owner)
        self.full_name = "Builder"
        self.label = "BLD"
        self.ability = "Construct Buildings"
        self.max_actions = 5
        self.actions_left = self.max_actions
        
        # Construction ship - moderate health, light shields
        self.max_health = 90
        self.health = self.max_health
        self.armor = 1
        self.max_shield = 30
        self.shield = self.max_shield

class Colonizer(Ship):
    def __init__(self, grid_position, owner=0):
        super().__init__(grid_position, move_range=3, owner=owner)
        self.full_name = "Colonizer"
        self.label = "COL"
        self.ability = "Establish Colony"
        self.max_actions = 5
        self.actions_left = self.max_actions
        
        # Colony ship - high health to protect colonists
        self.max_health = 150
        self.health = self.max_health
        self.armor = 2
        self.max_shield = 50
        self.shield = self.max_shield 