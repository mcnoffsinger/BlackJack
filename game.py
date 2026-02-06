import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
RED = (180, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BlackJack")

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    deck = [(rank, suit) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck

def card_value(card):
    rank = card[0]
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11
    return int(rank)

def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for c in hand if c[0] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def draw_card(card, x, y):
    rect = pygame.Rect(x, y, 80, 120)
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

    rank, suit = card
    color = RED if suit in ['Hearts', 'Diamonds'] else BLACK
    suit_symbol = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}[suit]

    screen.blit(font.render(rank, True, color), (x + 5, y + 5))
    screen.blit(font.render(suit_symbol, True, color), (x + 30, y + 50))

def draw_hidden_card(x, y):
    rect = pygame.Rect(x, y, 80, 120)
    pygame.draw.rect(screen, (0, 0, 128), rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

def draw_button(text, x, y, w, h):
    pygame.draw.rect(screen, (70, 70, 70), (x, y, w, h))
    pygame.draw.rect(screen, WHITE, (x, y, w, h), 2)
    surf = font.render(text, True, WHITE)
    screen.blit(surf, surf.get_rect(center=(x + w // 2, y + h // 2)))
    return pygame.Rect(x, y, w, h)

class BlackJackGame:
    def __init__(self):
        self.money = 1500
        self.bet = 100
        self.roulette_mode = False
        self.reset_round()

    def reset_round(self):
        self.deck = create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.player_turn = True
        self.game_over = False
        self.message = ""
        self.dealt = False

    def deal(self):
        if self.money <= 0:
            return
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.dealt = True
        if hand_value(self.player_hand) == 21:
            self.stand()

    def hit(self):
        if self.player_turn and not self.game_over:
            self.player_hand.append(self.deck.pop())
            if hand_value(self.player_hand) > 21:
                if self.roulette_mode:
                    self.message = "BANG! You busted and the dealer shot you! 💥"
                    self.money = 0
                else:
                    self.message = "Bust! You lose!"
                    self.money -= self.bet
                self.game_over = True

    def stand(self):
        self.player_turn = False
        while hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())

        p = hand_value(self.player_hand)
        d = hand_value(self.dealer_hand)

        if d > 21 or p > d:
            self.message = "You win!"
            self.money += self.bet
        elif p < d:
            if self.roulette_mode:
                self.message = "BANG! Dealer shoots you! 💥"
                self.money = 0
            else:
                self.message = "Dealer wins!"
                self.money -= self.bet
        else:
            self.message = "Push!"

        self.game_over = True

    def change_bet(self, amt):
        if not self.dealt:
            self.bet = max(10, min(self.money, self.bet + amt))

def main():
    clock = pygame.time.Clock()
    game = BlackJackGame()
    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game.dealt:
                    if deal_btn.collidepoint(mouse):
                        game.deal()
                    elif bet_up_btn.collidepoint(mouse):
                        game.change_bet(10)
                    elif bet_down_btn.collidepoint(mouse):
                        game.change_bet(-10)
                    elif roulette_btn.collidepoint(mouse):
                        game.roulette_mode = not game.roulette_mode

                elif not game.game_over:
                    if hit_btn.collidepoint(mouse):
                        game.hit()
                    elif stand_btn.collidepoint(mouse):
                        game.stand()

                else:
                    if new_round_btn.collidepoint(mouse):
                        game = BlackJackGame() if game.money <= 0 else game.reset_round() or game

        screen.fill(RED if game.game_over and game.money <= 0 else GREEN)

        screen.blit(big_font.render("BlackJack", True, WHITE),
                    (SCREEN_WIDTH // 2 - 150, 10))
        screen.blit(font.render(f"Money: ${game.money}", True, WHITE), (20, 80))
        screen.blit(font.render(f"Bet: ${game.bet}", True, WHITE), (20, 120))

        if not game.dealt:
            screen.blit(font.render("Betting Menu", True, WHITE), (300, 200))
            deal_btn = draw_button("Deal", 300, 260, 100, 50)
            bet_up_btn = draw_button("+$10", 150, 115, 60, 30)
            bet_down_btn = draw_button("-$10", 220, 115, 60, 30)
            roulette_btn = draw_button(
                f"Russian Roulette: {'ON' if game.roulette_mode else 'OFF'}",
                430, 260, 300, 50
            )
            hit_btn = stand_btn = new_round_btn = pygame.Rect(0, 0, 0, 0)

        else:
            screen.blit(font.render("Dealer:", True, WHITE), (50, 170))
            for i, c in enumerate(game.dealer_hand):
                if i == 0 and game.player_turn:
                    draw_hidden_card(50 + i * 90, 200)
                else:
                    draw_card(c, 50 + i * 90, 200)

            screen.blit(font.render("Player:", True, WHITE), (50, 360))
            for i, c in enumerate(game.player_hand):
                draw_card(c, 50 + i * 90, 390)

            if not game.game_over:
                hit_btn = draw_button("Hit", 300, 530, 80, 50)
                stand_btn = draw_button("Stand", 400, 530, 80, 50)
                new_round_btn = pygame.Rect(0, 0, 0, 0)
            else:
                screen.blit(font.render(game.message, True, WHITE),
                            (SCREEN_WIDTH // 2 - 200, 520))
                new_round_btn = draw_button(
                    "Restart" if game.money <= 0 else "New Round",
                    320, 560, 160, 40
                )
                hit_btn = stand_btn = pygame.Rect(0, 0, 0, 0)

            deal_btn = bet_up_btn = bet_down_btn = roulette_btn = pygame.Rect(0, 0, 0, 0)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
