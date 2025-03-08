import pygame
import random
from sys import exit
from twilio.rest import Client

class Phone:
    def __init__(self):
        # Initialize pygame and create phone window
        pygame.init()

        # twilio account info
        account_sid = ''
        auth_token = ''
        client = Client(account_sid, auth_token)

        self.screen = pygame.display.set_mode((277, 638))
        pygame.display.set_caption("Nokia Bounce")
        self.clock = pygame.time.Clock()

        # Load Nokia phone image (make sure the file exists)
        self.phoneImage = pygame.image.load("Images/nokia.PNG")

        # Font for buttons and text
        font = pygame.font.Font('freesansbold.ttf', 15)
        self.font = font  # Save font for later use

        # Create and label keypad buttons (simulate 12 buttons: 1,2,3,...,* ,0,#)
        self.buttonColors = []
        for i in range(12):
            surface = pygame.Surface((60, 40))
            surface.fill((174, 174, 174))
            self.buttonColors.append(surface)

        self.textNum = []
        for i in range(9):
            self.textNum.append(font.render(str(i + 1), True, 'black'))
        self.textNum.append(font.render("*", True, 'black'))
        self.textNum.append(font.render("0", True, 'black'))
        self.textNum.append(font.render("+", True, 'black'))

        # Define keypad rectangles for touchscreen events
        self.keypad_rects = [
            pygame.Rect(30, 410, 60, 40),   # Button 1
            pygame.Rect(110, 430, 60, 40),  # Button 2
            pygame.Rect(185, 410, 60, 40),  # Button 3
            pygame.Rect(35, 460, 60, 40),   # Button 4
            pygame.Rect(110, 470, 60, 40),  # Button 5
            pygame.Rect(185, 460, 60, 40),  # Button 6
            pygame.Rect(35, 500, 60, 40),   # Button 7
            pygame.Rect(105, 510, 60, 40),  # Button 8
            pygame.Rect(185, 500, 60, 40),  # Button 9
            pygame.Rect(35, 550, 60, 40),   # Button *
            pygame.Rect(110, 560, 60, 40),  # Button 0
            pygame.Rect(180, 550, 60, 40)   # Button #
        ]

        # Control flags for keypad/WASD input
        self.phone_left = False
        self.phone_right = False
        self.phone_jump = False
        self.phone_down = False  # Optional for downward action

        # --- GAME VARIABLES (classic Bounce) ---
        self.GAME_WIDTH, self.GAME_HEIGHT = 500, 400
        self.gameSurface = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))

        # Game constants
        self.ground_height = self.GAME_HEIGHT - 40
        self.BALL_RADIUS = 15
        self.GRAVITY = 0.5
        self.JUMP_STRENGTH = -15
        self.ACCELERATION = 0.5
        self.FRICTION = 0.9
        self.SPEED_LIMIT = 7
        self.FINISH_LINE = 1000

        # Colors for game (adjust as needed)
        self.GREEN = (129, 175, 12)
        self.RED_BLOCK = (67, 82, 61)
        self.RED_BLOCK_DARK = (67, 82, 61)
        self.RED_BALL = (67, 82, 61)
        self.GOLD = (67, 82, 61)
        self.BLACK = (67, 82, 61)
        self.WHITE = (255, 255, 255)

        # Game state: ball and world variables (world coordinates)
        self.ball_x = 100
        self.ball_y = self.ground_height - self.BALL_RADIUS
        self.ball_velocity_y = 0
        self.ball_velocity_x = 0
        self.on_ground = True
        self.score = 0

        self.platforms = [
            (200, 300, 100, 10),
            (400, 250, 100, 10),
            (600, 200, 100, 10)
        ]
        self.original_rings = [
            (250, 270),
            (450, 220),
            (650, 170)
        ]
        self.rings = list(self.original_rings)
        self.spikes = [
            (350, self.ground_height - 20),
            (550, self.ground_height - 20)
        ]

        self.camera_x = 0
        self.running = True
        self.game_over = False
        self.level_complete = False

        # Define where on the phone image the game will be displayed.
        self.game_display_rect = pygame.Rect(25, 70, 225, 250)

        # text input box
        self.input_rect = pygame.Rect(35, 150, 200, 200)
        self.user_text = ''
        self.color = pygame.Color(self.GREEN)
        self.base_font = pygame.font.Font(None, 20)
        self.isTexting = False
        self.messageTitle = self.base_font.render('Send Message:', True, self.BLACK)


        #Main Menu Screen
        self.menuWindow = pygame.Rect(35, 150, 200, 200)
        self.menuTitle = self.base_font.render('Nokia Menu', True, self.BLACK)
        self.menuOption1 = self.base_font.render('Bounce Game: Press 1', True, self.BLACK)
        self.menuOption2 = self.base_font.render('Messaging: Press 2', True, self.BLACK)
        self.isMenu = True

    def update_game(self):
        """Update the game state using classic Bounce logic with controls."""
        keys = pygame.key.get_pressed()
        # Horizontal movement via controls (either keypad flags or WASD)
        if self.phone_left or keys[pygame.K_a]:
            self.ball_velocity_x -= self.ACCELERATION
        elif self.phone_right or keys[pygame.K_d]:
            self.ball_velocity_x += self.ACCELERATION
        else:
            self.ball_velocity_x *= self.FRICTION

        # Jump control via keypad or WASD/SPACE
        if (self.phone_jump or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.ball_velocity_y = self.JUMP_STRENGTH
            self.on_ground = False

        # Apply gravity
        self.ball_velocity_y += self.GRAVITY

        # Apply velocity
        self.ball_x += self.ball_velocity_x
        self.ball_y += self.ball_velocity_y

        # Clamp horizontal and vertical positions
        if self.ball_x < self.BALL_RADIUS:
            self.ball_x = self.BALL_RADIUS
            self.ball_velocity_x = 0
        if self.ball_x > self.FINISH_LINE - self.BALL_RADIUS:
            self.ball_x = self.FINISH_LINE - self.BALL_RADIUS
            self.ball_velocity_x = 0
        if self.ball_y < self.BALL_RADIUS:
            self.ball_y = self.BALL_RADIUS
            self.ball_velocity_y = 0

        # Ground collision
        if self.ball_y > self.ground_height - self.BALL_RADIUS:
            self.ball_y = self.ground_height - self.BALL_RADIUS
            self.ball_velocity_y = 0
            self.on_ground = True

        # Platform vertical collision (only if falling onto platform)
        for plat in self.platforms:
            px, py, pw, ph = plat
            if px < self.ball_x < px + pw:
                if py - self.BALL_RADIUS < self.ball_y < py + ph and self.ball_velocity_y > 0:
                    self.ball_y = py - self.BALL_RADIUS
                    self.ball_velocity_y = 0
                    self.on_ground = True
                    break

        # Horizontal collision with platforms to prevent sliding through
        ball_rect = pygame.Rect(self.ball_x - self.BALL_RADIUS, self.ball_y - self.BALL_RADIUS,
                                2 * self.BALL_RADIUS, 2 * self.BALL_RADIUS)
        for plat in self.platforms:
            px, py, pw, ph = plat
            platform_rect = pygame.Rect(px, py, pw, ph)
            if ball_rect.colliderect(platform_rect):
                if self.ball_y > py + 5:  # Adjust threshold as needed
                    if self.ball_velocity_x > 0:
                        self.ball_x = platform_rect.left - self.BALL_RADIUS
                        self.ball_velocity_x = 0
                    elif self.ball_velocity_x < 0:
                        self.ball_x = platform_rect.right + self.BALL_RADIUS
                        self.ball_velocity_x = 0
                    ball_rect = pygame.Rect(self.ball_x - self.BALL_RADIUS, self.ball_y - self.BALL_RADIUS,
                                            2 * self.BALL_RADIUS, 2 * self.BALL_RADIUS)

        # Collision with rings (collectibles)
        collected_rings = []
        for rx, ry in self.rings:
            if abs(rx - self.ball_x) < self.BALL_RADIUS and abs(ry - self.ball_y) < self.BALL_RADIUS:
                self.score += 100
            else:
                collected_rings.append((rx, ry))
        self.rings = collected_rings

        # Collision with spikes → game over
        for spike in self.spikes:
            if (spike[0] < self.ball_x < spike[0] + 20 and
                spike[1] - 20 < self.ball_y < spike[1]):
                self.game_over = True
                break

        # Level complete if ball reaches finish line
        if self.ball_x >= self.FINISH_LINE - self.BALL_RADIUS:
            self.level_complete = True

        # Camera follows the ball (but stops at finish line)
        if self.ball_x > self.GAME_WIDTH // 2:
            self.camera_x = min(self.ball_x - self.GAME_WIDTH // 2, self.FINISH_LINE)

    def draw_game(self):
        """Draw the game world onto the game surface."""
        self.gameSurface.fill(self.GREEN)
        for i in range(0, self.FINISH_LINE + 1000, 50):
            rect = pygame.Rect(i - self.camera_x, self.ground_height, 50, 40)
            pygame.draw.rect(self.gameSurface, self.RED_BLOCK, rect)
            pygame.draw.rect(self.gameSurface, self.RED_BLOCK_DARK, rect, 2)
        for plat in self.platforms:
            px, py, pw, ph = plat
            rect = pygame.Rect(px - self.camera_x, py, pw, ph)
            pygame.draw.rect(self.gameSurface, self.RED_BLOCK, rect)
            pygame.draw.rect(self.gameSurface, self.RED_BLOCK_DARK, rect, 2)
        for rx, ry in self.rings:
            pygame.draw.circle(self.gameSurface, self.GOLD, (rx - self.camera_x, ry), 10, 3)
        for spike in self.spikes:
            points = [
                (spike[0] - self.camera_x, spike[1]),
                (spike[0] - self.camera_x + 10, spike[1] - 20),
                (spike[0] - self.camera_x + 20, spike[1])
            ]
            pygame.draw.polygon(self.gameSurface, self.BLACK, points)
        pygame.draw.line(self.gameSurface, self.BLACK,
                         (self.FINISH_LINE - self.camera_x, 0),
                         (self.FINISH_LINE - self.camera_x, self.GAME_HEIGHT), 2)
        pygame.draw.circle(self.gameSurface, self.RED_BALL,
                           (int(self.ball_x - self.camera_x), int(self.ball_y)),
                           self.BALL_RADIUS)

    def draw_end_screen(self):
        """Draw the end screen (game over or level complete) on the game surface."""
        self.gameSurface.fill(self.GREEN)
        title = "LEVEL COMPLETE!" if self.level_complete else "GAME OVER!"
        title_text = self.font.render(title, True, self.BLACK)
        score_text = self.font.render(f"Score: {self.score}", True, self.BLACK)
        instr_text = self.font.render("Press R to Restart or Q to Quit", True, self.BLACK)
        self.gameSurface.blit(title_text,
                              title_text.get_rect(center=(self.GAME_WIDTH//2, self.GAME_HEIGHT//3 - 40)))
        self.gameSurface.blit(score_text,
                              score_text.get_rect(center=(self.GAME_WIDTH//2, self.GAME_HEIGHT//2)))
        self.gameSurface.blit(instr_text,
                              instr_text.get_rect(center=(self.GAME_WIDTH//2, self.GAME_HEIGHT//3 + 40)))

    def reset_game(self):
        """Reset game state variables."""
        self.ball_x = 100
        self.ball_y = self.ground_height - self.BALL_RADIUS
        self.ball_velocity_y = 0
        self.ball_velocity_x = 0
        self.on_ground = True
        self.camera_x = 0
        self.score = 0
        self.rings = list(self.original_rings)
        self.game_over = False
        self.level_complete = False

    def run(self):
        """Main loop: update game, draw UI, and handle keyboard/touch input."""
        while True:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # Handle keyboard input
                if event.type == pygame.KEYDOWN:
                    # WhatsApp texting
                    if self.isTexting:
                        if event.key == pygame.K_KP_ENTER:
                            account_sid = ''
                            auth_token = ''
                            client = Client(account_sid, auth_token)
                            message = client.messages.create(from_='', body=self.user_text,
                                                             to='')
                            print(message.sid)
                            self.user_text = ''
                        elif event.key == pygame.K_BACKSPACE:
                            self.user_text = self.user_text[:-1]
                        else:
                            self.user_text += event.unicode

                    if not (self.game_over or self.level_complete):
                        if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_KP8):
                            if self.on_ground:
                                self.ball_velocity_y = self.JUMP_STRENGTH
                                self.on_ground = False
                                self.phone_jump = True
                        if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_KP4):
                            self.phone_left = True
                        if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_KP6):
                            self.phone_right = True
                        if event.key in (pygame.K_s, pygame.K_KP5):
                            self.phone_down = True
                    if self.game_over or self.level_complete:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            exit()

                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_KP4):
                        self.phone_left = False
                    if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_KP6):
                        self.phone_right = False
                    if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_KP8):
                        self.phone_jump = False
                    if event.key in (pygame.K_s, pygame.K_KP5):
                        self.phone_down = False

                # Handle touchscreen events (FINGERDOWN/FINGERUP)
                if event.type == pygame.FINGERDOWN:
                    touch_x = event.x * self.screen.get_width()
                    touch_y = event.y * self.screen.get_height()
                    for idx, rect in enumerate(self.keypad_rects):
                        if rect.collidepoint(touch_x, touch_y):
                            self.buttonColors[idx].fill((117, 117, 117))
                            if idx == 3:  # Button 4: left
                                self.phone_left = True
                            elif idx == 7:  # Button 8: jump
                                if self.on_ground:
                                    self.ball_velocity_y = self.JUMP_STRENGTH
                                    self.on_ground = False
                                self.phone_jump = True
                            elif idx == 5:  # Button 6: right
                                self.phone_right = True

                if event.type == pygame.FINGERUP:
                    touch_x = event.x * self.screen.get_width()
                    touch_y = event.y * self.screen.get_height()
                    for idx, rect in enumerate(self.keypad_rects):
                        if rect.collidepoint(touch_x, touch_y):
                            self.buttonColors[idx].fill((174, 174, 174))
                            if idx == 3:  # Button 4: left
                                self.phone_left = False
                            elif idx == 7:  # Button 8: jump
                                self.phone_jump = False
                            elif idx == 5:  # Button 6: right
                                self.phone_right = False

                # Handle keypad button color change on key press/release (numeric keys)
                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_KP1:
                            self.buttonColors[0].fill((117, 117, 117))
                            if self.isMenu:
                                self.isMenu = False  # Exit menu and start Bounce game
                        case pygame.K_KP2:
                            self.buttonColors[1].fill((117, 117, 117))
                            if self.isMenu:
                                self.isMenu = False
                                self.isTexting = True
                        case pygame.K_KP3:
                            self.buttonColors[2].fill((117, 117, 117))
                        case pygame.K_KP4:
                            self.buttonColors[3].fill((117, 117, 117))
                        case pygame.K_KP5:
                            self.buttonColors[4].fill((117, 117, 117))
                        case pygame.K_KP6:
                            self.buttonColors[5].fill((117, 117, 117))
                        case pygame.K_KP7:
                            self.buttonColors[6].fill((117, 117, 117))
                        case pygame.K_KP8:
                            self.buttonColors[7].fill((117, 117, 117))
                        case pygame.K_KP9:
                            self.buttonColors[8].fill((117, 117, 117))
                        case pygame.K_KP_MULTIPLY:
                            self.buttonColors[9].fill((117, 117, 117))
                            if not self.isMenu:
                                self.isMenu = True
                                self.isTexting = False
                        case pygame.K_KP_0:
                            self.buttonColors[10].fill((117, 117, 117))
                        case pygame.K_HASH:
                            self.buttonColors[11].fill((117, 117, 117))
                if event.type == pygame.KEYUP:
                    match event.key:
                        case pygame.K_KP1:
                            self.buttonColors[0].fill((174, 174, 174))
                        case pygame.K_KP2:
                            self.buttonColors[1].fill((174, 174, 174))
                        case pygame.K_KP3:
                            self.buttonColors[2].fill((174, 174, 174))
                        case pygame.K_KP4:
                            self.buttonColors[3].fill((174, 174, 174))
                        case pygame.K_KP5:
                            self.buttonColors[4].fill((174, 174, 174))
                        case pygame.K_KP6:
                            self.buttonColors[5].fill((174, 174, 174))
                        case pygame.K_KP7:
                            self.buttonColors[6].fill((174, 174, 174))
                        case pygame.K_KP8:
                            self.buttonColors[7].fill((174, 174, 174))
                        case pygame.K_KP9:
                            self.buttonColors[8].fill((174, 174, 174))
                        case pygame.K_KP_MULTIPLY:
                            self.buttonColors[9].fill((174, 174, 174))
                        case pygame.K_KP_0:
                            self.buttonColors[10].fill((174, 174, 174))
                        case pygame.K_HASH:
                            self.buttonColors[11].fill((174, 174, 174))

            # Only update and draw the game when not in the menu
            if not self.isMenu:
                if not (self.game_over or self.level_complete):
                    self.update_game()

                if not (self.game_over or self.level_complete):
                    self.draw_game()
                else:
                    self.draw_end_screen()
            else:
                # Static background when in the menu
                self.gameSurface.fill(self.GREEN)

            scaled_game = pygame.transform.scale(self.gameSurface,
                                                   (self.game_display_rect.width, self.game_display_rect.height))
            self.screen.blit(scaled_game, (self.game_display_rect.x, self.game_display_rect.y))

            # Draw keypad buttons
            self.screen.blit(self.buttonColors[0], (30, 410))
            self.screen.blit(self.buttonColors[1], (110, 430))
            self.screen.blit(self.buttonColors[2], (185, 410))
            self.screen.blit(self.buttonColors[3], (35, 460))
            self.screen.blit(self.buttonColors[4], (110, 470))
            self.screen.blit(self.buttonColors[5], (185, 460))
            self.screen.blit(self.buttonColors[6], (35, 500))
            self.screen.blit(self.buttonColors[7], (105, 510))
            self.screen.blit(self.buttonColors[8], (185, 500))
            self.screen.blit(self.buttonColors[9], (35, 550))
            self.screen.blit(self.buttonColors[10], (110, 560))
            self.screen.blit(self.buttonColors[11], (180, 550))

            self.buttonColors[0].blit(self.textNum[0], (10, 12))
            self.buttonColors[1].blit(self.textNum[1], (22, 8))
            self.buttonColors[2].blit(self.textNum[2], (38, 14))
            self.buttonColors[3].blit(self.textNum[3], (10, 6))
            self.buttonColors[4].blit(self.textNum[4], (22, 14))
            self.buttonColors[5].blit(self.textNum[5], (38, 8))
            self.buttonColors[6].blit(self.textNum[6], (12, 10))
            self.buttonColors[7].blit(self.textNum[7], (26, 16))
            self.buttonColors[8].blit(self.textNum[8], (36, 12))
            self.buttonColors[9].blit(self.textNum[9], (16, 12))
            self.buttonColors[10].blit(self.textNum[10], (20, 12))
            self.buttonColors[11].blit(self.textNum[11], (34, 12))

            # Draw textbox if texting
            if self.isTexting:
                pygame.draw.rect(self.screen, self.color, self.input_rect)
                text_surface = self.base_font.render(self.user_text, True, self.BLACK)
                self.screen.blit(self.messageTitle, (self.input_rect.x + 15, self.input_rect.y + 30))
                self.screen.blit(text_surface, (self.input_rect.x + 15, self.input_rect.y + 60))

            # Draw menu overlay when in menu mode
            if self.isMenu:
                pygame.draw.rect(self.screen, self.color, self.menuWindow)
                self.screen.blit(self.menuTitle, (self.menuWindow.x + 15, self.menuWindow.y + 30))
                self.screen.blit(self.menuOption1, (self.menuWindow.x + 15, self.menuWindow.y + 100))
                self.screen.blit(self.menuOption2, (self.menuWindow.x + 15, self.menuWindow.y + 130))

            self.screen.blit(self.phoneImage, (0, 0))
            pygame.display.update()



if __name__ == "__main__":
    phone = Phone()
    phone.run()
