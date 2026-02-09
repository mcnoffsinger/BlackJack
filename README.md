# BlackJack
## Team Members
* Samuel Taiwo
* Jessica Kamienski
* Karan Modi
* Maxwell Noffsinger
## Game Overview
In this virtual blackjack game, players will compete with a dealer to win money by playing BlackJack. The player begins with 1500 dollars to bet and can gain or lose money according to their bet each round. If the player reaches 0 or decides to stop playing, the game ends and a summary is printed to the screen. There are modifiers and different game modes for the player to interct with.
## Game Type
Card Game
## Core Mechanics
1. Player can Stand or Hit each round to play BlackJack
2. Full Deck of cards is simulated to correctly deal random cards
3. Player can customize their bet at the start of each round
4. Pygame visuals (if we can get it to work)
5. Player can double down or surrender

## How to Run
### How to Run
* Python 3.8+
* Pygame Downloaded

### Steps
1. Clone or download this repo
2. Open terminal/command prompt (perferably Pycharm or VScode)
3. Navigate to the project folder
4. Download Pygame
```python
python -m pip install pygame-ce
```
5. Run
```python
Game.py
```
6. Follow on-screen prompts

## Win & Lose Conditions
### Win
* If the user gets a hand with the value of 21
* If the user gets a hand with a value higher than the dealer but not over 21
### Lose
* If the user gets a hand over the value of 21
* if the player gets a hand with a value lower than the dealer and the dealer's value is not over 21

## Controls / Input
User will only use their mouse clicker to make descisions during the game.

## Design Decisions
### Why we chose BlackJack
* Concepts of BlackJack are fimiliar within the whole team
* Can be coded easily with Pygame within a IDE. (Not a lot of problems)
