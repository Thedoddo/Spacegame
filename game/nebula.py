import pygame
import numpy as np
from .constants import NEBULA_TYPES, NEBULA_COLORS, NEBULA_EFFECTS, GRID_SIZE

class Nebula:
    def __init__(self, nebula_type, center_position, size=15):
        self.nebula_type = nebula_type
        self.center_position = center_position  # (x, y) grid coordinates
        self.size = size  # Radius in grid units
        self.name = NEBULA_TYPES[nebula_type]
        self.base_color = NEBULA_COLORS[nebula_type]
        self.effects = NEBULA_EFFECTS[nebula_type]
        
        # Generate color variations for this specific nebula
        self.color_variants = self._generate_color_variants()
        
        # Generate cloud points for visual effect
        self.cloud_points = self._generate_cloud_points()
        
    def _generate_color_variants(self):
        """Generate color variations for this specific nebula"""
        import random
        base_r, base_g, base_b, base_a = self.base_color
        variants = []
        
        # Create 5-8 different color variants for this nebula
        num_variants = random.randint(5, 8)
        
        for _ in range(num_variants):
            if self.nebula_type == 'DARK':
                # Dark nebulae: vary between purple, blue, and green tints
                tint_type = random.choice(['purple', 'blue', 'green', 'neutral'])
                if tint_type == 'purple':
                    r = base_r + random.randint(-20, 40)  # More red for purple
                    g = base_g + random.randint(-30, 10)  # Less green
                    b = base_b + random.randint(20, 60)   # More blue
                elif tint_type == 'blue':
                    r = base_r + random.randint(-40, 10)  # Less red
                    g = base_g + random.randint(-20, 30)  # Vary green
                    b = base_b + random.randint(40, 80)   # Much more blue
                elif tint_type == 'green':
                    r = base_r + random.randint(-30, 20)  # Less red
                    g = base_g + random.randint(30, 70)   # More green
                    b = base_b + random.randint(-20, 40)  # Vary blue
                else:  # neutral
                    r = base_r + random.randint(-20, 20)
                    g = base_g + random.randint(-20, 20)
                    b = base_b + random.randint(-20, 20)
                    
            elif self.nebula_type == 'EMISSION':
                # Emission nebulae: vary between red, pink, and magenta
                r = base_r + random.randint(-30, 30)
                g = base_g + random.randint(-40, 60)   # Vary green for pink/magenta
                b = base_b + random.randint(-50, 100)  # Vary blue for different pinks
                
            elif self.nebula_type == 'REFLECTION':
                # Reflection nebulae: vary blue shades and cyan tints
                r = base_r + random.randint(-30, 50)   # Sometimes more cyan
                g = base_g + random.randint(-20, 40)   # Vary for cyan effect
                b = base_b + random.randint(-20, 50)   # Keep mostly blue
                
            elif self.nebula_type == 'PLANETARY':
                # Planetary nebulae: vary between cyan, green, and teal
                r = base_r + random.randint(-40, 30)   # Less red
                g = base_g + random.randint(-30, 30)   # Vary green
                b = base_b + random.randint(-30, 50)   # Vary blue for teal
                
            elif self.nebula_type == 'SUPERNOVA':
                # Supernova remnants: vary between orange, yellow, and red
                r = base_r + random.randint(-20, 30)   # Keep high red
                g = base_g + random.randint(-50, 50)   # Vary for orange/yellow
                b = base_b + random.randint(-60, 40)   # Less blue, sometimes more for white-hot
            
            # Clamp values to valid range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Vary alpha slightly too
            a = base_a + random.randint(-20, 20)
            a = max(30, min(150, a))  # Keep some transparency
            
            variants.append((r, g, b, a))
        
        return variants
    
    def _generate_cloud_points(self):
        """Generate random points within the nebula for cloudy visual effect"""
        points = []
        center_x, center_y = self.center_position
        
        # Generate multiple layers of cloud density
        num_points = self.size * 8  # More points for larger nebulae
        
        for _ in range(num_points):
            # Use normal distribution for more realistic cloud density
            angle = np.random.uniform(0, 2 * np.pi)
            # Most points near center, some scattered further out
            distance = np.random.normal(0, self.size / 3)
            distance = abs(distance)  # Ensure positive
            distance = min(distance, self.size)  # Cap at nebula size
            
            x = center_x + distance * np.cos(angle)
            y = center_y + distance * np.sin(angle)
            
            # Add some randomness to make it look more natural
            x += np.random.uniform(-0.5, 0.5)
            y += np.random.uniform(-0.5, 0.5)
            
            # Vary the size of cloud particles
            particle_size = np.random.uniform(0.5, 2.0)
            
            # Assign a random color variant to this particle
            color_variant = np.random.choice(len(self.color_variants))
            
            points.append((x, y, particle_size, color_variant))
            
        return points
    
    def contains_position(self, grid_x, grid_y):
        """Check if a grid position is within this nebula"""
        center_x, center_y = self.center_position
        distance = ((grid_x - center_x) ** 2 + (grid_y - center_y) ** 2) ** 0.5
        return distance <= self.size
    
    def get_effects_for_position(self, grid_x, grid_y):
        """Get the nebula effects for a specific position"""
        if self.contains_position(grid_x, grid_y):
            return self.effects
        return {}
    
    def draw(self, screen, offset_x, offset_y, zoom_level):
        """Draw the nebula with cloudy visual effects"""
        scaled_grid_size = GRID_SIZE * zoom_level
        
        # Draw cloud particles
        for point_x, point_y, particle_size, color_variant_index in self.cloud_points:
            # Convert grid coordinates to screen coordinates
            screen_x = point_x * scaled_grid_size + offset_x
            screen_y = point_y * scaled_grid_size + offset_y
            
            # Only draw if on screen
            if (-100 <= screen_x <= screen.get_width() + 100 and 
                -100 <= screen_y <= screen.get_height() + 100):
                
                # Create a gradient circle for each cloud particle
                particle_radius = max(2, int(particle_size * scaled_grid_size))
                
                # Get the color variant for this particle
                particle_color = self.color_variants[color_variant_index]
                
                # Create multiple circles with decreasing alpha for soft edges
                for i in range(3):
                    alpha_multiplier = (3 - i) / 3.0
                    current_alpha = int(particle_color[3] * alpha_multiplier)
                    current_color = (*particle_color[:3], current_alpha)
                    current_radius = max(1, particle_radius - i * 2)
                    
                    if current_radius > 0:
                        # Create a temporary surface for this circle
                        circle_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(circle_surface, current_color, 
                                         (current_radius, current_radius), current_radius)
                        
                        # Blit to screen
                        screen.blit(circle_surface, 
                                  (screen_x - current_radius, screen_y - current_radius))
        
        # Draw nebula name if zoomed in enough
        if zoom_level > 0.3:
            center_x, center_y = self.center_position
            screen_x = center_x * scaled_grid_size + offset_x
            screen_y = center_y * scaled_grid_size + offset_y
            
            if (0 <= screen_x <= screen.get_width() and 
                0 <= screen_y <= screen.get_height()):
                
                font = pygame.font.Font(None, max(16, int(24 * zoom_level)))
                text = font.render(self.name, True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_x, screen_y))
                
                # Add a dark background for better readability
                bg_rect = text_rect.inflate(8, 4)
                bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 128))
                screen.blit(bg_surface, bg_rect)
                screen.blit(text, text_rect)
        
        # Draw hitbox/boundary circle for debugging and future nebula-only buildings
        center_x, center_y = self.center_position
        center_screen_x = center_x * scaled_grid_size + offset_x
        center_screen_y = center_y * scaled_grid_size + offset_y
        hitbox_radius = int(self.size * scaled_grid_size)
        
        # Only draw hitbox if it's visible on screen
        if (-hitbox_radius <= center_screen_x <= screen.get_width() + hitbox_radius and 
            -hitbox_radius <= center_screen_y <= screen.get_height() + hitbox_radius):
            
            # Draw a subtle boundary circle
            boundary_color = (*self.base_color[:3], 60)  # Very transparent version of nebula color
            if hitbox_radius > 2:
                # Create a surface for the boundary circle
                boundary_surface = pygame.Surface((hitbox_radius * 2, hitbox_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(boundary_surface, boundary_color, 
                                 (hitbox_radius, hitbox_radius), hitbox_radius, 2)
                screen.blit(boundary_surface, 
                          (center_screen_x - hitbox_radius, center_screen_y - hitbox_radius))
    
    def __str__(self):
        return f"{self.name} at {self.center_position}" 