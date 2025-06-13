import pygame
import numpy as np
from .constants import *
from .planet import Planet, Sun, PLANET_TYPES, SUN_TYPES
from .unit import Ship, Frigate, Destroyer, Cruiser, Battleship, Carrier, Fighter, Bomber, BuilderShip, Corvette

class Galaxy:
    def __init__(self):
        self.ships = []
        self.selected_unit = None
        self.move_tiles = []

        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = None
        self.planets = []  # List of all planets
        self.asteroids = []  # List of all asteroids

        self.pan_speed = 20  # Speed for panning
        self.zoom_level = 1.0  # Initial zoom level
        self.build_mode = False
        self.build_warning = None  # Store warning message for UI
        self.building_just_placed = False  # Track if a building was just placed
        self.generate_planets()
        self.generate_asteroids()
        self.spawn_ship()

    def is_space_free(self, x, y, size):
        # Check if the area (x, y, size) is at least 1 grid away from all existing planets
        for obj in self.planets:
            ox, oy = obj.grid_position
            osize = obj.size
            # Calculate bounding boxes with 1-grid buffer
            if (x + size + 1 > ox and x < ox + osize + 1 and
                y + size + 1 > oy and y < oy + osize + 1):
                return False
        return True

    def generate_planets(self):
        import string
        self.planets.clear()
        system_letters = list(string.ascii_uppercase)
        system_index = 0
        # Ensure at least one system near the spawn corners, but slightly away
        spawn_systems = [(50, 50), (GALAXY_SIZE - 50, GALAXY_SIZE - 50)]
        sun_positions = []
        for spawn_x, spawn_y in spawn_systems:
            if not self.is_space_free(spawn_x, spawn_y, 9):
                continue
            system_label = system_letters[system_index % len(system_letters)]
            sun_type = list(SUN_TYPES.keys())[system_index % len(SUN_TYPES)]
            sun = Sun(sun_type, (spawn_x, spawn_y), system_label)
            self.planets.append(sun)
            sun_positions.append((spawn_x, spawn_y))
            print(f"Star ({system_label}-{sun_type}) placed at: ({spawn_x}, {spawn_y})")
            # Generate planets around the sun
            num_planets = np.random.randint(3, 6)
            for planet_num in range(num_planets):
                for attempt in range(30):
                    angle = np.random.uniform(0, 2 * np.pi)
                    distance = np.random.randint(10, 20)
                    planet_type = list(PLANET_TYPES.keys())[np.random.randint(0, len(PLANET_TYPES))]
                    planet_size = np.random.randint(2, 7)
                    x = int(spawn_x + distance * np.cos(angle))
                    y = int(spawn_y + distance * np.sin(angle))
                    if self.is_space_free(x, y, planet_size):
                        planet = Planet(planet_type, (x, y), size=planet_size, system_label=system_label)
                        self.planets.append(planet)
                        break
            system_index += 1

        # Randomly generate the rest of the systems
        num_systems = np.random.randint(3, 9)  # Adjust as needed
        min_distance = 100  # Minimum distance between suns
        for _ in range(num_systems):
            for attempt in range(100):  # Try up to 100 times to find a valid position
                sun_x = np.random.randint(0, GALAXY_SIZE - 9)
                sun_y = np.random.randint(0, GALAXY_SIZE - 9)
                if not self.is_space_free(sun_x, sun_y, 9):
                    continue
                too_close = False
                for (other_x, other_y) in sun_positions:
                    if ((sun_x - other_x) ** 2 + (sun_y - other_y) ** 2) ** 0.5 < min_distance:
                        too_close = True
                        break
                if not too_close:
                    system_label = system_letters[system_index % len(system_letters)]
                    sun_type = list(SUN_TYPES.keys())[system_index % len(SUN_TYPES)]
                    sun = Sun(sun_type, (sun_x, sun_y), system_label)
                    self.planets.append(sun)
                    sun_positions.append((sun_x, sun_y))
                    print(f"Star ({system_label}-{sun_type}) placed at: ({sun_x}, {sun_y})")
                    # Generate planets around the sun
                    num_planets = np.random.randint(3, 6)
                    for planet_num in range(num_planets):
                        for attempt in range(30):
                            angle = np.random.uniform(0, 2 * np.pi)
                            distance = np.random.randint(10, 20)
                            planet_type = list(PLANET_TYPES.keys())[np.random.randint(0, len(PLANET_TYPES))]
                            planet_size = np.random.randint(2, 7)
                            x = int(sun_x + distance * np.cos(angle))
                            y = int(sun_y + distance * np.sin(angle))
                            if self.is_space_free(x, y, planet_size):
                                planet = Planet(planet_type, (x, y), size=planet_size, system_label=system_label)
                                self.planets.append(planet)
                                break
                    system_index += 1
                    break  # Sun placed, move to next system

        print(f"Total planets generated: {len(self.planets)}")
        print(f"Sun positions: {sun_positions}")

    def generate_asteroids(self):
        """Generate dense asteroid field patches scattered throughout the galaxy"""
        import random
        self.asteroids.clear()
        
        # Generate 25-40 asteroid field patches (even more patches)
        num_asteroid_patches = random.randint(25, 40)
        
        for patch_num in range(num_asteroid_patches):
            # Find a center point for this patch
            for attempt in range(50):  # Try up to 50 times to find a valid center
                center_x = random.randint(20, GALAXY_SIZE - 20)
                center_y = random.randint(20, GALAXY_SIZE - 20)
                
                # Check if center is far enough from planets and suns
                too_close = False
                for planet in self.planets:
                    px, py = planet.grid_position
                    distance = ((center_x - px) ** 2 + (center_y - py) ** 2) ** 0.5
                    if distance < 25:  # At least 25 grids away from planets
                        too_close = True
                        break
                
                if not too_close:
                    # Choose a random patch shape
                    patch_shapes = ['cluster', 'line', 'ring', 'scattered', 'dense_core', 'spiral']
                    patch_shape = random.choice(patch_shapes)
                    
                    # Create different shaped patches with 40-80 asteroids
                    asteroids_in_patch = random.randint(40, 80)
                    patch_radius = random.randint(12, 20)
                    
                    if patch_shape == 'cluster':
                        # Dense circular cluster
                        for _ in range(asteroids_in_patch):
                            for asteroid_attempt in range(20):
                                offset_x = random.randint(-patch_radius//2, patch_radius//2)
                                offset_y = random.randint(-patch_radius//2, patch_radius//2)
                                x = center_x + offset_x
                                y = center_y + offset_y
                                
                                if 0 <= x < GALAXY_SIZE and 0 <= y < GALAXY_SIZE:
                                    position_free = True
                                    for existing_asteroid in self.asteroids:
                                        if existing_asteroid['position'] == (x, y):
                                            position_free = False
                                            break
                                    
                                    if position_free:
                                        asteroid = {'position': (x, y), 'type': 'asteroid'}
                                        self.asteroids.append(asteroid)
                                        break
                    
                    elif patch_shape == 'line':
                        # Linear asteroid belt
                        angle = random.uniform(0, 2 * 3.14159)  # Random direction
                        for i in range(asteroids_in_patch):
                            distance = random.randint(-patch_radius, patch_radius)
                            perpendicular_offset = random.randint(-3, 3)  # Small perpendicular spread
                            
                            x = center_x + int(distance * 0.7071) + int(perpendicular_offset * 0.7071)  # cos/sin approximation
                            y = center_y + int(distance * 0.7071) + int(perpendicular_offset * -0.7071)
                            
                            if 0 <= x < GALAXY_SIZE and 0 <= y < GALAXY_SIZE:
                                position_free = True
                                for existing_asteroid in self.asteroids:
                                    if existing_asteroid['position'] == (x, y):
                                        position_free = False
                                        break
                                
                                if position_free:
                                    asteroid = {'position': (x, y), 'type': 'asteroid'}
                                    self.asteroids.append(asteroid)
                    
                    elif patch_shape == 'ring':
                        # Ring-shaped asteroid field
                        inner_radius = patch_radius // 3
                        outer_radius = patch_radius
                        for _ in range(asteroids_in_patch):
                            for asteroid_attempt in range(20):
                                angle = random.uniform(0, 2 * 3.14159)
                                radius = random.randint(inner_radius, outer_radius)
                                
                                x = center_x + int(radius * 0.7071)  # Approximate cos
                                y = center_y + int(radius * 0.7071)  # Approximate sin
                                
                                if 0 <= x < GALAXY_SIZE and 0 <= y < GALAXY_SIZE:
                                    position_free = True
                                    for existing_asteroid in self.asteroids:
                                        if existing_asteroid['position'] == (x, y):
                                            position_free = False
                                            break
                                    
                                    if position_free:
                                        asteroid = {'position': (x, y), 'type': 'asteroid'}
                                        self.asteroids.append(asteroid)
                                        break
                    
                    elif patch_shape == 'scattered':
                        # Wide scattered field
                        for _ in range(asteroids_in_patch):
                            for asteroid_attempt in range(20):
                                offset_x = random.randint(-patch_radius, patch_radius)
                                offset_y = random.randint(-patch_radius, patch_radius)
                                x = center_x + offset_x
                                y = center_y + offset_y
                                
                                if 0 <= x < GALAXY_SIZE and 0 <= y < GALAXY_SIZE:
                                    position_free = True
                                    for existing_asteroid in self.asteroids:
                                        if existing_asteroid['position'] == (x, y):
                                            position_free = False
                                            break
                                    
                                    if position_free:
                                        asteroid = {'position': (x, y), 'type': 'asteroid'}
                                        self.asteroids.append(asteroid)
                                        break
                    
                    elif patch_shape == 'dense_core':
                        # Dense center with sparse outer ring
                        core_asteroids = asteroids_in_patch // 2
                        outer_asteroids = asteroids_in_patch - core_asteroids
                        
                        # Dense core
                        for _ in range(core_asteroids):
                            for asteroid_attempt in range(20):
                                offset_x = random.randint(-patch_radius//3, patch_radius//3)
                                offset_y = random.randint(-patch_radius//3, patch_radius//3)
                                x = center_x + offset_x
                                y = center_y + offset_y
                                
                                if 0 <= x < GALAXY_SIZE and 0 <= y < GALAXY_SIZE:
                                    position_free = True
                                    for existing_asteroid in self.asteroids:
                                        if existing_asteroid['position'] == (x, y):
                                            position_free = False
                                            break
                                    
                                    if position_free:
                                        asteroid = {'position': (x, y), 'type': 'asteroid'}
                                        self.asteroids.append(asteroid)
                                        break
                        
                        # Sparse outer ring
                        for _ in range(outer_asteroids):
                            for asteroid_attempt in range(20):
                                offset_x = random.randint(-patch_radius, patch_radius)
                                offset_y = random.randint(-patch_radius, patch_radius)
                                # Skip if too close to center
                                if abs(offset_x) < patch_radius//2 and abs(offset_y) < patch_radius//2:
                                    continue
                                    
                                x = center_x + offset_x
                                y = center_y + offset_y
                                
                                if 0 <= x < GALAXY_SIZE and 0 <= y < GALAXY_SIZE:
                                    position_free = True
                                    for existing_asteroid in self.asteroids:
                                        if existing_asteroid['position'] == (x, y):
                                            position_free = False
                                            break
                                    
                                    if position_free:
                                        asteroid = {'position': (x, y), 'type': 'asteroid'}
                                        self.asteroids.append(asteroid)
                                        break
                    
                    elif patch_shape == 'spiral':
                        # Spiral pattern
                        for i in range(asteroids_in_patch):
                            angle = (i / asteroids_in_patch) * 4 * 3.14159  # 2 full rotations
                            radius = (i / asteroids_in_patch) * patch_radius
                            
                            x = center_x + int(radius * 0.7071) + random.randint(-2, 2)  # Add some randomness
                            y = center_y + int(radius * 0.7071) + random.randint(-2, 2)
                            
                            if 0 <= x < GALAXY_SIZE and 0 <= y < GALAXY_SIZE:
                                position_free = True
                                for existing_asteroid in self.asteroids:
                                    if existing_asteroid['position'] == (x, y):
                                        position_free = False
                                        break
                                
                                if position_free:
                                    asteroid = {'position': (x, y), 'type': 'asteroid'}
                                    self.asteroids.append(asteroid)
                    
                    print(f"Generated {patch_shape} asteroid patch {patch_num + 1} at ({center_x}, {center_y}) with {len([a for a in self.asteroids if abs(a['position'][0] - center_x) <= patch_radius and abs(a['position'][1] - center_y) <= patch_radius])} asteroids")
                    break
        
        print(f"Generated {len(self.asteroids)} total asteroids in {num_asteroid_patches} patches")

    def spawn_ship(self):
        self.ships.clear()
        # Player 1 ships
        self.ships.append(BuilderShip((0, 0), owner=0))
        self.ships.append(Carrier((2, 0), owner=0))
        self.ships.append(Corvette((0, 2), owner=0))
        self.ships.append(Frigate((2, 2), owner=0))
        self.ships.append(Destroyer((0, 4), owner=0))
        self.ships.append(Cruiser((2, 4), owner=0))
        self.ships.append(Battleship((0, 6), owner=0))
        self.ships.append(Fighter((2, 6), owner=0))
        self.ships.append(Bomber((0, 8), owner=0))
        # Player 2 BuilderShip
        self.ships.append(BuilderShip((GALAXY_SIZE-1, GALAXY_SIZE-1), owner=1))

    def handle_click(self, pos, current_player):
        from .constants import GRID_SIZE
        self.building_just_placed = False  # Reset flag at start of each click
        scaled_grid_size = round(GRID_SIZE * self.zoom_level)
        grid_x = (pos[0] - self.offset_x) // scaled_grid_size
        grid_y = (pos[1] - self.offset_y) // scaled_grid_size
        selected_building_type = getattr(self, 'selected_building_type', None)
        
        print(f"Clicked grid: ({grid_x}, {grid_y}), current_player: {current_player}")
        print("Ships:")
        for ship in self.ships:
            print(f"  {ship.label} at {ship.grid_position}, owner: {ship.owner}")
        
        # --- DEBUG: Print move_tiles and click for ship movement ---
        if self.selected_unit and getattr(self.selected_unit, 'unit_type', None) == 'SHIP':
            print(f"DEBUG: move_tiles={self.move_tiles}, clicked=({grid_x}, {grid_y})")
        
        # --- LOGIC ORDER ---
        # 1. Ship selection (highest priority)
        # 2. Ship movement (if selected and click is in move_tiles)
        # 3. Planet clicks (selection or building placement)
        # 4. Deselect if nothing found
        
        # Find clicked ship
        clicked_ship = None
        for ship in self.ships:
            if ship.grid_position[0] == grid_x and ship.grid_position[1] == grid_y:
                clicked_ship = ship
                print(f"Clicked ship found: {ship.label} at {ship.grid_position}, owner: {ship.owner}, current_player: {current_player}")
                break
        
        # Find clicked planet
        clicked_planet = None
        for planet in self.planets:
            px, py = planet.grid_position
            if px <= grid_x < px + planet.size and py <= grid_y < py + planet.size:
                clicked_planet = planet
                print(f"Clicked planet found: {getattr(planet, 'system_label', '?')}-{getattr(planet, 'type_label', '?')} at {planet.grid_position} (size {planet.size})")
                break
        
        # 1. Ship selection (HIGHEST PRIORITY)
        if clicked_ship:
            if clicked_ship.owner == current_player:
                print(f"Selecting ship: {clicked_ship.label}")
                # Clear previous selections
                for s in self.ships:
                    s.set_selected(False)
                for p in self.planets:
                    p.selected = False
                
                self.selected_unit = clicked_ship
                clicked_ship.set_selected(True)
                
                # Only show move tiles if ship has actions left
                if hasattr(clicked_ship, 'actions_left') and clicked_ship.actions_left > 0:
                    self.move_tiles = self.get_move_tiles(clicked_ship)
                    print(f"DEBUG: Generated {len(self.move_tiles)} move tiles for {clicked_ship.label} with actions_left={clicked_ship.actions_left}, move_range={clicked_ship.move_range}")
                else:
                    self.move_tiles = []  # No movement allowed
                    print(f"DEBUG: {clicked_ship.label} has no actions left ({getattr(clicked_ship, 'actions_left', 'N/A')})")
                
                self.build_mode = False  # Not in build mode for ships
                return
            else:
                print(f"Cannot select {clicked_ship.label} - owned by player {clicked_ship.owner}, current player is {current_player}")
                return
        
        # 2. Ship movement (if ship is selected and click is in move tiles)
        if self.selected_unit and getattr(self.selected_unit, 'unit_type', None) == 'SHIP':
            print(f"DEBUG: Checking move for ship {self.selected_unit.label} at {self.selected_unit.grid_position} with move_tiles={self.move_tiles}")
            
            # Check if ship has actions left before allowing movement
            if hasattr(self.selected_unit, 'actions_left') and self.selected_unit.actions_left <= 0:
                print(f"DEBUG: {self.selected_unit.label} has no actions left ({self.selected_unit.actions_left})")
                return
            
            if (grid_x, grid_y) in self.move_tiles:
                print(f"DEBUG: Attempting to move ship to ({grid_x}, {grid_y})")
                # Check if destination is occupied by another ship or planet
                occupied = False
                docking_carrier = None
                for ship in self.ships:
                    if ship.grid_position == (grid_x, grid_y):
                        # Check for docking with friendly Carrier
                        if (ship.label == 'CAR' and self.selected_unit.label in ('FIG', 'BOM') and ship.owner == self.selected_unit.owner):
                            docking_carrier = ship
                        else:
                            occupied = True
                        break
                for planet in self.planets:
                    px, py = planet.grid_position
                    if px <= grid_x < px + planet.size and py <= grid_y < py + planet.size:
                        occupied = True
                        break
                if docking_carrier and not occupied:
                    # Dock the fighter/bomber
                    if docking_carrier.can_dock(self.selected_unit):
                        docking_carrier.dock_unit(self.selected_unit)
                        print(f"DEBUG: {self.selected_unit.label} docked with Carrier at {docking_carrier.grid_position}")
                        self.ships.remove(self.selected_unit)
                        self.selected_unit.set_selected(False)
                        self.selected_unit = None
                        self.move_tiles = []
                        self.build_mode = False
                        return
                    else:
                        print(f"DEBUG: Carrier at {docking_carrier.grid_position} is full!")
                        return
                if not occupied:
                    print(f"Moving ship {self.selected_unit.label} to ({grid_x}, {grid_y})")
                    self.selected_unit.grid_position = (grid_x, grid_y)
                    if hasattr(self.selected_unit, 'actions_left'):
                        self.selected_unit.actions_left -= 1
                        print(f"DEBUG: {self.selected_unit.label} actions_left now {self.selected_unit.actions_left}")
                    
                    # Update move tiles for remaining actions
                    if hasattr(self.selected_unit, 'actions_left') and self.selected_unit.actions_left > 0:
                        self.move_tiles = self.get_move_tiles(self.selected_unit)
                    else:
                        self.move_tiles = []
                    return
        
        # 3. Handle planet clicks (selection or building placement)
        if clicked_planet:
            # If we have a building selected and we're in build mode, try to place building
            if self.build_mode and self.selected_unit == clicked_planet and selected_building_type:
                # Calculate which grid cell within the planet was clicked
                px, py = clicked_planet.grid_position
                grid_cell_x = grid_x - px
                grid_cell_y = grid_y - py
                
                # Require builder ship within 6 grids
                builder_in_range = False
                for ship in self.ships:
                    if ship.unit_type == 'SHIP' and getattr(ship, 'label', None) == 'BLD' and ship.owner == current_player:
                        sx, sy = ship.grid_position
                        distance = abs(sx - px) + abs(sy - py)
                        if distance <= 6:
                            builder_in_range = True
                            break
                
                if not builder_in_range:
                    self.build_warning = 'A builder ship must be within 6 grids of this planet to build!'
                    print(f"DEBUG: No builder in range for planet at {px}, {py}")
                    return  # Don't reselect planet, just show warning
                
                self.build_warning = None
                
                if clicked_planet.can_build(current_player):
                    # Check if building type is allowed on this planet
                    if not clicked_planet.can_build_type(selected_building_type):
                        self.build_warning = f'{selected_building_type} cannot be built on {clicked_planet.planet_type.title()} planets!'
                        print(f"DEBUG: {selected_building_type} not allowed on {clicked_planet.planet_type}")
                        return  # Don't reselect planet, just show warning
                    
                    # Try to place the building
                    if clicked_planet.place_building(grid_cell_x, grid_cell_y, current_player, selected_building_type):
                        print(f"Building placed at ({grid_cell_x}, {grid_cell_y}) for player {current_player} type {selected_building_type}")
                        self.building_just_placed = True  # Mark that a building was successfully placed
                        # Assign planet ownership if not already owned
                        if not hasattr(clicked_planet, 'owner') or clicked_planet.owner is None:
                            clicked_planet.owner = current_player
                            print(f"Planet {clicked_planet.system_label}-{clicked_planet.type_label} now owned by player {current_player}")
                        return  # Building placed successfully, don't reselect
                    else:
                        # Building placement failed (probably clicked on occupied cell)
                        self.build_warning = 'Cannot place building here - cell may be occupied!'
                        print(f"DEBUG: Building placement failed at ({grid_cell_x}, {grid_cell_y})")
                        return  # Don't reselect planet, just show warning
                else:
                    self.build_warning = 'Cannot build on this planet!'
                    print(f"DEBUG: Cannot build on planet (can_build returned False)")
                    return  # Don't reselect planet, just show warning
            
            # If we're not trying to place a building, handle planet selection
            else:
                print(f"Selecting planet: {getattr(clicked_planet, 'system_label', '?')}-{getattr(clicked_planet, 'type_label', '?')}")
                # Clear previous selections
                for s in self.ships:
                    s.set_selected(False)
                for p in self.planets:
                    p.selected = False
                
                self.selected_unit = clicked_planet
                clicked_planet.selected = True
                self.move_tiles = []
                # Enter build mode if buildable, else just show tooltip
                if hasattr(clicked_planet, 'can_build') and clicked_planet.can_build(current_player) and getattr(clicked_planet, 'planet_type', None) != 'SUN':
                    self.build_mode = True
                    print(f"DEBUG: Entering build mode for planet {getattr(clicked_planet, 'system_label', '?')}-{getattr(clicked_planet, 'type_label', '?')}")
                else:
                    self.build_mode = False
                    print(f"DEBUG: Cannot build on planet {getattr(clicked_planet, 'system_label', '?')}-{getattr(clicked_planet, 'type_label', '?')} (can_build={hasattr(clicked_planet, 'can_build') and clicked_planet.can_build(current_player)}, planet_type={getattr(clicked_planet, 'planet_type', None)})")
                return
        
        # 4. Deselect if nothing found (only if we didn't click on anything valid)
        print("Deselecting unit.")
        # Clear previous selections
        for s in self.ships:
            s.set_selected(False)
        for p in self.planets:
            p.selected = False
        self.build_mode = False  # Exit build mode on deselect
        self.selected_unit = None
        self.build_warning = None
        self.move_tiles = []  # Clear move tiles

    def get_move_tiles(self, ship):
        tiles = []
        for x in range(max(0, ship.grid_position[0] - ship.move_range), min(GALAXY_SIZE, ship.grid_position[0] + ship.move_range + 1)):
            for y in range(max(0, ship.grid_position[1] - ship.move_range), min(GALAXY_SIZE, ship.grid_position[1] + ship.move_range + 1)):
                if abs(x - ship.grid_position[0]) + abs(y - ship.grid_position[1]) <= ship.move_range:
                    tiles.append((x, y))
        return tiles

    def handle_mouse_down(self, pos):
        self.dragging = True
        self.last_mouse_pos = pos

    def handle_mouse_up(self):
        self.dragging = False
        self.last_mouse_pos = None

    def handle_mouse_motion(self, pos):
        if self.dragging and self.last_mouse_pos:
            dx = pos[0] - self.last_mouse_pos[0]
            dy = pos[1] - self.last_mouse_pos[1]
            self.offset_x += dx
            self.offset_y += dy
            self.last_mouse_pos = pos

    def handle_zoom(self, zoom_in):
        from .constants import WINDOW_WIDTH, WINDOW_HEIGHT
        # Calculate world coordinates at the center of the screen before zoom
        center_screen_x = WINDOW_WIDTH // 2
        center_screen_y = WINDOW_HEIGHT // 2
        world_x = (center_screen_x - self.offset_x) / (GRID_SIZE * self.zoom_level)
        world_y = (center_screen_y - self.offset_y) / (GRID_SIZE * self.zoom_level)
        # Change zoom level
        old_zoom = self.zoom_level
        if zoom_in:
            self.zoom_level = max(0.05, self.zoom_level - 0.1)  # Zoom out
        else:
            self.zoom_level = min(2.0, self.zoom_level + 0.1)  # Zoom in
        # Adjust offset to keep the same world point at the center
        self.offset_x = center_screen_x - int(world_x * GRID_SIZE * self.zoom_level)
        self.offset_y = center_screen_y - int(world_y * GRID_SIZE * self.zoom_level)

    def draw(self, screen):
        # Draw grid
        for x in range(0, GALAXY_SIZE * GRID_SIZE, GRID_SIZE):
            for y in range(0, GALAXY_SIZE * GRID_SIZE, GRID_SIZE):
                rect = pygame.Rect(x + self.offset_x, y + self.offset_y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)
        
        # Draw move range tiles
        for tile in self.move_tiles:
            rect = pygame.Rect(tile[0] * GRID_SIZE + self.offset_x, tile[1] * GRID_SIZE + self.offset_y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, (0, 255, 0, 128), rect)
        
        # Draw planets
        for planet in self.planets:
            planet.draw(screen, self.offset_x, self.offset_y)
        
        # Draw ships
        for ship in self.ships:
            ship.draw(screen, self.offset_x, self.offset_y)

    @property
    def selected_planet(self):
        if self.selected_unit and self.selected_unit.unit_type == 'PLANET':
            return self.selected_unit
        return None

    @property
    def selected_ship(self):
        if self.selected_unit and self.selected_unit.unit_type == 'SHIP':
            return self.selected_unit
        return None

    def reset_all_ship_actions(self):
        for ship in self.ships:
            if hasattr(ship, 'reset_actions'):
                ship.reset_actions()

    def handle_pan(self, dx, dy):
        self.offset_x += dx * self.pan_speed
        self.offset_y += dy * self.pan_speed
        max_offset = GALAXY_SIZE * GRID_SIZE
        self.offset_x = max(-max_offset, min(max_offset, self.offset_x))
        self.offset_y = max(-max_offset, min(max_offset, self.offset_y))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.handle_pan(1, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.handle_pan(-1, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.handle_pan(0, 1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.handle_pan(0, -1)

    def render(self, screen):
        # Calculate visible grid range
        from .constants import WINDOW_WIDTH, WINDOW_HEIGHT
        scaled_grid_size = round(GRID_SIZE * self.zoom_level)
        start_x = max(0, (-self.offset_x) // scaled_grid_size)
        end_x = min(GALAXY_SIZE, (WINDOW_WIDTH - self.offset_x) // scaled_grid_size + 2)
        start_y = max(0, (-self.offset_y) // scaled_grid_size)
        end_y = min(GALAXY_SIZE, (WINDOW_HEIGHT - self.offset_y) // scaled_grid_size + 2)

        # Draw grid (only visible cells)
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                rect = pygame.Rect(x * scaled_grid_size + self.offset_x, y * scaled_grid_size + self.offset_y, scaled_grid_size, scaled_grid_size)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

        # Draw coordinate labels if zoomed out
        if self.zoom_level <= 0.4:
            font_size = 28 if self.zoom_level <= 0.2 else 22
            font = pygame.font.Font(None, font_size)
            label_interval = 50 if self.zoom_level <= 0.2 else 10

            # Top edge (x labels)
            for x in range(start_x, end_x, label_interval):
                label = font.render(str(x), True, (200, 200, 200))
                px = x * scaled_grid_size + self.offset_x
                screen.blit(label, (px + 2, 2))
            # Left edge (y labels)
            for y in range(start_y, end_y, label_interval):
                label = font.render(str(y), True, (200, 200, 200))
                py = y * scaled_grid_size + self.offset_y
                screen.blit(label, (2, py + 2))

        # Draw move range tiles (only if visible)
        for tile in self.move_tiles:
            tx, ty = tile
            if start_x <= tx < end_x and start_y <= ty < end_y:
                rect = pygame.Rect(tx * scaled_grid_size + self.offset_x, ty * scaled_grid_size + self.offset_y, scaled_grid_size, scaled_grid_size)
                pygame.draw.rect(screen, (100, 150, 255), rect)  # Solid blue highlight
                pygame.draw.rect(screen, (0, 100, 255), rect, 3)  # Blue border
        
        # Draw planets (only if visible)
        for planet in self.planets:
            px, py = planet.grid_position
            if (px + planet.size > start_x and px < end_x and
                py + planet.size > start_y and py < end_y):
                planet.render(screen, self.offset_x, self.offset_y, self.zoom_level)
                # Always show tooltip if selected or in build mode
                if ((getattr(planet, 'selected', False) or self.build_mode) and hasattr(planet, 'render_tooltip')):
                    # Tooltip always to the right of the planet grid
                    scaled_grid_size = round(GRID_SIZE * self.zoom_level)
                    tooltip_offset_x = (planet.grid_position[0] + planet.size) * scaled_grid_size + self.offset_x + 8
                    tooltip_offset_y = planet.grid_position[1] * scaled_grid_size + self.offset_y
                    planet.render_tooltip(screen, tooltip_offset_x, tooltip_offset_y)
                # Draw grid overlay if selected and not a sun
                if getattr(planet, 'selected', False) and getattr(planet, 'planet_type', None) != 'SUN':
                    scaled_grid_size = round(GRID_SIZE * self.zoom_level)
                    for gx in range(planet.size):
                        for gy in range(planet.size):
                            cell_x = (planet.grid_position[0] + gx) * scaled_grid_size + self.offset_x
                            cell_y = (planet.grid_position[1] + gy) * scaled_grid_size + self.offset_y
                            rect = pygame.Rect(cell_x, cell_y, scaled_grid_size, scaled_grid_size)
                            pygame.draw.rect(screen, (0, 255, 0), rect, 2)
                            # Draw building icon if present
                            if planet.planet_grid[gy][gx] is not None:
                                pygame.draw.rect(screen, (0, 120, 255), rect.inflate(-scaled_grid_size//3, -scaled_grid_size//3))
        
        # Draw ships (only if visible)
        for ship in self.ships:
            sx, sy = ship.grid_position
            if (start_x <= sx < end_x and start_y <= sy < end_y):
                ship.render(screen, self.offset_x, self.offset_y, self.zoom_level)
        
        # Draw asteroids (only if visible)
        for asteroid in self.asteroids:
            ax, ay = asteroid['position']
            if (start_x <= ax < end_x and start_y <= ay < end_y):
                scaled_grid_size = round(GRID_SIZE * self.zoom_level)
                rect = pygame.Rect(ax * scaled_grid_size + self.offset_x, ay * scaled_grid_size + self.offset_y, scaled_grid_size, scaled_grid_size)
                pygame.draw.rect(screen, (120, 120, 120), rect)  # Gray asteroids
                pygame.draw.rect(screen, (80, 80, 80), rect, max(1, scaled_grid_size // 10))  # Darker border
        
        # Draw tooltip only for selected unit
        if self.selected_unit and hasattr(self.selected_unit, 'render_tooltip'):
            self.selected_unit.render_tooltip(screen, self.offset_x, self.offset_y)

        # Draw debug markers for all suns
        for planet in self.planets:
            if getattr(planet, 'planet_type', None) == 'SUN':
                px, py = planet.grid_position
                scaled_grid_size = round(GRID_SIZE * self.zoom_level)
                cx = int(px * scaled_grid_size + self.offset_x + (planet.size * scaled_grid_size) // 2)
                cy = int(py * scaled_grid_size + self.offset_y + (planet.size * scaled_grid_size) // 2)
                pygame.draw.circle(screen, (255, 0, 0), (cx, cy), max(8, int(10 * self.zoom_level)))

    def handle_right_click(self, pos):
        # Only deselect on right click
        for s in self.ships:
            s.set_selected(False)
        for p in self.planets:
            p.selected = False
        self.build_mode = False  # Exit build mode on deselect
        self.selected_unit = None
        self.build_warning = None
        print("Deselecting unit (right click).")
        self.move_tiles = []