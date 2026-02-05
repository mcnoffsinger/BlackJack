import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

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
    else:
        return int(rank)

def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card[0] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def draw_card(card, x, y):
    card_rect = pygame.Rect(x, y, 80, 120)
    pygame.draw.rect(screen, WHITE, card_rect)
    pygame.draw.rect(screen, BLACK, card_rect, 2)
    
    rank, suit = card
    color = RED if suit in ['Hearts', 'Diamonds'] else BLACK
    
    rank_text = font.render(rank, True, color)
    suit_symbol = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}[suit]
    suit_text = font.render(suit_symbol, True, color)
    
    screen.blit(rank_text, (x + 5, y + 5))
    screen.blit(suit_text, (x + 30, y + 50))

def draw_hidden_card(x, y):
    card_rect = pygame.Rect(x, y, 80, 120)
    pygame.draw.rect(screen, (0, 0, 128), card_rect)
    pygame.draw.rect(screen, BLACK, card_rect, 2)

def draw_button(text, x, y, w, h, hover=False):
    color = (100, 100, 100) if hover else (70, 70, 70)
    pygame.draw.rect(screen, color, (x, y, w, h))
    pygame.draw.rect(screen, WHITE, (x, y, w, h), 2)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
    screen.blit(text_surf, text_rect)
    return pygame.Rect(x, y, w, h)

class BlackJackGame:
    def __init__(self):
        self.money = 1500
        self.bet = 100
        self.reset_round()
    
    def reset_round(self):
        self.deck = create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.player_turn = True
        self.message = ""
        self.dealt = False
    
    def deal(self):
        if self.bet > self.money:
            self.bet = self.money
        if self.money <= 0:
            self.message = "Game Over - Out of money!"
            return
        
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.dealt = True
        
        if hand_value(self.player_hand) == 21:
            self.stand()
    
    def hit(self):
        if not self.game_over and self.player_turn and self.dealt:
            self.player_hand.append(self.deck.pop())
            if hand_value(self.player_hand) > 21:
                self.message = "Bust! You lose!"
                self.money -= self.bet
                self.game_over = True
    
    def stand(self):
        if not self.game_over and self.dealt:
            self.player_turn = False
            while hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())
            
            player_val = hand_value(self.player_hand)
            dealer_val = hand_value(self.dealer_hand)
            
            if dealer_val > 21:
                self.message = "Dealer busts! You win!"
                self.money += self.bet
            elif player_val > dealer_val:
                self.message = "You win!"
                self.money += self.bet
            elif player_val < dealer_val:
                self.message = "Dealer wins!"
                self.money -= self.bet
            else:
                self.message = "Push!"
            
            self.game_over = True
    
    def change_bet(self, amount):
        if not self.dealt:
            self.bet = max(10, min(self.money, self.bet + amount))

def main():
    clock = pygame.time.Clock()
    game = BlackJackGame()
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game.dealt:
                    if deal_btn.collidepoint(mouse_pos):
                        game.deal()
                    elif bet_up_btn.collidepoint(mouse_pos):
                        game.change_bet(10)
                    elif bet_down_btn.collidepoint(mouse_pos):
                        game.change_bet(-10)
                elif not game.game_over:
                    if hit_btn.collidepoint(mouse_pos):
                        game.hit()
                    elif stand_btn.collidepoint(mouse_pos):
                        game.stand()
                else:
                    if new_round_btn.collidepoint(mouse_pos):
                        if game.money > 0:
                            game.reset_round()
                        else:
                            game = BlackJackGame()
        
        screen.fill(GREEN)
        
        title = big_font.render("BlackJack", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 10))
        
        money_text = font.render(f"Money: ${game.money}", True, WHITE)
        screen.blit(money_text, (20, 80))
        
        bet_text = font.render(f"Bet: ${game.bet}", True, WHITE)
        screen.blit(bet_text, (20, 120))
        
        if not game.dealt:
            deal_btn = draw_button("Deal", 300, 300, 100, 50)
            bet_up_btn = draw_button("+$10", 150, 115, 60, 30)
            bet_down_btn = draw_button("-$10", 220, 115, 60, 30)
            hit_btn = pygame.Rect(0, 0, 0, 0)
            stand_btn = pygame.Rect(0, 0, 0, 0)
            new_round_btn = pygame.Rect(0, 0, 0, 0)
        else:
            dealer_label = font.render("Dealer:", True, WHITE)
            screen.blit(dealer_label, (50, 170))
            
            for i, card in enumerate(game.dealer_hand):
                if i == 0 and game.player_turn and not game.game_over:
                    draw_hidden_card(50 + i * 90, 200)
                else:
                    draw_card(card, 50 + i * 90, 200)
            
            if not game.player_turn or game.game_over:
                dealer_val = font.render(f"Value: {hand_value(game.dealer_hand)}", True, WHITE)
                screen.blit(dealer_val, (50 + len(game.dealer_hand) * 90 + 20, 250))
            
            player_label = font.render("Player:", True, WHITE)
            screen.blit(player_label, (50, 360))
            
            for i, card in enumerate(game.player_hand):
                draw_card(card, 50 + i * 90, 390)
            
            player_val = font.render(f"Value: {hand_value(game.player_hand)}", True, WHITE)
            screen.blit(player_val, (50 + len(game.player_hand) * 90 + 20, 440))
            
            if not game.game_over:
                hit_btn = draw_button("Hit", 300, 530, 80, 50)
                stand_btn = draw_button("Stand", 400, 530, 80, 50)
                new_round_btn = pygame.Rect(0, 0, 0, 0)
                deal_btn = pygame.Rect(0, 0, 0, 0)
                bet_up_btn = pygame.Rect(0, 0, 0, 0)
                bet_down_btn = pygame.Rect(0, 0, 0, 0)
            else:
                msg = font.render(game.message, True, WHITE)
                screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 530))
                btn_text = "New Round" if game.money > 0 else "Restart"
                new_round_btn = draw_button(btn_text, 320, 560, 120, 40)
                hit_btn = pygame.Rect(0, 0, 0, 0)
                stand_btn = pygame.Rect(0, 0, 0, 0)
                deal_btn = pygame.Rect(0, 0, 0, 0)
                bet_up_btn = pygame.Rect(0, 0, 0, 0)
                bet_down_btn = pygame.Rect(0, 0, 0, 0)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
