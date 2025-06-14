import pygame
from .constants import *
from .galaxy import Galaxy
from .player import Player

class GameState:
    def __init__(self):
        self.current_player = 0
        self.players = [Player("Player 1"), Player("Player 2")]
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
        if (self.galaxy.build_mode and self.galaxy.selected_unit and 
            hasattr(self.galaxy.selected_unit, 'get_allowed_buildings')):
            buildings = self.galaxy.selected_unit.get_allowed_buildings()
            return buildings
        # If not in planet build mode, show no buildings
        return []

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.end_turn_button.collidepoint(event.pos):
                    self.end_turn()
                    return
                if self.debug_button.collidepoint(event.pos):
                    self.debug_add_resources()
                    return
                # Building menu click (only if zoomed in enough)
                if self.galaxy.build_mode and self.galaxy.zoom_level >= 0.4:  # Only show building menu when in build mode and zoomed in
                    available_buildings = self.get_available_buildings()
                    y_offset = 0
                    for display_name, rect in self.building_buttons:
                        if display_name in available_buildings:
                            adjusted_rect = pygame.Rect(rect.x, 100 + y_offset, rect.width, rect.height)
                            if adjusted_rect.collidepoint(event.pos):
                                self.selected_building_type = display_name
                                print(f"DEBUG: Selected building type: {display_name}")
                                return
                            y_offset += 52
                self.handle_left_click(event.pos)
            elif event.button == 3:  # Right click
                self.handle_right_click(event.pos)
            elif event.button == 4:  # Mouse wheel up
                self.galaxy.handle_zoom(False)  # Zoom in
            elif event.button == 5:  # Mouse wheel down
                self.galaxy.handle_zoom(True)   # Zoom out
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                # Deploy Carrier ability if selected
                unit = self.galaxy.selected_unit
                if unit and getattr(unit, 'label', None) == 'CAR':
                    deployed = unit.deploy_units(self.galaxy)
                    if deployed:
                        print(f"Carrier at {unit.grid_position} deployed units!")
                    else:
                        print(f"Carrier at {unit.grid_position} could not deploy units.")
                # Dock Fighter/Bomber to nearest Carrier
                elif unit and getattr(unit, 'label', None) in ('FIG', 'BOM'):
                    carriers = [s for s in self.galaxy.ships if getattr(s, 'label', None) == 'CAR' and s.owner == unit.owner and s.can_dock(unit)]
                    if not carriers:
                        print("DEBUG: No available friendly Carrier to dock!")
                        return
                    # Find nearest Carrier
                    ux, uy = unit.grid_position
                    carriers.sort(key=lambda c: abs(c.grid_position[0] - ux) + abs(c.grid_position[1] - uy))
                    carrier = carriers[0]
                    carrier.dock_unit(unit)
                    print(f"DEBUG: {unit.label} docked with Carrier at {carrier.grid_position}")
                    self.galaxy.ships.remove(unit)
                    unit.set_selected(False)
                    self.galaxy.selected_unit = None
                    self.galaxy.move_tiles = []
                    self.galaxy.build_mode = False
            elif event.key == pygame.K_HOME or event.key == pygame.K_c:
                # Press HOME or C to center view on galaxy
                self.galaxy.center_view_on_galaxy()

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
            from .constants import BUILDING_COSTS
            player = self.players[self.current_player]
            
            if self.selected_building_type in BUILDING_COSTS:
                costs = BUILDING_COSTS[self.selected_building_type]
                
                # Check if player can afford it
                can_afford = True
                for resource, amount in costs.items():
                    if player.get_resource(resource) < amount:
                        can_afford = False
                        self.galaxy.build_warning = f'Not enough {resource}! Need {amount}, have {player.get_resource(resource)}'
                        return
                
        # Let galaxy handle the click logic (building vs selection)
                self.galaxy.handle_click(pos, self.current_player)
                
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
        self.galaxy.update()

    def render(self, screen):
        self.galaxy.render(screen)
        self.render_ui(screen)
        # Draw build warning if present
        if self.galaxy.build_warning:
            warning_text = self.font_medium.render(self.galaxy.build_warning, True, (255, 60, 60))
            screen_width = screen.get_width()
            screen.blit(warning_text, (screen_width // 2 - warning_text.get_width() // 2, 20))
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

    def _render_building_menu(self, screen):
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
            
            y_offset = 20  # Start below header
            
            # Draw header on surface
            header_text = self.font_header.render("Buildings", True, (255, 255, 255))
            self._building_menu_surface.blit(header_text, (5, 0))
            
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
        screen_width = screen.get_width()
        screen.blit(self._building_menu_surface, (screen_width - 180, 80))

    def render_ui(self, screen):
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
        player = self.players[self.current_player]
        for planet in self.galaxy.planets:
            if hasattr(planet, 'owner') and planet.owner == self.current_player:
                production = planet.get_resource_production()
                for resource, amount in production.items():
                    player.add_resource(resource, amount)
                    print(f"Player {self.current_player} gained {amount} {resource} from {planet.system_label}-{planet.type_label}")
        

        
        self.current_player = (self.current_player + 1) % len(self.players)
        if self.current_player == 0:
            self.current_turn += 1
        self.galaxy.reset_all_ship_actions()
        if self.galaxy.selected_unit:
            self.galaxy.selected_unit.set_selected(False)
            self.galaxy.selected_unit = None

    def debug_add_resources(self):
        player = self.players[self.current_player]
        for resource in player.resources:
            player.resources[resource] += 100 
        # Mark menu for update after adding resources
        self._menu_needs_update = True 

 