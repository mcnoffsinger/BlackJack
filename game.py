import pygame
import random
import math
import time

pygame.init()

# -------------------- CONFIG --------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 40, 40)
GREEN = (22, 92, 45)       # deep casino green
GOLD = (255, 215, 0)
GRAY = (70, 70, 70)
DARK = (40, 40, 40)
BLUE = (0, 0, 128)

AI_DIFFICULTIES = ["Easy", "Normal", "Hard"]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("BlackJack")

font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 80)

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


# -------------------- TABLE TEXTURE --------------------
table_texture = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
table_texture.fill(GREEN)

# subtle felt grid pattern
for i in range(0, SCREEN_WIDTH, 40):
    pygame.draw.line(table_texture, (18, 80, 38), (i, 0), (i, SCREEN_HEIGHT))
for j in range(0, SCREEN_HEIGHT, 40):
    pygame.draw.line(table_texture, (18, 80, 38), (0, j), (SCREEN_WIDTH, j))


# -------------------- VIGNETTE LIGHTING --------------------
vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
for i in range(200):
    alpha = int(180 * (i / 200))
    pygame.draw.rect(
        vignette,
        (0, 0, 0, alpha),
        (i, i, SCREEN_WIDTH - 2 * i, SCREEN_HEIGHT - 2 * i),
        1
    )


# -------------------- UTILITY FUNCTIONS --------------------
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


# -------------------- GRAPHICS: BUTTONS --------------------
def draw_button(text, x, y, w, h, color=GRAY):
    rect = pygame.Rect(x, y, w, h)

    # glossy gradient
    top = pygame.Surface((w, h // 2), pygame.SRCALPHA)
    bottom = pygame.Surface((w, h // 2), pygame.SRCALPHA)
    top.fill((min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255)))
    bottom.fill(color)

    pygame.draw.rect(screen, color, rect, border_radius=10)
    screen.blit(top, (x, y))
    screen.blit(bottom, (x, y + h // 2))
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)

    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))
    return rect


# -------------------- GRAPHICS: DROPDOWN --------------------
def draw_dropdown(title, value, options, x, y, w, h, open_menu):
    main = draw_button(f"{title}: {value}", x, y, w, h)
    opts = []
    if open_menu:
        for i, o in enumerate(options):
            r = draw_button(o, x, y - (i + 1) * h, w, h, DARK)
            opts.append((o, r))
    return main, opts


# -------------------- GRAPHICS: CARDS --------------------
def draw_card(card, x, y, scale_x=1):
    width = int(80 * scale_x)
    height = 120
    r = pygame.Rect(x + (80 - width) // 2, y, width, height)

    # card back during flip
    if scale_x < 0.2:
        shadow = pygame.Rect(r.x + 4, r.y + 4, width, height)
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow, border_radius=8)
        pygame.draw.rect(screen, BLUE, r, border_radius=8)
        pygame.draw.rect(screen, BLACK, r, 2, border_radius=8)
        return

    # shadow
    shadow = pygame.Rect(r.x + 4, r.y + 4, width, height)
    pygame.draw.rect(screen, (0, 0, 0, 80), shadow, border_radius=8)

    # card face
    pygame.draw.rect(screen, WHITE, r, border_radius=8)
    pygame.draw.rect(screen, BLACK, r, 2, border_radius=8)

    suit_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
    color = RED if card[1] in ['Hearts', 'Diamonds'] else BLACK

    rank = font.render(card[0], True, color)
    suit = font.render(suit_symbols[card[1]], True, color)

    screen.blit(rank, (r.x + 8, r.y + 6))
    screen.blit(suit, (r.x + 8, r.y + 28))

# -------------------- GAME CLASS --------------------
class Game:
    def __init__(self):
        self.money = 1500
        self.bet = 100
        self.wins = 0
        self.up_points = 0

        # mode toggles
        self.roulette = False
        self.ai = "Normal"
        self.ai_open = False

        # upgrade system
        self.upgrades = {
            "cards": {"lvl": 0, "max": 2},
            "nerves": {"lvl": 0, "max": 3},
            "payout": {"lvl": 0, "max": 3},
        }

        # round state
        self.reset_round()
        self.lost_screen = False
        self.flipping = False
        self.flip_progress = 0

        # ---------------- RUSSIAN ROULETTE STATE ----------------
        self.rr_running = False
        self.rr_anim = 0
        self.rr_result = None

        self.rr_multiplier = 1
        self.rr_streak = 0

        self.burn_popup = ""
        self.burn_timer = 0

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

        # reset roulette state
        self.rr_running = False
        self.rr_anim = 0
        self.rr_result = None

    # ---------------- RUSSIAN ROULETTE ----------------
    def play_russian_roulette(self):
        self.rr_running = True
        self.rr_anim = 0
        self.rr_result = None

        # 1 bullet in 6 chambers
        chamber = random.randint(1, 6)

        # delay reveal for animation
        pygame.time.set_timer(pygame.USEREVENT + 1, 1200, loops=1)

        # store result
        self.rr_result = (chamber == 1)

    # ---------------- NORMAL BLACKJACK ----------------
    def deal(self):
        if self.roulette:
            self.play_russian_roulette()
            self.dealt = True
            return
# Reworked Extra Cards: Instead of more cards, we "re-roll" the start
        # Level 0: 1 attempt, Level 1: 2 attempts, Level 2: 3 attempts
        attempts = 1 + self.upgrades["cards"]["lvl"]
        best_hand = []
        best_value = 0

        for _ in range(attempts):
            # Temporary deck for simulation to avoid draining the real deck
            temp_deck = self.deck[:]
            random.shuffle(temp_deck)
            test_hand = [temp_deck.pop(), temp_deck.pop()]
            test_val = hand_value(test_hand)

            # Keep the hand if it's better than current best but not bust
            if test_val > best_value and test_val <= 21:
                best_hand = test_hand
                best_value = test_val


        # Apply the best hand found and remove those specific cards from the actual deck
        self.player = best_hand
        for card in self.player:
            if card in self.deck:
                self.deck.remove(card)

       
        self.dealer = [self.deck.pop(), self.deck.pop()]
        self.dealt = True
        self.flipping = True
        self.flip_progress = 0

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
        if self.roulette:
            return
        self.player.append(self.deck.pop())
        if hand_value(self.player) > 21:
            self.lose()

    def stand(self):
        if self.roulette:
            return
        self.finish_dealer()
        p, d = hand_value(self.player), hand_value(self.dealer)

        if d > 21 or p > d:
            self.win()
        elif p < d:
            self.lose()
        else:
            if self.msg == "":
                self.msg = "Push"
            self.over = True

    def finish_dealer(self):
        if self.roulette:
            return

        nerves_level = self.upgrades["nerves"]["lvl"]
        nerves_chance = {0: 0, 1: 0.3, 2: 0.6, 3: 0.9}[nerves_level]

        # dealer stress mechanic
        if nerves_chance > 0 and len(self.dealer) > 1 and random.random() < nerves_chance:
            burned_card = random.choice(self.dealer[1:])
            self.dealer.remove(burned_card)

            #  popup indicator
            self.burn_popup = f"Dealer burned {burned_card[0]}!"
            self.burn_timer = 60  # lasts ~1 second at 60 FPS

            # keep original message (optional)
            self.msg = f"Dealer stressed out! Card {burned_card[0]} burned 🔥"

        base = {"Easy": 15, "Normal": 17, "Hard": 19}[self.ai]
        base += nerves_level

        while hand_value(self.dealer) < base:
            self.dealer.append(self.deck.pop())

    def win(self):
        if self.roulette:
            self.money += 1000000
            self.msg = "Click... You survived! +$1,000,000"
            self.over = True
            return

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
            self.msg = "💥 BANG! You died!"
            self.money = 0
            self.over = True
            return

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

        # ---------------- MONEY ZERO → GAME OVER ----------------
        if g.money <= 0 and not g.lost_screen:
            if g.dealt:
                g.finish_dealer()
            g.lost_screen = True
            g.over = True

        # ---------------- EVENT HANDLING ----------------
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False

            # ROULETTE RESULT EVENT
            if e.type == pygame.USEREVENT + 1 and g.rr_running:

                if g.rr_result:  # player died
                    g.msg = "💥 BANG! You died!"
                    g.money = 0
                    g.rr_multiplier = 1
                    g.rr_streak = 0

                else:  # survived
                    g.rr_streak += 1
                    g.rr_multiplier = 2 ** g.rr_streak
                    winnings = 1000000 * g.rr_multiplier

                    g.msg = f"Click... You survived! +${winnings:,} (x{g.rr_multiplier})"
                    g.money += winnings

                g.over = True
                g.rr_running = False

            # ---------------- MOUSE CLICK ----------------
            if e.type == pygame.MOUSEBUTTONDOWN:

                # Restart from game over
                if g.lost_screen:
                    g = Game()
                    continue

                # BEFORE DEALING
                if not g.dealt:
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

                # AFTER DEALING
                else:
                    if not g.over:
                        if not g.roulette:
                            if hit.collidepoint(mouse):
                                g.hit()
                            if stand.collidepoint(mouse):
                                g.stand()
                    else:
                        if nxt.collidepoint(mouse):
                            g.reset_round()

        # ---------------- DRAW TABLE BACKGROUND ----------------
        screen.blit(table_texture, (0, 0))

        # ---------------- GAME OVER SCREEN ----------------
        if g.lost_screen:
            anim_offset += 0.08
            scale = 1 + 0.05 * math.sin(anim_offset)

            # final cards
            for i, c in enumerate(g.dealer):
                draw_card(c, 200 + i * 90, 180)
            for i, c in enumerate(g.player):
                draw_card(c, 200 + i * 90, 360)

            # text
            screen.blit(font.render(f"Dealer Final: {hand_value(g.dealer)}", True, WHITE), (200, 150))
            screen.blit(font.render(f"Your Final: {hand_value(g.player)}", True, WHITE), (200, 340))

            # dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            # animated GAME OVER
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

        # ---------------- NORMAL GAME UI ----------------

        # title with glow
        title = big_font.render("BLACKJACK", True, GOLD)
        glow = big_font.render("BLACKJACK", True, GOLD)
        screen.blit(glow, (258, 12))
        screen.blit(title, (260, 10))

        # HUD
        screen.blit(font.render(f"Money: ${g.money}", True, WHITE), (20, 80))
        screen.blit(font.render(f"Bet: ${g.bet}", True, WHITE), (20, 110))
        screen.blit(font.render(f"Upgrade Points: {g.up_points}", True, WHITE), (20, 140))

        # betting buttons
        bet_up = draw_button("+", 140, 105, 30, 30)
        bet_dn = draw_button("-", 180, 105, 30, 30)
        all_in = draw_button("ALL IN", 220, 105, 90, 30, RED)

        # ---------------- BEFORE DEAL ----------------
        if not g.dealt:
            deal = draw_button("DEAL", 120, 260, 160, 60)
            ai_btn, ai_opts = draw_dropdown("AI", g.ai, AI_DIFFICULTIES, 520, 180, 240, 35, g.ai_open)

            # RR Multiplier indicator
            if g.rr_multiplier > 1:
                txt = font.render(f"Roulette Multiplier: x{g.rr_multiplier}", True, (255, 200, 120))
                screen.blit(txt, (520, 150))

            rr_col = rainbow(t * 3) if g.roulette else GRAY
            rr = draw_button("Russian Roulette", 520, 230, 240, 45, rr_col)

            # upgrades
            screen.blit(font.render("Upgrades", True, WHITE), (560, 300))
            up_btns = {}
            y = 330
            for k, label in [
                ("cards", "Starting Luck"),
                ("nerves", "Dealer Nerves"),
                ("payout", "Bonus Payout")
            ]:
                lvl = g.upgrades[k]["lvl"]
                mx = g.upgrades[k]["max"]
                up_btns[k] = draw_button(f"{label} {lvl}/{mx}", 520, y, 240, 35)
                y += 45

            hit = stand = nxt = pygame.Rect(0, 0, 0, 0)
        # ---------------- AFTER DEAL ----------------
        else:

            # ---------------- ROULETTE ANIMATION ----------------
            if g.roulette and g.rr_running:
                g.rr_anim += 0.2
                angle = int(g.rr_anim * 40) % 360

                center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

                # cylinder body
                pygame.draw.circle(screen, (60, 60, 60), center, 130)
                pygame.draw.circle(screen, (20, 20, 20), center, 130, 6)

                # center metal
                pygame.draw.circle(screen, (100, 100, 100), center, 40)

                # chambers
                for i in range(6):
                    a = math.radians(i * 60 + angle)
                    cx = center[0] + math.cos(a) * 70
                    cy = center[1] + math.sin(a) * 70
                    pygame.draw.circle(screen, (180, 180, 180), (int(cx), int(cy)), 25)
                    pygame.draw.circle(screen, (40, 40, 40), (int(cx), int(cy)), 25, 4)

                rr_title = big_font.render("Russian Roulette", True, WHITE)
                screen.blit(rr_title, rr_title.get_rect(center=(SCREEN_WIDTH // 2, 80)))


                pygame.display.flip()
                clock.tick(60)
                continue

            # ---------------- NORMAL BLACKJACK RENDERING ----------------
            if g.flipping:
                g.flip_progress += 0.08
                if g.flip_progress >= 1:
                    g.flipping = False
                scale_x = abs(math.cos(g.flip_progress * math.pi))
            else:
                scale_x = 1

            # dealer cards (centered row)
            dealer_start_x = SCREEN_WIDTH // 2 - (len(g.dealer) * 90) // 2
            for i, c in enumerate(g.dealer):
                draw_card(c, dealer_start_x + i * 90, 180, scale_x)

            # player cards (centered row)
            player_start_x = SCREEN_WIDTH // 2 - (len(g.player) * 90) // 2
            for i, c in enumerate(g.player):
                draw_card(c, player_start_x + i * 90, 360, scale_x)

            # Dealer Nerves popup indicator
            if g.burn_timer > 0:
                popup = font.render(g.burn_popup, True, (255, 120, 120))
                screen.blit(popup, popup.get_rect(center=(SCREEN_WIDTH // 2, 140)))
                g.burn_timer -= 1

            # values
            screen.blit(font.render(f"Dealer: {hand_value(g.dealer)}", True, WHITE), (50, 150))
            screen.blit(font.render(f"Player: {hand_value(g.player)}", True, WHITE), (50, 520))

            # action buttons
            if not g.over:
                hit = draw_button("Hit", SCREEN_WIDTH // 2 - 120, 530, 100, 40)
                stand = draw_button("Stand", SCREEN_WIDTH // 2 + 20, 530, 100, 40)
                nxt = pygame.Rect(0, 0, 0, 0)
            else:
                msg = font.render(g.msg, True, WHITE)
                screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 520)))

                nxt = draw_button("Next Round", SCREEN_WIDTH // 2 - 90, 560, 180, 40)
                hit = stand = pygame.Rect(0, 0, 0, 0)

            deal = rr = ai_btn = pygame.Rect(0, 0, 0, 0)
            ai_opts = []
            up_btns = {}

        # ---------------- FINAL TOUCH: VIGNETTE ----------------


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# -------------------- PROGRAM ENTRY --------------------
if __name__ == "__main__":
    main()
