import pygame
import math
import random

class Ship:
    def __init__(self, x, y, ship_type, team):
        self.x = x
        self.y = y
        self.ship_type = ship_type
        self.team = team  # 0 = player, 1 = enemy
        self.angle = 0  # facing direction in degrees
        self.velocity_x = 0
        self.velocity_y = 0
        self.health = 100
        self.max_health = 100
        
        # Ship stats based on type
        self.stats = self._get_ship_stats()
        self.max_health = self.stats['health']
        self.health = self.max_health
        
        # Combat
        self.last_shot_time = 0
        self.target = None
        
    def _get_ship_stats(self):
        stats = {
            'Fighter': {'width': 20, 'height': 10, 'speed': 3, 'turn_rate': 5, 'health': 30, 'damage': 15, 'range': 150, 'fire_rate': 500},
            'Corvette': {'width': 30, 'height': 15, 'speed': 2.5, 'turn_rate': 4, 'health': 50, 'damage': 20, 'range': 180, 'fire_rate': 700},
            'Frigate': {'width': 40, 'height': 20, 'speed': 2, 'turn_rate': 3, 'health': 80, 'damage': 30, 'range': 200, 'fire_rate': 1000},
            'Destroyer': {'width': 60, 'height': 25, 'speed': 1.5, 'turn_rate': 2, 'health': 120, 'damage': 45, 'range': 250, 'fire_rate': 1200},
            'Cruiser': {'width': 80, 'height': 30, 'speed': 1, 'turn_rate': 1.5, 'health': 180, 'damage': 60, 'range': 300, 'fire_rate': 1500},
            'Battleship': {'width': 100, 'height': 40, 'speed': 0.8, 'turn_rate': 1, 'health': 250, 'damage': 80, 'range': 350, 'fire_rate': 2000}
        }
        return stats.get(self.ship_type, stats['Fighter'])
    
    def update(self, dt):
        # Apply velocity
        self.x += self.velocity_x * dt / 16  # Normalize for 60 FPS
        self.y += self.velocity_y * dt / 16
        
        # Apply friction
        self.velocity_x *= 0.98
        self.velocity_y *= 0.98
        
        # Keep in bounds (2000x2000 battlefield)
        self.x = max(50, min(1950, self.x))
        self.y = max(50, min(1950, self.y))
    
    def move_forward(self, dt):
        # Convert angle to radians
        angle_rad = math.radians(self.angle)
        
        # Apply thrust
        thrust = self.stats['speed']
        self.velocity_x += math.cos(angle_rad) * thrust * dt / 16
        self.velocity_y += math.sin(angle_rad) * thrust * dt / 16
        
        # Limit max speed
        max_speed = self.stats['speed'] * 2
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > max_speed:
            self.velocity_x = (self.velocity_x / speed) * max_speed
            self.velocity_y = (self.velocity_y / speed) * max_speed
    
    def turn_left(self, dt):
        self.angle -= self.stats['turn_rate'] * dt / 16
        self.angle = self.angle % 360
    
    def turn_right(self, dt):
        self.angle += self.stats['turn_rate'] * dt / 16
        self.angle = self.angle % 360
    
    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot_time > self.stats['fire_rate']
    
    def shoot(self, target_x, target_y):
        if not self.can_shoot():
            return None
            
        self.last_shot_time = pygame.time.get_ticks()
        
        # Calculate shot direction
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.stats['range']:
            return None  # Out of range
        
        # Create projectile
        return Projectile(self.x, self.y, dx/distance, dy/distance, self.stats['damage'], self.team)
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0  # Return True if destroyed
    
    def get_rect(self):
        return pygame.Rect(self.x - self.stats['width']//2, self.y - self.stats['height']//2, 
                          self.stats['width'], self.stats['height'])
    
    def draw(self, screen, camera_x, camera_y):
        # Calculate screen position
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Don't draw if off screen
        if screen_x < -50 or screen_x > 850 or screen_y < -50 or screen_y > 650:
            return
        
        # Ship color based on team
        color = (0, 100, 255) if self.team == 0 else (255, 100, 0)
        
        # Draw ship as rotated rectangle
        ship_surface = pygame.Surface((self.stats['width'], self.stats['height']), pygame.SRCALPHA)
        pygame.draw.rect(ship_surface, color, (0, 0, self.stats['width'], self.stats['height']))
        
        # Add ship type indicator
        font = pygame.font.Font(None, 16)
        text = font.render(self.ship_type[:3], True, (255, 255, 255))
        ship_surface.blit(text, (2, 2))
        
        # Rotate ship
        rotated_surface = pygame.transform.rotate(ship_surface, -self.angle)
        rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_surface, rotated_rect)
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = 30
            bar_height = 4
            health_ratio = self.health / self.max_health
            
            # Background
            pygame.draw.rect(screen, (255, 0, 0), 
                           (screen_x - bar_width//2, screen_y - 25, bar_width, bar_height))
            # Health
            pygame.draw.rect(screen, (0, 255, 0), 
                           (screen_x - bar_width//2, screen_y - 25, bar_width * health_ratio, bar_height))

class Projectile:
    def __init__(self, x, y, dx, dy, damage, team):
        self.x = x
        self.y = y
        self.dx = dx * 8  # Projectile speed
        self.dy = dy * 8
        self.damage = damage
        self.team = team
        self.lifetime = 2000  # 2 seconds
        self.created_time = pygame.time.get_ticks()
    
    def update(self, dt):
        self.x += self.dx * dt / 16
        self.y += self.dy * dt / 16
        
        # Check if expired
        return pygame.time.get_ticks() - self.created_time > self.lifetime
    
    def get_rect(self):
        return pygame.Rect(self.x - 2, self.y - 2, 4, 4)
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if 0 <= screen_x <= 800 and 0 <= screen_y <= 600:
            color = (255, 255, 0) if self.team == 0 else (255, 100, 100)
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 3)

class TacticalCombat:
    def __init__(self):
        self.ships = []
        self.projectiles = []
        self.camera_x = 1000  # Center camera
        self.camera_y = 1000
        self.selected_ship = None
        self.paused = False
        self.speed_multiplier = 1.0
        
        # Create test battle
        self._create_test_battle()
    
    def _create_test_battle(self):
        # Player ships (left side)
        ship_types = ['Fighter', 'Corvette', 'Frigate', 'Destroyer']
        for i, ship_type in enumerate(ship_types):
            ship = Ship(200, 800 + i * 100, ship_type, 0)
            ship.angle = 0  # Facing right
            self.ships.append(ship)
        
        # Enemy ships (right side)
        for i, ship_type in enumerate(ship_types):
            ship = Ship(1800, 800 + i * 100, ship_type, 1)
            ship.angle = 180  # Facing left
            self.ships.append(ship)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_1:
                self.speed_multiplier = 0.5
            elif event.key == pygame.K_2:
                self.speed_multiplier = 1.0
            elif event.key == pygame.K_3:
                self.speed_multiplier = 2.0
            elif event.key == pygame.K_4:
                self.speed_multiplier = 4.0
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                world_x = mouse_x + self.camera_x - 400
                world_y = mouse_y + self.camera_y - 300
                
                # Select ship
                self.selected_ship = None
                for ship in self.ships:
                    if ship.team == 0:  # Only select player ships
                        distance = math.sqrt((ship.x - world_x)**2 + (ship.y - world_y)**2)
                        if distance < 30:
                            self.selected_ship = ship
                            break
            
            elif event.button == 3:  # Right click
                if self.selected_ship:
                    mouse_x, mouse_y = event.pos
                    world_x = mouse_x + self.camera_x - 400
                    world_y = mouse_y + self.camera_y - 300
                    
                    # Move command - turn ship toward target
                    dx = world_x - self.selected_ship.x
                    dy = world_y - self.selected_ship.y
                    target_angle = math.degrees(math.atan2(dy, dx))
                    self.selected_ship.angle = target_angle
    
    def update(self, dt):
        if self.paused:
            return
        
        effective_dt = dt * self.speed_multiplier
        
        # Update ships
        for ship in self.ships[:]:
            ship.update(effective_dt)
            
            # Simple AI for enemy ships
            if ship.team == 1:
                # Find nearest player ship
                nearest_enemy = None
                nearest_distance = float('inf')
                
                for other_ship in self.ships:
                    if other_ship.team != ship.team and other_ship.health > 0:
                        distance = math.sqrt((ship.x - other_ship.x)**2 + (ship.y - other_ship.y)**2)
                        if distance < nearest_distance:
                            nearest_distance = distance
                            nearest_enemy = other_ship
                
                if nearest_enemy:
                    # Turn toward enemy
                    dx = nearest_enemy.x - ship.x
                    dy = nearest_enemy.y - ship.y
                    target_angle = math.degrees(math.atan2(dy, dx))
                    
                    angle_diff = (target_angle - ship.angle + 180) % 360 - 180
                    if abs(angle_diff) > 5:
                        if angle_diff > 0:
                            ship.turn_right(effective_dt)
                        else:
                            ship.turn_left(effective_dt)
                    else:
                        ship.move_forward(effective_dt)
                    
                    # Shoot if in range and facing target
                    if nearest_distance < ship.stats['range'] and abs(angle_diff) < 15:
                        projectile = ship.shoot(nearest_enemy.x, nearest_enemy.y)
                        if projectile:
                            self.projectiles.append(projectile)
        
        # Handle player ship controls
        keys = pygame.key.get_pressed()
        if self.selected_ship and self.selected_ship.health > 0:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.selected_ship.move_forward(effective_dt)
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.selected_ship.turn_left(effective_dt)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.selected_ship.turn_right(effective_dt)
            if keys[pygame.K_LCTRL]:
                # Auto-shoot at nearest enemy
                nearest_enemy = None
                nearest_distance = float('inf')
                
                for other_ship in self.ships:
                    if other_ship.team != self.selected_ship.team and other_ship.health > 0:
                        distance = math.sqrt((self.selected_ship.x - other_ship.x)**2 + (self.selected_ship.y - other_ship.y)**2)
                        if distance < nearest_distance:
                            nearest_distance = distance
                            nearest_enemy = other_ship
                
                if nearest_enemy:
                    projectile = self.selected_ship.shoot(nearest_enemy.x, nearest_enemy.y)
                    if projectile:
                        self.projectiles.append(projectile)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            if projectile.update(effective_dt):
                self.projectiles.remove(projectile)
                continue
            
            # Check collisions with ships
            for ship in self.ships:
                if ship.team != projectile.team and ship.health > 0:
                    if projectile.get_rect().colliderect(ship.get_rect()):
                        if ship.take_damage(projectile.damage):
                            print(f"{ship.ship_type} destroyed!")
                        self.projectiles.remove(projectile)
                        break
        
        # Update camera to follow selected ship
        if self.selected_ship:
            target_x = self.selected_ship.x - 400
            target_y = self.selected_ship.y - 300
            self.camera_x += (target_x - self.camera_x) * 0.1
            self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Keep camera in bounds
        self.camera_x = max(0, min(1200, self.camera_x))
        self.camera_y = max(0, min(1400, self.camera_y))
    
    def draw(self, screen):
        # Clear screen
        screen.fill((10, 10, 30))  # Dark space background
        
        # Draw grid
        grid_size = 100
        for x in range(0, 2000, grid_size):
            screen_x = x - self.camera_x
            if -10 <= screen_x <= 810:
                pygame.draw.line(screen, (30, 30, 50), (screen_x, 0), (screen_x, 600))
        
        for y in range(0, 2000, grid_size):
            screen_y = y - self.camera_y
            if -10 <= screen_y <= 610:
                pygame.draw.line(screen, (30, 30, 50), (0, screen_y), (800, screen_y))
        
        # Draw ships
        for ship in self.ships:
            if ship.health > 0:
                ship.draw(screen, self.camera_x, self.camera_y)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen, self.camera_x, self.camera_y)
        
        # Draw selection indicator
        if self.selected_ship and self.selected_ship.health > 0:
            screen_x = self.selected_ship.x - self.camera_x
            screen_y = self.selected_ship.y - self.camera_y
            pygame.draw.circle(screen, (0, 255, 0), (int(screen_x), int(screen_y)), 40, 2)
        
        # Draw UI
        self._draw_ui(screen)
    
    def _draw_ui(self, screen):
        font = pygame.font.Font(None, 24)
        
        # Instructions
        instructions = [
            "Left Click: Select ship",
            "Right Click: Move/Turn toward",
            "WASD/Arrows: Move selected ship",
            "Ctrl: Auto-fire",
            "Space: Pause",
            "1-4: Speed control",
            f"Speed: {self.speed_multiplier}x",
            "PAUSED" if self.paused else ""
        ]
        
        for i, instruction in enumerate(instructions):
            if instruction:
                color = (255, 255, 0) if instruction == "PAUSED" else (255, 255, 255)
                text = font.render(instruction, True, color)
                screen.blit(text, (10, 10 + i * 25))
        
        # Ship status
        if self.selected_ship:
            status_text = f"Selected: {self.selected_ship.ship_type} - Health: {self.selected_ship.health}/{self.selected_ship.max_health}"
            text = font.render(status_text, True, (0, 255, 0))
            screen.blit(text, (10, 400))

def run_tactical_combat():
    """Standalone function to run tactical combat demo"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tactical Combat Demo")
    clock = pygame.time.Clock()
    
    combat = TacticalCombat()
    running = True
    
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            else:
                combat.handle_event(event)
        
        combat.update(dt)
        combat.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    run_tactical_combat() 