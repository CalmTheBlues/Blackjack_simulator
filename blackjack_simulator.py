import requests
import random
import math

deck_url_base = "https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count="

card_value = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'JACK': 10,
    'QUEEN': 10,
    'KING': 10,
    'ACE': 1
}

class Player:
    def __init__(self, budget):
        self.balance = budget
        self.current_bet = 0
        self.hand = []
        self.smart = None

    def resetHand(self):
        self.hand=[]

    def placeBet(self, bet_amount):
        self.current_bet = bet_amount

    def botPlay(self, players, max_val, min_val): #logic for how a bot will make a move
        # Decision for hard totals (no Aces or Aces counted as 1)
        dealer_card = players[0].hand[0]['value']
        dealer_card = card_value[dealer_card]

        # Decision for soft totals (Ace counted as 11)
        if 13 <= max_val <= 16:
            if dealer_card >= 7:
                return 'hit'
            else:
                return 'double down'
        elif max_val == 17:
            if dealer_card >= 7:
                return 'hit'
            else:
                return 'double down'
        elif max_val == 18:
            if dealer_card <= 8:
                return 'stand'
            else:
                return 'hit'
        elif max_val == 19:
            return 'stand'
        elif max_val == 20:
            return 'stand'
        elif max_val == 21:
            return 'stand'
        #Decisions for hard total
        if min_val > 21:
            return 'stand'
        if min_val <= 8:
            return 'hit'
        elif min_val == 9:
            if 3 <= dealer_card <= 6:
                return 'double down'
            else:
                return 'hit'
        elif min_val == 10:
            if dealer_card <= 9:
                return 'double down'
            else:
                return 'hit'
        elif min_val == 11:
            return 'double down'
        elif min_val == 12:
            if 4 <= dealer_card <= 6:
                return 'stand'
            else:
                return 'hit'
        elif 13 <= min_val <= 16:
            if 2 <= dealer_card <= 6:
                return 'stand'
            else:
                return 'hit'
        elif min_val >= 17:
            return 'stand'

        # Default to hit if no specific strategy matches
        return 'hit'


    def getHandValue(self) -> int:
        playerTotal = 0
        num_aces = 0
        for card in self.hand:
            if card['value'] == 'ACE':
                num_aces += 1
            else:
                playerTotal += card_value[card['value']]
                
        possible_totals = {playerTotal}
        for _ in range(num_aces):
            possible_totals = {total + 1 for total in possible_totals} | {total + 11 for total in possible_totals}
        valid_totals = [total for total in possible_totals] #removed  if total <= 21
        
        return sorted(valid_totals)
    
    def addCard(self, card):
        self.hand.append(card)
        
    def doubleDown(self):
        self.balance = self.balance - self.current_bet
        self.current_bet *= 2
        
    def split(self):
        # to do
        x += 1
        
    def Blackjack(self):
        self.balance += math.ceil(self.current_bet * 2.5)

class BlackJack: 
    def __init__(self, num_bots):
        self.deck_url = None
        self.deck = None
        self.deck_id = None
        self.num_chips = 0
        self.wager = None
        self.players: list[Player] = []
        #self.player_hands = []
        self.num_bots = 0
        self.card_count = None
        self.max_deck = None
        self.count = 0

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
                return -1
            if int(num_decks) > 0 and int(num_decks) <= 6:
                self.getNewDecks(num_decks) 
                return int(num_decks)
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
                
    def getBalanceAmount(self):
        while True:
            try:
                balance = int(input("How much money would you like to play with: "))
                if balance > 0:
                    self.players.append(Player(balance))
                    break
                else:
                    print("Balance needs to be above zero.")
            except ValueError:
                print("Invalid input. Please enter an integer between 0 and 2^31 - 1")
                
    def getBetAmount(self, idx) -> int:
        while True:
            available_balance = self.players[idx].balance
            try:
                bet = int(input(f"Available balance is {available_balance}. How much money would you like to bet on this hand: "))
                if bet > 0 and bet <= available_balance:
                    self.players[idx].current_bet = bet
                    self.players[idx].balance -= bet
                    break
                else:
                    print("Balance needs to be above 0 and less than current balance.")
            except ValueError:
                print(f"Invalid input. Please enter an integer between 0 and {available_balance}")

    def playmates(self, numbots):
        self.num_bots = numbots
        #self.player_hands = [[] for _ in range(numbots + 2)]  # empty lists for each hand plus 2 is for  yourself and dealer
        self.players.append(Player(-1)) #append dealer as special player with balance -1
        for _ in range(numbots): # append bots with budget 100
            self.players.append(Player(100))

    def deal_cards(self):
        draw_url = f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={1}"
        for i in range(2): #will go through 
            for j in range(self.num_bots + 2): #you are at index 0, dealer is 1 bots take up the rest
                card = requests.get(draw_url)
                drawn_card = card.json()["cards"][0]  # get the first card from the response
                self.players[j].hand.append(drawn_card)  # append the card to the player's hand
                self.card_count -= 1
                if j == 1 and i == 1: #don't include dealer's unseen card
                    continue
                self.cardVal(drawn_card)
                #print("line")
    
    def cardVal(self, card):
        val = card_value[card['value']]
        print(val)
        if val >= 10:
            self.count -= 1
        elif 7 <= val <=9:
            self.count += 0
        elif val <= 6:
            self.count += 1
        #print(self.count)
         

    def hit(self, idx):
        draw_url = f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={1}"
        card = requests.get(draw_url)
        print(f"Card: {card}")
        drawn_card = card.json()["cards"][0]
        self.players[idx].hand.append(drawn_card)
        self.card_count -= 1
        self.cardVal(drawn_card)
        
    def doubleDown(self):
        #TO DO
        self.players[0].doubleDown()
        self.hit(0)
        self.printHands(True)
        
    def split(self):
        #TO DO
        x+=1
    
    def deckSize(self, num_decks): #use this to keep track of how many cards are left in the deck
        if self.card_count <= (0.25 * self.max_deck):
            self.getNewDecks(num_decks)
            self.count = 0

    def printHands(self, hide_dealers):
        for idx, player in enumerate(self.players):
            if idx == 0:
                player_name = "Player"
            elif idx == 1:
                player_name = "Dealer"
            else:
                player_name = f"Bot {idx - 1}"
            
            if idx == 1 and hide_dealers:
                card_names = [f"{player.hand[0]['value']} of {player.hand[0]['suit']} and UNKNOWN"]
            else:
                card_names = [f"{card['value']} of {card['suit']}" for card in player.hand]
            print(f"{player_name}'s hand: {', '.join(card_names)}")
    
    def playerHandVal(self, idx): #should return the player's hand's value 
        playerTotal = 0
        num_aces = 0
        for card in self.players[idx].hand:
            if card['value'] == 'ACE':
                num_aces += 1
            else:
                playerTotal += card_value[card['value']]
                
        possible_totals = {playerTotal}
        for _ in range(num_aces):
            possible_totals = {total + 1 for total in possible_totals} | {total + 11 for total in possible_totals}
        valid_totals = [total for total in possible_totals if total <= 21]
        
        return sorted(valid_totals)

    def promptDecision(self, idx):
        #add something to determine if they are eligible to double down or split cards
        while(True):
            try:
                #to address adding the option to split when the user has double of the same number(not value)
                if (self.players[idx].hand[0]['value'] == self.players[idx].hand[1]['value']):
                    can_split = True
                    move = int(input("What move would you like to make (1: hit, 2: stay, 3: double down, 4: split): "))
                else:
                    move = int(input("What move would you like to make (1: hit, 2: stay, 3: double down): "))
                # Check if the input is within the valid range
                if move == 1 or move == 2 or move == 3 or (move == 4 and can_split):
                    break  # Exit the loop once a valid number is entered
                else:
                    print("Move unavailable") 
            except ValueError:
                if can_split:
                    print("Invalid input. Please enter either 1, 2, 3, or 4.")
                else:
                    print("Invalid input. Please enter either 1, 2, or 3.")
        
        if move == 1: #hit
            self.hit(idx)
            self.printHands(True)
            return 1
        if move == 2: #stay
            return 2
        if move == 3:
            self.doubleDown()
            return 3
        if move == 4:
            self.split()
        
    def revealDealer(self):
        for card in self.players[1].hand:
            card_names = [f"{card['value']} of {card['suit']}"]
            print(f"Dealer's hand: {card_names}")
            
    def dealerHit(self):
        #dealer_value = self.playerHandVal(1)
        dealer_value = self.players[1].getHandValue()
        print(f"Dealer's value: {dealer_value}")
        self.printHands(False)
        #dealer has a soft 17 (17 with an ace, this means the dealer has to hit)
        if dealer_value == 17 and any(card['value'] == 1 for card in self.players[1].hand):
            self.hit(1)
            self.printHands(False)
        dealer_value = self.players[1].getHandValue()
        while max(dealer_value) < 17:
            self.hit(1)
            self.printHands(False)
            dealer_value = self.players[1].getHandValue()
            if dealer_value == []:
                return
            print(dealer_value)
            
    def isBlackjack(self, idx):
        has_ace = False
        has_ten = False
        for card in self.players[idx].hand:
            if card_value[card['value']] == 1:
                has_ace = True
            if card_value[card['value']] == 0 | card_value[card['value']] == 10:
                has_ten = True
                
        return has_ace and has_ten
    
    def getMaxScoreFromHand(self, idx):
        values = self.players[idx].getHandValue()
        if len(values) == 1:
            return values[0]
        elif len(values) > 1:
            return max(values)
    def getMinScoreFromHand(self, idx):
        values = self.players[idx].getHandValue()
        if len(values) == 1:
            return values[0]
        elif len(values) > 1:
            return min(values)
    
    def resetPlayerHands(self):
        l = len(self.players)
        for i in range(l):
            self.players[i].resetHand()

                


def main():
    playGame = True
    game = BlackJack()
    decks = game.getDeckAmount() #0 or 1. 1 means don't play anymore
    if decks == -1: 
        print("Thanks for playing")
        playGame = False
        
    game.getBalanceAmount()
    game.getBotAmount()
    l = len(game.players)
    while(playGame):
        game.deal_cards()
        game.getBetAmount(0)
        game.printHands(True)
        #need to change this to be based on the current length of players instead of length
        #at the start. but before this we need to implement taking bots out of the game if they run
        #out of money
        for idx in range(l): #one round loop
            if game.isBlackjack(idx):
                game.players[idx].Blackjack()
                continue
            if idx == 1: #dealer's turn
                continue
            if idx != 0 and idx != 1: #sanity check
                max_val = game.getMaxScoreFromHand(idx)
                min_val = game.getMinScoreFromHand(idx)
                move = game.players[idx].botPlay(game.players, max_val, min_val)
                if move == "stand": 
                    continue
                elif move == 'hit':
                    while move == 'hit':
                        game.hit(idx)
                        max_val = game.getMaxScoreFromHand(idx)
                        min_val = game.getMinScoreFromHand(idx)
                        move = game.players[idx].botPlay(game.players, max_val, min_val)
                        if move != 'hit':
                            break
                elif move == "double down":
                    game.players[idx].doubleDown()
                    game.hit(idx)

            if idx == 0:
                move = game.promptDecision(idx)
                
                if move == 2:
                    continue
                elif move == 3:
                    game.players[0].doubleDown()
                    game.hit(0)
                
                while move == 1: #keep offering decision to hit or stay until they bust, hit 21, or stay
                    #need to fix that if the user hits they cannot double down or split
                    move = game.promptDecision(idx)
                    if move == 2:
                        continue
  
        game.revealDealer()
        game.dealerHit()
        
        player_value = game.getMaxScoreFromHand(0)
        dealer_value = game.getMaxScoreFromHand(1)
        if game.isBlackjack(0):
            print(f"BLACKJACK!")
        elif player_value == None:
            print(f"Player has busted")
        elif dealer_value == None:
            print(f"Dealer has busted. Everyone in wins")
            game.players[0].balance += game.players[0].current_bet * 2
        elif player_value > dealer_value:
            print(f"Player has won {game.players[0].current_bet}")
            game.players[0].balance += game.players[0].current_bet * 2
        elif player_value == dealer_value:
            print(f"Player has pushed with the dealer")
            game.players[0].balance += game.players[0].current_bet
        elif player_value < dealer_value:
            print(f"Player has lost the hand. Current balance is {game.players[0].balance}")
        
        game.players[0].current_bet = 0
            
        if game.players[0].balance == 0:
            print("Out of money. Restart to play again")
            playGame = False
        game.deckSize(decks) #reshuffle deck if card count is getting low
        game.resetPlayerHands() #reset players' hands 
            
            


if __name__ == "__main__":
    main()
    