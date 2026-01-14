import pygame
import random
import sys
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
GRID_SIZE = 8
CELL_SIZE = 70
GRID_OFFSET_X = 30
GRID_OFFSET_Y = 100
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BG_COLOR = (240, 240, 250)

# Candy colors
CANDY_COLORS = [
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
    (148, 0, 211),    # Purple
]

class Candy:
    def __init__(self, row: int, col: int, color_index: int):
        self.row = row
        self.col = col
        self.color_index = color_index
        self.x = col * CELL_SIZE + GRID_OFFSET_X
        self.y = row * CELL_SIZE + GRID_OFFSET_Y
        self.target_x = self.x
        self.target_y = self.y
        self.alpha = 255  # For fade animation

    def update_position(self, speed: float = 0.3):
        """Smooth animation to target position"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        self.x += dx * speed
        self.y += dy * speed

    def set_target(self, row: int, col: int):
        """Set target position for animation"""
        self.target_x = col * CELL_SIZE + GRID_OFFSET_X
        self.target_y = row * CELL_SIZE + GRID_OFFSET_Y

    def is_at_target(self) -> bool:
        """Check if candy reached target position"""
        return abs(self.x - self.target_x) < 1 and abs(self.y - self.target_y) < 1

    def draw(self, screen: pygame.Surface):
        """Draw the candy"""
        color = CANDY_COLORS[self.color_index]

        # Create surface with alpha for fade effect
        candy_surface = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10), pygame.SRCALPHA)
        candy_surface.fill((*color, self.alpha))

        # Draw circle
        pygame.draw.circle(
            candy_surface,
            (*color, self.alpha),
            (CELL_SIZE // 2 - 5, CELL_SIZE // 2 - 5),
            CELL_SIZE // 2 - 10
        )

        # Add highlight for 3D effect
        pygame.draw.circle(
            candy_surface,
            (255, 255, 255, self.alpha // 2),
            (CELL_SIZE // 2 - 5 - 10, CELL_SIZE // 2 - 5 - 10),
            CELL_SIZE // 6
        )

        screen.blit(candy_surface, (int(self.x) + 5, int(self.y) + 5))


class CandyCrush:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Candy Crush")
        self.clock = pygame.time.Clock()
        self.score = 0
        self.selected_candy: Optional[Tuple[int, int]] = None
        self.grid: List[List[Optional[Candy]]] = []
        self.animation_state = "idle"  # idle, swapping, disappearing, falling, swapping_back
        self.swap_candies: List[Candy] = []
        self.disappearing_candies: List[Candy] = []
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.game_over = False

        # Button rectangles for game over screen
        self.restart_button = pygame.Rect(0, 0, 180, 50)
        self.quit_button = pygame.Rect(0, 0, 180, 50)

        self.init_grid()

    def init_grid(self):
        """Initialize game grid with random candies"""
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # Keep generating random colors until no match is created
                while True:
                    color_index = random.randint(0, len(CANDY_COLORS) - 1)
                    self.grid[row][col] = Candy(row, col, color_index)

                    # Check if this creates a match
                    if not self.would_create_match(row, col):
                        break

    def reset_game(self):
        """Reset the game to initial state"""
        self.score = 0
        self.selected_candy = None
        self.animation_state = "idle"
        self.swap_candies = []
        self.disappearing_candies = []
        self.game_over = False
        self.init_grid()

    def would_create_match(self, row: int, col: int) -> bool:
        """Check if placing this candy would create a match"""
        if not self.grid[row][col]:
            return False

        color = self.grid[row][col].color_index

        # Check horizontal
        count = 1
        # Check left
        c = col - 1
        while c >= 0 and self.grid[row][c] and self.grid[row][c].color_index == color:
            count += 1
            c -= 1
        # Check right
        c = col + 1
        while c < GRID_SIZE and self.grid[row][c] and self.grid[row][c].color_index == color:
            count += 1
            c += 1
        if count >= 3:
            return True

        # Check vertical
        count = 1
        # Check up
        r = row - 1
        while r >= 0 and self.grid[r][col] and self.grid[r][col].color_index == color:
            count += 1
            r -= 1
        # Check down
        r = row + 1
        while r < GRID_SIZE and self.grid[r][col] and self.grid[r][col].color_index == color:
            count += 1
            r += 1
        if count >= 3:
            return True

        return False

    def find_matches(self) -> List[Tuple[int, int]]:
        """Find all matches on the board"""
        matches = set()

        # Check horizontal matches
        for row in range(GRID_SIZE):
            col = 0
            while col < GRID_SIZE:
                if not self.grid[row][col]:
                    col += 1
                    continue

                color = self.grid[row][col].color_index
                match_length = 1

                # Count consecutive candies of same color
                for c in range(col + 1, GRID_SIZE):
                    if self.grid[row][c] and self.grid[row][c].color_index == color:
                        match_length += 1
                    else:
                        break

                if match_length >= 3:
                    for c in range(col, col + match_length):
                        matches.add((row, c))

                col += 1

        # Check vertical matches
        for col in range(GRID_SIZE):
            row = 0
            while row < GRID_SIZE:
                if not self.grid[row][col]:
                    row += 1
                    continue

                color = self.grid[row][col].color_index
                match_length = 1

                # Count consecutive candies of same color
                for r in range(row + 1, GRID_SIZE):
                    if self.grid[r][col] and self.grid[r][col].color_index == color:
                        match_length += 1
                    else:
                        break

                if match_length >= 3:
                    for r in range(row, row + match_length):
                        matches.add((r, col))

                row += 1

        return list(matches)

    def has_valid_moves(self) -> bool:
        """Check if there are any valid moves left on the board"""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if not self.grid[row][col]:
                    continue

                # Try swapping with each adjacent cell
                for dr, dc in directions:
                    new_row, new_col = row + dr, col + dc

                    # Check if adjacent cell is valid
                    if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                        if not self.grid[new_row][new_col]:
                            continue

                        # Temporarily swap
                        self.grid[row][col], self.grid[new_row][new_col] = \
                            self.grid[new_row][new_col], self.grid[row][col]

                        # Update positions temporarily
                        self.grid[row][col].row, self.grid[row][col].col = row, col
                        self.grid[new_row][new_col].row, self.grid[new_row][new_col].col = new_row, new_col

                        # Check if this creates a match
                        matches = self.find_matches()

                        # Swap back
                        self.grid[row][col], self.grid[new_row][new_col] = \
                            self.grid[new_row][new_col], self.grid[row][col]

                        # Restore positions
                        self.grid[row][col].row, self.grid[row][col].col = row, col
                        self.grid[new_row][new_col].row, self.grid[new_row][new_col].col = new_row, new_col

                        if matches:
                            return True

        return False

    def swap_candies_at(self, pos1: Tuple[int, int], pos2: Tuple[int, int]):
        """Swap two candies and start swap animation"""
        row1, col1 = pos1
        row2, col2 = pos2

        candy1 = self.grid[row1][col1]
        candy2 = self.grid[row2][col2]

        # Swap in grid
        self.grid[row1][col1] = candy2
        self.grid[row2][col2] = candy1

        # Update candy positions
        candy1.row, candy1.col = row2, col2
        candy2.row, candy2.col = row1, col1

        # Set animation targets
        candy1.set_target(row2, col2)
        candy2.set_target(row1, col1)

        self.swap_candies = [candy1, candy2]
        self.animation_state = "swapping"

    def is_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """Check if two positions are adjacent"""
        row1, col1 = pos1
        row2, col2 = pos2
        return (abs(row1 - row2) == 1 and col1 == col2) or \
               (abs(col1 - col2) == 1 and row1 == row2)

    def handle_click(self, mouse_pos: Tuple[int, int]):
        """Handle mouse click on grid"""
        if self.animation_state != "idle":
            return

        x, y = mouse_pos
        col = (x - GRID_OFFSET_X) // CELL_SIZE
        row = (y - GRID_OFFSET_Y) // CELL_SIZE

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if self.selected_candy is None:
                self.selected_candy = (row, col)
            else:
                if self.selected_candy == (row, col):
                    self.selected_candy = None
                elif self.is_adjacent(self.selected_candy, (row, col)):
                    self.swap_candies_at(self.selected_candy, (row, col))
                    self.selected_candy = None
                else:
                    self.selected_candy = (row, col)

    def remove_matches(self):
        """Remove matched candies and start disappearing animation"""
        matches = self.find_matches()

        if matches:
            self.disappearing_candies = []
            for row, col in matches:
                if self.grid[row][col]:
                    self.disappearing_candies.append(self.grid[row][col])

            self.animation_state = "disappearing"
            self.score += len(matches) * 10
            return True
        return False

    def apply_gravity(self):
        """Make candies fall down and generate new ones"""
        self.animation_state = "falling"

        for col in range(GRID_SIZE):
            # Count empty spaces from bottom
            empty_count = 0
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col] is None:
                    empty_count += 1
                elif empty_count > 0:
                    # Move candy down
                    candy = self.grid[row][col]
                    self.grid[row + empty_count][col] = candy
                    self.grid[row][col] = None
                    candy.row = row + empty_count
                    candy.set_target(row + empty_count, col)

            # Generate new candies at top
            for i in range(empty_count):
                row = i
                color_index = random.randint(0, len(CANDY_COLORS) - 1)
                candy = Candy(row, col, color_index)
                candy.y = -CELL_SIZE * (empty_count - i)
                candy.target_y = row * CELL_SIZE + GRID_OFFSET_Y
                self.grid[row][col] = candy

    def update(self):
        """Update game state and animations"""
        if self.animation_state == "swapping":
            all_at_target = all(candy.is_at_target() for candy in self.swap_candies)

            if not all_at_target:
                for candy in self.swap_candies:
                    candy.update_position(0.3)
            else:
                # Check if swap created matches
                if not self.remove_matches():
                    # Invalid swap, swap back manually
                    candy1, candy2 = self.swap_candies[0], self.swap_candies[1]
                    row1, col1 = candy1.row, candy1.col
                    row2, col2 = candy2.row, candy2.col

                    # Swap back in grid
                    self.grid[row1][col1] = candy2
                    self.grid[row2][col2] = candy1

                    # Update positions (swap them back)
                    candy1.row, candy1.col = row2, col2
                    candy2.row, candy2.col = row1, col1

                    # Set targets for swap back animation
                    candy1.set_target(row2, col2)
                    candy2.set_target(row1, col1)

                    self.animation_state = "swapping_back"
                # If matches found, remove_matches() already set state to "disappearing"

        elif self.animation_state == "swapping_back":
            all_at_target = all(candy.is_at_target() for candy in self.swap_candies)

            if not all_at_target:
                for candy in self.swap_candies:
                    candy.update_position(0.3)
            else:
                self.animation_state = "idle"
                # Check if there are any valid moves left
                if not self.game_over and not self.has_valid_moves():
                    self.game_over = True

        elif self.animation_state == "disappearing":
            all_disappeared = True
            for candy in self.disappearing_candies:
                if candy.alpha > 0:
                    candy.alpha = max(0, candy.alpha - 15)
                    all_disappeared = False

            if all_disappeared:
                # Remove candies from grid
                for candy in self.disappearing_candies:
                    if self.grid[candy.row][candy.col] == candy:
                        self.grid[candy.row][candy.col] = None

                self.disappearing_candies = []
                self.apply_gravity()

        elif self.animation_state == "falling":
            all_at_target = True
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col]:
                        if not self.grid[row][col].is_at_target():
                            self.grid[row][col].update_position(0.25)
                            all_at_target = False

            if all_at_target:
                # Check for new matches after falling
                if not self.remove_matches():
                    self.animation_state = "idle"
                    # Check if there are any valid moves left
                    if not self.game_over and not self.has_valid_moves():
                        self.game_over = True

    def draw_button(self, rect: pygame.Rect, text: str, mouse_pos: Tuple[int, int], color_type: str = "green"):
        """Draw a button with hover effect"""
        is_hovered = rect.collidepoint(mouse_pos)

        # Button color based on hover state and type
        if color_type == "red":
            button_color = (200, 100, 100) if is_hovered else (150, 70, 70)
            border_color = (255, 150, 150) if is_hovered else (200, 100, 100)
        else:  # green
            button_color = (100, 200, 100) if is_hovered else (70, 150, 70)
            border_color = (150, 255, 150) if is_hovered else (100, 200, 100)

        # Draw button background
        pygame.draw.rect(self.screen, button_color, rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=10)

        # Draw text
        button_text = self.small_font.render(text, True, WHITE)
        text_rect = button_text.get_rect(center=rect.center)
        self.screen.blit(button_text, text_rect)

    def draw(self):
        """Draw the game"""
        self.screen.fill(BG_COLOR)

        # Draw title
        title = self.font.render("Candy Crush", True, BLACK)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))

        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (20, 60))

        # Draw grid background
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = col * CELL_SIZE + GRID_OFFSET_X
                y = row * CELL_SIZE + GRID_OFFSET_Y
                pygame.draw.rect(self.screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)

        # Highlight selected candy
        if self.selected_candy and self.animation_state == "idle":
            row, col = self.selected_candy
            x = col * CELL_SIZE + GRID_OFFSET_X
            y = row * CELL_SIZE + GRID_OFFSET_Y
            pygame.draw.rect(self.screen, (255, 215, 0), (x, y, CELL_SIZE, CELL_SIZE), 4)

        # Draw candies
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].draw(self.screen)

        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # Game over text
            game_over_text = self.font.render("GAME OVER!", True, WHITE)
            self.screen.blit(
                game_over_text,
                (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 80)
            )

            # No moves left text
            no_moves_text = self.small_font.render("No more valid moves!", True, WHITE)
            self.screen.blit(
                no_moves_text,
                (WINDOW_WIDTH // 2 - no_moves_text.get_width() // 2, WINDOW_HEIGHT // 2 - 20)
            )

            # Final score
            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 215, 0))
            self.screen.blit(
                final_score_text,
                (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, WINDOW_HEIGHT // 2 + 30)
            )

            # Position buttons
            button_y = WINDOW_HEIGHT // 2 + 110
            button_spacing = 20
            total_button_width = self.restart_button.width * 2 + button_spacing
            start_x = (WINDOW_WIDTH - total_button_width) // 2

            self.restart_button.x = start_x
            self.restart_button.y = button_y
            self.quit_button.x = start_x + self.restart_button.width + button_spacing
            self.quit_button.y = button_y

            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()

            # Draw buttons
            self.draw_button(self.restart_button, "Restart", mouse_pos, "green")
            self.draw_button(self.quit_button, "Quit", mouse_pos, "red")

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.game_over:
                        # Check if buttons were clicked
                        if self.restart_button.collidepoint(mouse_pos):
                            self.reset_game()
                        elif self.quit_button.collidepoint(mouse_pos):
                            running = False
                    else:
                        self.handle_click(mouse_pos)
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = CandyCrush()
    game.run()
