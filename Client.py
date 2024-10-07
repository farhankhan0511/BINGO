import pygame
import sys
from Network import Network
import pickle
from Game import game 

# Initialize Pygame
pygame.init()


# Screen size and settings
screen_width, screen_height = 500, 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.scrap.init()
pygame.display.set_caption("Dynamic Box Grid")

font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 36)
wintext = pygame.font.SysFont("comicsans", 52)

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
black = (0, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
gray = (128, 128, 128)

# Grid settings
rows, cols = 5, 5
box_size = 500 // cols

# Placeholder grid to indicate where boxes could go
placeholders = [[pygame.Rect( x * box_size,  y * box_size, box_size, box_size) for x in range(cols)] for y in range(rows)]

# Track box positions

# Draw the placeholders and boxes
def draw_board(player,box_positions):
    for row in range(rows):
        for col in range(cols):
            if box_positions[row][col] is None:
                pygame.draw.rect(screen, blue, placeholders[row][col], 2)  # Draw empty placeholder
            else:
                player.board[row][col].draw(screen, placeholders[row][col])  # Pass the correct rect to draw
def edit(player, network,game):
    running = True
    clock = pygame.time.Clock()
    ready_button_rect = pygame.Rect(150, 468, 170, 50)  # Position for the "Ready" button
    button_color = (0, 128, 0)  # Green color for the button
    edit_complete = False  # Track if the player has completed their edits
    box_positions = [[None for _ in range(cols)] for _ in range(rows)]
    while running:
        # print(f"Player ID: {player.id}")  # Debugging to show player ID on every frame
        clock.tick(60)
        screen.fill(WHITE)  # Fill the background with white
        # print(player.board)
            # print(g.players[player.id].getboard())
        mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
        
        # Check if all boxes are filled (edit is complete)
        edit_complete = all(all(cell is not None for cell in row) for row in box_positions)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Proper quit handling
                running = False

            # Check for mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_row = mouse_pos[1] // box_size
                clicked_col = mouse_pos[0] // box_size

                # Check if the click is within the game grid and edit is still allowed
                if not edit_complete and clicked_row < rows and clicked_col < cols and box_positions[clicked_row][clicked_col] is None:
                    box_positions[clicked_row][clicked_col] = player.editbox(clicked_row, clicked_col)
                    box_positions[clicked_row][clicked_col].assign()
                    box_positions[clicked_row][clicked_col].draw(screen, placeholders[clicked_row][clicked_col])
                    player.board=box_positions

                # Check if the "Ready" button was clicked only if all boxes are filled
                if edit_complete and ready_button_rect.collidepoint(mouse_pos):
                    player.pready = True  # Mark the player as ready
                    
                    player.board=box_positions
                    network.send(("updateplayer",pickle.dumps(player))) 
                    
                     # Notify the server about readiness
                    print("Player marked as ready, waiting for other players...")
                    run=True
                    while run:
                        game=network.send("get")
                        if game.gameplayon():
                            run=False
                            running=False
                            gameplay(player,network,game)

        # Draw the grid with placeholders and boxes
        draw_board(player,box_positions)

        # Draw the "Ready" button (only active if edit is complete)
        if edit_complete:
            pygame.draw.rect(screen, button_color, ready_button_rect)
            ready_text = small_font.render("Ready", True, WHITE)
        else:
            pygame.draw.rect(screen, (128, 128, 128), ready_button_rect)  # Inactive button
            ready_text = small_font.render("Complete All Edits First", True, WHITE)

        screen.blit(ready_text, (ready_button_rect.x + 30, ready_button_rect.y + 10))

        # Display a message when all edits are done but waiting for the player to click "Ready"
        if edit_complete:
            waiting_text = small_font.render("Click 'Ready' to continue", True, gray)
            screen.blit(waiting_text, (150, 580))

        pygame.display.flip()

        # Continuously check with the network if both players are ready
        



def gameplay(player, network,game):
    # print(player.board)
    running = True
    clock=pygame.time.Clock()
    box_positions=player.board
    while running:
        
        
        player=network.send("updatedp")
        
        # print("Gameplay is on bitch")
        clock.tick(60)
        if not running:
            break 
        screen.fill(WHITE)
        draw_board(player,box_positions)
        # network.send(("update",pickle.dumps(game)))
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_row = mouse_pos[1] // box_size
                clicked_col = mouse_pos[0] // box_size

                # Check if the click is within the game grid and edit is still allowed
                if game.winner(player)==-1 and player.went==False and game.over==False and clicked_row < rows and clicked_col < cols and box_positions[clicked_row][clicked_col].cutted==False:
                    # box_positions[clicked_row][clicked_col].cut()
                    
                    # network.send(("updateplayer",pickle.dumps(player))) 
                    box_positions[clicked_row][clicked_col].color=(153, 174, 176)
                    game=network.send(f"move,{clicked_row},{clicked_col}")
                    
                    if game is None:
                        print("Error: No game state received from the server after making a move.")
                        running = False
                    # game=network.send(("update",pickle.dumps(game)))
                    box_positions=player.board
                    draw_board(player,box_positions)
            draw_board(player,box_positions)
        if game and game.winner(player) != -1:
            winner=game.winner(player)
            print(winner)
            if player.id == winner :
                text = wintext.render("BINGO!!!", True, WHITE)
                print("You win!")
            else:
                text = wintext.render("You Lose", True, WHITE)
                print("You lose!")

            screen.blit(text, (80, 200))
            pygame.display.flip()  # Ensure the text is displayed
            pygame.time.delay(4000)  # Delay for 4 seconds to show the message

            # Wait for player to close the game window after displaying result
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # User closes window
                        waiting = False
                        running=False

            # Once the waiting loop finishes, quit pygame
            pygame.quit()
        else:
            pygame.display.flip()

        
        
        
def copy_to_clipboard(text):
    pygame.scrap.put(pygame.SCRAP_TEXT, str(text).encode('utf-8'))
    print("Copied to clipboard:", text)


def display_passkey_screen(passkey,game,player,network):
    running = True
    clock=pygame.time.Clock()
    
    while running:
        clock.tick(60)
        
        game=network.send("get")
        # print(game)
        # print(game.ready)
        # print(player.id)
        if game.connected():
            running = False
            pygame.time.delay(2000)
            screen.fill(WHITE)
            
            edit(player, network,game)
        
        screen.fill(WHITE)
        copy_button_rect = pygame.Rect(220, 320, 200, 50)

        # Display the passkey
        passkey_text = font.render(f"Passkey: {passkey}", True, black)
        screen.blit(passkey_text, (screen_width // 2 - passkey_text.get_width() // 2, 150))

        # Display waiting message
        waiting_text = small_font.render("Waiting for another player...", True, gray)
        screen.blit(waiting_text, (screen_width // 2 - waiting_text.get_width() // 2, 220))

        # Draw the "Copy" button
        pygame.draw.rect(screen, blue, copy_button_rect)
        copy_text = small_font.render("Copy Passkey", True, WHITE)
        screen.blit(copy_text, (copy_button_rect.x + 20, copy_button_rect.y + 10))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Check if the "Copy" button was clicked
                if copy_button_rect.collidepoint(mouse_pos):
                    copy_to_clipboard(passkey)  # Copy passkey to clipboard
        
            

        # Update the display
        pygame.display.flip()


def display_passkey_entry_screen(network):
   
    running = True
    clock=pygame.time.Clock()
    passkey_input = ""
    input_box_rect = pygame.Rect(200, 150, 240, 50)
    join_button_rect = pygame.Rect(220, 240, 200, 50)
    
    while running:
        clock.tick(60)
        screen.fill(WHITE)
        
        # Draw input box for passkey
        pygame.draw.rect(screen, GRAY, input_box_rect, 2)
        passkey_text = font.render(passkey_input, True, black)
        screen.blit(passkey_text, (input_box_rect.x + 10, input_box_rect.y + 10))
        
        # Draw the "Join" button
        pygame.draw.rect(screen, blue, join_button_rect)
        join_text = small_font.render("Join Game", True, WHITE)
        screen.blit(join_text, (join_button_rect.x + 40, join_button_rect.y + 10))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Handle typing in the passkey input box
                if event.key == pygame.K_BACKSPACE:
                    passkey_input = passkey_input[:-1]
                else:
                    passkey_input += event.unicode  # Append character to passkey input

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Check if the "Join" button was clicked
                if join_button_rect.collidepoint(mouse_pos):
                    # Attempt to join the game using the entered passkey
                    if passkey_input.isdigit():  # Ensure the passkey is a number
                        passkey = int(passkey_input)
                        game1 = network.send(f"Join,{passkey}")
                        if not game1:
                            passkey_input=""
                            continue
                        print("kere")
                        print(game1)
                        if game1 and isinstance(game1,game):
                            print("Successfully joined game!")
                            running = False
                            player = network.getplayer()
                            print(player.id)
                            print(game1.connected())
                            game1.setready()
                            print(game1.connected())
                            player.went=True
                            game1.players[player.id]=player
                            # network.send(("updateplayer",pickle.dumps(player)))
                            network.send(("update",pickle.dumps(game1)))
                            
                            if game1.connected():

                                running=False
                                screen.fill(WHITE)
                                edit(player,network,game1)
                        else:
                            print("Invalid passkey or game not found.")
        
        # Update the display
        pygame.display.flip()


def main_menu():
    clock=pygame.time.Clock()
    network = Network()
    
    running = True
    while running:
        clock.tick(60)
        screen.fill(WHITE)

        create_button_rect = pygame.Rect(220, 150, 200, 60)
        join_button_rect = pygame.Rect(220, 250, 200, 60)

        pygame.draw.rect(screen, blue, create_button_rect)
        create_text = font.render("Create", True, WHITE)
        screen.blit(create_text, (create_button_rect.x + 40, create_button_rect.y + 10))

        pygame.draw.rect(screen, black, join_button_rect)
        join_text = font.render("Join", True, WHITE)
        screen.blit(join_text, (join_button_rect.x + 55, join_button_rect.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if create_button_rect.collidepoint(mouse_pos):
                    game = network.send("Create")
                    passkey=game.passkey
                    player = network.getplayer()
                    
                    
                    display_passkey_screen(passkey,game,player,network)
                    

                elif join_button_rect.collidepoint(mouse_pos):
                    display_passkey_entry_screen(network)
                    
                    

        pygame.display.flip()

# Start the game with the main menu
running=True
while running:
    main_menu()
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()  # Close Pygame window
                
    
pygame.quit()
