import pygame
import random

pygame.init()

# -------------------- CONFIG --------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
RED = (180, 0, 0)
GRAY = (70, 70, 70)
BLUE = (0, 0, 128)

AI_DIFFICULTIES = ["Easy", "Normal", "Hard"]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BlackJack")

font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 72)

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


# -------------------- CARD LOGIC --------------------
def create_deck():
    deck = [(rank, suit) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck


def card_value(card):
    if card[0] in ['J', 'Q', 'K']:
        return 10
    if card[0] == 'A':
        return 11
    return int(card[0])


def hand_value(hand):
    value = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[0] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


# -------------------- DRAWING --------------------
def draw_card(card, x, y):
    rect = pygame.Rect(x, y, 80, 120)
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

    rank, suit = card
    color = RED if suit in ['Hearts', 'Diamonds'] else BLACK
    symbol = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}[suit]

    screen.blit(font.render(rank, True, color), (x + 5, y + 5))
    screen.blit(font.render(symbol, True, color), (x + 30, y + 50))


def draw_hidden_card(x, y):
    rect = pygame.Rect(x, y, 80, 120)
    pygame.draw.rect(screen, BLUE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)


def draw_button(text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, GRAY, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))
    return rect


# -------------------- GAME CLASS --------------------
class BlackJackGame:
    def __init__(self):
        self.money = 1500
        self.bet = 100

        # Permanent upgrades
        self.up_extra_card = False
        self.up_dealer_nerves = False
        self.up_bonus_payout = False

        self.ai_difficulty = "Normal"
        self.reset_round()

    def reset_round(self):
        self.deck = create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.dealt = False
        self.player_turn = True
        self.game_over = False
        self.message = ""

    def deal(self):
        if self.money <= 0:
            return

        cards = 3 if self.up_extra_card else 2
        self.player_hand = [self.deck.pop() for _ in range(cards)]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.dealt = True

        if hand_value(self.player_hand) == 21:
            self.stand()

    def hit(self):
        if self.player_turn and not self.game_over:
            self.player_hand.append(self.deck.pop())
            if hand_value(self.player_hand) > 21:
                self.money -= self.bet
                self.message = "Bust!"
                self.game_over = True

    def stand(self):
        self.player_turn = False

        base_stand = {"Easy": 15, "Normal": 17, "Hard": 19}[self.ai_difficulty]
        if self.up_dealer_nerves:
            base_stand += 1

        while hand_value(self.dealer_hand) < base_stand:
            self.dealer_hand.append(self.deck.pop())

        p, d = hand_value(self.player_hand), hand_value(self.dealer_hand)

        if d > 21 or p > d:
            payout = int(self.bet * (1.5 if self.up_bonus_payout else 1))
            self.money += payout
            self.message = f"You win! +${payout}"
        elif p < d:
            self.money -= self.bet
            self.message = "Dealer wins!"
        else:
            self.message = "Push!"

        self.game_over = True


# -------------------- MAIN LOOP --------------------
def main():
    clock = pygame.time.Clock()
    game = BlackJackGame()
    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game.dealt:
                    if deal_btn.collidepoint(mouse):
                        game.deal()
                    if up1.collidepoint(mouse):
                        game.up_extra_card = not game.up_extra_card
                    if up2.collidepoint(mouse):
                        game.up_dealer_nerves = not game.up_dealer_nerves
                    if up3.collidepoint(mouse):
                        game.up_bonus_payout = not game.up_bonus_payout
                else:
                    if not game.game_over:
                        if hit_btn.collidepoint(mouse):
                            game.hit()
                        if stand_btn.collidepoint(mouse):
                            game.stand()
                    else:
                        if new_btn.collidepoint(mouse):
                            game.reset_round()

        screen.fill(GREEN)

        screen.blit(big_font.render("BlackJack", True, WHITE), (260, 10))
        screen.blit(font.render(f"Money: ${game.money}", True, WHITE), (20, 80))
        screen.blit(font.render(f"Bet: ${game.bet}", True, WHITE), (20, 110))

        if not game.dealt:
            deal_btn = draw_button("Deal", 330, 240, 140, 50)

            screen.blit(font.render("Permanent Upgrades", True, WHITE), (290, 300))
            up1 = draw_button(f"Extra Card: {'ON' if game.up_extra_card else 'OFF'}", 240, 340, 320, 40)
            up2 = draw_button(f"Dealer Nerves: {'ON' if game.up_dealer_nerves else 'OFF'}", 240, 390, 320, 40)
            up3 = draw_button(f"Bonus Payout: {'ON' if game.up_bonus_payout else 'OFF'}", 240, 440, 320, 40)

            hit_btn = stand_btn = new_btn = pygame.Rect(0, 0, 0, 0)

        else:
            screen.blit(font.render("Dealer", True, WHITE), (50, 160))
            for i, c in enumerate(game.dealer_hand):
                if i == 0 and game.player_turn:
                    draw_hidden_card(50 + i * 90, 190)
                else:
                    draw_card(c, 50 + i * 90, 190)

            if not game.player_turn:
                screen.blit(font.render(f"Value: {hand_value(game.dealer_hand)}", True, WHITE), (50, 320))

            screen.blit(font.render("Player", True, WHITE), (50, 340))
            for i, c in enumerate(game.player_hand):
                draw_card(c, 50 + i * 90, 370)

            screen.blit(font.render(f"Value: {hand_value(game.player_hand)}", True, WHITE), (50, 500))

            if not game.game_over:
                hit_btn = draw_button("Hit", 320, 530, 80, 40)
                stand_btn = draw_button("Stand", 420, 530, 80, 40)
                new_btn = pygame.Rect(0, 0, 0, 0)
            else:
                screen.blit(font.render(game.message, True, WHITE), (320, 530))
                new_btn = draw_button("New Round", 310, 560, 180, 35)
                hit_btn = stand_btn = pygame.Rect(0, 0, 0, 0)

            deal_btn = up1 = up2 = up3 = pygame.Rect(0, 0, 0, 0)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
