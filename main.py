import pygame
import sys
from game.game_state import GameState
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
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
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.game_state.end_turn()
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    self.toggle_fullscreen()
                elif event.key == pygame.K_F3:
                    self.show_fps = not self.show_fps  # Toggle FPS display with F3
            self.game_state.handle_event(event)

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
        self.game_state.update_screen_size(self.screen.get_size())

    def update(self):
        self.game_state.update()

    def render(self):
        self.screen.fill((0, 0, 0))  # Black background
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