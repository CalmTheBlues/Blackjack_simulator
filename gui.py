import tkinter as tk
from tkinter import *
from blackjack_simulator_log import BlackJack, Player
import pygame
from io import BytesIO
import requests
import sys
import os
from pygame.surface import Surface

BASE_WIDTH = 1280
BASE_HEIGHT = 720

TABLE_COLOR = pygame.Color(53, 101, 77) #green
window_size = (1280, 720) #default size

card_back = 'https://deckofcardsapi.com/static/img/back.png'
CARD_IMG_FOLDER = './img/cards/'

PLAYER_ZONES = {
    #min x, max x, min y, max y
    'player0': (576, 800, 100, 200), #dealer
    'player1': (576, 780, 400, 720)
}

CHIP_VALUES = [1, 5, 25, 100]
CHIP_IMAGES = ['./img/chips/1_dollar_chip.png',
               './img/chips/5_dollar_chip.png',
               './img/chips/25_dollar_chip.png',
               './img/chips/100_dollar_chip.png']

# Betting zone coordinates
CHIP_ZONES = [
    (300, 600, 100, 100),  # x, y, width, height for each chip area
    (500, 600, 100, 100),
    (700, 600, 100, 100),
    (900, 600, 100, 100),
]

CHIP_BUTTON_ZONES = []
for i, chip in enumerate(CHIP_IMAGES):
    x, y, w, h = CHIP_ZONES[i]
    CHIP_BUTTON_ZONES.append({
        "chip": (x, y, w, h),  # Chip area
        "+": (x + (w), y + (h // 2), 30, 20),  # + button directly to the right
        "-": (x - 30 - 10, y + (h // 2), 30, 20)      # - button directly to the left
    })

def display_chips_and_bet(screen, player_bet, chip_bets, scale_x, scale_y):
    font = pygame.font.Font(None, 24)

    # Display the total bet
    bet_text = font.render(f"Total Bet: ${player_bet}", True, (255, 255, 255))
    text_width, text_height = bet_text.get_size()
    
    total_bet_pos = (600*scale_x, 700*scale_y)
    text_width = text_width * scale_x
    text_height = text_height * scale_y
    # Clear the previous value by drawing a rectangle over it
    pygame.draw.rect(
    screen,
    TABLE_COLOR,  # Use the table's background color
    pygame.Rect(total_bet_pos[0], total_bet_pos[1], text_width+100, text_height+100)
    )
    screen.blit(bet_text, total_bet_pos)

    # Display each chip, its +/- buttons, and count
    for i, zones in enumerate(CHIP_BUTTON_ZONES):
        # Draw chip image
        chip_image = pygame.image.load(CHIP_IMAGES[i])
        chip_image = pygame.transform.scale(chip_image, (zones["chip"][2], zones["chip"][3]))
        screen.blit(chip_image, (zones["chip"][0]*scale_x, zones["chip"][1]*scale_y))

        # Draw + button
        pygame.draw.rect(screen, (0, 255, 0),
        pygame.Rect(zones["+"][0]*scale_x, zones["+"][1]*scale_y, zones["+"][2]*scale_x, zones["+"][3]*scale_y))  # Green button
        plus_text = font.render("+", True, (0, 0, 0))
        screen.blit(plus_text, ((zones["+"][0] + 10)*scale_x, zones["+"][1]*scale_y))

        # Draw - button
        pygame.draw.rect(screen,
        (255, 0, 0),
        pygame.Rect(zones["-"][0]*scale_x, zones["-"][1]*scale_y, zones["-"][2]*scale_x, zones["-"][3]*scale_y))  # Red button
        minus_text = font.render("-", True, (0, 0, 0))
        screen.blit(minus_text, ((zones["-"][0] + 10)*scale_x, zones["-"][1]*scale_y))

        # Display chip count
        count_text = font.render(f"x{chip_bets[CHIP_VALUES[i]]}", True, (255, 255, 255))
        chip_count_width, chip_count_height = count_text.get_size()

        # Clear the previous value by drawing a rectangle over it
        pygame.draw.rect(
        screen,
        TABLE_COLOR,  # Use the table's background color
        pygame.Rect((zones["chip"][0] + zones["chip"][2] + 10)*scale_x, zones["chip"][1]*scale_y, (chip_count_width+10)*scale_x, (chip_count_height+10)*scale_y))

        screen.blit(count_text, ((zones["chip"][0] + zones["chip"][2] + 10)*scale_x, zones["chip"][1]*scale_y))


def display_card_image(screen, card_url, base_position, scale_x, scale_y, base_size=(128, 128)):
    """
    Function to scale card image to screen size and display it on the screen.
    Downloads and caches images locally for faster reuse.
    
    Args:
        screen (pygame.surface.Surface): The screen to display the card onto
        card_url (str): Link to the card's PNG file
        base_position (tuple): Coordinates for the position of the card before scaling to screen size
        scale_x (float): Scaling factor for width
        scale_y (float): Scaling factor for height
        base_size (tuple): Base size of the card before scaling (default: (128, 128))
    Returns:
        None
    """
    # Extract a valid filename from the URL
    filename = os.path.join(CARD_IMG_FOLDER, os.path.basename(card_url))

    # Check if the image is already saved locally
    if not os.path.exists(filename):
        # Fetch the image and save it locally
        response = requests.get(card_url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
        else:
            print(f"Failed to fetch {card_url}: {response.status_code}")
            return

    # Load the image from the local file
    card_img = pygame.image.load(filename)

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

def display_player_balance(screen, player, scale_x, scale_y):
    balance = player.balance

   # Render the balance text
    balance_font = pygame.font.Font('black_jack/BLACKJAR.TTF', 24)
    balance_text = balance_font.render(f"Balance: ${balance}", True, (255, 255, 255))
    text_width, text_height = balance_text.get_size()

    # Put player balance in the top left corner
    text_position = (0, 0)

    # Clear the previous value by drawing a rectangle over it
    pygame.draw.rect(
    screen,
    TABLE_COLOR,  # Use the table's background color
    pygame.Rect(text_position[0], text_position[1], (text_width*scale_x)+20, (text_height*scale_y)+10))


    # Display the balance text on the screen
    screen.blit(balance_text, text_position)


def playGame(window_size, game, player):
    pygame.init()

    #Initial blackjack information
    game = game
    player = player

    game.players.append(player)
    game.getNewDecks("1")
    print(game.deck_id)
    #game.deal_cards()

    player_cards = [player.hand[i]['images']['png'] for i in range(len(player.hand))]
    dealer_cards = [game.players[0].hand[i]['images']['png'] for i in range(len(game.players[0].hand))]

    #Initial screen information
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    pygame.display.set_caption("Blackjack")
    screen.fill(TABLE_COLOR)
    clock = pygame.time.Clock()
    clock.tick(60)  # Control the game loop speed

    # Initialize the players bet and chip counts to 0
    player.current_bet = 0
    chip_bets = {value: 0 for value in CHIP_VALUES}

    # Button properties
    button_width = 100
    button_height = 50
    button_spacing = 20  # Space between buttons

    running = True
    while running:
        # Find the current player
        current_player = game.current_player_idx

        # Decide whether or not the dealer should be hiding their card
        if current_player == 0:
            hide_dealer = 0
        else:
            hide_dealer = 1


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
                elif stand_button.collidepoint(x, y):
                    game.stand(current_player)
                elif bet_button.collidepoint(x, y):
                    game.deal_cards()
                    player.balance = player.balance - player.current_bet
                for i, zones in enumerate(CHIP_BUTTON_ZONES):
                    # Check for + button click
                    if zones["+"][0]*scale_x <= x <= (zones["+"][0] + zones["+"][2])*scale_x and zones["+"][1]*scale_y <= y <= (zones["+"][1] + zones["+"][3])*scale_y:
                        player.current_bet += CHIP_VALUES[i]
                        chip_bets[CHIP_VALUES[i]] += 1
                        print(f"Added {CHIP_VALUES[i]}, Total Bet: ${player.current_bet}")

                    # Check for - button click
                    elif zones["-"][0]*scale_x <= x <= (zones["-"][0] + zones["-"][2])*scale_x and zones["-"][1]*scale_y <= y <= (zones["-"][1] + zones["-"][3])*scale_y:
                        if chip_bets[CHIP_VALUES[i]] > 0:  # Ensure chip count doesn't go negative
                            player.current_bet -= CHIP_VALUES[i]
                            chip_bets[CHIP_VALUES[i]] -= 1
                            print(f"Removed {CHIP_VALUES[i]}, Total Bet: ${player.current_bet}")

        # Display each player's current hand value
        for idx, player in enumerate(game.players[hide_dealer:]): # When dealer is hiding, skip over them and don't show their value
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

            position = PLAYER_ZONES[f'player{idx+hide_dealer}'] # If we skip over the dealer, add 1 to each player's idx

            # Calculate scaled position of where to place the hand value
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

            # Display the value
            screen.blit(value_text, value_position)


        # Calculate button positions for the bottom-right corner
        bet_button = pygame.Rect(
            window_size[0] - (button_width*2) - 20,
            window_size[1] - button_height - 40,
            (button_width*2) - 40,
            button_height
        )

        # Calculate button positions for the bottom-left corner
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

        # Display chips
        display_chips_and_bet(screen, player.current_bet, chip_bets, scale_x, scale_y)


        # Display player's balance
        display_player_balance(screen, player, scale_x, scale_y)

        # Display dealer's cards
        if hide_dealer == 0:
            display_player_cards(screen, dealer_cards, PLAYER_ZONES["player0"], scale_x, scale_y)
        else:
            display_player_cards(screen, dealer_cards, PLAYER_ZONES["player0"], scale_x, scale_y, hide_dealer)

        # Display player's cards (assuming a single player for now)
        display_player_cards(screen, player_cards, PLAYER_ZONES["player1"], scale_x, scale_y)

        # Draw Place Bet button
        pygame.draw.rect(screen, (255, 0, 0), bet_button)
        bet_font = pygame.font.Font('black_jack/BLACKJAR.TTF', 32)
        bet_text = bet_font.render("Place Bet", True, (255, 255, 255))
        bet_text_rect = bet_text.get_rect(center=bet_button.center)
        screen.blit(bet_text, bet_text_rect)


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

        # UPDATE PLAYER HANDS INFORMATION
        player_cards = [player.hand[i]['images']['png'] for i in range(len(player.hand))]
        dealer_cards = [game.players[0].hand[i]['images']['png'] for i in range(len(game.players[0].hand))]

        pygame.display.update()

def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    errorLabel.config(text=f"Some update text. You input: IP: {ip}, Port: {port}")
    errorLabel.update()     

    # Close this window and start the game with the info passed to you from the server
    app.withdraw()     # Hides the window
    game = BlackJack()
    player = Player(1234)
    try:
        playGame(window_size, game, player)  # User begins playing the game
    except Exception as e:
        print(e)
        app.quit()

    app.quit()         # Kills the window
    sys.exit()



# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./img/blackjack logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()


if __name__ == "__main__":
    startScreen()
