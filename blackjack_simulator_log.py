import requests
import math
import json
import atexit
import random

# Wipe game log on exit
@atexit.register
def wipe_game_log():
    with open('game_log.json', 'w') as log_file:
        json.dump([], log_file)

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
        self.original_balance = budget  # Store the original balance
        self.balance = budget
        self.current_bet = 0
        self.hand = []
        self.winnings = 0

    def placeBet(self, bet_amount):
        self.current_bet = bet_amount
        self.balance = self.balance - self.current_bet


    def getHandValue(self) -> list:
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
        valid_totals = [total for total in possible_totals if total <= 21]
        
        return sorted(valid_totals) if valid_totals else None
    
    def addCard(self, card):
        self.hand.append(card)
        
    def doubleDown(self):
        self.balance = self.balance - self.current_bet
        self.current_bet *= 2
        
    def split(self):
        # to do
        pass
        
    def Blackjack(self):
        self.balance += math.ceil(self.current_bet * 2.5)
        self.winnings += math.ceil(self.current_bet * 1.5)
    
    def resetHand(self):
        self.hand = []

class BlackJack: 
    def __init__(self):
        self.deck_url = None
        self.deck = None
        self.deck_id = None
        self.num_chips = 0
        self.wager = None
        self.players: list[Player] = [Player(-1)]
        self.num_bots = 0
        self.card_count = None
        self.max_deck = None
        self.game_log = []  # New feature for logging games
        self.hand_log = []  # Log for individual hands within a game
        self.round_active = True  # New attribute to track if the round is active
        self.loss_limit = None  # Loss limit for responsible gambling
        self.current_player_idx = 1
        self.running_count = 0

    def set_loss_limit(self):
        while True:
            try:
                limit = float(input("Enter the loss limit you want to set: "))
                if limit <= 0:
                    print("Please enter a positive value for the loss limit.")
                else:
                    self.loss_limit = limit
                    print(f"Your loss limit is set to {self.loss_limit}.")
                    break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def check_loss_limit(self):
        original_balance = self.players[0].original_balance
        current_balance = self.players[0].balance
        if self.loss_limit is not None and (original_balance - current_balance) >= self.loss_limit:
            print("You have reached your loss limit. Quitting the game for responsible gambling.")
            return True
        return False

    def log_hand(self, result, player_balance):
        # Log the result of each hand
        hand_entry = {
            'result': result,
            'player_balance': player_balance
        }
        self.hand_log.append(hand_entry)

    def log_game(self):
        # Log the entire game
        game_entry = {
            'hands': self.hand_log[:],
            'final_balance': self.players[0].balance
        }
        self.game_log.append(game_entry)
        # Write the game log to a file to persist between sessions
        with open('game_log.json', 'w') as log_file:
            json.dump(self.game_log, log_file, indent=4)
        # Clear the hand log for the next game
        self.hand_log = []

    def load_game_log(self):
        # Load the game log from a file if it exists
        try:
            with open('game_log.json', 'r') as log_file:
                self.game_log = json.load(log_file)
                print("Game Log Loaded Successfully.")
        except FileNotFoundError:
            print("No previous game log found.")

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
        for _ in range(numbots): # append bots with budget 100
            self.players.append(Player(100))

    def deal_cards(self):
        draw_url = f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={1}"
        card = requests.get(draw_url)
        for i in range(2): #will go through twice to deal two cards to each player
            for j in range(self.num_bots + 2): #you are at index 0, dealer is 1 bots take up the rest
                drawn_card = card.json()["cards"][0]  # get the first card from the response
                self.players[j].hand.append(drawn_card)  # append the card to the player's hand
                if j == 0 and len(self.players[j].hand) > 1:
                    if card_value[drawn_card['value']] == '1' or card_value[drawn_card['value']] > 9:
                        self.running_count -= 1
                    elif card_value[drawn_card['value']] < 7:
                        self.running_count += 1
                self.card_count -= 1
        self.current_player_idx = 1
                
    def hit(self, idx):
        draw_url = f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count={1}"
        card = requests.get(draw_url)
        drawn_card = card.json()["cards"][0]
        self.players[idx].hand.append(drawn_card)
        if self.players[idx].getHandValue() == None:
            self.stand(idx)
        self.card_count -= 1
        
    def stand(self, idx):
        if self.current_player_idx == len(self.players) - 1:
            self.current_player_idx = 0
        else:
            self.current_player_idx = idx+1
        
    def doubleDown(self, idx):
        self.players[idx].doubleDown()
        self.hit(idx)
        self.stand(idx)
        self.printHands(True)
        
    def split(self, idx):
        new_hand = Player(self.players[idx].balance)
        self.players[idx].balance -= self.players[idx].current_bet
        split_card = self.players[idx].hand.pop(1)
        new_hand.addCard(split_card)
        self.players.insert(idx, new_hand)

    
    def deckSize(self): #use this to keep track of how many cards are left in the deck
        if self.card_count <= (0.25 * self.max_deck):
            print("time to reshuffle") 

    def printHands(self, hide_dealers):
        for idx, player in enumerate(self.players):
            if idx == 1:
                player_name = "Player"
            elif idx == 0:
                player_name = "Dealer"
            else:
                player_name = f"Player {idx - 1}"
            
            if idx == 1 and hide_dealers:
                card_names = [f"{player.hand[1]['value']} of {player.hand[1]['suit']} and UNKNOWN"]
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
        
        return sorted(valid_totals) if valid_totals else None

    def promptDecision(self, idx):
        while(True):
            try:
                if self.players[idx].hand[0]['value'] == self.players[idx].hand[1]['value']:
                    can_split = True
                    move = int(input("What move would you like to make (1: hit, 2: stay, 3: double down, 4: split): "))
                else:
                    can_split = False
                    move = int(input("What move would you like to make (1: hit, 2: stay, 3: double down): "))

                if move in [1, 2, 3] or (move == 4 and can_split):
                    break
                else:
                    print("Move unavailable")
            except ValueError:
                if can_split:
                    print("Invalid input. Please enter either 1, 2, 3, or 4.")
                else:
                    print("Invalid input. Please enter either 1, 2, or 3.")

        if move == 1:  # hit
            self.hit(idx)
            player_value = self.getMaxScoreFromHand(idx)
            if player_value is None or player_value > 21:
                print("Player has busted.")
                self.round_active = False  # Mark the round as inactive because the player busted
                self.end_game("Loss")
                return 2  # Signal that the player has busted and round must end
            self.printHands(True)
            return 1
        elif move == 2:  # stay
            self.stand()
            return 2
        elif move == 3:  # double down
            self.doubleDown()
            player_value = self.getMaxScoreFromHand(idx)
            if player_value is None or player_value > 21:
                print("Player has busted.")
                self.round_active = False  # Mark the round as inactive because the player busted
                self.end_game("Loss")
                return 2  # Signal that the player has busted and round must end
            return 3
        elif move == 4 and can_split:  # split (if applicable)
            self.split()
            return 4

    
    def revealDealer(self):
        card_names = [f"{card['value']} of {card['suit']}" for card in self.players[1].hand]
        print(f"Dealer's hand: {', '.join(card_names)}")

    def dealerHit(self):

        dealer_value = self.players[0].getHandValue()
        if dealer_value is None:  # If dealer hand is empty or busts, do not proceed
            return
        
        # Check if all players have busted
        if all(player.getHandValue() is None for player in self.players[1:]):  # Exclude dealer
            return  # Exit if every player has busted

        print(f"Dealer's value: {dealer_value}")
        self.printHands(False)

        # Handle soft 17 case
        if dealer_value == 17 and any(card['value'] == 'ACE' for card in self.players[0].hand):
            self.hit(0)
            self.printHands(False)

        dealer_value = self.players[0].getHandValue()
        while dealer_value and max(dealer_value) < 17:
            self.hit(0)
            self.printHands(False)
            dealer_value = self.players[0].getHandValue()
            print(f"Dealer's new value: {dealer_value}")
        
    def getMaxScoreFromHand(self, idx):
        values = self.players[idx].getHandValue()
        print(values)
        if values == None:
            return None
        if len(values) == 1:
            return values[0]
        elif len(values) > 1:
            return max(values)
        

    def end_game(self, result):
        print(f"Round ended with result: {result}")
        player_balance = self.players[1].balance
        self.log_hand(result, player_balance)
        self.log_game()  # Ensure the game log is updated after each game
        self.round_active = False  # Mark the round as inactive
        for player in self.players:
            player.resetHand()

        # Check if loss limit is reached after losing a bet
        if result == "Loss" and self.check_loss_limit():
            print("Under your limit.")

    def view_game_log(self):
        # View the game log after each hand if the player wants to
        view_log = input("Would you like to view the game log? (yes/no): ").lower()
        if view_log == 'yes':
            if not self.game_log:
                print("No games have been played yet.")
            else:
                for idx, entry in enumerate(self.game_log):
                    for hand_idx, hand in enumerate(entry['hands']):
                        print(f"Hand {hand_idx + 1}: Result - {hand['result']}, Player Balance - {hand['player_balance']}")

    def isBlackjack(self, idx):
        has_ace = False
        has_ten = False
        if len(self.players[idx].hand) == 2:
            for card in self.players[idx].hand:
                if card['value'] == 'ACE':
                    has_ace = True
                if card_value[card['value']] == 10:
                    has_ten = True

            return has_ace and has_ten
        
    def end_round(self, isSplit):
        # Determine the outcome
        print(f'num players: {len(self.players)}')
        print(f'players: {self.players}')
        player_value = self.getMaxScoreFromHand(1)
        dealer_value = self.getMaxScoreFromHand(0)

        if isSplit:
            split_value = self.getMaxScoreFromHand(2)
            if split_value == None:
                self.end_game("Loss")
                return "Loss"
            elif dealer_value is None or dealer_value > 21:
                self.players[1].balance += self.players[2].current_bet * 2
                self.end_game("Win")
                return "Win"
            elif split_value > dealer_value:
                self.players[1].balance += self.players[2].current_bet * 2
                self.end_game("Win")
                return "Win"
            elif split_value == dealer_value:
                self.players[1].balance += self.players[2].current_bet
                self.end_game("Push")
                return "Push"
            else:
                self.end_game("Loss")
                return "Loss"

        print(f'dealer_value: {dealer_value}')
        print(f'player_value: {player_value}')
        
        if (player_value == None):
            print(f'Player has lost the hand. Current balance is {self.players[1].balance}')
            self.end_game("Loss")
            return "Loss"
        elif dealer_value is None or dealer_value > 21:
            print("Dealer has busted. Player wins.")
            self.players[1].balance += self.players[1].current_bet * 2
            self.end_game("Win")
            return "Win"
        elif player_value > dealer_value:
            print(f"Player wins with {player_value}")
            self.players[1].balance += self.players[1].current_bet * 2
            self.end_game("Win")
            return "Win"
        elif player_value == dealer_value:
            print(f"Push with the dealer. Player's bet is returned.")
            self.players[1].balance += self.players[1].current_bet
            self.end_game("Push")
            return "Push"
        else:
            print(f"Player has lost the hand. Current balance is {self.players[1].balance}")
            self.end_game("Loss")
            return "Loss"


def main():
    playGame = True
    game = BlackJack()
    game.load_game_log()  # Load previous game log if available
    decks = game.getDeckAmount()  # 0 or 1. 1 means don't play anymore
    if decks == 1:
        print("Thanks for playing")
        playGame = False

    game.getBalanceAmount()
    game.set_loss_limit()  # Set the loss limit for responsible gambling
    game.getBotAmount()

    while playGame:
        game.round_active = True  # Reactivate the round before starting a new one
        game.deal_cards()
        l = len(game.players)

        game.getBetAmount(0)
        if not game.round_active:
            break
        game.printHands(True)

        # Player's turn
        for idx in range(l):
            if idx == 1:  
                continue
            if idx != 0:
                continue

            # Check if player has blackjack at the start
            if game.isBlackjack(idx):
                print("BLACKJACK!")
                game.players[idx].Blackjack()
                game.round_active = False
                game.end_game("Blackjack")
                break

            # Player makes moves until they stay or bust
            while game.round_active:
                move = game.promptDecision(idx)
                if move == 2:  # Player chooses to stay
                    break
                elif move == 3:  # Player doubles down
                    break

            if not game.round_active:  # If the player busted, end the round
                break

        # Dealer's turn
        if game.round_active:
            game.revealDealer()
            game.dealerHit()

            game.end_round()

        # Reset bet for the next round
        game.players[0].current_bet = 0

        # Check if player is out of money
        if game.players[0].balance == 0:
            print("Out of money. Restart to play again")
            playGame = False

        game.view_game_log()



if __name__ == "__main__":
    main()
