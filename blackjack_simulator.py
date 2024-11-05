import requests

deck_url_base = "https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count="


class BlackJack: 
    def __init__(self):
        self.deck_url = None
        self.deck = None
        self.deck_id = None
        self.num_chips = 0
        self.wager = None
        self.player_hands = []
        self.num_bots = 0
        self.card_count = None
        self.max_deck = None

    def getNewDecks(self, num_decks):
        self.deck_url = deck_url_base + num_decks
        response = requests.get(self.deck_url)
        self.deck = response.json()
        self.deck_id = self.deck["deck_id"]
        self.card_count = 52 * int(num_decks)
        self.max_deck = 52 * int(num_decks)

    def getDeckAmount(self): #API allows 1-6 decks
        while True:
            num_decks = input("How many decks would you like to play with (1-6): ")
            if num_decks.lower() == 'e':
                return 1
            if int(num_decks) > 0 and int(num_decks) <= 6:
                self.getNewDecks(num_decks) 
                return 0
            else:
                print("Input out of range, must be in [1,6]")

    def getBotAmount(self): #validate amount of bots, have only 6 people at the table not including dealer
        while True:
            try:
                num_bots = int(input("How many bots would you like to play with (0-5): "))
                # Check if the input is within the valid range
                if num_bots >= 0 and num_bots <= 5:
                    self.playmates(num_bots)
                    break  # Exit the loop once a valid number is entered
                else:
                    print("Input out of range, must be in [0,5].") 
            except ValueError:
                print("Invalid input. Please enter an integer between 0 and 5.")


    def playmates(self, numbots):
        self.num_bots = numbots
        self.player_hands = [[] for _ in range(numbots + 2)]  # empty lists for each hand plus 2 is for  yourself and dealer

    def deal_cards(self):
        draw_url = f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={1}"
        for i in range(2): #will go through 
            for j in range(self.num_bots + 2): #you are at index 0, dealer is 1 bots take up the rest
                card = requests.get(draw_url)
                drawn_card = card.json()["cards"][0]  # get the first card from the response
                self.player_hands[j].append(drawn_card)  # append the card to the player's hand
                self.card_count -= 1
    def hit(self, idx):
        draw_url = f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={1}"
        card = requests.get(draw_url)
        drawn_card = card.json()["cards"][0]
        self.player_hands[idx].append(drawn_card)
        self.card_count -= 1
    
    def deckSize(self): #use this to keep track of how many cards are left in the deck
        if self.card_count <= (0.25 * self.max_deck):
            print("time to reshuffle") 

    def printHands(self):
        for idx, hand in enumerate(self.player_hands):
            if idx == 0:
                player_name = "Player"
            elif idx == 1:
                player_name = "Dealer"
            else:
                player_name = f"Bot {idx - 1}"
            
            card_names = [f"{card['value']} of {card['suit']}" for card in hand]
            print(f"{player_name}'s hand: {', '.join(card_names)}")
    
    def playerHandVal(self, idx): #should return the player's hand's value 
        playerTotal = 0
        for item in self.player_hands[idx]:
            if item["value"] == 0: #face card values are labeled as '0'
                playerTotal += 10
            elif 1 < item["value"] < 10:
                playerTotal += item["value"]
            if item["value"] == 1 and playerTotal + item["value"] > 21: #handle Ace's 1 or 11 cases
                pass 


    def promptDecision(self, idx):
        #add something to determine if they are eligible to double down or split cards
        while(True):
            try:
                move = int(input("What move would you like to make: 1: stay, 2: hit"))
                # Check if the input is within the valid range
                if move == 1 or move == 2:
                    break  # Exit the loop once a valid number is entered
                else:
                    print("Move unavailable") 
            except ValueError:
                print("Invalid input. Please enter either 1 or 2.")
        
        if move == 1: #hit
            self.hit(idx)
            return 1
        if move == 2: #stay
            return 2


def main():
    playGame = True
    game = BlackJack()
    decks = game.getDeckAmount() #0 or 1. 1 means don't play anymore
    if decks == 1: 
        print("Thanks for playing")
        playGame = False
    game.getBotAmount()
    print(playGame)
    l = len(game.player_hands)
    while(playGame):
        for idx in range(l):
            if idx == 1: #dealer's turn
                continue
            playerTotal = game.playerHandVal(idx) #will need to add function to determine if it is a bust or if it is blackjack
                                                    #if blackjack will need to add win and payout functions
            move = game.promptDecision(idx)
            while move == 1: #keep offering decision to hit or stay until they bust, hit 21, or stay
                move = game.promptDecision(idx)
            
            


if __name__ == "__main__":
    main()
    