import pygame
import sys
from game.game_state import GameState
from game.dev_playground import DevPlayground
from game.main_menu import MainMenu
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE
from tactical_combat import run_tactical_combat

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Game states
        self.main_menu = MainMenu()
        self.game_state = None
        self.current_state = "MAIN_MENU"  # Can be "MAIN_MENU", "GAME", or "DEV_PLAYGROUND"
        
        self.running = True
        self.fullscreen = False
        self.windowed_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.show_fps = True  # Toggle FPS display
        self.fps_font = pygame.font.Font(None, 36)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    self.toggle_fullscreen()
                elif event.key == pygame.K_F3:
                    self.show_fps = not self.show_fps  # Toggle FPS display with F3
                elif event.key == pygame.K_ESCAPE:
                    if self.current_state == "MAIN_MENU":
                        self.running = False
                    else:
                        # Return to main menu from game states
                        self.current_state = "MAIN_MENU"
                        self.game_state = None
                elif event.key == pygame.K_SPACE and self.current_state in ["GAME", "DEV_PLAYGROUND"]:
                    if self.game_state:
                        self.game_state.end_turn()
            
            # Handle state-specific events
            if self.current_state == "MAIN_MENU":
                result = self.main_menu.handle_event(event)
                if result:
                    self.handle_menu_selection(result)
            elif self.current_state in ["GAME", "DEV_PLAYGROUND"] and self.game_state:
                result = self.game_state.handle_event(event)
                if result == "MAIN_MENU":
                    self.current_state = "MAIN_MENU"
                    self.game_state = None

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Switch to fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Switch back to windowed mode
            self.screen = pygame.display.set_mode(self.windowed_size)
        
        # Update the game state with new screen dimensions
        if self.game_state:
            self.game_state.update_screen_size(self.screen.get_size())
        self.main_menu.update_screen_size(self.screen.get_size())

    def handle_menu_selection(self, selection):
        """Handle main menu selections"""
        if selection == "New Game":
            self.current_state = "GAME"
            self.game_state = GameState()
            print("Starting new game...")
        elif selection == "vs AI":
            self.current_state = "GAME"
            self.game_state = GameState(ai_players=[1])  # Player 2 is AI
            print("Starting game vs AI...")
        elif selection == "Tactical Combat":
            print("Starting tactical combat demo...")
            # Run tactical combat in a separate function
            run_tactical_combat()
            # After tactical combat ends, we're back to the main menu
        elif selection == "Dev Playground":
            self.current_state = "DEV_PLAYGROUND"
            self.game_state = DevPlayground()
            print("Entering dev playground...")
        elif selection == "Exit":
            self.running = False

    def update(self):
        if self.current_state in ["GAME", "DEV_PLAYGROUND"] and self.game_state:
            self.game_state.update()

    def render(self):
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.current_state == "MAIN_MENU":
            self.main_menu.render(self.screen)
        elif self.current_state in ["GAME", "DEV_PLAYGROUND"] and self.game_state:
            self.game_state.render(self.screen)
        
        # Draw FPS counter LAST so it appears above everything else
        if self.show_fps:
            fps = self.clock.get_fps()
            fps_text = self.fps_font.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
            # Add a small black background for better visibility
            fps_bg = pygame.Rect(8, 8, fps_text.get_width() + 4, fps_text.get_height() + 4)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), fps_bg)
            self.screen.blit(fps_text, (10, 10))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 