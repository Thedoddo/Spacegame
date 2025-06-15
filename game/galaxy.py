import pygame
import numpy as np
import random
from .constants import *
from .planet import Planet, Sun, PLANET_TYPES, SUN_TYPES
from .unit import Ship, Frigate, Destroyer, Cruiser, Battleship, Carrier, Fighter, Bomber, BuilderShip, Corvette
from .nebula import Nebula
from .orbital import Orbital

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
        self.nebulae = []  # List of all nebulae
        self.orbitals = []  # List of all orbital structures

        self.pan_speed = 20  # Speed for panning
        self.zoom_level = 1.0  # Initial zoom level
        self.build_mode = False
        self.build_warning = None  # Store warning message for UI
        self.building_just_placed = False  # Track if a building was just placed
        self.orbital_just_placed = False  # Track if an orbital was just placed
        
        # Shipyard interaction tracking
        self.current_shipyard_buttons = None
        self.current_shipyard_object = None
        self.generate_planets()
        self.generate_asteroids()
        self.generate_nebulae()
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
            
            # Generate planets around the sun - GUARANTEE one volcanic or rocky planet
            num_planets = np.random.randint(4, 8)  # More planets per system
            has_mining_planet = False
            
            for planet_num in range(num_planets):
                for attempt in range(30):
                    angle = np.random.uniform(0, 2 * np.pi)
                    distance = np.random.randint(10, 20)
                    
                    # For the first planet in starting systems, guarantee volcanic or rocky
                    if planet_num == 0 and not has_mining_planet:
                        planet_type = np.random.choice(['VOLCANIC', 'ROCKY'])
                        has_mining_planet = True
                        print(f"  Guaranteed {planet_type} planet for starting system {system_label}")
                    else:
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
        num_systems = np.random.randint(8, 15)  # More systems for denser galaxy
        min_distance = 80  # Reduced minimum distance for denser systems
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
                    num_planets = np.random.randint(4, 8)  # More planets per system
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
                else:
                    pass

        print(f"Total planets generated: {len(self.planets)}")
        print(f"Sun positions: {sun_positions}")

    def generate_asteroids(self):
        """Generate dense asteroid field patches scattered throughout the galaxy"""
        import random
        self.asteroids.clear()
        
        # Generate 40-60 asteroid field patches (much denser)
        num_asteroid_patches = random.randint(40, 60)
        
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
                    
                    # Create different shaped patches with 60-120 asteroids
                    asteroids_in_patch = random.randint(60, 120)
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

    def generate_nebulae(self):
        """Generate nebulae scattered throughout the galaxy"""
        import random
        self.nebulae.clear()
        
        # Generate 8-15 nebulae across the galaxy (much denser)
        num_nebulae = random.randint(8, 15)
        
        for nebula_num in range(num_nebulae):
            # Find a position for this nebula
            for attempt in range(50):  # Try up to 50 times to find a valid position
                center_x = random.randint(30, GALAXY_SIZE - 30)
                center_y = random.randint(30, GALAXY_SIZE - 30)
                nebula_size = random.randint(12, 25)  # Radius in grid units
                
                # Check if nebula is far enough from planets and suns
                too_close = False
                for planet in self.planets:
                    px, py = planet.grid_position
                    distance = ((center_x - px) ** 2 + (center_y - py) ** 2) ** 0.5
                    if distance < nebula_size + 15:  # Keep nebulae away from systems
                        too_close = True
                        break
                
                # Check distance from other nebulae
                for existing_nebula in self.nebulae:
                    nx, ny = existing_nebula.center_position
                    distance = ((center_x - nx) ** 2 + (center_y - ny) ** 2) ** 0.5
                    if distance < nebula_size + existing_nebula.size + 5:  # Allow closer nebulae
                        too_close = True
                        break
                
                if not too_close:
                    # Choose a random nebula type
                    nebula_type = random.choice(list(NEBULA_TYPES.keys()))
                    
                    # Create the nebula
                    nebula = Nebula(nebula_type, (center_x, center_y), nebula_size)
                    self.nebulae.append(nebula)
                    
                    print(f"Generated {nebula.name} at ({center_x}, {center_y}) with size {nebula_size}")
                    break
        
        print(f"Generated {len(self.nebulae)} total nebulae")

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

    def handle_click(self, pos, player, player_id):
        from .constants import GRID_SIZE
        
        # Check for shipyard button clicks first (highest priority)
        if (self.current_shipyard_buttons and self.current_shipyard_object and 
            hasattr(self.current_shipyard_object, 'handle_shipyard_click')):
            # player is now the actual player object
            handled, message = self.current_shipyard_object.handle_shipyard_click(pos, self.current_shipyard_buttons, player)
            if handled:
                if message:
                    self.build_warning = message
                    print(f"Shipyard action: {message}")
                return
        
        self.building_just_placed = False  # Reset flag at start of each click
        self.orbital_just_placed = False  # Reset orbital flag at start of each click
        scaled_grid_size = max(1, round(GRID_SIZE * self.zoom_level))  # Prevent division by zero
        grid_x = int((pos[0] - self.offset_x) // scaled_grid_size)
        grid_y = int((pos[1] - self.offset_y) // scaled_grid_size)
        selected_building_type = getattr(self, 'selected_building_type', None)
        
        print(f"Clicked grid: ({grid_x}, {grid_y}), current_player: {player_id}")
        print("Ships:")
        for ship in self.ships:
            print(f"  {ship.label} at {ship.grid_position}, owner: {ship.owner}")
        
        # --- DEBUG: Print move_tiles and click for ship movement ---
        if self.selected_unit and getattr(self.selected_unit, 'unit_type', None) == 'SHIP':
            print(f"DEBUG: move_tiles={self.move_tiles}, clicked=({grid_x}, {grid_y})")
        
        # --- LOGIC ORDER ---
        # 1. Ship selection (highest priority - unless explicitly in build mode)
        # 2. Ship movement (if selected and click is in move_tiles)
        # 3. Planet clicks (selection or building placement)
        # 4. Orbital placement (only if in build mode with building selected)
        # 5. Deselect if nothing found
        
        # Find clicked ship
        clicked_ship = None
        for ship in self.ships:
            if ship.grid_position[0] == grid_x and ship.grid_position[1] == grid_y:
                clicked_ship = ship
                print(f"Clicked ship found: {ship.label} at {ship.grid_position}, owner: {ship.owner}, current_player: {player_id}")
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
            if clicked_ship.owner == player_id:
                print(f"Selecting ship: {clicked_ship.label}")
                # Clear previous selections
                for s in self.ships:
                    s.set_selected(False)
                for p in self.planets:
                    p.selected = False
                for o in self.orbitals:
                    o.selected = False
                
                # Clear shipyard buttons when selection changes
                self.current_shipyard_buttons = None
                self.current_shipyard_object = None
                
                # Clear build mode and selected building when selecting ships
                self.build_mode = False
                self.selected_building_type = None
                
                # Set the selected unit and mark ship as selected
                self.selected_unit = clicked_ship
                clicked_ship.set_selected(True)
                
                # Only show move tiles if ship has actions left
                if hasattr(clicked_ship, 'actions_left') and clicked_ship.actions_left > 0:
                    self.move_tiles = self.get_move_tiles(clicked_ship)
                    print(f"DEBUG: Generated {len(self.move_tiles)} move tiles for {clicked_ship.label} with actions_left={clicked_ship.actions_left}, move_range={clicked_ship.move_range}")
                else:
                    self.move_tiles = []  # No movement allowed
                    print(f"DEBUG: {clicked_ship.label} has no actions left ({getattr(clicked_ship, 'actions_left', 'N/A')})")
                
                return
            else:
                print(f"Cannot select {clicked_ship.label} - owned by player {clicked_ship.owner}, current player is {player_id}")
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
                    if ship.unit_type == 'SHIP' and getattr(ship, 'label', None) == 'BLD' and ship.owner == player_id:
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
                
                if clicked_planet.can_build(player_id):
                    # Check if building type is allowed on this planet
                    if not clicked_planet.can_build_type(selected_building_type):
                        self.build_warning = f'{selected_building_type} cannot be built on {clicked_planet.planet_type.title()} planets!'
                        print(f"DEBUG: {selected_building_type} not allowed on {clicked_planet.planet_type}")
                        return  # Don't reselect planet, just show warning
                    
                    # Try to place the building
                    if clicked_planet.place_building(grid_cell_x, grid_cell_y, player_id, selected_building_type):
                        print(f"Building placed at ({grid_cell_x}, {grid_cell_y}) for player {player_id} type {selected_building_type}")
                        self.building_just_placed = True  # Mark that a building was successfully placed
                        # Assign planet ownership if not already owned
                        if not hasattr(clicked_planet, 'owner') or clicked_planet.owner is None:
                            clicked_planet.owner = player_id
                            print(f"Planet {clicked_planet.system_label}-{clicked_planet.type_label} now owned by player {player_id}")
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
                # Don't automatically enter build mode - only show tooltip
                self.build_mode = False
                print(f"DEBUG: Planet selected: {getattr(clicked_planet, 'system_label', '?')}-{getattr(clicked_planet, 'type_label', '?')} (tooltip only)")
                return
        
        # 4. Handle orbital clicks (selection or placement)
        clicked_orbital = None
        for orbital in self.orbitals:
            ox, oy = orbital.grid_position
            if (grid_x >= ox and grid_x < ox + orbital.size and
                grid_y >= oy and grid_y < oy + orbital.size):
                clicked_orbital = orbital
                print(f"Clicked orbital found: {orbital.name} at {orbital.grid_position}")
                break
            
        if clicked_orbital:
            if clicked_orbital.owner == player_id:
                print(f"Selecting orbital: {clicked_orbital.name}")
                # Clear previous selections
                for s in self.ships:
                    s.set_selected(False)
                for p in self.planets:
                    p.selected = False
                for o in self.orbitals:
                    o.selected = False
                
                self.selected_unit = clicked_orbital
                clicked_orbital.selected = True
                self.move_tiles = []
                self.build_mode = False
                return
            else:
                print(f"Cannot select {clicked_orbital.name} - owned by player {clicked_orbital.owner}")
                return
        
        # 5. Handle orbital placement in empty space (only if in build mode)
        if self.build_mode and selected_building_type and selected_building_type in ORBITAL_TYPES.values():
            # Double-check affordability before placing orbital
            from .constants import ORBITAL_COSTS
            if selected_building_type in ORBITAL_COSTS:
                costs = ORBITAL_COSTS[selected_building_type]
                can_afford = True
                for resource, amount in costs.items():
                    if player.get_resource(resource) < amount:
                        can_afford = False
                        self.build_warning = f'Not enough {resource}! Need {amount}, have {player.get_resource(resource)}'
                        print(f"DEBUG: Galaxy-level affordability check failed for {selected_building_type}")
                        return
                
                if not can_afford:
                    print(f"DEBUG: Galaxy-level affordability check failed for {selected_building_type}")
                    return
            # Check if we have a builder ship within range
            builder_in_range = False
            for ship in self.ships:
                if ship.unit_type == 'SHIP' and getattr(ship, 'label', None) == 'BLD' and ship.owner == player_id:
                    sx, sy = ship.grid_position
                    distance = abs(sx - grid_x) + abs(sy - grid_y)
                    if distance <= 8:  # Longer range for orbital construction
                        builder_in_range = True
                        break
            
            if not builder_in_range:
                self.build_warning = 'A builder ship must be within 8 grids to build orbital structures!'
                print(f"DEBUG: No builder in range for orbital at {grid_x}, {grid_y}")
                return
            
            self.build_warning = None
            
            # Find the orbital type key from the display name
            orbital_type_key = None
            for key, display_name in ORBITAL_TYPES.items():
                if display_name == selected_building_type:
                    orbital_type_key = key
                    break
            
            if orbital_type_key:
                # Create a temporary orbital to test placement
                temp_orbital = Orbital(orbital_type_key, (grid_x, grid_y), player_id)
                
                if temp_orbital.can_be_placed_at(self, grid_x, grid_y):
                    # Place the orbital
                    new_orbital = Orbital(orbital_type_key, (grid_x, grid_y), player_id)
                    self.orbitals.append(new_orbital)
                    self.orbital_just_placed = True  # Mark that an orbital was successfully placed
                    print(f"Orbital {selected_building_type} placed at ({grid_x}, {grid_y}) for player {player_id}")
                    return
                else:
                    # Check specific placement restrictions and give helpful error messages
                    if orbital_type_key == 'NEBULA_RESEARCH_STATION':
                        self.build_warning = 'Nebula Research Station must be placed within 5 grids of a nebula!'
                    elif orbital_type_key == 'ORBITAL_SHIPYARD':
                        self.build_warning = 'Orbital Shipyard must be placed 8-15 grids from a planet!'
                    elif orbital_type_key == 'DEEP_SPACE_FORTRESS':
                        self.build_warning = 'Deep Space Fortress must be placed away from planets, nebulae, and other orbitals!'
                    else:
                        self.build_warning = f'Cannot place {selected_building_type} here!'
                    print(f"DEBUG: Orbital placement failed at ({grid_x}, {grid_y})")
                    return
            else:
                print(f"ERROR: Could not find orbital type for {selected_building_type}")
                return
        
        # 6. Deselect if nothing found (only if we didn't click on anything valid)
        print("Deselecting unit.")
        # Clear previous selections
        for s in self.ships:
            s.set_selected(False)
        for p in self.planets:
            p.selected = False
        for o in self.orbitals:
            o.selected = False
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

    def handle_zoom(self, zoom_in, screen=None):
        # Get screen dimensions dynamically
        if screen:
            screen_width = screen.get_width()
            screen_height = screen.get_height()
        else:
            from .constants import WINDOW_WIDTH, WINDOW_HEIGHT
            screen_width = WINDOW_WIDTH
            screen_height = WINDOW_HEIGHT
        
        # Change zoom level first
        old_zoom = self.zoom_level
        if zoom_in:
            self.zoom_level = max(0.01, self.zoom_level - 0.1)  # Zoom out much further
        else:
            self.zoom_level = min(2.0, self.zoom_level + 0.1)  # Zoom in
        
        # If zooming from extreme zoom back to normal, reset to galaxy center
        if old_zoom <= 0.05 and self.zoom_level > 0.05:
            # Reset view to center of galaxy when coming back from extreme zoom
            self.center_view_on_galaxy(screen)
        else:
            # Normal zoom behavior - try to maintain center point
            center_screen_x = screen_width // 2
            center_screen_y = screen_height // 2
            
            # Prevent division by extremely small numbers
            safe_zoom = max(0.001, old_zoom)
            world_x = (center_screen_x - self.offset_x) / (GRID_SIZE * safe_zoom)
            world_y = (center_screen_y - self.offset_y) / (GRID_SIZE * safe_zoom)
            
            # Adjust offset to keep the same world point at the center
            new_offset_x = center_screen_x - (world_x * GRID_SIZE * self.zoom_level)
            new_offset_y = center_screen_y - (world_y * GRID_SIZE * self.zoom_level)
            
            # Clamp offsets to reasonable bounds
            max_offset = GALAXY_SIZE * GRID_SIZE
            self.offset_x = max(-max_offset, min(max_offset, new_offset_x))
            self.offset_y = max(-max_offset, min(max_offset, new_offset_y))
    
    def center_view_on_galaxy(self, screen=None):
        """Center the view on the galaxy"""
        # Get screen dimensions dynamically
        if screen:
            screen_width = screen.get_width()
            screen_height = screen.get_height()
        else:
            from .constants import WINDOW_WIDTH, WINDOW_HEIGHT
            screen_width = WINDOW_WIDTH
            screen_height = WINDOW_HEIGHT
            
        galaxy_center_x = GALAXY_SIZE // 2
        galaxy_center_y = GALAXY_SIZE // 2
        
        # Center the view on the galaxy center
        self.offset_x = (screen_width // 2) - (galaxy_center_x * GRID_SIZE * self.zoom_level)
        self.offset_y = (screen_height // 2) - (galaxy_center_y * GRID_SIZE * self.zoom_level)

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
        if keys[pygame.K_HOME] or keys[pygame.K_c]:
            # Press HOME or C to center view on galaxy
            self.center_view_on_galaxy()
        
        # Shipyard updates are now handled only in end_turn_update() method

    def render(self, screen):
        # Calculate visible grid range using dynamic screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        scaled_grid_size = max(1, round(GRID_SIZE * self.zoom_level))  # Prevent division by zero
        
        # Use more robust bounds calculation for extreme zoom levels
        if self.zoom_level <= 0.05:
            # At extreme zoom, show everything to prevent disappearing objects
            start_x = 0
            end_x = GALAXY_SIZE
            start_y = 0
            end_y = GALAXY_SIZE
        else:
            # Normal visibility culling using dynamic screen dimensions
            start_x = max(0, int((-self.offset_x) // scaled_grid_size - 10))  # Add buffer
            end_x = min(GALAXY_SIZE, int((screen_width - self.offset_x) // scaled_grid_size + 10))
            start_y = max(0, int((-self.offset_y) // scaled_grid_size - 10))
            end_y = min(GALAXY_SIZE, int((screen_height - self.offset_y) // scaled_grid_size + 10))

        # Optimize grid drawing based on zoom level
        if self.zoom_level > 0.3:
            # Draw detailed grid when zoomed in
            for x in range(start_x, end_x):
                for y in range(start_y, end_y):
                    rect = pygame.Rect(x * scaled_grid_size + self.offset_x, y * scaled_grid_size + self.offset_y, scaled_grid_size, scaled_grid_size)
                    pygame.draw.rect(screen, (50, 50, 50), rect, 1)
        elif self.zoom_level > 0.1:
            # Draw sparse grid when moderately zoomed out
            grid_interval = 5
            for x in range(start_x, end_x, grid_interval):
                for y in range(start_y, end_y, grid_interval):
                    rect = pygame.Rect(x * scaled_grid_size + self.offset_x, y * scaled_grid_size + self.offset_y, scaled_grid_size * grid_interval, scaled_grid_size * grid_interval)
                    pygame.draw.rect(screen, (30, 30, 30), rect, 1)
        elif self.zoom_level > 0.02:
            # Draw major grid every 50 units when zoomed out
            grid_interval = 50
            # Align to 50-unit boundaries
            start_x_major = (start_x // grid_interval) * grid_interval
            start_y_major = (start_y // grid_interval) * grid_interval
            for x in range(start_x_major, end_x + grid_interval, grid_interval):
                for y in range(start_y_major, end_y + grid_interval, grid_interval):
                    rect = pygame.Rect(x * scaled_grid_size + self.offset_x, y * scaled_grid_size + self.offset_y, 
                                     scaled_grid_size * grid_interval, scaled_grid_size * grid_interval)
                    pygame.draw.rect(screen, (70, 70, 70), rect, max(1, int(2 * self.zoom_level / 0.02)))
        elif self.zoom_level > 0.01:
            # Draw ultra-major grid every 100 units when extremely zoomed out
            grid_interval = 100
            start_x_major = (start_x // grid_interval) * grid_interval
            start_y_major = (start_y // grid_interval) * grid_interval
            for x in range(start_x_major, end_x + grid_interval, grid_interval):
                for y in range(start_y_major, end_y + grid_interval, grid_interval):
                    rect = pygame.Rect(x * scaled_grid_size + self.offset_x, y * scaled_grid_size + self.offset_y, 
                                     scaled_grid_size * grid_interval, scaled_grid_size * grid_interval)
                    pygame.draw.rect(screen, (90, 90, 90), rect, max(1, int(3 * self.zoom_level / 0.01)))
        # Skip grid entirely when extremely zoomed out (zoom_level <= 0.01)

        # Draw coordinate labels if zoomed out
        if self.zoom_level <= 0.4:
            if self.zoom_level <= 0.05:
                # When extremely zoomed out, show labels every 100 units
                font_size = max(12, int(24 * self.zoom_level / 0.01))
                font = pygame.font.Font(None, font_size)
                label_interval = 100
                # Align labels to 100-unit boundaries
                start_x_label = (start_x // label_interval) * label_interval
                start_y_label = (start_y // label_interval) * label_interval
            elif self.zoom_level <= 0.1:
                # When fully zoomed out, show labels every 50 units
                font_size = max(16, int(32 * self.zoom_level / 0.05))
                font = pygame.font.Font(None, font_size)
                label_interval = 50
                # Align labels to 50-unit boundaries
                start_x_label = (start_x // label_interval) * label_interval
                start_y_label = (start_y // label_interval) * label_interval
            elif self.zoom_level <= 0.2:
                font_size = 28
                font = pygame.font.Font(None, font_size)
                label_interval = 50
                start_x_label = start_x
                start_y_label = start_y
            else:
                font_size = 22
                font = pygame.font.Font(None, font_size)
                label_interval = 10
                start_x_label = start_x
                start_y_label = start_y

            # Top edge (x labels)
            for x in range(start_x_label, end_x + label_interval, label_interval):
                if x >= 0:  # Don't show negative coordinates
                    label = font.render(str(x), True, (200, 200, 200))
                    px = x * scaled_grid_size + self.offset_x
                    if px >= 0 and px < screen_width - 50:  # Only show if on screen
                        screen.blit(label, (px + 2, 2))
            # Left edge (y labels)
            for y in range(start_y_label, end_y + label_interval, label_interval):
                if y >= 0:  # Don't show negative coordinates
                    label = font.render(str(y), True, (200, 200, 200))
                    py = y * scaled_grid_size + self.offset_y
                    if py >= 0 and py < screen_height - 30:  # Only show if on screen
                        screen.blit(label, (2, py + 2))

        # Set .selected for all planets and ships
        for planet in self.planets:
            planet.set_selected(planet is self.selected_unit)
        for ship in self.ships:
            ship.set_selected(ship is self.selected_unit)

        # Draw move range tiles (only if visible)
        # Ensure move_tiles is updated for selected ship
        if self.selected_unit and getattr(self.selected_unit, 'unit_type', None) == 'SHIP':
            self.move_tiles = self.get_move_tiles(self.selected_unit)
        else:
            self.move_tiles = []
        for tile in self.move_tiles:
            tx, ty = tile
            if start_x <= tx < end_x and start_y <= ty < end_y:
                rect = pygame.Rect(tx * scaled_grid_size + self.offset_x, ty * scaled_grid_size + self.offset_y, scaled_grid_size, scaled_grid_size)
                pygame.draw.rect(screen, (100, 150, 255), rect)  # Solid blue highlight
                pygame.draw.rect(screen, (0, 100, 255), rect, 3)  # Blue border
        
        # Draw planets (only if visible, optimized for zoom level)
        for planet in self.planets:
            px, py = planet.grid_position
            if (px + planet.size > start_x and px < end_x and
                py + planet.size > start_y and py < end_y):
                planet.render(screen, self.offset_x, self.offset_y, self.zoom_level)
                # Show tooltip for selected planet
                if planet is self.selected_unit and hasattr(planet, 'render_tooltip'):
                    scaled_grid_size = round(GRID_SIZE * self.zoom_level)
                    tooltip_offset_x = (planet.grid_position[0] + planet.size) * scaled_grid_size + self.offset_x + 8
                    tooltip_offset_y = planet.grid_position[1] * scaled_grid_size + self.offset_y
                    mouse_pos = pygame.mouse.get_pos()
                    ship_buttons = planet.render_tooltip(screen, tooltip_offset_x, tooltip_offset_y, mouse_pos)
                    # Store shipyard buttons for click handling
                    if ship_buttons:
                        self.current_shipyard_buttons = ship_buttons
                        self.current_shipyard_object = planet
                
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
        
        # Draw orbitals (only if visible)
        for orbital in self.orbitals:
            ox, oy = orbital.grid_position
            if (ox + orbital.size > start_x and ox < end_x and
                oy + orbital.size > start_y and oy < end_y):
                orbital.render(screen, self.offset_x, self.offset_y, self.zoom_level)
                # Show tooltip for selected orbital
                if orbital is self.selected_unit and hasattr(orbital, 'render_tooltip'):
                    scaled_grid_size = round(GRID_SIZE * self.zoom_level)
                    tooltip_offset_x = (orbital.grid_position[0] + orbital.size) * scaled_grid_size + self.offset_x + 8
                    tooltip_offset_y = orbital.grid_position[1] * scaled_grid_size + self.offset_y
                    mouse_pos = pygame.mouse.get_pos()
                    ship_buttons = orbital.render_tooltip(screen, tooltip_offset_x, tooltip_offset_y, mouse_pos)
                    # Store shipyard buttons for click handling
                    if ship_buttons:
                        self.current_shipyard_buttons = ship_buttons
                        self.current_shipyard_object = orbital
        
        # Draw ships (only if visible)
        for ship in self.ships:
            sx, sy = ship.grid_position
            if (start_x <= sx < end_x and start_y <= sy < end_y):
                ship.render(screen, self.offset_x, self.offset_y, self.zoom_level)
                # Show tooltip for selected ship
                if ship is self.selected_unit and hasattr(ship, 'render_tooltip'):
                    ship.render_tooltip(screen, self.offset_x, self.offset_y, self.zoom_level)
        
        # Draw nebulae (in background, only if visible, optimized for zoom level)
        if self.zoom_level > 0.15:
            # Draw detailed nebulae when zoomed in enough
            for nebula in self.nebulae:
                nx, ny = nebula.center_position
                nebula_size = nebula.size
                if (nx + nebula_size > start_x and nx - nebula_size < end_x and
                    ny + nebula_size > start_y and ny - nebula_size < end_y):
                    nebula.draw(screen, self.offset_x, self.offset_y, self.zoom_level)
        else:
            # Draw simplified nebulae as colored circles when zoomed out (always visible)
            for nebula in self.nebulae:
                nx, ny = nebula.center_position
                nebula_size = nebula.size
                if (nx + nebula_size > start_x and nx - nebula_size < end_x and
                    ny + nebula_size > start_y and ny - nebula_size < end_y):
                    scaled_grid_size = max(1, round(GRID_SIZE * self.zoom_level))
                    center_x = nx * scaled_grid_size + self.offset_x
                    center_y = ny * scaled_grid_size + self.offset_y
                    
                    # Ensure nebulae are always visible with minimum radius
                    if self.zoom_level <= 0.05:
                        radius = max(6, int(nebula_size * 0.5))  # Larger minimum for extreme zoom
                    else:
                        radius = max(3, int(nebula_size * self.zoom_level))
                    # Draw simple colored circle
                    color = nebula.base_color[:3]  # Remove alpha
                    pygame.draw.circle(screen, color, (int(center_x), int(center_y)), radius)
        
        # Draw asteroids (only if visible, fixed to grid positions)
        scaled_grid_size = max(1, round(GRID_SIZE * self.zoom_level))
        for asteroid in self.asteroids:
            ax, ay = asteroid['position']
            if (start_x <= ax < end_x and start_y <= ay < end_y):
                # Calculate screen position using integer grid coordinates
                screen_x = int(ax * scaled_grid_size + self.offset_x)
                screen_y = int(ay * scaled_grid_size + self.offset_y)
                
                # Draw asteroid as a small gray circle
                asteroid_size = max(2, int(3 * self.zoom_level))  # Scale size with zoom but keep minimum
                pygame.draw.circle(screen, (150, 150, 150), (screen_x + scaled_grid_size//2, screen_y + scaled_grid_size//2), asteroid_size)
        
        # Draw tooltip only for selected unit (but not ships/planets/orbitals, they're handled above)
        if (self.selected_unit and hasattr(self.selected_unit, 'render_tooltip') and 
            self.selected_unit not in self.ships and 
            self.selected_unit not in self.planets and 
            self.selected_unit not in self.orbitals):
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
        for o in self.orbitals:
            o.selected = False
        self.build_mode = False  # Exit build mode on deselect
        self.selected_unit = None
        self.selected_building_type = None  # Clear selected building
        self.build_warning = None
        print("Deselecting unit (right click).")
        self.move_tiles = []

    def is_position_empty(self, position):
        """Check if a position is empty (no ships, planets, or orbitals)"""
        x, y = position
        
        # Check bounds
        if x < 0 or y < 0 or x >= GALAXY_SIZE or y >= GALAXY_SIZE:
            return False
        
        # Check for ships
        for ship in self.ships:
            if ship.grid_position == (x, y):
                return False
        
        # Check for planets
        for planet in self.planets:
            px, py = planet.grid_position
            if (x >= px and x < px + planet.size and
                y >= py and y < py + planet.size):
                return False
        
        # Check for orbitals
        for orbital in self.orbitals:
            ox, oy = orbital.grid_position
            if (x >= ox and x < ox + orbital.size and
                y >= oy and y < oy + orbital.size):
                return False
        
        return True

    def get_planet_at_screen_pos(self, pos):
        """Return the planet at the given screen position, or None if none."""
        mouse_x, mouse_y = pos
        for planet in self.planets:
            # Calculate planet's screen position and size
            scaled_grid_size = max(1, round(GRID_SIZE * self.zoom_level))
            px = planet.grid_position[0] * scaled_grid_size + self.offset_x
            py = planet.grid_position[1] * scaled_grid_size + self.offset_y
            size = max(4, int(planet.size * scaled_grid_size))
            rect = pygame.Rect(px, py, size, size)
            if rect.collidepoint(mouse_x, mouse_y):
                return planet
        return None

    def end_turn_update(self):
        """Called at the end of each turn to update shipyard construction"""
        print("=== TURN UPDATE: Processing Shipyards ===")
        
        # Update shipyards on planets
        for planet in self.planets:
            if hasattr(planet, 'update_shipyard') and planet.build_queue:
                print(f"Updating shipyard on planet {getattr(planet, 'system_label', '?')}-{getattr(planet, 'type_label', '?')}")
                planet.update_shipyard(self)
        
        # Update shipyards on orbitals
        for orbital in self.orbitals:
            if hasattr(orbital, 'update_shipyard') and orbital.build_queue:
                print(f"Updating orbital shipyard: {orbital.name}")
                orbital.update_shipyard(self)
        
        print("=== SHIPYARD UPDATE COMPLETE ===")