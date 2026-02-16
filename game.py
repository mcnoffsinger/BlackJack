import pygame
import random
import math
import time

pygame.init()

# -------------------- CONFIG --------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
RED = (180, 0, 0)
GRAY = (70, 70, 70)
DARK = (40, 40, 40)
BLUE = (0, 0, 128)

AI_DIFFICULTIES = ["Easy", "Normal", "Hard"]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BlackJack")

font = pygame.font.Font(None, 26)
big_font = pygame.font.Font(None, 72)

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


# -------------------- GAME LOGIC --------------------
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


def rainbow(t):
    return (
        int(128 + 127 * math.sin(t)),
        int(128 + 127 * math.sin(t + 2)),
        int(128 + 127 * math.sin(t + 4))
    )


# -------------------- DRAWING --------------------
def draw_button(text, x, y, w, h, color=GRAY):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))
    return rect


def draw_dropdown(title, value, options, x, y, w, h, open_menu):
    main = draw_button(f"{title}: {value}", x, y, w, h)
    opts = []
    if open_menu:
        for i, o in enumerate(options):
            r = draw_button(o, x, y - (i + 1) * h, w, h, DARK)
            opts.append((o, r))
    return main, opts


def draw_card(card, x, y, scale_x=1):
    """Draw a card with optional horizontal scale for flip animation."""
    width = int(80 * scale_x)
    r = pygame.Rect(x + (80 - width)//2, y, width, 120)
    if scale_x < 0.2:
        # Draw card back
        pygame.draw.rect(screen, BLUE, r)
        pygame.draw.rect(screen, BLACK, r, 2)
        return
    pygame.draw.rect(screen, WHITE, r)
    pygame.draw.rect(screen, BLACK, r, 2)
    suit_symbols = {'Hearts': ' H', 'Diamonds': ' D', 'Clubs': ' C', 'Spades': ' S'}
    color = RED if card[1] in ['Hearts', 'Diamonds'] else BLACK
    text = f"{card[0]}{suit_symbols[card[1]]}"
    screen.blit(font.render(text, True, color), (r.x + 6, r.y + 6))


# -------------------- GAME CLASS --------------------
class Game:
    def __init__(self):
        self.money = 1500
        self.bet = 100
        self.wins = 0
        self.up_points = 0

        self.roulette = False
        self.ai = "Normal"
        self.ai_open = False

        self.upgrades = {
            "cards": {"lvl": 0, "max": 2},
            "nerves": {"lvl": 0, "max": 3},
            "payout": {"lvl": 0, "max": 3},
        }

        self.reset_round()
        self.lost_screen = False
        self.flipping = False
        self.flip_progress = 0

    def reset_round(self):
        self.deck = create_deck()
        self.player = []
        self.dealer = []
        self.dealt = False
        self.turn = True
        self.over = False
        self.msg = ""
        self.bet = max(10, min(self.bet, self.money))
        self.lost_screen = False
        self.flipping = False
        self.flip_progress = 0

    def deal(self):
        count = 2 + self.upgrades["cards"]["lvl"]
        self.player = [self.deck.pop() for _ in range(count)]
        self.dealer = [self.deck.pop(), self.deck.pop()]
        self.dealt = True
        self.flipping = True
        self.flip_progress = 0

        # Check immediate blackjack
        p = hand_value(self.player)
        d = hand_value(self.dealer)
        if p == 21 and d == 21:
            self.msg = "Both have Blackjack! PUSH"
            self.over = True
        elif p == 21:
            self.msg = "Blackjack! You win!"
            self.money += int(self.bet * 1.5)
            self.over = True
        elif d == 21:
            self.msg = "Dealer has Blackjack!"
            self.money = max(0, self.money - self.bet)
            self.over = True

    def hit(self):
        self.player.append(self.deck.pop())
        if hand_value(self.player) > 21:
            self.lose()

    def stand(self):
        self.finish_dealer()
        p, d = hand_value(self.player), hand_value(self.dealer)
        if d > 21 or p > d:
            self.win()
        elif p < d:
            self.lose()
        else:
            self.msg = "Push"
            self.over = True

    def finish_dealer(self):
        base = {"Easy": 15, "Normal": 17, "Hard": 19}[self.ai]
        base += self.upgrades["nerves"]["lvl"]
        while hand_value(self.dealer) < base:
            self.dealer.append(self.deck.pop())

    def win(self):
        if self.roulette:
            self.money += 1000000
            self.msg = "You survived! +$1,000,000 💰"
            self.over = True
        else:
            mult = 1 + self.upgrades["payout"]["lvl"] * 0.25
            gain = int(self.bet * mult)
            self.money += gain
            self.wins += 1
            if self.wins % 2 == 0:
                self.up_points += 1
            self.msg = f"Win +${gain}"
            self.over = True

    def lose(self):
        if self.roulette:
            if random.random() < 0.5:
                self.money += 1000000
                self.msg = "You survived! +$1,000,000 💰"
            else:
                self.msg = "You died 💥"
                self.money = 0
                self.over = True
        else:
            self.money = max(0, self.money - self.bet)
            self.msg = f"You lost -${self.bet}"
            self.over = True


# -------------------- MAIN LOOP --------------------
def main():
    clock = pygame.time.Clock()
    g = Game()
    start = time.time()
    run = True
    anim_offset = 0

    while run:
        t = time.time() - start
        mouse = pygame.mouse.get_pos()

        if g.money <= 0 and not g.lost_screen:
            if g.dealt:
                g.finish_dealer()
            g.lost_screen = True
            g.over = True

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False

            if e.type == pygame.MOUSEBUTTONDOWN:
                if g.lost_screen:
                    g = Game()
                    continue

                elif not g.dealt:
                    if deal.collidepoint(mouse):
                        g.deal()
                    if bet_up.collidepoint(mouse):
                        g.bet = min(g.money, g.bet + 10)
                    if bet_dn.collidepoint(mouse):
                        g.bet = max(10, g.bet - 10)
                    if all_in.collidepoint(mouse) and g.money > 0:
                        g.bet = g.money
                    if rr.collidepoint(mouse):
                        g.roulette = not g.roulette
                    if ai_btn.collidepoint(mouse):
                        g.ai_open = not g.ai_open
                    for o, r in ai_opts:
                        if r.collidepoint(mouse):
                            g.ai = o
                            g.ai_open = False
                    for key, btn in up_btns.items():
                        if btn.collidepoint(mouse):
                            u = g.upgrades[key]
                            if g.up_points > 0 and u["lvl"] < u["max"]:
                                u["lvl"] += 1
                                g.up_points -= 1
                else:
                    if not g.over:
                        if hit.collidepoint(mouse):
                            g.hit()
                        if stand.collidepoint(mouse):
                            g.stand()
                    else:
                        if nxt.collidepoint(mouse):
                            g.reset_round()

        screen.fill(GREEN)

        # ---------------- GAME OVER SCREEN ----------------
        if g.lost_screen:
            anim_offset += 0.08
            scale = 1 + 0.05 * math.sin(anim_offset)

            # Draw final cards
            for i, c in enumerate(g.dealer):
                draw_card(c, 200 + i * 90, 180)
            for i, c in enumerate(g.player):
                draw_card(c, 200 + i * 90, 360)

            screen.blit(font.render(f"Dealer Final: {hand_value(g.dealer)}", True, WHITE), (200, 150))
            screen.blit(font.render(f"Your Final: {hand_value(g.player)}", True, WHITE), (200, 340))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            loss_text = big_font.render("GAME OVER", True, RED)
            scaled = pygame.transform.rotozoom(loss_text, 0, scale)
            screen.blit(scaled, scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))

            reason = font.render("You have no money left!", True, WHITE)
            screen.blit(reason, reason.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

            sub = font.render("Click to Restart", True, WHITE)
            screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

            pygame.display.flip()
            clock.tick(60)
            continue

        # ---------------- NORMAL GAME ----------------
        screen.blit(big_font.render("BlackJack", True, WHITE), (260, 10))
        screen.blit(font.render(f"Money: ${g.money}", True, WHITE), (20, 80))
        screen.blit(font.render(f"Bet: ${g.bet}", True, WHITE), (20, 110))
        screen.blit(font.render(f"Upgrade Points: {g.up_points}", True, WHITE), (20, 140))

        bet_up = draw_button("+", 140, 105, 30, 30)
        bet_dn = draw_button("-", 180, 105, 30, 30)
        all_in = draw_button("ALL IN", 220, 105, 90, 30, RED)

        if not g.dealt:
            deal = draw_button("DEAL", 120, 260, 160, 60)
            ai_btn, ai_opts = draw_dropdown("AI", g.ai, AI_DIFFICULTIES, 520, 180, 240, 35, g.ai_open)
            rr_col = rainbow(t * 3) if g.roulette else GRAY
            rr = draw_button("Russian BlackJack", 520, 230, 240, 45, rr_col)

            screen.blit(font.render("Upgrades", True, WHITE), (560, 300))
            up_btns = {}
            y = 330
            for k, label in [("cards", "Extra Cards"), ("nerves", "Dealer Nerves"), ("payout", "Bonus Payout")]:
                lvl = g.upgrades[k]["lvl"]
                mx = g.upgrades[k]["max"]
                up_btns[k] = draw_button(f"{label} {lvl}/{mx}", 520, y, 240, 35)
                y += 45

            hit = stand = nxt = pygame.Rect(0, 0, 0, 0)

        else:
            # Card flip animation
            if g.flipping:
                g.flip_progress += 0.08
                if g.flip_progress >= 1:
                    g.flipping = False
                scale_x = abs(math.cos(g.flip_progress * math.pi))
            else:
                scale_x = 1

            for i, c in enumerate(g.dealer):
                draw_card(c, 50 + i * 90, 180, scale_x)
            for i, c in enumerate(g.player):
                draw_card(c, 50 + i * 90, 360, scale_x)

            screen.blit(font.render(f"Dealer: {hand_value(g.dealer)}", True, WHITE), (50, 150))
            screen.blit(font.render(f"Player: {hand_value(g.player)}", True, WHITE), (50, 520))

            if not g.over:
                hit = draw_button("Hit", 300, 530, 80, 40)
                stand = draw_button("Stand", 400, 530, 80, 40)
                nxt = pygame.Rect(0, 0, 0, 0)
            else:
                screen.blit(font.render(g.msg, True, WHITE), (300, 530))
                nxt = draw_button("Next Round", 300, 560, 180, 35)
                hit = stand = pygame.Rect(0, 0, 0, 0)

            deal = rr = ai_btn = pygame.Rect(0, 0, 0, 0)
            ai_opts = []
            up_btns = {}

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
