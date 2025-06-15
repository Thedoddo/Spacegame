import pygame
from .constants import SHIP_COSTS, SHIP_BUILD_TIME, SHIP_TYPES

class ShipyardMixin:
    """Mixin class to add shipyard functionality to planets and orbitals"""
    
    def __init__(self):
        # Initialize shipyard-specific attributes
        self.build_queue = []  # List of ships being built: [{'ship_type': str, 'turns_remaining': int, 'total_turns': int}, ...]
        self.shipyard_dropdown_open = False
        self.shipyard_dropdown_selected = None
        
    def has_shipyard(self):
        """Check if this object has a shipyard building"""
        if hasattr(self, 'planet_grid'):  # Planet
            for row in self.planet_grid:
                for cell in row:
                    if cell is not None and cell.get('type') == 'Shipyard':
                        return True
        elif hasattr(self, 'orbital_type'):  # Orbital
            return self.orbital_type == 'ORBITAL_SHIPYARD'
        return False
    
    def can_build_ship(self, ship_type, player):
        """Check if this shipyard can build the specified ship type"""
        if not self.has_shipyard():
            return False, "No shipyard present"
        
        if ship_type not in SHIP_COSTS:
            return False, f"Unknown ship type: {ship_type}"
        
        # Check if player has enough resources
        costs = SHIP_COSTS[ship_type]
        for resource, amount in costs.items():
            if player.get_resource(resource) < amount:
                return False, f"Not enough {resource}! Need {amount}, have {player.get_resource(resource)}"
        
        return True, "Can build"
    
    def add_ship_to_queue(self, ship_type, player):
        """Add a ship to the construction queue"""
        can_build, message = self.can_build_ship(ship_type, player)
        if not can_build:
            return False, message
        
        # Deduct resources
        costs = SHIP_COSTS[ship_type]
        for resource, amount in costs.items():
            player.spend_resource(resource, amount)
        
        # Add to queue
        build_time = SHIP_BUILD_TIME[ship_type]
        self.build_queue.append({
            'ship_type': ship_type,
            'turns_remaining': build_time,
            'total_turns': build_time,
            'owner': player.player_id if hasattr(player, 'player_id') else 0
        })
        
        return True, f"{ship_type} added to construction queue"
    
    def update_shipyard(self, galaxy):
        """Update shipyard construction progress"""
        if not self.build_queue:
            return
        
        # Process the first ship in queue
        current_ship = self.build_queue[0]
        current_ship['turns_remaining'] -= 1
        
        # If ship is completed, spawn it
        if current_ship['turns_remaining'] <= 0:
            self._spawn_completed_ship(current_ship, galaxy)
            self.build_queue.pop(0)
    
    def _spawn_completed_ship(self, ship_data, galaxy):
        """Spawn a completed ship near the shipyard"""
        from .unit import (Corvette, Frigate, Destroyer, Cruiser, Battleship, 
                          Carrier, Fighter, Bomber, Scout, Transport, Builder, Colonizer)
        
        ship_classes = {
            'Corvette': Corvette,
            'Frigate': Frigate,
            'Destroyer': Destroyer,
            'Cruiser': Cruiser,
            'Battleship': Battleship,
            'Carrier': Carrier,
            'Fighter': Fighter,
            'Bomber': Bomber,
            'Scout': Scout,
            'Transport': Transport,
            'Builder': Builder,
            'Colonizer': Colonizer
        }
        
        ship_type = ship_data['ship_type']
        owner = ship_data['owner']
        
        if ship_type not in ship_classes:
            print(f"ERROR: Unknown ship type {ship_type}")
            return
        
        # Find a suitable spawn position near the shipyard
        spawn_pos = self._find_spawn_position(galaxy)
        if spawn_pos:
            new_ship = ship_classes[ship_type](spawn_pos, owner)
            galaxy.ships.append(new_ship)
            print(f"{ship_type} completed and spawned at {spawn_pos}")
        else:
            print(f"WARNING: No space to spawn {ship_type} near shipyard")
    
    def _find_spawn_position(self, galaxy):
        """Find an empty position near the shipyard to spawn ships"""
        # Get shipyard position
        if hasattr(self, 'grid_position'):
            base_x, base_y = self.grid_position
            size = getattr(self, 'size', 1)
        else:
            return None
        
        # Try positions in expanding rings around the shipyard
        for radius in range(1, 6):  # Search up to 5 tiles away
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) == radius or abs(dy) == radius:  # Only check perimeter
                        x = base_x + dx
                        y = base_y + dy
                        
                        # Check if position is valid and empty
                        if galaxy.is_position_empty((x, y)):
                            return (x, y)
        
        return None
    
    def cancel_ship_construction(self, queue_index, player):
        """Cancel a ship in the construction queue and refund resources"""
        if 0 <= queue_index < len(self.build_queue):
            ship_data = self.build_queue[queue_index]
            ship_type = ship_data['ship_type']
            
            # Calculate refund (full refund for now, could be partial in future)
            refund_costs = SHIP_COSTS[ship_type].copy()
            
            # Refund resources to player
            for resource, amount in refund_costs.items():
                player.add_resource(resource, amount)
            
            # Remove from queue
            removed_ship = self.build_queue.pop(queue_index)
            
            return True, f"{ship_type} construction cancelled. Resources refunded."
        
        return False, "Invalid queue position"
    
    def render_shipyard_tooltip(self, screen, offset_x, offset_y, mouse_pos=None):
        """Render an interactive shipyard tooltip with dropdown menu"""
        if not self.has_shipyard():
            return
        
        font = pygame.font.Font(None, 16)
        small_font = pygame.font.Font(None, 14)
        tiny_font = pygame.font.Font(None, 12)
        
        # Base tooltip info
        lines = ["=== SHIPYARD ==="]
        
        # Show build queue with detailed progress and cancel buttons
        queue_buttons = []
        if self.build_queue:
            lines.append("Build Queue:")
            for i, ship in enumerate(self.build_queue):
                progress = ship['total_turns'] - ship['turns_remaining']
                total = ship['total_turns']
                percentage = int((progress / total) * 100) if total > 0 else 0
                
                if ship['turns_remaining'] > 0:
                    lines.append(f"  {i+1}. {ship['ship_type']} - {percentage}% ({ship['turns_remaining']} turns left)")
                else:
                    lines.append(f"  {i+1}. {ship['ship_type']} - READY TO DEPLOY!")
        else:
            lines.append("Build Queue: Empty")
        
        lines.append("")
        lines.append("Available Ships:")
        
        # Calculate tooltip dimensions
        max_width = max(font.size(line)[0] for line in lines) + 16
        tooltip_height = len(lines) * 18 + 12
        
        # Add space for cancel buttons if there's a queue
        cancel_button_height = 0
        if self.build_queue:
            cancel_button_height = len(self.build_queue) * 22 + 10
        
        # Add space for ship buttons
        available_ships = list(SHIP_TYPES.values())
        buttons_per_row = 2
        button_rows = (len(available_ships) + buttons_per_row - 1) // buttons_per_row
        button_height = 28
        button_spacing = 4
        
        dropdown_height = button_rows * (button_height + button_spacing) + 8
        total_height = tooltip_height + cancel_button_height + dropdown_height
        
        # Position tooltip
        tooltip_rect = pygame.Rect(offset_x, offset_y, max_width, total_height)
        
        # Keep tooltip on screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        if tooltip_rect.right > screen_width:
            tooltip_rect.x = screen_width - tooltip_rect.width - 5
        if tooltip_rect.bottom > screen_height:
            tooltip_rect.y = screen_height - tooltip_rect.height - 5
        if tooltip_rect.x < 0:
            tooltip_rect.x = 5
        if tooltip_rect.y < 0:
            tooltip_rect.y = 5
        
        # Draw tooltip background
        tooltip_surface = pygame.Surface((tooltip_rect.width, tooltip_rect.height))
        tooltip_surface.set_alpha(240)
        tooltip_surface.fill((25, 25, 35))
        screen.blit(tooltip_surface, (tooltip_rect.x, tooltip_rect.y))
        
        # Draw border
        pygame.draw.rect(screen, (80, 120, 200), tooltip_rect, 2)
        
        # Draw text
        y_offset = 8
        for line in lines:
            color = (255, 255, 255)
            if "SHIPYARD" in line:
                color = (100, 200, 255)
            elif "Build Queue" in line:
                color = (200, 200, 100)
            elif "READY TO DEPLOY" in line:
                color = (100, 255, 100)  # Green for completed ships
            elif "%" in line and "turns left" in line:
                color = (255, 200, 100)  # Orange for in-progress ships
            elif "Available Ships" in line:
                color = (150, 150, 255)
            
            text = font.render(line, True, color)
            screen.blit(text, (tooltip_rect.x + 8, tooltip_rect.y + y_offset))
            y_offset += 18
        
        # Draw cancel buttons for queue items
        if self.build_queue:
            cancel_y = tooltip_rect.y + tooltip_height
            for i, ship in enumerate(self.build_queue):
                cancel_button_rect = pygame.Rect(
                    tooltip_rect.x + max_width - 60, 
                    cancel_y + i * 22, 
                    50, 18
                )
                
                # Check if mouse is over cancel button
                mouse_over_cancel = mouse_pos and cancel_button_rect.collidepoint(mouse_pos)
                
                # Button color
                cancel_color = (120, 40, 40) if not mouse_over_cancel else (160, 60, 60)
                
                # Draw cancel button
                pygame.draw.rect(screen, cancel_color, cancel_button_rect)
                pygame.draw.rect(screen, (200, 100, 100), cancel_button_rect, 1)
                
                # Draw cancel text
                cancel_text = tiny_font.render("CANCEL", True, (255, 255, 255))
                text_rect = cancel_text.get_rect(center=cancel_button_rect.center)
                screen.blit(cancel_text, text_rect)
                
                queue_buttons.append(('cancel', i, cancel_button_rect))
        
        # Draw ship construction buttons
        button_y = tooltip_rect.y + tooltip_height + cancel_button_height
        button_width = (max_width - 24) // buttons_per_row
        
        ship_buttons = []
        for i, ship_type in enumerate(available_ships):
            row = i // buttons_per_row
            col = i % buttons_per_row
            
            button_x = tooltip_rect.x + 8 + col * (button_width + 8)
            button_rect = pygame.Rect(button_x, button_y + row * (button_height + button_spacing), 
                                    button_width, button_height)
            
            # Check if mouse is over button
            mouse_over = mouse_pos and button_rect.collidepoint(mouse_pos)
            
            # Button color based on affordability (would need player reference)
            button_color = (60, 60, 80) if not mouse_over else (80, 80, 120)
            text_color = (255, 255, 255)
            
            # Draw button
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, (120, 120, 140), button_rect, 1)
            
            # Draw ship name and cost
            ship_text = small_font.render(ship_type, True, text_color)
            cost_info = SHIP_COSTS[ship_type]
            cost_text = small_font.render(f"M:{cost_info.get('Minerals', 0)} E:{cost_info.get('Energy', 0)}", True, (200, 200, 200))
            time_text = small_font.render(f"{SHIP_BUILD_TIME[ship_type]} turns", True, (150, 150, 150))
            
            screen.blit(ship_text, (button_rect.x + 4, button_rect.y + 2))
            screen.blit(cost_text, (button_rect.x + 4, button_rect.y + 12))
            screen.blit(time_text, (button_rect.x + 4, button_rect.y + 22))
            
            ship_buttons.append(('build', ship_type, button_rect))
        
        # Combine all buttons for return
        all_buttons = queue_buttons + ship_buttons
        return all_buttons  # Return button info for click handling
    
    def handle_shipyard_click(self, mouse_pos, ship_buttons, player):
        """Handle clicks on shipyard buttons"""
        if not ship_buttons:
            return False, None
        
        for button_data in ship_buttons:
            if len(button_data) == 3:
                button_type, button_info, button_rect = button_data
                
                if button_rect.collidepoint(mouse_pos):
                    if button_type == 'build':
                        # Handle ship construction
                        ship_type = button_info
                        success, message = self.add_ship_to_queue(ship_type, player)
                        return True, message
                    
                    elif button_type == 'cancel':
                        # Handle construction cancellation
                        queue_index = button_info
                        success, message = self.cancel_ship_construction(queue_index, player)
                        return True, message
        
        return False, None 