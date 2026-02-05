#Random Imported for the card shuffle
import random

#Money user Starts with
money = 1500
# round counter
roundCount = 0

#Method to initialize the game
def initialize_game():
    print("Welcome to Blackjack!")
    ask_round()

#Card Suits
suits = ["H", "D", "C", "S"]
#Card values
values = {
    "A": 11,
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10
}



#Asks the user if they want to start the round
def ask_round():
    global roundCount
    print("Would you like to play a round?")
    x = input("Y or N: ")
    if x == "Y" or x == "y" and money > 0:
        start_round()
        roundCount += 1
    else:
        print("The game has been stopped")



#The round is started
def start_round():
    print("the round has started!")
    handle_money()
    deck = build_deck()
    player_hand = [deck.pop(0), deck.pop(0)]
    dealer_hand = [deck.pop(0), deck.pop(0)]

    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)

    print(f"Player hand: {player_hand} (value: {player_value})")
    print(f"Dealer hand: {dealer_hand} (value: {dealer_value})")


def build_deck():
    deck = []
    for suit in suits:
        for value in values:
            deck.append(value + suit)
    random.shuffle(deck)
    return deck

def calculate_hand_value(hand):
    total = 0
    aces = 0

    for card in hand:
        value = card[:-1]  # everything except the last character (the suit)
        total += values[value]

        if value == "A":
            aces += 1

    # Adjust Aces from 11 → 1 if needed
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total


def game_summary():
    print("YOur summary (placeholder)")
    print(f"Rounds played: {roundCount}")


def handle_money():
    global money
    print("How much money would you like to bet? ")
    betMoney = int(input())

    if money > betMoney:
        money = money - betMoney
        print("Transaction successful! Round Starting.")
    else:
        print("You don't have enough money to bet!")
        ask_round()



initialize_game()