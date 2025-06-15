import pygame
from .constants import *

class MainMenu:
    def __init__(self):
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 48)
        self.font_subtitle = pygame.font.Font(None, 32)
        
        # Menu state
        self.selected_option = 0
        self.options = ["New Game", "vs AI", "Tactical Combat", "Dev Playground", "Exit"]
        
        # Button rects (will be updated in update_screen_size)
        self.button_rects = []
        self.update_screen_size((WINDOW_WIDTH, WINDOW_HEIGHT))
        
    def update_screen_size(self, screen_size):
        """Update button positions when screen size changes"""
        width, height = screen_size
        
        # Calculate button positions
        button_width = 300
        button_height = 60
        button_spacing = 20
        
        # Ensure buttons start below the subtitle with proper spacing
        subtitle_bottom = height // 4 + 80 + 40  # subtitle position + font height + spacing
        buttons_total_height = len(self.options) * (button_height + button_spacing) - button_spacing
        start_y = max(subtitle_bottom, height // 2 - buttons_total_height // 2)
        
        self.button_rects = []
        for i, option in enumerate(self.options):
            x = width // 2 - button_width // 2
            y = start_y + i * (button_height + button_spacing)
            self.button_rects.append(pygame.Rect(x, y, button_width, button_height))
    
    def handle_event(self, event):
        """Handle menu events. Returns the selected option or None"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected_option]
            elif event.key == pygame.K_ESCAPE:
                return "Exit"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for i, rect in enumerate(self.button_rects):
                    if rect.collidepoint(event.pos):
                        return self.options[i]
        
        elif event.type == pygame.MOUSEMOTION:
            # Update selected option based on mouse position
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(event.pos):
                    self.selected_option = i
                    break
        
        return None
    
    def render(self, screen):
        """Render the main menu"""
        screen.fill((10, 10, 30))  # Dark blue background
        
        width, height = screen.get_size()
        
        # Draw title
        title_text = self.font_title.render("Galactic Conquest", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 4))
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.font_subtitle.render("4X Space Strategy Game", True, (180, 180, 180))
        subtitle_rect = subtitle_text.get_rect(center=(width // 2, height // 4 + 80))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw menu options
        for i, (option, rect) in enumerate(zip(self.options, self.button_rects)):
            # Button background
            if i == self.selected_option:
                color = (60, 60, 120)  # Highlighted
                border_color = (100, 100, 200)
            else:
                color = (40, 40, 80)   # Normal
                border_color = (80, 80, 120)
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, border_color, rect, 3)
            
            # Button text
            text_color = (255, 255, 255) if i == self.selected_option else (200, 200, 200)
            text = self.font_button.render(option, True, text_color)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        
        # Draw controls hint
        controls_text = self.font_subtitle.render("Use arrow keys or mouse to navigate, Enter/Click to select", True, (120, 120, 120))
        controls_rect = controls_text.get_rect(center=(width // 2, height - 50))
        screen.blit(controls_text, controls_rect) 