import tkinter as tk
from tkinter import *
from blackjack_simulator_log import BlackJack, Player
import pygame
from io import BytesIO
import requests
import sys
from pygame.surface import Surface

BASE_WIDTH = 1280
BASE_HEIGHT = 720

TABLE_COLOR = pygame.Color(53, 101, 77) #green
window_size = (1280, 720) #default size

card_back = 'https://deckofcardsapi.com/static/img/back.png'


PLAYER_ZONES = {
    #min x, max x, min y, max y
    'dealer': (576, 800, 100, 200),
    'player1': (576, 780, 400, 720),
    'player1split2': (604, 808, 400, 720),
    'player1split1': (350, 554, 400, 720), 
}

def display_card_image(screen: Surface, card_url: str, base_position: tuple, scale_x: float, scale_y: float, base_size=(128, 128)):
    """
    Function to scale card image to screen size and display it on the screen
    Args:
        screen (pygame.surface.Surface): The screen to display the card onto
        card_url (str): link to the card's png file
        base_position (tuple): coordinates for the position of the card before scaling to screen size
        scale_x (float): scaling factor for width
        scale_y (float): scaling factor for height
    Returns: None
    """
    response = requests.get(card_url)
    img_data = BytesIO(response.content)
    card_img = pygame.image.load(img_data)

    # Scale image size based on window scale factors
    scaled_size = (int(base_size[0] * scale_x), int(base_size[1] * scale_y))
    card_img = pygame.transform.scale(card_img, scaled_size)

    # Scale position
    scaled_position = (int(base_position[0] * scale_x), int(base_position[1] * scale_y))

    screen.blit(card_img, scaled_position)


def display_player_cards(screen, player_cards, base_position, scale_x, scale_y, hide_one=0, card_offset=(30, 20), base_size=(128, 128)):
    if hide_one:
        for i, card_url in enumerate(player_cards):
            card_position = (base_position[0] + i * card_offset[0], base_position[2] + i *card_offset[1])
            if i == 1:
                display_card_image(screen, card_back, card_position, scale_x, scale_y, base_size)
            else:
                display_card_image(screen, card_url, card_position, scale_x, scale_y, base_size)

    else:
        for i, card_url in enumerate(player_cards):
            # Calculate the position for each card in the player's hand
            card_position = (base_position[0] + i * card_offset[0], base_position[2] + i * card_offset[1])
            display_card_image(screen, card_url, card_position, scale_x, scale_y, base_size)

def display_player_balance(screen, player):
    balance = player.balance

   # Render the balance text
    balance_font = pygame.font.Font('black_jack/BLACKJAR.TTF', 24)
    balance_text = balance_font.render(f"Balance: ${balance}", True, (255, 255, 255))

    # Put player balance in the top left corner
    text_position = (0, 0)

    # Display the balance text on the screen
    screen.blit(balance_text, text_position)


def playGame(window_size, decks, bots, balance):
    pygame.init()

    #Initial blackjack information
    game = BlackJack()
    player = Player(balance, True)

    game.players.append(player)
    game.getNewDecks(decks)
    print(game.deck_id)
    game.deal_cards()

    player_cards = [player.hand[i]['images']['png'] for i in range(len(player.hand))]
    dealer_cards = [game.players[0].hand[i]['images']['png'] for i in range(len(game.players[0].hand))]
    
    player_cards_split_1 = []
    player_cards_split_2 = []

    #Initial screen information
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    pygame.display.set_caption("Blackjack")
    screen.fill(TABLE_COLOR)
    clock = pygame.time.Clock()
    clock.tick(60)  # Control the game loop speed



    # Button properties
    button_width = 100
    button_height = 50
    button_spacing = 20  # Space between buttons

    running = True
    split_hands = False
    while running:
        current_player = game.current_player_idx
        scale_x = window_size[0] / BASE_WIDTH
        scale_y = window_size[1] / BASE_HEIGHT


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_size = event.size
                pygame.display.set_caption("Blackjack")
                screen.fill(TABLE_COLOR)
                scale_x = window_size[0] / BASE_WIDTH
                scale_y = window_size[1] / BASE_HEIGHT
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                if hit_button.collidepoint(x, y):
                    game.hit(current_player)
                    print(game.players[idx].hand)
                elif stand_button.collidepoint(x, y):
                    game.stand(current_player)
                elif split_button.collidepoint(x, y):
                    game.split(current_player)
                    split_hands = True


        for idx, player in enumerate(game.players[1:]):
            value = player.getHandValue()

            # Create font and grab its size
            value_font = pygame.font.Font('black_jack/BLACKJAR.TTF', 16)

            if game.isBlackjack(idx):
                value_text = value_font.render("Blackjack!", True, (0, 255, 0))
            elif value:
                value_text = value_font.render(f"{value}", True, (255, 255, 255))
            else:
                value_text = value_font.render(f"Bust!", True, (255, 0, 0))

            text_width, text_height = value_text.get_size()

            if not split_hands:
                position = PLAYER_ZONES[f'player{idx+1}'] # We skip over the dealer so add +1 to each idx
            elif split_hands and idx == 1:
                position = PLAYER_ZONES[f'player1split1']
            elif split_hands and idx == 2:
                position = PLAYER_ZONES[f'player1split2']
            
            value_position = (
            position[0] * scale_x,  # Adjust position to align with the player's cards
            (position[2] - 30) * scale_y  # Slightly above the cards
            )
            

            # Clear the previous value by drawing a rectangle over it
            pygame.draw.rect(
            screen,
            TABLE_COLOR,  # Use the table's background color
            pygame.Rect(value_position[0], value_position[1], text_width, text_height)
            )

            screen.blit(value_text, value_position)


        # Recalculate button positions for the bottom-left corner
        hit_button = pygame.Rect(
            20,  # Left margin
            window_size[1] - button_height - 20,  # Bottom margin
            button_width,
            button_height,
        )
        stand_button = pygame.Rect(
            hit_button.right + button_spacing,  # Place next to the "Hit" button
            window_size[1] - button_height - 20,
            button_width,
            button_height,
        )
        
        split_button = pygame.Rect(
            stand_button.right + button_spacing,
            window_size[1] - button_height - 20,
            button_width,
            button_height,
        )

        
        # Calculate scale factors for x and y
        scale_x = window_size[0] / BASE_WIDTH
        scale_y = window_size[1] / BASE_HEIGHT
        
        # Display player's balance
        display_player_balance(screen, player)

        # Display dealer's cards
        if current_player == 0:
            display_player_cards(screen, dealer_cards, PLAYER_ZONES["dealer"], scale_x, scale_y)
        else:
            display_player_cards(screen, dealer_cards, PLAYER_ZONES["dealer"], scale_x, scale_y, 1)

        # Display player's cards (assuming a single player for now)
        if split_hands:
            #draw over the previous cards that are still on screen
            pygame.draw.rect(
                screen,
                TABLE_COLOR,  # Use the table's background color
                pygame.Rect(PLAYER_ZONES['player1'][0] * scale_x,
                            PLAYER_ZONES['player1'][2] * scale_x,
                            (PLAYER_ZONES['player1'][1] - PLAYER_ZONES['player1'][0]) * scale_x,
                            (PLAYER_ZONES['player1'][3] - PLAYER_ZONES['player1'][2]) * scale_x)
            )
            
            player_cards_split_1 = [game.players[1].hand[i]['images']['png'] for i in range(len(game.players[1].hand))]
            player_cards_split_2 = [game.players[2].hand[i]['images']['png'] for i in range(len(game.players[2].hand))]
            
            display_player_cards(screen, player_cards_split_1, PLAYER_ZONES["player1split2"], scale_x, scale_y)
            display_player_cards(screen, player_cards_split_2, PLAYER_ZONES["player1split1"], scale_x, scale_y)
        else:
            display_player_cards(screen, player_cards, PLAYER_ZONES["player1"], scale_x, scale_y)
        
        # Draw hit button
        pygame.draw.rect(screen, (255, 0, 0), hit_button)
        hit_font = pygame.font.Font('black_jack/BLACKJAR.TTF', 32)
        hit_text = hit_font.render("Hit", True, (255, 255, 255))
        hit_text_rect = hit_text.get_rect(center=hit_button.center)
        screen.blit(hit_text, hit_text_rect)

        # Draw stand button
        pygame.draw.rect(screen, (255, 0, 0), stand_button)
        stand_font = pygame.font.Font('black_jack/BLACKJAR.TTF', 32)
        stand_text = stand_font.render("Stand", True, (255, 255, 255))
        stand_text_rect = stand_text.get_rect(center=stand_button.center)
        screen.blit(stand_text, stand_text_rect)
        
        # Draw split button
        if (player.isNotBot and len(player.hand) == 2 and player.hand[0]['value'] == player.hand[1]['value']):
            pygame.draw.rect(screen, (255, 0, 0), split_button)
            split_font = pygame.font.Font('black_jack/BLACKJAR.TTF', 32)
            split_text = split_font.render("Split", True, (255, 255, 255))
            split_text_rect = split_text.get_rect(center=split_button.center)
            screen.blit(split_text, split_text_rect)

        # UPDATE PLAYER HANDS INFORMATION
        player_cards = [player.hand[i]['images']['png'] for i in range(len(player.hand))]
        dealer_cards = [game.players[0].hand[i]['images']['png'] for i in range(len(game.players[0].hand))]

        pygame.display.update()


def validate_input(decks, balance, bots):
    error_message = ""
    # Validate Number of Decks (must be an integer between 1 and 6)
    if not decks.isdigit() or not (1 <= int(decks) <= 6):
        error_message += "Number of Decks must be an integer between 1 and 6.\n"

    # Validate Balance (must be a positive number)
    try:
        balance = float(balance)
        if balance <= 0:
            error_message += "Balance must be a positive number.\n"
    except ValueError:
        error_message += "Balance must be a valid number.\n"

    # Validate Number of Bots (must be an integer between 0 and 2)
    if not bots.isdigit() or not (0 <= int(bots) <= 2):
        error_message += "Number of Bots must be an integer between 0 and 2.\n"

    return error_message

def joinServer(decks:str, balance:int, bots:int, errorLabel:tk.Label, app:tk.Tk) -> None:

    # Validate inputs
    error_message = validate_input(decks, balance, bots)
    if error_message:
        errorLabel.config(text=error_message, fg="red")
        return
    
    # If inputs are valid, proceed
    errorLabel.config(text="Joining server...", fg="green")
    # Add logic to connect to the server or proceed with the app
    app.withdraw()     # Hides the window

    decks = str(decks)
    balance = int(balance)
    bots = int(bots)

    try:
        playGame(window_size, decks, bots, balance)  # User begins playing the game
    except Exception as e:
        print(f"The code stopped running because {e}")
        app.quit()

    app.quit()         # Kills the window
    sys.exit()



# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Game Info")

    image = tk.PhotoImage(file="./blackjack logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    deckLabel = tk.Label(text="Number of Decks (1-6):")
    deckLabel.grid(column=0, row=1, sticky="W", padx=8)

    deckEntry = tk.Entry(app)
    deckEntry.grid(column=1, row=1)

    moneyLabel = tk.Label(text="Your Balance:")
    moneyLabel.grid(column=0, row=2, sticky="W", padx=8)

    moneyEntry = tk.Entry(app)
    moneyEntry.grid(column=1, row=2)

    botLabel = tk.Label(text="Number of Bots (0-2):")
    botLabel.grid(column=0, row=3, sticky="W", padx=8)

    botEntry = tk.Entry(app)
    botEntry.grid(column=1, row=3)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(deckEntry.get(), moneyEntry.get(), botEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=5, columnspan=2)

    app.mainloop()


if __name__ == "__main__":
    startScreen()
