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


PLAYER_ZONES = {
    #min x, max x, min y, max y
    'dealer': (576, 800, 100, 200),
    'player1': (576, 780, 400, 720)
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


def display_player_cards(screen, player_cards, base_position, scale_x, scale_y, card_offset=(30, 20), base_size=(128, 128)):
    for i, card_url in enumerate(player_cards):
        # Calculate the position for each card in the player's hand
        card_position = (base_position[0] + i * card_offset[0], base_position[2] + i * card_offset[1])
        display_card_image(screen, card_url, card_position, scale_x, scale_y, base_size)

def playGame(window_size, game, player):
    pygame.init()

    #Initial blackjack information
    game = game
    player = player

    game.players.append(player)
    game.getNewDecks("1")
    print(game.deck_id)
    game.deal_cards()

    player_cards = [player.hand[i]['images']['png'] for i in range(len(player.hand))]
    dealer_cards = [game.players[0].hand[i]['images']['png'] for i in range(len(game.players[0].hand))]

    #Initial screen information
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    pygame.display.set_caption("Blackjack")
    screen.fill(TABLE_COLOR)
    clock = pygame.time.Clock()

    rectangle = pygame.Rect((0, 0), (100, 100))

    running = True
    while running:
        pygame.draw.rect(screen, (255, 0, 0), rectangle)

        pygame.display.update()
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
                if rectangle.collidepoint(x, y):
                    game.hit(1)


        # Calculate scale factors for x and y
        scale_x = window_size[0] / BASE_WIDTH
        scale_y = window_size[1] / BASE_HEIGHT

        # Display dealer's cards
        display_player_cards(screen, dealer_cards, PLAYER_ZONES["dealer"], scale_x, scale_y)

        # Display player's cards (assuming a single player for now)
        display_player_cards(screen, player_cards, PLAYER_ZONES["player1"], scale_x, scale_y)



        # UPDATE PLAYER HANDS INFORMATION
        player_cards = [player.hand[i]['images']['png'] for i in range(len(player.hand))]
        dealer_cards = [game.players[0].hand[i]['images']['png'] for i in range(len(game.players[0].hand))]
        pygame.display.update()
        clock.tick(10)  # Control the game loop speed


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

    image = tk.PhotoImage(file="./blackjack logo.png")

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
