import tkinter as tk
from tkinter import *
from blackjack_simulator import BlackJack, Player
import pygame
from io import BytesIO
import requests
import sys

BASE_WIDTH = 1280
BASE_HEIGHT = 720

screenWidth = 1280
screenHeight = 720
TABLE_COLOR = pygame.Color(53, 101, 77)
window_size = (1280, 720)

def display_card_image(screen, card_url, base_position, scale_x, scale_y, base_size=(128, 128)):
    response = requests.get(card_url)
    img_data = BytesIO(response.content)
    card_img = pygame.image.load(img_data)

    # Scale image size based on window scale factors
    scaled_size = (int(base_size[0] * scale_x), int(base_size[1] * scale_y))
    card_img = pygame.transform.scale(card_img, scaled_size)

    # Scale position
    scaled_position = (int(base_position[0] * scale_x), int(base_position[1] * scale_y))

    screen.blit(card_img, scaled_position)


def playGame(window_size, game, player):
    pygame.init()

    game = game
    player = player

    #Initial information
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    pygame.display.set_caption("Blackjack")
    screen.fill(TABLE_COLOR)
    clock = pygame.time.Clock()

    game.players.append(player)
    game.playmates(0)
    game.getNewDecks("1")
    print(game.deck_id)
    game.deal_cards()

    print(player.hand)
    player_cards = []
    player_cards = [player.hand[i]['images']['png'] for i in range(len(player.hand))]

    
    # Calculate scale factors for x and y
    scale_x = window_size[0] / BASE_WIDTH
    scale_y = window_size[1] / BASE_HEIGHT

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_size = event.size
                pygame.display.set_caption("Blackjack")
                screen.fill(TABLE_COLOR)
                scale_x = window_size[0] / BASE_WIDTH
                scale_y = window_size[1] / BASE_HEIGHT


        display_card_image(screen, player_cards[0], (576, 440), scale_x, scale_y)
        display_card_image(screen, player_cards[1], (596, 420), scale_x, scale_y)
        pygame.display.update()


def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best
    #client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client.connect((ip, int(port)))

    # Get the required information from your server (screen width, height & player paddle, "left or "right)
    #resp = client.recv(512)
    #initData = json.loads(resp.decode())

    # If you have messages you'd like to show the user use the errorLabel widget like so
    errorLabel.config(text=f"Some update text. You input: IP: {ip}, Port: {port}")
    # You may or may not need to call this, depending on how many times you update the label
    errorLabel.update()     

    # Close this window and start the game with the info passed to you from the server
    app.withdraw()     # Hides the window (we'll kill it later)
    game = BlackJack()
    player = Player(1234)
    playGame(window_size, game, player)  # User will be either left or right paddle
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
