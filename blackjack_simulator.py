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
    
    def playmates(self, numbots):
        self.num_bots = numbots
        self.player_hands = [_ for i in range(numbots + 1)] #plus 1 is for dealer

    def deal_cards(self):
        draw_url = f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={1}"
        for i in range(2): #will go through 
            for j in range(self.num_bots): #you are at index 0, dealer is 1 bots take up the rest
                card = requests.get(draw_url)
                self.player_hands[j] = card.json()["cards"]

    