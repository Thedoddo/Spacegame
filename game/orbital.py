import pygame
from .constants import *
from .shipyard import ShipyardMixin

class Orbital(ShipyardMixin):
    """Represents an orbital structure that can be built in space"""
    
    def __init__(self, orbital_type, grid_position, owner=0):
        ShipyardMixin.__init__(self)
        self.orbital_type = orbital_type
        self.grid_position = grid_position
        self.owner = owner
        self.selected = False
        self.health = 100
        self.max_health = 100
        
        # Set properties based on orbital type
        self.name = ORBITAL_TYPES.get(orbital_type, orbital_type)
        self.size = 2  # Orbitals are 2x2 grid cells
        
        # Initialize based on type
        if orbital_type == 'NEBULA_RESEARCH_STATION':
            self.color = (0, 255, 255)  # Cyan
            self.description = "Advanced research facility for nebula studies"
        elif orbital_type == 'ORBITAL_SHIPYARD':
            self.color = (255, 165, 0)  # Orange
            self.description = "Constructs ships in deep space"
        elif orbital_type == 'DEEP_SPACE_FORTRESS':
            self.color = (255, 0, 0)  # Red
            self.description = "Heavily armed defensive platform"
        else:
            self.color = (128, 128, 128)  # Gray default
            self.description = "Unknown orbital structure"
    
    def render(self, screen, offset_x, offset_y, zoom_level=1.0):
        """Render the orbital structure"""
        scaled_grid_size = round(GRID_SIZE * zoom_level)
        
        # Calculate screen position
        px = self.grid_position[0] * scaled_grid_size + offset_x
        py = self.grid_position[1] * scaled_grid_size + offset_y
        
        # Don't render if completely off-screen
        if (px + self.size * scaled_grid_size < 0 or px > screen.get_width() or
            py + self.size * scaled_grid_size < 0 or py > screen.get_height()):
            return
        
        # Draw main structure (2x2 grid)
        structure_rect = pygame.Rect(px, py, self.size * scaled_grid_size, self.size * scaled_grid_size)
        
        # Draw filled rectangle with orbital color
        pygame.draw.rect(screen, self.color, structure_rect)
        
        # Draw border (thicker if selected)
        border_width = 3 if self.selected else 1
        border_color = (255, 255, 0) if self.selected else (255, 255, 255)
        pygame.draw.rect(screen, border_color, structure_rect, border_width)
        
        # Draw orbital type indicator in center
        if zoom_level > 0.3:
            center_x = px + (self.size * scaled_grid_size) // 2
            center_y = py + (self.size * scaled_grid_size) // 2
            
            # Draw different shapes based on type
            if self.orbital_type == 'NEBULA_RESEARCH_STATION':
                # Draw a cross pattern for research
                line_length = scaled_grid_size // 3
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x - line_length, center_y), 
                               (center_x + line_length, center_y), 2)
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x, center_y - line_length), 
                               (center_x, center_y + line_length), 2)
            elif self.orbital_type == 'ORBITAL_SHIPYARD':
                # Draw a diamond for shipyard
                diamond_size = scaled_grid_size // 4
                points = [
                    (center_x, center_y - diamond_size),
                    (center_x + diamond_size, center_y),
                    (center_x, center_y + diamond_size),
                    (center_x - diamond_size, center_y)
                ]
                pygame.draw.polygon(screen, (255, 255, 255), points)
            elif self.orbital_type == 'DEEP_SPACE_FORTRESS':
                # Draw a square for fortress
                fortress_size = scaled_grid_size // 3
                fortress_rect = pygame.Rect(center_x - fortress_size//2, center_y - fortress_size//2, 
                                          fortress_size, fortress_size)
                pygame.draw.rect(screen, (255, 255, 255), fortress_rect, 2)
        
        # Draw health bar if damaged
        if self.health < self.max_health and zoom_level > 0.4:
            health_bar_width = self.size * scaled_grid_size
            health_bar_height = 4
            health_bar_x = px
            health_bar_y = py - health_bar_height - 2
            
            # Background (red)
            health_bg_rect = pygame.Rect(health_bar_x, health_bar_y, health_bar_width, health_bar_height)
            pygame.draw.rect(screen, (255, 0, 0), health_bg_rect)
            
            # Foreground (green)
            health_ratio = self.health / self.max_health
            health_fg_width = int(health_bar_width * health_ratio)
            if health_fg_width > 0:
                health_fg_rect = pygame.Rect(health_bar_x, health_bar_y, health_fg_width, health_bar_height)
                pygame.draw.rect(screen, (0, 255, 0), health_fg_rect)
        
        # Draw label when zoomed in enough
        if zoom_level > 0.5:
            font_size = max(12, min(18, scaled_grid_size // 4))
            font = pygame.font.Font(None, font_size)
            
            # Abbreviate name for display
            if self.orbital_type == 'NEBULA_RESEARCH_STATION':
                label = "NRS"
            elif self.orbital_type == 'ORBITAL_SHIPYARD':
                label = "OSY"
            elif self.orbital_type == 'DEEP_SPACE_FORTRESS':
                label = "DSF"
            else:
                label = "ORB"
            
            label_text = font.render(label, True, (255, 255, 255))
            label_rect = label_text.get_rect()
            label_rect.center = (px + (self.size * scaled_grid_size) // 2, 
                               py + self.size * scaled_grid_size + 8)
            screen.blit(label_text, label_rect)
    
    def render_tooltip(self, screen, offset_x=0, offset_y=0, mouse_pos=None):
        """Render tooltip with orbital information"""
        # If this is an orbital shipyard, use the shipyard tooltip
        if self.has_shipyard():
            return self.render_shipyard_tooltip(screen, offset_x, offset_y, mouse_pos)
        
        # Otherwise, use the regular orbital tooltip
        font = pygame.font.Font(None, 18)
        lines = [
            f"{self.name}",
            f"Owner: Player {self.owner + 1}",
            f"Health: {self.health}/{self.max_health}",
            f"Position: ({self.grid_position[0]}, {self.grid_position[1]})",
            "",
            self.description
        ]
        
        # Add production information
        production = self.get_resource_production()
        if production:
            lines.append("")
            lines.append("Production per turn:")
            for resource, amount in production.items():
                lines.append(f"  {resource}: +{amount}")
        
        # Add special abilities
        abilities = self.get_special_abilities()
        if abilities:
            lines.append("")
            lines.append("Special Abilities:")
            for ability in abilities:
                lines.append(f"  {ability}")
        
        width = max(font.size(line)[0] for line in lines) + 12
        height = len(lines) * 22 + 8
        tooltip_rect = pygame.Rect(offset_x, offset_y, width, height)
        
        pygame.draw.rect(screen, (30, 30, 30), tooltip_rect)
        pygame.draw.rect(screen, (255, 255, 255), tooltip_rect, 1)
        
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (tooltip_rect.x + 6, tooltip_rect.y + 4 + i * 22))
        
        return None  # No interactive buttons for regular orbitals
    
    def get_resource_production(self):
        """Get resource production per turn for this orbital"""
        from .constants import ORBITAL_PRODUCTION
        return ORBITAL_PRODUCTION.get(self.name, {})
    
    def get_special_abilities(self):
        """Get list of special abilities for this orbital type"""
        abilities = []
        
        if self.orbital_type == 'NEBULA_RESEARCH_STATION':
            abilities.append("Double science from nearby nebulae")
            abilities.append("Can research advanced technologies")
        elif self.orbital_type == 'ORBITAL_SHIPYARD':
            abilities.append("Can construct ships without planets")
            abilities.append("25% faster ship construction")
        elif self.orbital_type == 'DEEP_SPACE_FORTRESS':
            abilities.append("Long-range defensive fire")
            abilities.append("Provides area defense bonus")
        
        return abilities
    
    def can_be_placed_at(self, galaxy, grid_x, grid_y):
        """Check if this orbital can be placed at the given position"""
        # Check if the 2x2 area is free of other objects
        for dx in range(self.size):
            for dy in range(self.size):
                check_x = grid_x + dx
                check_y = grid_y + dy
                
                # Check bounds
                if check_x < 0 or check_y < 0 or check_x >= GALAXY_SIZE or check_y >= GALAXY_SIZE:
                    return False
                
                # Check for planets
                for planet in galaxy.planets:
                    px, py = planet.grid_position
                    if (check_x >= px and check_x < px + planet.size and
                        check_y >= py and check_y < py + planet.size):
                        return False
                
                # Check for other orbitals
                for orbital in galaxy.orbitals:
                    ox, oy = orbital.grid_position
                    if (check_x >= ox and check_x < ox + orbital.size and
                        check_y >= oy and check_y < oy + orbital.size):
                        return False
                
                # Check for ships (they can move, but don't place on top of them)
                for ship in galaxy.ships:
                    sx, sy = ship.grid_position
                    if check_x == sx and check_y == sy:
                        return False
        
        # Type-specific placement restrictions
        if self.orbital_type == 'NEBULA_RESEARCH_STATION':
            return self._can_place_nebula_research_station(galaxy, grid_x, grid_y)
        elif self.orbital_type == 'ORBITAL_SHIPYARD':
            return self._can_place_orbital_shipyard(galaxy, grid_x, grid_y)
        elif self.orbital_type == 'DEEP_SPACE_FORTRESS':
            return self._can_place_deep_space_fortress(galaxy, grid_x, grid_y)
        
        return True
    
    def _can_place_nebula_research_station(self, galaxy, grid_x, grid_y):
        """Nebula Research Station must be placed within or near a nebula"""
        # Check if placement is within or adjacent to any nebula
        for nebula in galaxy.nebulae:
            nx, ny = nebula.center_position
            nebula_size = nebula.size
            
            # Calculate distance from orbital center to nebula center
            orbital_center_x = grid_x + self.size // 2
            orbital_center_y = grid_y + self.size // 2
            distance = ((orbital_center_x - nx) ** 2 + (orbital_center_y - ny) ** 2) ** 0.5
            
            # Allow placement if within nebula or within 5 grids of nebula edge
            if distance <= nebula_size + 5:
                return True
        
        return False  # Must be near a nebula
    
    def _can_place_orbital_shipyard(self, galaxy, grid_x, grid_y):
        """Orbital Shipyard should be placed near planets for resource access"""
        # Check if placement is within reasonable distance of any planet
        min_distance_to_planet = float('inf')
        
        for planet in galaxy.planets:
            px, py = planet.grid_position
            planet_center_x = px + planet.size // 2
            planet_center_y = py + planet.size // 2
            
            # Calculate distance from orbital center to planet center
            orbital_center_x = grid_x + self.size // 2
            orbital_center_y = grid_y + self.size // 2
            distance = ((orbital_center_x - planet_center_x) ** 2 + (orbital_center_y - planet_center_y) ** 2) ** 0.5
            
            min_distance_to_planet = min(min_distance_to_planet, distance)
        
        # Must be within 15 grids of a planet (but not too close to avoid overlap)
        return 8 <= min_distance_to_planet <= 15
    
    def _can_place_deep_space_fortress(self, galaxy, grid_x, grid_y):
        """Deep Space Fortress should be placed in deep space, away from other major structures"""
        # Check minimum distance from planets
        for planet in galaxy.planets:
            px, py = planet.grid_position
            planet_center_x = px + planet.size // 2
            planet_center_y = py + planet.size // 2
            
            orbital_center_x = grid_x + self.size // 2
            orbital_center_y = grid_y + self.size // 2
            distance = ((orbital_center_x - planet_center_x) ** 2 + (orbital_center_y - planet_center_y) ** 2) ** 0.5
            
            # Must be at least 10 grids away from any planet
            if distance < 10:
                return False
        
        # Check minimum distance from nebulae
        for nebula in galaxy.nebulae:
            nx, ny = nebula.center_position
            orbital_center_x = grid_x + self.size // 2
            orbital_center_y = grid_y + self.size // 2
            distance = ((orbital_center_x - nx) ** 2 + (orbital_center_y - ny) ** 2) ** 0.5
            
            # Must be at least 8 grids away from nebula edge
            if distance < nebula.size + 8:
                return False
        
        # Check minimum distance from other orbitals
        for orbital in galaxy.orbitals:
            if orbital == self:
                continue
            ox, oy = orbital.grid_position
            other_center_x = ox + orbital.size // 2
            other_center_y = oy + orbital.size // 2
            
            orbital_center_x = grid_x + self.size // 2
            orbital_center_y = grid_y + self.size // 2
            distance = ((orbital_center_x - other_center_x) ** 2 + (orbital_center_y - other_center_y) ** 2) ** 0.5
            
            # Must be at least 12 grids away from other orbitals
            if distance < 12:
                return False
        
        return True  # Can be placed in deep space
    
    def update(self, galaxy):
        """Update orbital each turn"""
        # Add resources to owner
        if hasattr(galaxy, 'players') and self.owner < len(galaxy.players):
            player = galaxy.players[self.owner]
            production = self.get_resource_production()
            for resource, amount in production.items():
                player.add_resource(resource, amount)
        
        # Special orbital effects
        if self.orbital_type == 'NEBULA_RESEARCH_STATION':
            self._update_nebula_research(galaxy)
        elif self.orbital_type == 'ORBITAL_SHIPYARD':
            self._update_shipyard(galaxy)
        elif self.orbital_type == 'DEEP_SPACE_FORTRESS':
            self._update_fortress(galaxy)
    
    def _update_nebula_research(self, galaxy):
        """Handle nebula research station special effects"""
        # Check for nearby nebulae and provide bonus science
        bonus_science = 0
        for nebula in galaxy.nebulae:
            nx, ny = nebula.grid_position
            ox, oy = self.grid_position
            
            # Check if nebula overlaps with orbital area (within nebula effect range)
            distance = ((nx - ox) ** 2 + (ny - oy) ** 2) ** 0.5
            if distance <= nebula.size + 5:  # Within effect range
                bonus_science += 2
        
        if bonus_science > 0 and hasattr(galaxy, 'players'):
            player = galaxy.players[self.owner]
            player.add_resource('Science', bonus_science)
    
    def _update_shipyard(self, galaxy):
        """Handle orbital shipyard special effects"""
        # Future: Implement ship construction queue
        pass
    
    def _update_fortress(self, galaxy):
        """Handle deep space fortress special effects"""
        # Future: Implement area defense and combat effects
        pass 