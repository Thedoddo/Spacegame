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
                # Building menu click
                if self.galaxy.build_mode:  # Only show building menu when in build mode
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

    def handle_left_click(self, pos):
        # Set the selected building type
        self.galaxy.selected_building_type = self.selected_building_type
        
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
                else:
                    print(f"ERROR: Building was placed but player couldn't afford it!")
            else:
                print(f"DEBUG: No costs defined for {self.selected_building_type}")

    def handle_right_click(self, pos):
        self.galaxy.handle_right_click(pos)

    def update(self):
        self.galaxy.update()

    def render(self, screen):
        self.galaxy.render(screen)
        self.render_ui(screen)
        # Draw build warning if present
        if self.galaxy.build_warning:
            font = pygame.font.Font(None, 32)
            warning_text = font.render(self.galaxy.build_warning, True, (255, 60, 60))
            screen.blit(warning_text, (WINDOW_WIDTH // 2 - warning_text.get_width() // 2, 20))
        # Draw End Turn button
        pygame.draw.rect(screen, (60, 60, 60), self.end_turn_button)
        font = pygame.font.Font(None, 32)
        text = font.render("End Turn", True, WHITE)
        screen.blit(text, (self.end_turn_button.x + 20, self.end_turn_button.y + 10))
        # Draw Debug button
        pygame.draw.rect(screen, (100, 40, 40), self.debug_button)
        debug_font = pygame.font.Font(None, 28)
        debug_text = debug_font.render("+100 All (Debug)", True, WHITE)
        screen.blit(debug_text, (self.debug_button.x + 8, self.debug_button.y + 8))
        # Draw resources near End Turn button
        player = self.players[self.current_player]
        res_font = pygame.font.Font(None, 24)
        res_y = self.end_turn_button.y - 28 * len(player.resources) - 10
        for resource, amount in player.resources.items():
            res_text = res_font.render(f"{resource}: {amount}", True, WHITE)
            screen.blit(res_text, (self.end_turn_button.x + 10, res_y))
            res_y += 28
        # Draw building selection menu if in build mode
        if self.galaxy.build_mode:
            font = pygame.font.Font(None, 26)
            cost_font = pygame.font.Font(None, 18)
            from .constants import BUILDING_COLORS, BUILDING_COSTS
            available_buildings = self.get_available_buildings()
            y_offset = 0
            
            # Show menu header
            header_font = pygame.font.Font(None, 20)
            header_text = header_font.render("Buildings", True, (255, 255, 255))
            screen.blit(header_text, (WINDOW_WIDTH - 175, 80))
            
            for display_name, rect in self.building_buttons:
                if display_name in available_buildings:
                    # Adjust rect position based on filtered list
                    adjusted_rect = pygame.Rect(rect.x, 100 + y_offset, rect.width, rect.height)
                    
                    # Check if player can afford this building
                    player = self.players[self.current_player]
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
                        # Darken color if can't afford
                        base_color = BUILDING_COLORS.get(display_name, (80, 80, 80))
                        color = tuple(c // 3 for c in base_color)  # Much darker
                    
                    pygame.draw.rect(screen, color, adjusted_rect)
                    # Highlight border if selected
                    border_color = (0, 180, 255) if self.selected_building_type == display_name else (255, 255, 255)
                    pygame.draw.rect(screen, border_color, adjusted_rect, 3)
                    
                    # Draw building name
                    label = font.render(display_name, True, (0, 0, 0))
                    screen.blit(label, (adjusted_rect.x + 10, adjusted_rect.y + 4))
                    
                    # Draw cost information below building name
                    if display_name in BUILDING_COSTS:
                        costs = BUILDING_COSTS[display_name]
                        cost_y = adjusted_rect.y + 24
                        for resource, amount in costs.items():
                            # Color code cost text based on affordability
                            if player.get_resource(resource) >= amount:
                                cost_color = (0, 120, 0)  # Green if affordable
                            else:
                                cost_color = (180, 0, 0)  # Red if not affordable
                            
                            cost_text = cost_font.render(f"{resource}: {amount}", True, cost_color)
                            screen.blit(cost_text, (adjusted_rect.x + 12, cost_y))
                            cost_y += 16
                    

                    
                    y_offset += 52

    def render_ui(self, screen):
        font = pygame.font.Font(None, 36)
        player_text = font.render(f"Player {self.current_player + 1}'s Turn", True, WHITE)
        screen.blit(player_text, (10, 10))
        turn_text = font.render(f"Turn: {self.current_turn}", True, WHITE)
        screen.blit(turn_text, (10, 50))
        # Draw resources
        res_font = pygame.font.Font(None, 28)
        player = self.players[self.current_player]
        res_y = 90
        for resource, amount in player.resources.items():
            res_text = res_font.render(f"{resource}: {amount}", True, WHITE)
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