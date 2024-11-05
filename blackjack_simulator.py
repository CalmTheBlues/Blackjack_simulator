import requests

deck_url_base = "https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count="


class BlackJack: 
    def __init__(self, num_decks):
        self.deck_url = deck_url_base + num_decks
        response = requests.get(self.deck_url)
        self.deck = response.json()
        self.deck_id = self.deck["deck_id"]
        self.num_chips = 0
        self.wager = None
        self.player_hands = []
        self.num_bots = 0
        self.card_count = 52 * int(num_decks)
        self.max_deck = 52 * int(num_decks)

    def getNewDecks(self, num_decks):
        self.deck_url = deck_url_base + num_decks
        response = requests.get(self.deck_url)
        self.deck = response.json()
        self.deck_id = self.deck["deck_id"]
        self.card_count = 52 * int(num_decks)
        self.max_deck = 52 * int(num_decks)


    def playmates(self, numbots):
        self.num_bots = numbots
        self.player_hands = [[] for _ in range(numbots + 2)]  # empty lists for each hand plus 2 is for  yourself and dealer
        self.deal_cards()

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
    
    def deckSize(self):
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


def main():
    while (True):
        num_decks = input("How many decks would you like to play with (1-6): ")
        if num_decks == 'e':
            print("Thanks for playing")
            break
        
        game = BlackJack(num_decks)
        numBots = int(input("How man bots would you like to play with: "))
        game.playmates(numBots)
        game.printHands()
        game.hit(0)
        game.printHands()

if __name__ == "__main__":
    main()
    