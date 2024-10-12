import threading
import pygame
from pygame import Surface

from hand_tracking import process_hand
from game_logic import game_loop
from shared_data import shared_data


def choose_players(screen: Surface) -> None:
    font = pygame.font.SysFont('Arial', 40)
    button_width, button_height = 200, 50
    button_x = (screen.get_width() - button_width) // 2
    one_player_y = (screen.get_height() // 2) - button_height // 2 - 30
    two_player_y = (screen.get_height() // 2) + button_height // 2 + 10

    while True:
        screen.fill((0, 0, 0))

        pygame.draw.rect(screen, (100, 100, 100), (button_x, one_player_y, button_width, button_height))
        pygame.draw.rect(screen, (100, 100, 100), (button_x, two_player_y, button_width, button_height))

        one_player_text = font.render("1 игрок", True, (255, 255, 255))
        two_player_text = font.render("2 игрока", True, (255, 255, 255))

        screen.blit(one_player_text, (button_x + (button_width - one_player_text.get_width()) // 2, one_player_y))
        screen.blit(two_player_text, (button_x + (button_width - two_player_text.get_width()) // 2, two_player_y))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_x <= event.pos[0] <= button_x + button_width:
                    if one_player_y <= event.pos[1] <= one_player_y + button_height:
                        shared_data.player_count = 1
                        return
                    elif two_player_y <= event.pos[1] <= two_player_y + button_height:
                        shared_data.player_count = 2
                        return


def main():
    pygame.init()
    screen = pygame.display.set_mode((1040, 480))
    pygame.display.set_caption("Камень Ножницы Бумага")
    choose_players(screen)

    hand_thread = threading.Thread(target=process_hand)
    hand_thread.daemon = True
    hand_thread.start()
    game_loop(screen)


if __name__ == "__main__":
    main()
