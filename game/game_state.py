import pygame
from .constants import *
from .galaxy import Galaxy
from .player import Player
from .ai_player import AIPlayer

class GameState:
    def __init__(self, ai_players=None):
        self.current_player = 0
        self.players = [Player("Player 1"), Player("Player 2")]
        
        # AI setup - ai_players is a list of player indices that should be AI
        self.ai_players = ai_players or []  # e.g., [1] means Player 2 is AI
        self.ai_controllers = {}
        
        # Initialize AI controllers for AI players
        for player_id in self.ai_players:
            if player_id < len(self.players):
                self.ai_controllers[player_id] = AIPlayer(player_id)
                self.players[player_id].name = f"AI Player {player_id + 1}"
        
        self.galaxy = Galaxy()
        self.current_turn = 1
        self.selected_building_type = None  # Track which building is selected for placement
        # UI buttons
        self.end_turn_button = pygame.Rect(WINDOW_WIDTH - 160, WINDOW_HEIGHT - 60, 150, 50)
        self.debug_button = pygame.Rect(WINDOW_WIDTH - 160, 10, 150, 40)
        # Building menu button rects
        self.building_buttons = []
        self._init_building_buttons()

        # Pre-create fonts for better performance
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 28)
        self.font_building = pygame.font.Font(None, 26)
        self.font_cost = pygame.font.Font(None, 18)
        self.font_header = pygame.font.Font(None, 20)
        self.font_message = pygame.font.Font(None, 24)
        
        # Cache for building menu rendering
        self._building_menu_cache = {}
        self._last_build_state = None
        self._building_menu_surface = None
        self._menu_needs_update = True
        self._frame_counter = 0

        self.build_menu_tab = 0  # 0 = Buildings, 1 = Orbitals
        self.build_menu_open = False
        
        # AI turn delay
        self.ai_turn_timer = 0
        self.ai_turn_delay = 1000  # 1 second delay for AI turns (in milliseconds)

    def _init_building_buttons(self):
        # Place building buttons vertically on the right side
        x = WINDOW_WIDTH - 180
        y = 100
        button_height = 44
        self.building_buttons = []
        for key, display_name in BUILDING_TYPES.items():
            rect = pygame.Rect(x, y, 160, button_height)
            self.building_buttons.append((display_name, rect))
            y += button_height + 8

    def get_available_buildings(self):
        """Get buildings available for the currently selected planet"""
        if (self.galaxy.selected_unit and 
            hasattr(self.galaxy.selected_unit, 'get_allowed_buildings')):
            buildings = self.galaxy.selected_unit.get_allowed_buildings()
            return buildings
        # If no planet selected, show no buildings
        return []

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # UI buttons and build menu tab take priority
                if self.end_turn_button.collidepoint(event.pos):
                    print("DEBUG: End Turn button clicked")
                    self.end_turn()
                    return
                if self.debug_button.collidepoint(event.pos):
                    print("DEBUG: Debug button clicked")
                    self.debug_add_resources()
                    return
                if self.build_menu_open:
                    tab_x = self.end_turn_button.x - 180
                    tab_y = 60
                    # Check tab clicks
                    for i, tab in enumerate(BUILD_MENU_TABS):
                        tab_rect = pygame.Rect(tab_x + i*90, tab_y, 90, 32)
                        if tab_rect.collidepoint(event.pos):
                            print(f"DEBUG: Build menu tab '{tab}' clicked")
                            self.build_menu_tab = i
                            self._menu_needs_update = True
                            return
                    
                    # Check building button clicks
                    if self.build_menu_tab == 0:  # Buildings tab
                        available_buildings = self.get_available_buildings()
                        y_offset = 100
                        for display_name, rect in self.building_buttons:
                            if display_name in available_buildings:
                                button_rect = pygame.Rect(tab_x, y_offset, 160, 44)
                                if button_rect.collidepoint(event.pos):
                                    print(f"DEBUG: Building '{display_name}' selected")
                                    self.selected_building_type = display_name
                                    # Automatically enter build mode if a planet is selected
                                    if (self.galaxy.selected_unit and 
                                        hasattr(self.galaxy.selected_unit, 'get_allowed_buildings')):
                                        self.galaxy.build_mode = True
                                        print(f"DEBUG: Auto-entered build mode for planet building")
                                    self._menu_needs_update = True
                                    return
                                y_offset += 52
                    elif self.build_menu_tab == 1:  # Orbitals tab
                        y_offset = 100
                        for key, display_name in ORBITAL_TYPES.items():
                            button_rect = pygame.Rect(tab_x, y_offset, 160, 44)
                            if button_rect.collidepoint(event.pos):
                                print(f"DEBUG: Orbital '{display_name}' selected")
                                self.selected_building_type = display_name
                                # Automatically enter build mode for orbital placement
                                self.galaxy.build_mode = True
                                print(f"DEBUG: Auto-entered build mode for orbital placement")
                                self._menu_needs_update = True
                                return
                            y_offset += 52
                
                # Handle selection and movement through galaxy.handle_click
                # Set the selected building type first
                self.galaxy.selected_building_type = self.selected_building_type
                
                # Call galaxy's handle_click which handles selection, movement, and building placement
                print("DEBUG: Calling galaxy.handle_click for all click logic")
                player = self.players[self.current_player]
                self.galaxy.handle_click(event.pos, player, self.current_player)
                
                # Handle resource deduction if building was placed
                if self.selected_building_type and self.galaxy.building_just_placed:
                    from .constants import BUILDING_COSTS
                    player = self.players[self.current_player]
                    
                    if self.selected_building_type in BUILDING_COSTS:
                        costs = BUILDING_COSTS[self.selected_building_type]
                        
                        # Deduct resources since building was successfully placed
                        for resource, amount in costs.items():
                            player.spend_resource(resource, amount)
                            print(f"Player {self.current_player} spent {amount} {resource} on {self.selected_building_type}")
                        # Mark menu for update after spending resources
                        self._menu_needs_update = True
            elif event.button == 3:  # Right click
                print("DEBUG: Right click")
                self.handle_right_click(event.pos)
            elif event.button == 4:  # Mouse wheel up
                print("DEBUG: Mouse wheel up (zoom in)")
                self.galaxy.handle_zoom(False)  # Zoom in
            elif event.button == 5:  # Mouse wheel down
                print("DEBUG: Mouse wheel down (zoom out)")
                self.galaxy.handle_zoom(True)   # Zoom out
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                print("DEBUG: E pressed - toggling build menu")
                self.build_menu_open = not self.build_menu_open
                # Context-sensitive default tab when opening
                if self.build_menu_open:
                    if self.galaxy.selected_unit and hasattr(self.galaxy.selected_unit, 'get_allowed_buildings'):
                        self.build_menu_tab = 0  # Planetary
                        print("DEBUG: Build menu opened - default to planetary tab")
                    else:
                        self.build_menu_tab = 1  # Orbitals
                        print("DEBUG: Build menu opened - default to orbital tab")
                else:
                    # When closing build menu, reset build mode and selected building
                    self.galaxy.build_mode = False
                    self.selected_building_type = None
                    if hasattr(self.galaxy, 'selected_building_type'):
                        self.galaxy.selected_building_type = None
                    print("DEBUG: Build menu closed - resetting build mode and selected building")
                self._menu_needs_update = True
                return
            elif event.key == pygame.K_b:
                # Toggle build mode if a planet is selected
                if self.galaxy.selected_unit and hasattr(self.galaxy.selected_unit, 'get_allowed_buildings'):
                    self.galaxy.build_mode = not self.galaxy.build_mode
                    print(f"DEBUG: Build mode toggled to {self.galaxy.build_mode}")
                else:
                    print("DEBUG: No planet selected for build mode")
            elif event.key == pygame.K_HOME or event.key == pygame.K_c:
                print("DEBUG: Center view on galaxy")
                self.galaxy.center_view_on_galaxy()
            elif event.key == pygame.K_q:
                # Special ability hotkey
                if self.galaxy.selected_unit and hasattr(self.galaxy.selected_unit, 'unit_type') and self.galaxy.selected_unit.unit_type == 'SHIP':
                    ship = self.galaxy.selected_unit
                    if ship.owner == self.current_player:
                        if ship.label == 'CAR':  # Carrier deployment
                            if hasattr(ship, 'deploy_units') and ship.actions_left > 0:
                                if ship.deploy_units(self.galaxy):
                                    print(f"DEBUG: Carrier at {ship.grid_position} deployed units")
                                else:
                                    print(f"DEBUG: Carrier deployment failed - no units or no space")
                            else:
                                print(f"DEBUG: Carrier has no actions left or no deploy method")
                        elif ship.label in ('FIG', 'BOM'):  # Fighter/Bomber docking
                            if ship.actions_left > 0:
                                # Find nearest friendly carrier within range
                                nearest_carrier = None
                                min_distance = float('inf')
                                sx, sy = ship.grid_position
                                for other_ship in self.galaxy.ships:
                                    if (other_ship.label == 'CAR' and other_ship.owner == ship.owner and 
                                        hasattr(other_ship, 'can_dock') and other_ship.can_dock(ship)):
                                        ox, oy = other_ship.grid_position
                                        distance = abs(sx - ox) + abs(sy - oy)
                                        if distance <= ship.move_range and distance < min_distance:
                                            nearest_carrier = other_ship
                                            min_distance = distance
                                
                                if nearest_carrier:
                                    # Move to carrier and dock
                                    ship.grid_position = nearest_carrier.grid_position
                                    nearest_carrier.dock_unit(ship)
                                    self.galaxy.ships.remove(ship)
                                    ship.set_selected(False)
                                    self.galaxy.selected_unit = None
                                    self.galaxy.move_tiles = []
                                    print(f"DEBUG: {ship.label} docked with Carrier at {nearest_carrier.grid_position}")
                                else:
                                    print(f"DEBUG: No friendly Carrier within range for {ship.label}")
                            else:
                                print(f"DEBUG: {ship.label} has no actions left")
                        else:
                            print(f"DEBUG: {ship.label} has no special ability")
                    else:
                        print(f"DEBUG: Cannot use ability - ship owned by player {ship.owner}, current player is {self.current_player}")
                else:
                    print("DEBUG: No ship selected for special ability")

    def handle_left_click(self, pos):
        # Set the selected building type
        self.galaxy.selected_building_type = self.selected_building_type
        
        # Mark menu for update when selection changes
        if hasattr(self, '_menu_needs_update'):
            self._menu_needs_update = True
        
        print(f"DEBUG: handle_left_click - selected_building_type: {self.selected_building_type}")
        print(f"DEBUG: handle_left_click - build_mode: {self.galaxy.build_mode}")
        
        # If we have a building selected and we're in build mode, check affordability first
        if self.selected_building_type and self.galaxy.build_mode:
            from .constants import BUILDING_COSTS, ORBITAL_COSTS
            player = self.players[self.current_player]
            
            print(f"DEBUG: Checking affordability for {self.selected_building_type}")
            print(f"DEBUG: Player resources: {player.resources}")
            
            # Check building costs
            if self.selected_building_type in BUILDING_COSTS:
                costs = BUILDING_COSTS[self.selected_building_type]
                print(f"DEBUG: Building costs: {costs}")
                
                # Check if player can afford it
                for resource, amount in costs.items():
                    if player.get_resource(resource) < amount:
                        self.galaxy.build_warning = f'Not enough {resource}! Need {amount}, have {player.get_resource(resource)}'
                        print(f"DEBUG: Cannot afford building - {resource}: need {amount}, have {player.get_resource(resource)}")
                        return  # Don't proceed with building placement
            
            # Check orbital costs
            elif self.selected_building_type in ORBITAL_COSTS:
                costs = ORBITAL_COSTS[self.selected_building_type]
                print(f"DEBUG: Orbital costs: {costs}")
                
                # Check if player can afford it
                for resource, amount in costs.items():
                    if player.get_resource(resource) < amount:
                        self.galaxy.build_warning = f'Not enough {resource}! Need {amount}, have {player.get_resource(resource)}'
                        print(f"DEBUG: Cannot afford orbital - {resource}: need {amount}, have {player.get_resource(resource)}")
                        return  # Don't proceed with orbital placement
            
            print(f"DEBUG: Player can afford {self.selected_building_type}")
        
        # Let galaxy handle the click logic (building vs selection) - only if we can afford it
        player = self.players[self.current_player]
        self.galaxy.handle_click(pos, player, self.current_player)
                
        # Only deduct resources if a building was actually placed
        if self.selected_building_type and self.galaxy.building_just_placed:
            from .constants import BUILDING_COSTS
            player = self.players[self.current_player]
            
            # Check if building has costs and deduct them
            if self.selected_building_type in BUILDING_COSTS:
                costs = BUILDING_COSTS[self.selected_building_type]
                
                # Check if player can afford it first (this should have been checked already, but just in case)
                can_afford = True
                for resource, amount in costs.items():
                    if player.get_resource(resource) < amount:
                        can_afford = False
                        break
                
                if can_afford:
                    # Deduct resources since building was successfully placed
                    for resource, amount in costs.items():
                        player.spend_resource(resource, amount)
                        print(f"Player {self.current_player} spent {amount} {resource} on {self.selected_building_type}")
                    # Mark menu for update after spending resources
                    self._menu_needs_update = True
                else:
                    print(f"ERROR: Building was placed but player couldn't afford it!")
            else:
                print(f"DEBUG: No costs defined for {self.selected_building_type}")
        
        # Only deduct resources if an orbital was actually placed
        if self.selected_building_type and self.galaxy.orbital_just_placed:
            from .constants import ORBITAL_COSTS
            player = self.players[self.current_player]
            
            # Check if orbital has costs and deduct them
            if self.selected_building_type in ORBITAL_COSTS:
                costs = ORBITAL_COSTS[self.selected_building_type]
                
                # Check if player can afford it first (this should have been checked already, but just in case)
                can_afford = True
                for resource, amount in costs.items():
                    if player.get_resource(resource) < amount:
                        can_afford = False
                        break
                
                if can_afford:
                    # Deduct resources since orbital was successfully placed
                    for resource, amount in costs.items():
                        player.spend_resource(resource, amount)
                        print(f"Player {self.current_player} spent {amount} {resource} on orbital {self.selected_building_type}")
                    # Mark menu for update after spending resources
                    self._menu_needs_update = True
                else:
                    print(f"ERROR: Orbital was placed but player couldn't afford it!")
            else:
                print(f"DEBUG: No costs defined for orbital {self.selected_building_type}")

    def handle_right_click(self, pos):
        self.galaxy.handle_right_click(pos)

    def update_screen_size(self, new_size):
        """Update UI elements when screen size changes (for fullscreen toggle)"""
        width, height = new_size
        
        # Update button positions
        self.end_turn_button = pygame.Rect(width - 160, height - 60, 150, 50)
        self.debug_button = pygame.Rect(width - 160, 10, 150, 40)
        
        # Update building buttons
        self._init_building_buttons_with_size(width, height)
    
    def _init_building_buttons_with_size(self, width, height):
        """Initialize building buttons with specific screen dimensions"""
        x = width - 180
        y = 100
        button_height = 44
        self.building_buttons = []
        for key, display_name in BUILDING_TYPES.items():
            rect = pygame.Rect(x, y, 160, button_height)
            self.building_buttons.append((display_name, rect))
            y += button_height + 8

    def update(self):
        """Update game state, including AI turns"""
        # Handle AI turns with a delay
        if self.is_current_player_ai():
            self.ai_turn_timer += 16  # Assuming ~60 FPS (16ms per frame)
            
            if self.ai_turn_timer >= self.ai_turn_delay:
                # Execute AI turn
                ai_controller = self.ai_controllers[self.current_player]
                ai_controller.take_turn(self)
                
                # Auto-end turn for AI
                self.end_turn()
                self.ai_turn_timer = 0
        
        self.galaxy.update()

    def render(self, screen):
        self.galaxy.render(screen)
        self.render_ui(screen)
        
        # Draw build warning if present
        if self.galaxy.build_warning:
            warning_text = self.font_medium.render(self.galaxy.build_warning, True, (255, 60, 60))
            screen_width = screen.get_width()
            screen.blit(warning_text, (screen_width // 2 - warning_text.get_width() // 2, 20))
        
        # Draw shipyard status
        self._render_shipyard_status(screen)
        
        # Draw AI debug panel if current player is AI
        if self.is_current_player_ai():
            self._render_ai_debug_panel(screen)
        
        # Draw End Turn button
        pygame.draw.rect(screen, (60, 60, 60), self.end_turn_button)
        text = self.font_medium.render("End Turn", True, WHITE)
        screen.blit(text, (self.end_turn_button.x + 20, self.end_turn_button.y + 10))
        
        # Draw Debug button
        pygame.draw.rect(screen, (100, 40, 40), self.debug_button)
        debug_text = self.font_small.render("+100 All (Debug)", True, WHITE)
        screen.blit(debug_text, (self.debug_button.x + 8, self.debug_button.y + 8))
        
        # Draw resources near End Turn button
        player = self.players[self.current_player]
        res_y = self.end_turn_button.y - 28 * len(player.resources) - 10
        for resource, amount in player.resources.items():
            res_text = self.font_message.render(f"{resource}: {amount}", True, WHITE)
            screen.blit(res_text, (self.end_turn_button.x + 10, res_y))
            res_y += 28
        
        # Draw building selection menu if in build mode
        if self.galaxy.build_mode:
            self._render_building_menu(screen)
        
        # Draw build menu if open
        if self.build_menu_open:
            self._render_build_menu(screen)

    def _render_shipyard_status(self, screen):
        """Render shipyard construction status in the top-left corner"""
        active_shipyards = []
        
        # Check all planets for active shipyards
        for planet in self.galaxy.planets:
            if (hasattr(planet, 'has_shipyard') and planet.has_shipyard() and 
                hasattr(planet, 'build_queue') and planet.build_queue):
                for ship in planet.build_queue:
                    active_shipyards.append({
                        'location': f"{getattr(planet, 'system_label', '?')}-{getattr(planet, 'type_label', '?')}",
                        'ship_type': ship['ship_type'],
                        'turns_remaining': ship['turns_remaining'],
                        'progress': ship['total_turns'] - ship['turns_remaining'],
                        'total': ship['total_turns']
                    })
        
        # Check all orbitals for active shipyards
        for orbital in self.galaxy.orbitals:
            if (hasattr(orbital, 'has_shipyard') and orbital.has_shipyard() and 
                hasattr(orbital, 'build_queue') and orbital.build_queue):
                for ship in orbital.build_queue:
                    active_shipyards.append({
                        'location': orbital.name,
                        'ship_type': ship['ship_type'],
                        'turns_remaining': ship['turns_remaining'],
                        'progress': ship['total_turns'] - ship['turns_remaining'],
                        'total': ship['total_turns']
                    })
        
        if not active_shipyards:
            return
        
        # Draw shipyard status panel
        panel_width = 300
        panel_height = len(active_shipyards) * 25 + 40
        panel_rect = pygame.Rect(10, 10, panel_width, panel_height)
        
        # Semi-transparent background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill((20, 20, 30))
        screen.blit(panel_surface, (panel_rect.x, panel_rect.y))
        
        # Border
        pygame.draw.rect(screen, (100, 150, 200), panel_rect, 2)
        
        # Title
        title_text = self.font_small.render("ACTIVE SHIPYARDS", True, (100, 200, 255))
        screen.blit(title_text, (panel_rect.x + 10, panel_rect.y + 8))
        
        # Construction status
        y_offset = 30
        for shipyard in active_shipyards:
            if shipyard['turns_remaining'] > 0:
                status_text = f"{shipyard['location']}: {shipyard['ship_type']} ({shipyard['turns_remaining']} turns)"
                color = (255, 200, 100)
            else:
                status_text = f"{shipyard['location']}: {shipyard['ship_type']} READY!"
                color = (100, 255, 100)
            
            text = self.font_message.render(status_text, True, color)
            screen.blit(text, (panel_rect.x + 10, panel_rect.y + y_offset))
            
            # Progress bar
            if shipyard['total'] > 0:
                progress_width = 200
                progress_height = 4
                progress_x = panel_rect.x + 10
                progress_y = panel_rect.y + y_offset + 16
                
                # Background
                pygame.draw.rect(screen, (50, 50, 50), 
                               (progress_x, progress_y, progress_width, progress_height))
                
                # Progress
                progress_ratio = shipyard['progress'] / shipyard['total']
                filled_width = int(progress_width * progress_ratio)
                if shipyard['turns_remaining'] > 0:
                    progress_color = (255, 200, 100)
                else:
                    progress_color = (100, 255, 100)
                
                pygame.draw.rect(screen, progress_color,
                               (progress_x, progress_y, filled_width, progress_height))
            
            y_offset += 25

    def _render_building_menu(self, screen):
        # Draw tab toggle buttons
        tab_x = self.end_turn_button.x - 180
        tab_y = 60
        for i, tab in enumerate(BUILD_MENU_TABS):
            tab_rect = pygame.Rect(tab_x + i*90, tab_y, 90, 32)
            color = (80, 80, 80) if self.build_menu_tab != i else (0, 180, 255)
            pygame.draw.rect(screen, color, tab_rect)
            label = self.font_small.render(tab, True, WHITE)
            screen.blit(label, (tab_rect.x + 10, tab_rect.y + 4))
        
        # Show planetary or orbital options
        if self.build_menu_tab == 0:
            self._render_building_menu_planetary(screen)
        else:
            self._render_building_menu_orbital(screen)

    def _render_building_menu_planetary(self, screen):
        """Ultra-optimized building menu rendering with surface caching"""
        # Check if zoomed in enough to show building menu
        if self.galaxy.zoom_level < 0.4:
            # Show zoom in message instead of building menu (simple, no caching needed)
            screen_width = screen.get_width()
            message_bg = pygame.Rect(screen_width - 180, 80, 170, 80)
            pygame.draw.rect(screen, (40, 40, 40), message_bg)
            pygame.draw.rect(screen, (255, 255, 0), message_bg, 2)
            
            # Pre-rendered message text
            if not hasattr(self, '_zoom_message_cache'):
                self._zoom_message_cache = [
                    self.font_message.render("Zoom in to build", True, (255, 255, 0)),
                    self.font_message.render("Use mouse wheel", True, (255, 255, 0)),
                    self.font_message.render("or scroll to zoom", True, (255, 255, 0))
                ]
            
            for i, text in enumerate(self._zoom_message_cache):
                screen.blit(text, (screen_width - 175, 90 + i * 22))
            return
        
        # Increment frame counter for update limiting
        self._frame_counter += 1
        
        from .constants import BUILDING_COLORS, BUILDING_COSTS
        available_buildings = self.get_available_buildings()
        player = self.players[self.current_player]
        
        # Create a state key for caching
        build_state = (
            tuple(available_buildings),
            tuple((r, player.get_resource(r)) for r in ['Minerals', 'Energy', 'Science', 'Food']),
            self.selected_building_type,
            screen.get_width()  # Include screen width for fullscreen changes
        )
        
        # Check if we need to update the menu (state changed or every 10 frames for safety)
        if (build_state != self._last_build_state or 
            self._menu_needs_update or 
            self._building_menu_surface is None or
            self._frame_counter % 10 == 0):  # Refresh every 10 frames as fallback
            
            self._last_build_state = build_state
            self._menu_needs_update = False
            
            # Create or recreate the menu surface
            menu_width = 180
            menu_height = len(available_buildings) * 52 + 100
            self._building_menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
            self._building_menu_surface.fill((0, 0, 0, 0))  # Transparent background
            
            y_offset = 0  # Start at top since no header needed
            
            for display_name, rect in self.building_buttons:
                if display_name in available_buildings:
                    # Create rect relative to surface
                    adjusted_rect = pygame.Rect(0, y_offset, 160, 44)
                    
                    # Check affordability
                    can_afford = True
                    if display_name in BUILDING_COSTS:
                        costs = BUILDING_COSTS[display_name]
                        for resource, amount in costs.items():
                            if player.get_resource(resource) < amount:
                                can_afford = False
                                break
                    
                    # Color based on affordability
                    if can_afford:
                        color = BUILDING_COLORS.get(display_name, (80, 80, 80))
                    else:
                        base_color = BUILDING_COLORS.get(display_name, (80, 80, 80))
                        color = tuple(c // 3 for c in base_color)
                    
                    pygame.draw.rect(self._building_menu_surface, color, adjusted_rect)
                    
                    # Highlight border if selected
                    border_color = (0, 180, 255) if self.selected_building_type == display_name else (255, 255, 255)
                    pygame.draw.rect(self._building_menu_surface, border_color, adjusted_rect, 3)
                    
                    # Draw building name
                    label = self.font_building.render(display_name, True, (0, 0, 0))
                    self._building_menu_surface.blit(label, (adjusted_rect.x + 10, adjusted_rect.y + 4))
                    
                    # Draw cost information
                    if display_name in BUILDING_COSTS:
                        costs = BUILDING_COSTS[display_name]
                        cost_y = adjusted_rect.y + 24
                        for resource, amount in costs.items():
                            if player.get_resource(resource) >= amount:
                                cost_color = (0, 120, 0)
                            else:
                                cost_color = (180, 0, 0)
                            
                            cost_text = self.font_cost.render(f"{resource}: {amount}", True, cost_color)
                            self._building_menu_surface.blit(cost_text, (adjusted_rect.x + 12, cost_y))
                            cost_y += 16
                    
                    y_offset += 52
        
        # Simply blit the pre-rendered surface
        # Use the same positioning as click detection
        tab_x = self.end_turn_button.x - 180
        screen.blit(self._building_menu_surface, (tab_x, 100))

    def _render_building_menu_orbital(self, screen):
        # Render orbital options
        from .constants import ORBITAL_COSTS
        tab_x = self.end_turn_button.x - 180
        y_offset = 100
        player = self.players[self.current_player]
        
        for key, display_name in ORBITAL_TYPES.items():
            rect = pygame.Rect(tab_x, y_offset, 160, 44)
            
            # Check affordability
            can_afford = True
            if display_name in ORBITAL_COSTS:
                costs = ORBITAL_COSTS[display_name]
                for resource, amount in costs.items():
                    if player.get_resource(resource) < amount:
                        can_afford = False
                        break
            
            # Color based on affordability
            if can_afford:
                color = (60, 60, 120)
            else:
                color = (30, 30, 60)  # Darker if can't afford
            
            pygame.draw.rect(screen, color, rect)
            
            # Highlight border if selected
            border_color = (0, 180, 255) if self.selected_building_type == display_name else (255, 255, 255)
            pygame.draw.rect(screen, border_color, rect, 3)
            
            # Draw orbital name
            label = self.font_building.render(display_name, True, (255, 255, 0))
            screen.blit(label, (rect.x + 10, rect.y + 4))
            
            # Draw cost information
            if display_name in ORBITAL_COSTS:
                costs = ORBITAL_COSTS[display_name]
                cost_y = rect.y + 24
                for resource, amount in costs.items():
                    if player.get_resource(resource) >= amount:
                        cost_color = (0, 120, 0)
                    else:
                        cost_color = (180, 0, 0)
                    
                    cost_text = self.font_cost.render(f"{resource}: {amount}", True, cost_color)
                    screen.blit(cost_text, (rect.x + 12, cost_y))
                    cost_y += 16
                    
            y_offset += 52

    def render_ui(self, screen):
        # Show AI indicator if current player is AI
        if self.is_current_player_ai():
            player_text = self.font_large.render(f"AI Player {self.current_player + 1}'s Turn", True, (255, 255, 100))
            ai_thinking_text = self.font_small.render("AI is thinking...", True, (255, 255, 100))
            screen.blit(ai_thinking_text, (10, 45))
        else:
            player_text = self.font_large.render(f"Player {self.current_player + 1}'s Turn", True, WHITE)
        
        screen.blit(player_text, (10, 10))
        turn_text = self.font_large.render(f"Turn: {self.current_turn}", True, WHITE)
        screen.blit(turn_text, (10, 50))
        
        # Draw resources
        player = self.players[self.current_player]
        res_y = 90
        for resource, amount in player.resources.items():
            res_text = self.font_small.render(f"{resource}: {amount}", True, WHITE)
            screen.blit(res_text, (10, res_y))
            res_y += 28

    def end_turn(self):
        # Add resource production from planets owned by the current player
        current_player_obj = self.players[self.current_player]
        
        # Process shipyard construction for all players
        print(f"\n=== END OF TURN {self.current_turn} ===")
        self.galaxy.end_turn_update()
        
        for planet in self.galaxy.planets:
            if hasattr(planet, 'owner') and planet.owner is not None:
                owner = self.players[planet.owner]
                production = planet.get_resource_production()
                for resource, amount in production.items():
                    owner.add_resource(resource, amount)
                    print(f"Player {planet.owner} gained {amount} {resource} from planet {getattr(planet, 'system_label', '?')}-{getattr(planet, 'type_label', '?')}")
        
        # Process orbital production
        for orbital in self.galaxy.orbitals:
            if hasattr(orbital, 'owner') and orbital.owner is not None:
                owner = self.players[orbital.owner]
                production = orbital.get_resource_production()
                for resource, amount in production.items():
                    owner.add_resource(resource, amount)
                    print(f"Player {orbital.owner} gained {amount} {resource} from orbital {orbital.name}")
        
        # Reset all ship actions for the new turn
        self.galaxy.reset_all_ship_actions()
        
        # Switch to next player
        self.current_player = (self.current_player + 1) % len(self.players)
        if self.current_player == 0:  # Back to player 1, increment turn
            self.current_turn += 1
        
        print(f"Turn {self.current_turn}, Player {self.current_player + 1}'s turn")
        self._menu_needs_update = True

    def debug_add_resources(self):
        player = self.players[self.current_player]
        print(f"DEBUG: Adding 100 resources to player {self.current_player}")
        print(f"DEBUG: Before - Resources: {player.resources}")
        for resource in player.resources:
            player.resources[resource] += 100 
        print(f"DEBUG: After - Resources: {player.resources}")
        # Mark menu for update after adding resources
        self._menu_needs_update = True 

    def _render_build_menu(self, screen):
        # Implementation of _render_build_menu method - same as _render_building_menu
        self._render_building_menu(screen)

    def is_current_player_ai(self):
        """Check if the current player is AI"""
        return self.current_player in self.ai_players

    def _render_ai_debug_panel(self, screen):
        """Render AI debug information panel"""
        if self.current_player not in self.ai_controllers:
            return
            
        ai_controller = self.ai_controllers[self.current_player]
        debug_info = ai_controller.debug_info
        
        # Panel background
        panel_width = 400
        panel_height = 300
        panel_x = 10
        panel_y = 200
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (20, 20, 40, 200), panel_rect)
        pygame.draw.rect(screen, (100, 100, 150), panel_rect, 2)
        
        # Title
        title_text = self.font_header.render("AI DEBUG PANEL", True, (255, 255, 100))
        screen.blit(title_text, (panel_x + 10, panel_y + 5))
        
        y_offset = panel_y + 30
        line_height = 18
        
        # Strategy and basic stats
        strategy_text = self.font_cost.render(f"Strategy: {debug_info['current_strategy']}", True, WHITE)
        screen.blit(strategy_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        planets_text = self.font_cost.render(f"Owned Planets: {debug_info['owned_planets']}", True, WHITE)
        screen.blit(planets_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        shipyards_text = self.font_cost.render(f"Owned Shipyards: {debug_info['owned_shipyards']}", True, WHITE)
        screen.blit(shipyards_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Resources
        resources = debug_info['resource_status']
        resource_text = self.font_cost.render(f"Resources: M:{resources.get('Minerals', 0)} E:{resources.get('Energy', 0)} S:{resources.get('Science', 0)} F:{resources.get('Food', 0)}", True, WHITE)
        screen.blit(resource_text, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Turn activity
        activity_text = self.font_cost.render(f"This Turn: {debug_info['buildings_built_this_turn']} buildings, {debug_info['ships_built_this_turn']} ships, {debug_info['colonizations_this_turn']} colonies", True, WHITE)
        screen.blit(activity_text, (panel_x + 10, y_offset))
        y_offset += line_height + 5
        
        # Ship targets
        if debug_info['ship_targets']:
            targets_title = self.font_cost.render("Ship Targets:", True, (200, 200, 255))
            screen.blit(targets_title, (panel_x + 10, y_offset))
            y_offset += line_height
            
            for ship_id, target in list(debug_info['ship_targets'].items())[:6]:  # Limit to 6 ships
                target_text = self.font_cost.render(f"  {ship_id} -> {target}", True, (180, 180, 180))
                screen.blit(target_text, (panel_x + 15, y_offset))
                y_offset += line_height
                
        # Recent actions
        if debug_info['last_actions']:
            y_offset += 5
            actions_title = self.font_cost.render("Recent Actions:", True, (200, 255, 200))
            screen.blit(actions_title, (panel_x + 10, y_offset))
            y_offset += line_height
            
            for action in debug_info['last_actions'][-4:]:  # Show last 4 actions
                action_text = self.font_cost.render(f"  • {action}", True, (160, 160, 160))
                screen.blit(action_text, (panel_x + 15, y_offset))
                y_offset += line_height

 