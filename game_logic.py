from typing import Optional

import cv2
import pygame
from random import choice
import time

from pygame import Surface

from shared_data import shared_data
from enums.gesture import GestureType
from enums.finger import FingerState


def game_loop(screen: Surface):
    font = pygame.font.SysFont('Arial', 20)
    score_player1 = 0
    score_player2 = 0
    result_display_time = 0

    while True:
        screen.fill((0, 0, 0))
        with shared_data.lock:
            last_valid_gesture1 = shared_data.last_valid_gesture[1]
            last_valid_gesture2 = shared_data.last_valid_gesture[2] if shared_data.player_count == 2 else None
            frame = shared_data.frame
            fingers1 = shared_data.fingers[1]
            fingers2 = shared_data.fingers[2] if shared_data.player_count == 2 else {}
            round_in_progress = shared_data.round_in_progress
            result_texts = shared_data.result_texts

        player2_name = "Компьютер" if shared_data.player_count == 1 else "Игрок 2"
        score_text_player1 = font.render(f"Счет:", True, (255, 255, 255))
        score_text_player1_value = font.render(f"Игрок 1: {score_player1}", True, (255, 255, 255))
        score_text_player2_value = font.render(f"{player2_name}: {score_player2}", True, (255, 255, 255))
        screen.blit(score_text_player1, (650, 20))
        screen.blit(score_text_player1_value, (650, 50))
        screen.blit(score_text_player2_value, (650, 80))

        if frame is not None:
            for fingers in [fingers1, fingers2]:
                for finger_name, finger in fingers.items():
                    color = {
                        FingerState.STRAIGHT: (0, 255, 0),
                        FingerState.BENT: (0, 0, 255),
                        FingerState.INTERMEDIATE: (255, 0, 0)
                    }[finger.state]
                    cv2.circle(frame, (finger.tip_x, finger.tip_y), 5, color, -1)

            frame_surface = pygame.surfarray.make_surface(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            screen.blit(pygame.transform.rotate(frame_surface, -90), (0, 0))

        if shared_data.showing_result:
            if time.time() - result_display_time < 5:
                for i, result_text in enumerate(result_texts):
                    result_surface = font.render(result_text, True, (255, 255, 255))
                    screen.blit(result_surface, (650, 120 + i * 30))
            else:
                shared_data.showing_result = False
                shared_data.gesture = {1: None, 2: None}
                shared_data.last_valid_gesture = {1: None, 2: None}
        else:
            if not round_in_progress and last_valid_gesture1 is not None \
                    and (shared_data.player_count == 1 or last_valid_gesture2 is not None):
                shared_data.round_in_progress = True
                shared_data.countdown_start = time.time()

            if round_in_progress:
                countdown = int(4 - (time.time() - shared_data.countdown_start))
                if countdown > 0:
                    countdown_text = font.render(f"Отсчет: {countdown}", True, (255, 255, 255))
                    screen.blit(countdown_text, (650, 120))
                else:
                    player1_gesture: Optional[GestureType] = last_valid_gesture1
                    if shared_data.player_count == 2:
                        player2_gesture: Optional[GestureType] = last_valid_gesture2
                    else:
                        player2_gesture: Optional[GestureType] = choice(list(GestureType))

                    if player1_gesture == player2_gesture:
                        result = "Ничья"
                    elif (player1_gesture == GestureType.ROCK and player2_gesture == GestureType.SCISSORS) or \
                            (player1_gesture == GestureType.SCISSORS and player2_gesture == GestureType.PAPER) or \
                            (player1_gesture == GestureType.PAPER and player2_gesture == GestureType.ROCK):
                        result = "Игрок 1 выиграл"
                        score_player1 += 1
                    else:
                        result = "Игрок 2 выиграл" if shared_data.player_count == 2 else "Компьютер выиграл"
                        score_player2 += 1

                    shared_data.result_texts = [
                        f"Игрок 1: {player1_gesture.value if player1_gesture is not None else 'Неизвестно'}",
                        f"{'Игрок 2' if shared_data.player_count == 2 else 'Компьютер'}: {player2_gesture.value}",
                        f"Результат: {result}"
                    ]
                    result_display_time = time.time()
                    shared_data.showing_result = True
                    shared_data.round_in_progress = False

        pygame.display.update()
        time.sleep(0.02)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
