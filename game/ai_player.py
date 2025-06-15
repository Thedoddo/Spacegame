from .constants import BUILDING_TYPES, SHIP_TYPES, BUILDING_COSTS, SHIP_COSTS, PLANET_BUILDING_RESTRICTIONS
import random

class AIPlayer:
    def __init__(self, player_id, difficulty="easy"):
        self.player_id = player_id
        self.difficulty = difficulty
        self.strategy_state = "EXPAND"  # EXPAND, BUILD_ECONOMY, BUILD_MILITARY
        self.turns_in_state = 0
        
        # Debug information
        self.debug_info = {
            'current_strategy': self.strategy_state,
            'ship_targets': {},  # ship_id -> target info
            'last_actions': [],  # List of recent actions
            'resource_status': {},
            'owned_planets': 0,
            'owned_shipyards': 0,
            'ships_built_this_turn': 0,
            'buildings_built_this_turn': 0,
            'colonizations_this_turn': 0
        }
        
    def take_turn(self, game_state):
        """Main AI turn logic"""
        print(f"\n=== AI Player {self.player_id + 1} Turn ===")
        
        # Reset turn counters
        self.debug_info['ships_built_this_turn'] = 0
        self.debug_info['buildings_built_this_turn'] = 0
        self.debug_info['colonizations_this_turn'] = 0
        self.debug_info['last_actions'] = []
        
        player = game_state.players[self.player_id]
        galaxy = game_state.galaxy
        
        # Update debug info
        self._update_debug_info(player, galaxy)
        
        # Update strategy based on game state
        self._update_strategy(player, galaxy)
        
        # Execute actions based on current strategy
        if self.strategy_state == "EXPAND":
            self._expand_strategy(player, galaxy, game_state)
        elif self.strategy_state == "BUILD_ECONOMY":
            self._economy_strategy(player, galaxy, game_state)
        elif self.strategy_state == "BUILD_MILITARY":
            self._military_strategy(player, galaxy, game_state)
            
        self.turns_in_state += 1
        
        # Print debug summary
        self._print_debug_summary()
        
    def _update_debug_info(self, player, galaxy):
        """Update debug information"""
        self.debug_info['current_strategy'] = self.strategy_state
        self.debug_info['resource_status'] = player.resources.copy()
        
        # Count owned planets and shipyards
        owned_planets = [p for p in galaxy.planets if hasattr(p, 'owner') and p.owner == self.player_id]
        self.debug_info['owned_planets'] = len(owned_planets)
        self.debug_info['owned_shipyards'] = len([p for p in owned_planets if p.has_shipyard()])
        
        # Update ship targets
        ai_ships = [s for s in galaxy.ships if s.owner == self.player_id]
        for ship in ai_ships:
            ship_id = f"{ship.label}@{ship.grid_position}"
            target = self._find_target_for_ship(ship, galaxy, 'expand' if self.strategy_state == 'EXPAND' else 'military')
            if target:
                if hasattr(target, 'grid_position'):
                    target_info = f"{getattr(target, 'system_label', 'Unknown')}-{getattr(target, 'type_label', 'Target')} at {target.grid_position}"
                else:
                    target_info = "Unknown target"
                self.debug_info['ship_targets'][ship_id] = target_info
                
    def _print_debug_summary(self):
        """Print debug information"""
        print(f"AI Debug Summary:")
        print(f"  Strategy: {self.debug_info['current_strategy']}")
        print(f"  Owned Planets: {self.debug_info['owned_planets']}")
        print(f"  Owned Shipyards: {self.debug_info['owned_shipyards']}")
        print(f"  Resources: M:{self.debug_info['resource_status'].get('Minerals', 0)} E:{self.debug_info['resource_status'].get('Energy', 0)} S:{self.debug_info['resource_status'].get('Science', 0)} F:{self.debug_info['resource_status'].get('Food', 0)}")
        print(f"  This Turn: {self.debug_info['buildings_built_this_turn']} buildings, {self.debug_info['ships_built_this_turn']} ships, {self.debug_info['colonizations_this_turn']} colonizations")
        
        if self.debug_info['ship_targets']:
            print(f"  Ship Targets:")
            for ship_id, target in self.debug_info['ship_targets'].items():
                print(f"    {ship_id} -> {target}")
                
        if self.debug_info['last_actions']:
            print(f"  Actions: {', '.join(self.debug_info['last_actions'])}")
            
    def _log_action(self, action):
        """Log an action for debugging"""
        self.debug_info['last_actions'].append(action)
        
    def _update_strategy(self, player, galaxy):
        """Update AI strategy based on current situation"""
        owned_planets = [p for p in galaxy.planets if hasattr(p, 'owner') and p.owner == self.player_id]
        owned_shipyards = [p for p in owned_planets if p.has_shipyard()]
        
        minerals = player.get_resource('Minerals')
        energy = player.get_resource('Energy')
        
        # Switch strategies based on conditions
        if len(owned_planets) < 3:  # Expand until we have at least 3 planets
            self.strategy_state = "EXPAND"
        elif len(owned_shipyards) == 0 and minerals >= 150 and energy >= 100:  # Build economy when we have resources
            self.strategy_state = "BUILD_ECONOMY"
        elif minerals < 75 or energy < 50:  # Go back to expansion if low on resources
            self.strategy_state = "EXPAND"
        elif self.turns_in_state > 5:  # Rotate strategies every 5 turns
            strategies = ["EXPAND", "BUILD_ECONOMY", "BUILD_MILITARY"]
            current_idx = strategies.index(self.strategy_state)
            self.strategy_state = strategies[(current_idx + 1) % len(strategies)]
            self.turns_in_state = 0
            
        print(f"AI Strategy: {self.strategy_state}")
        
    def _expand_strategy(self, player, galaxy, game_state):
        """Focus on colonization and expansion"""
        # 1. Try to colonize planets with builder ships
        self._attempt_colonization(player, galaxy, game_state)
        
        # 2. Move existing ships towards unowned planets (use all actions)
        self._move_ships_to_targets(galaxy, 'expand')
        
        # 3. Build colonizer ships if we have shipyards
        self._build_ships(player, galaxy, ['Colonizer', 'Scout', 'Builder'])
        
        # 4. Build basic economy buildings on all owned planets
        self._build_multiple_buildings(player, galaxy, game_state)
        
    def _attempt_colonization(self, player, galaxy, game_state):
        """Attempt to colonize nearby planets with builder ships"""
        builders = [ship for ship in galaxy.ships if ship.label == 'BLD' and ship.owner == self.player_id]
        self._log_action(f"Found {len(builders)} builder ships")
        
        for builder in builders:
            # Find planets within building range (6 grids) - check ALL planets first
            all_nearby_planets = []
            bx, by = builder.grid_position
            
            for planet in galaxy.planets:
                # Skip suns, but include all other planets
                if hasattr(planet, 'planet_type') and planet.planet_type != 'SUN':
                    px, py = planet.grid_position
                    distance = abs(bx - px) + abs(by - py)
                    if distance <= 6:  # Building range
                        all_nearby_planets.append((planet, distance))
            
            # Filter to only unowned planets for colonization
            nearby_unowned_planets = [(p, d) for p, d in all_nearby_planets 
                                    if not hasattr(p, 'owner') or p.owner is None]
            
            self._log_action(f"Builder at {builder.grid_position} found {len(all_nearby_planets)} total nearby planets, {len(nearby_unowned_planets)} unowned")
            
            # Try to colonize the closest unowned planet
            nearby_unowned_planets.sort(key=lambda x: x[1])  # Sort by distance
            
            for target_planet, distance in nearby_unowned_planets:
                # Skip if planet is already owned
                if hasattr(target_planet, 'owner') and target_planet.owner is not None:
                    continue
                
                self._log_action(f"Attempting to colonize {target_planet.system_label}-{target_planet.type_label} at distance {distance}")
                
                # Get allowed buildings for this planet type
                allowed_buildings = target_planet.get_allowed_buildings()
                
                # Priority order for colonization buildings - prioritize resource generation
                minerals = player.get_resource('Minerals')
                energy = player.get_resource('Energy')
                
                # If we're low on minerals, prioritize mining buildings
                if minerals < 100:
                    colonization_priorities = ['Mining Station', 'Power Plant', 'Solar Array', 'Farm', 'Research Lab', 'Defense Turret']
                # If we're low on energy, prioritize energy buildings
                elif energy < 75:
                    colonization_priorities = ['Power Plant', 'Solar Array', 'Mining Station', 'Farm', 'Research Lab', 'Defense Turret']
                # If we have good resources, can build anything
                else:
                    colonization_priorities = ['Mining Station', 'Power Plant', 'Solar Array', 'Research Lab', 'Farm', 'Defense Turret']
                
                # Try to build the first available building type that's allowed on this planet
                building_built = False
                for building_type in colonization_priorities:
                    if building_type in allowed_buildings:
                        # Check if we can afford this building with current resources
                        if building_type in BUILDING_COSTS:
                            costs = BUILDING_COSTS[building_type]
                            can_afford = True
                            
                            # If we're very low on resources, only build very cheap buildings
                            if minerals < 50 and energy < 50:
                                # Only build if it costs less than 50 minerals and 30 energy
                                if costs.get('Minerals', 0) > 50 or costs.get('Energy', 0) > 30:
                                    continue
                            
                            # Check if we can afford it
                            for resource, amount in costs.items():
                                if player.get_resource(resource) < amount:
                                    can_afford = False
                                    break
                            
                            if not can_afford:
                                continue
                        
                        if self._try_build_on_planet(target_planet, building_type, player, game_state):
                            self._log_action(f"Successfully colonized {target_planet.system_label}-{target_planet.type_label} with {building_type}")
                            self.debug_info['colonizations_this_turn'] += 1
                            print(f"AI: Colonized planet {target_planet.system_label}-{target_planet.type_label} with {building_type}!")
                            
                            # Assign planet ownership
                            target_planet.owner = self.player_id
                            
                            # Try to build ONE additional building on the newly colonized planet (be conservative)
                            additional_buildings = ['Power Plant', 'Solar Array', 'Farm']  # Cheaper options first
                            for additional_building in additional_buildings:
                                if (additional_building in allowed_buildings and 
                                    additional_building != building_type and  # Don't build the same type twice
                                    player.can_afford(BUILDING_COSTS.get(additional_building, {})) and
                                    player.get_resource('Minerals') > 100):  # Keep some minerals for future expansion
                                    if self._try_build_on_planet(target_planet, additional_building, player, game_state):
                                        self._log_action(f"Built additional {additional_building} on new colony")
                                        break  # Only build ONE additional building to conserve resources
                            
                            building_built = True
                            break  # Successfully colonized with this building type
                        else:
                            self._log_action(f"Failed to build {building_type} on {target_planet.system_label}-{target_planet.type_label}")
                
                if building_built:
                    break  # Successfully colonized, move to next builder
                else:
                    self._log_action(f"Failed to colonize {target_planet.system_label}-{target_planet.type_label} - no suitable buildings")
        
    def _economy_strategy(self, player, galaxy, game_state):
        """Focus on economic development"""
        # 1. Build economic buildings on all planets FIRST
        self._build_multiple_buildings(player, galaxy, game_state)
        
        # 2. Continue expansion if we have builders and resources
        if player.get_resource('Minerals') > 100:
            self._attempt_colonization(player, galaxy, game_state)
            self._move_ships_to_targets(galaxy, 'expand')
        
        # 3. Only build shipyards if we have good resources (200+ minerals, 150+ energy)
        if player.get_resource('Minerals') >= 200 and player.get_resource('Energy') >= 150:
            self._build_shipyards(player, galaxy, game_state)
        
        # 4. Build transport and builder ships if we have shipyards
        self._build_ships(player, galaxy, ['Transport', 'Builder', 'Scout'])
        
    def _military_strategy(self, player, galaxy, game_state):
        """Focus on military buildup"""
        # 1. Move ships towards enemy positions (use all actions)
        self._move_ships_to_targets(galaxy, 'military')
        
        # 2. Build military ships
        self._build_ships(player, galaxy, ['Corvette', 'Frigate', 'Fighter', 'Destroyer'])
        
        # 3. Build defensive structures
        self._build_defensive_buildings(player, galaxy, game_state)
        
    def _build_ships(self, player, galaxy, preferred_ships):
        """Build ships from preferred list"""
        owned_shipyards = []
        
        # Find owned planets with shipyards
        for planet in galaxy.planets:
            if hasattr(planet, 'owner') and planet.owner == self.player_id and planet.has_shipyard():
                owned_shipyards.append(planet)
                
        # Find owned orbital shipyards
        for orbital in galaxy.orbitals:
            if hasattr(orbital, 'owner') and orbital.owner == self.player_id and orbital.has_shipyard():
                owned_shipyards.append(orbital)
                
        if not owned_shipyards:
            self._log_action("No shipyards available")
            return
            
        # Try to build ships
        for shipyard in owned_shipyards:
            if len(shipyard.build_queue) < 2:  # Don't overqueue
                for ship_type in preferred_ships:
                    if ship_type in SHIP_COSTS:
                        costs = SHIP_COSTS[ship_type]
                        if player.can_afford(costs):
                            success, message = shipyard.add_ship_to_queue(ship_type, player)
                            if success:
                                self._log_action(f"Queued {ship_type} at {getattr(shipyard, 'system_label', 'Orbital')}")
                                self.debug_info['ships_built_this_turn'] += 1
                                print(f"AI: Building {ship_type} at {getattr(shipyard, 'system_label', 'Orbital')}")
                                break
                        else:
                            self._log_action(f"Can't afford {ship_type} (need M:{costs.get('Minerals', 0)} E:{costs.get('Energy', 0)})")
            else:
                self._log_action(f"Shipyard queue full at {getattr(shipyard, 'system_label', 'Orbital')}")
                                
    def _build_shipyards(self, player, galaxy, game_state):
        """Build shipyards on owned planets"""
        owned_planets = [p for p in galaxy.planets if hasattr(p, 'owner') and p.owner == self.player_id]
        
        for planet in owned_planets:
            if not planet.has_shipyard() and planet.can_build(self.player_id):
                # Try to place a shipyard
                if self._try_build_on_planet(planet, 'Shipyard', player, game_state):
                    self._log_action(f"Built Shipyard on {planet.system_label}-{planet.type_label}")
                    print(f"AI: Built Shipyard on {planet.system_label}-{planet.type_label}")
                    break
                    
    def _build_multiple_buildings(self, player, galaxy, game_state):
        """Build multiple buildings on owned planets with smart resource management"""
        owned_planets = [p for p in galaxy.planets if hasattr(p, 'owner') and p.owner == self.player_id]
        
        minerals = player.get_resource('Minerals')
        energy = player.get_resource('Energy')
        
        # Determine building priorities based on current resources
        if minerals < 100:  # Low minerals - prioritize mineral generation
            priority_buildings = ['Mining Station', 'Power Plant', 'Solar Array']
        elif energy < 75:   # Low energy - prioritize energy generation
            priority_buildings = ['Power Plant', 'Solar Array', 'Mining Station']
        else:  # Good resources - balanced approach
            priority_buildings = ['Mining Station', 'Power Plant', 'Research Lab', 'Solar Array', 'Farm']
        
        buildings_built = 0
        max_buildings_per_turn = 3  # Limit building spam
        
        for planet in owned_planets:
            if buildings_built >= max_buildings_per_turn:
                break
                
            # Get current buildings on planet
            current_buildings = planet.buildings if hasattr(planet, 'buildings') else []
            
            # Try to build priority buildings
            for building_type in priority_buildings:
                if buildings_built >= max_buildings_per_turn:
                    break
                    
                # Check if we can afford this building
                building_cost = BUILDING_COSTS.get(building_type, {})
                can_afford = True
                for resource, cost in building_cost.items():
                    if player.get_resource(resource) < cost + 25:  # Keep 25 resource buffer
                        can_afford = False
                        break
                
                if not can_afford:
                    continue
                
                # Check if planet allows this building type
                if hasattr(planet, 'planet_type'):
                    restrictions = PLANET_BUILDING_RESTRICTIONS.get(planet.planet_type, [])
                    if building_type in restrictions:
                        continue
                
                # Check if we already have this building type on this planet
                has_building = any(b.get('type') == building_type for b in current_buildings)
                if has_building:
                    continue
                
                # Try to build it using the existing _try_build_on_planet method
                if self._try_build_on_planet(planet, building_type, player, game_state):
                    self._log_action(f"Built {building_type} on {getattr(planet, 'system_label', 'Unknown')}-{getattr(planet, 'type_label', 'Planet')}")
                    buildings_built += 1
                    break  # Move to next planet
        
        return buildings_built
        
    def _planet_has_building_type(self, planet, building_type):
        """Check if planet already has a building of this type"""
        if not hasattr(planet, 'buildings'):
            return False
            
        for row in planet.buildings:
            for building in row:
                if building and building.get('type') == building_type:
                    return True
        return False
        
    def _build_defensive_buildings(self, player, galaxy, game_state):
        """Build defensive structures"""
        owned_planets = [p for p in galaxy.planets if hasattr(p, 'owner') and p.owner == self.player_id]
        
        for planet in owned_planets:
            if planet.can_build(self.player_id):
                if self._try_build_on_planet(planet, 'Defense Grid', player, game_state):
                    print(f"AI: Built Defense Grid on {planet.system_label}-{planet.type_label}")
                    break
                    
    def _try_build_on_planet(self, planet, building_type, player, game_state):
        """Try to build a specific building on a planet"""
        self._log_action(f"Trying to build {building_type} on {getattr(planet, 'system_label', 'Unknown')}-{getattr(planet, 'type_label', 'Planet')}")
        
        if building_type not in BUILDING_COSTS:
            self._log_action(f"Building type {building_type} not in BUILDING_COSTS")
            return False
            
        costs = BUILDING_COSTS[building_type]
        if not player.can_afford(costs):
            self._log_action(f"Can't afford {building_type} (need M:{costs.get('Minerals', 0)} E:{costs.get('Energy', 0)}, have M:{player.get_resource('Minerals')} E:{player.get_resource('Energy')})")
            return False
            
        if not planet.can_build_type(building_type):
            self._log_action(f"{building_type} not allowed on {getattr(planet, 'planet_type', 'unknown')} planet")
            return False
            
        # Check if planet can be built on by this player
        if not planet.can_build(self.player_id):
            self._log_action(f"Planet {getattr(planet, 'system_label', 'Unknown')} cannot be built on by player {self.player_id}")
            return False
            
        # Find an empty spot on the planet
        empty_spots_found = 0
        for x in range(planet.size):
            for y in range(planet.size):
                # Check if spot is empty
                if hasattr(planet, 'buildings') and planet.buildings[x][y] is None:
                    empty_spots_found += 1
                    
                if planet.place_building(x, y, self.player_id, building_type):
                    # Deduct resources
                    for resource, amount in costs.items():
                        player.spend_resource(resource, amount)
                    
                    self._log_action(f"Successfully built {building_type} at ({x},{y})")
                    self.debug_info['buildings_built_this_turn'] += 1
                    return True
        
        self._log_action(f"No space for {building_type} on planet (found {empty_spots_found} empty spots, planet size: {planet.size}x{planet.size})")
        return False
        
    def _move_ships_to_targets(self, galaxy, purpose):
        """Move ships towards their targets using all available actions"""
        ai_ships = [s for s in galaxy.ships if s.owner == self.player_id]
        
        for ship in ai_ships:
            if ship.actions_left <= 0:
                continue
                
            # Find or assign target for this ship
            target = self._find_target_for_ship(ship, galaxy, purpose)
            if not target:
                continue
                
            # Store target for debugging
            ship_id = f"{ship.label}@{ship.grid_position}"
            target_id = f"{getattr(target, 'system_label', 'Unknown')}-{getattr(target, 'type_label', 'Target')}"
            self.debug_info['ship_targets'][ship_id] = target_id
            
            # Use ALL available actions to move towards target
            actions_used = 0
            max_actions = ship.actions_left
            
            for action in range(max_actions):
                if ship.actions_left <= 0:
                    break
                    
                # Calculate distance to target
                sx, sy = ship.grid_position
                tx, ty = target.grid_position
                distance = abs(sx - tx) + abs(sy - ty)
                
                # If we're close enough for builders to colonize, stop moving
                if ship.label == 'BLD' and distance <= 6:
                    self._log_action(f"Builder at {ship.grid_position} within colonization range of {target_id} (distance: {distance})")
                    break
                
                # Move towards target
                old_pos = ship.grid_position
                moved = self._move_ship_towards_target_optimized(ship, target, galaxy)
                
                if moved:
                    new_pos = ship.grid_position
                    new_distance = abs(new_pos[0] - tx) + abs(new_pos[1] - ty)
                    self._log_action(f"Moved {ship.label} from {old_pos} to {new_pos} (distance to target: {new_distance})")
                    actions_used += 1
                else:
                    # Can't move closer, stop trying
                    break
            
            if actions_used > 0:
                print(f"AI: Used {actions_used} actions to move {ship.label} towards {target_id}")

    def _move_ship_towards_target_optimized(self, ship, target, galaxy):
        """Move ship optimally towards target using full movement range"""
        if not hasattr(target, 'grid_position'):
            return False
            
        target_pos = target.grid_position
        ship_pos = ship.grid_position
        
        # Calculate distance to target
        distance_to_target = abs(target_pos[0] - ship_pos[0]) + abs(target_pos[1] - ship_pos[1])
        
        # If already at target or very close, don't move
        if distance_to_target <= 1:
            return False
            
        # Get all possible moves within movement range
        move_range = getattr(ship, 'move_range', 1)
        possible_moves = []
        
        for dx in range(-move_range, move_range + 1):
            for dy in range(-move_range, move_range + 1):
                # Manhattan distance check
                if abs(dx) + abs(dy) <= move_range and (dx != 0 or dy != 0):
                    new_pos = (ship_pos[0] + dx, ship_pos[1] + dy)
                    
                    # Check bounds
                    if 0 <= new_pos[0] < 1000 and 0 <= new_pos[1] < 1000:
                        # Check if position is empty
                        if galaxy.is_position_empty(new_pos):
                            # Calculate distance from this position to target
                            new_distance = abs(target_pos[0] - new_pos[0]) + abs(target_pos[1] - new_pos[1])
                            possible_moves.append((new_pos, new_distance))
        
        if not possible_moves:
            return False  # No valid moves
            
        # Sort by distance to target (closest first)
        possible_moves.sort(key=lambda x: x[1])
        
        # Take the best move (closest to target)
        best_move = possible_moves[0]
        new_pos = best_move[0]
        new_distance = best_move[1]
        
        # Only move if it gets us closer
        current_distance = abs(target_pos[0] - ship_pos[0]) + abs(target_pos[1] - ship_pos[1])
        if new_distance < current_distance:
            ship.grid_position = new_pos
            ship.actions_left -= 1
            print(f"AI: Moved {ship.label} from {ship_pos} to {new_pos} (distance to target: {new_distance})")
            return True
            
        return False
        
    def _find_target_for_ship(self, ship, galaxy, purpose):
        """Find appropriate target for ship based on its type and purpose"""
        if ship.label == 'BLD':  # Builder ships
            # Find closest unowned planet
            unowned_planets = [p for p in galaxy.planets 
                             if hasattr(p, 'planet_type') and p.planet_type != 'SUN' 
                             and (not hasattr(p, 'owner') or p.owner is None)]
            
            if unowned_planets:
                ship_pos = ship.grid_position
                closest_planet = min(unowned_planets, 
                                   key=lambda p: abs(p.grid_position[0] - ship_pos[0]) + abs(p.grid_position[1] - ship_pos[1]))
                return closest_planet
                
        elif ship.label == 'COL':  # Colonizer ships
            # Find closest unowned planet
            unowned_planets = [p for p in galaxy.planets 
                             if hasattr(p, 'planet_type') and p.planet_type != 'SUN' 
                             and (not hasattr(p, 'owner') or p.owner is None)]
            
            if unowned_planets:
                ship_pos = ship.grid_position
                closest_planet = min(unowned_planets, 
                                   key=lambda p: abs(p.grid_position[0] - ship_pos[0]) + abs(p.grid_position[1] - ship_pos[1]))
                return closest_planet
                
        elif ship.label == 'SCT':  # Scout ships
            # Find unexplored areas or enemy positions
            unowned_planets = [p for p in galaxy.planets 
                             if hasattr(p, 'planet_type') and p.planet_type != 'SUN' 
                             and (not hasattr(p, 'owner') or p.owner is None)]
            
            if unowned_planets:
                ship_pos = ship.grid_position
                closest_planet = min(unowned_planets, 
                                   key=lambda p: abs(p.grid_position[0] - ship_pos[0]) + abs(p.grid_position[1] - ship_pos[1]))
                return closest_planet
                
        else:  # Military ships
            if purpose == 'military':
                # Find enemy planets or ships
                enemy_planets = [p for p in galaxy.planets 
                               if hasattr(p, 'owner') and p.owner is not None and p.owner != self.player_id]
                
                if enemy_planets:
                    ship_pos = ship.grid_position
                    closest_enemy = min(enemy_planets, 
                                      key=lambda p: abs(p.grid_position[0] - ship_pos[0]) + abs(p.grid_position[1] - ship_pos[1]))
                    return closest_enemy
            else:
                # Default to expansion - find unowned planets
                unowned_planets = [p for p in galaxy.planets 
                                 if hasattr(p, 'planet_type') and p.planet_type != 'SUN' 
                                 and (not hasattr(p, 'owner') or p.owner is None)]
                
                if unowned_planets:
                    ship_pos = ship.grid_position
                    closest_planet = min(unowned_planets, 
                                       key=lambda p: abs(p.grid_position[0] - ship_pos[0]) + abs(p.grid_position[1] - ship_pos[1]))
                    return closest_planet
        
        return None 