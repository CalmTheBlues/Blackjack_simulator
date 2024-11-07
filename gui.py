import tkinter as tk
from tkinter import *
from blackjack_simulator import BlackJack
import pygame

screenWidth = 1280
screenHeight = 720
TABLE_COLOR = pygame.Color(53, 101, 77)

def playGame(screenWidth, screenHeight, game):
    game = game
    pygame.init()
    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption("Blackjack")
    screen.fill(TABLE_COLOR)
    #table = pygame.Surface.fill(WHITE, screen)
    card = pygame.Rect(0, 0, 120, 120)
    pygame.draw.rect(screen, (0, 0, 0), card)

    p1Area = pygame.Surface((640, 640))

    
    screen.blit(p1Area, 0, 0)

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
    playGame(screenWidth, screenHeight, game)  # User will be either left or right paddle
    #app.quit()         # Kills the window



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
