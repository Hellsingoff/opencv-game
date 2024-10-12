import cv2
import pygame
import random
import time
from shared_data import shared_data
from enums.gesture import GestureType
from enums.finger import FingerState
from typing import Optional


def game_loop() -> None:
    pygame.init()
    screen_width, screen_height = 1040, 480
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Камень Ножницы Бумага")
    font = pygame.font.SysFont('Arial', 20)
    score_player = 0
    score_computer = 0
    result_display_time = 0

    while True:
        screen.fill((0, 0, 0))
        with shared_data.lock:
            last_valid_gesture: Optional[GestureType] = shared_data.last_valid_gesture
            frame = shared_data.frame
            fingers = shared_data.fingers
            round_in_progress = shared_data.round_in_progress
            result_texts = shared_data.result_texts

        score_text = font.render(f"Счет - Игрок: {score_player} Компьютер: {score_computer}", True, (255, 255, 255))
        screen.blit(score_text, (650, 20))

        if frame is not None:
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
                    screen.blit(result_surface, (650, 80 + i * 30))
            else:
                shared_data.showing_result = False
                shared_data.gesture = None
                shared_data.last_valid_gesture = None
        else:
            if not round_in_progress and last_valid_gesture is not None:
                shared_data.round_in_progress = True
                shared_data.countdown_start = time.time()

            if round_in_progress:
                countdown = int(3 - (time.time() - shared_data.countdown_start))
                if countdown > 0:
                    countdown_text = font.render(f"Отсчет: {countdown}", True, (255, 255, 255))
                    screen.blit(countdown_text, (650, 50))
                else:
                    player_gesture = last_valid_gesture
                    computer_gesture = random.choice(list(GestureType))

                    if player_gesture == computer_gesture:
                        result = "Ничья"
                    elif (player_gesture == GestureType.ROCK and computer_gesture == GestureType.SCISSORS) or \
                            (player_gesture == GestureType.SCISSORS and computer_gesture == GestureType.PAPER) or \
                            (player_gesture == GestureType.PAPER and computer_gesture == GestureType.ROCK):
                        result = "Игрок выиграл"
                        score_player += 1
                    else:
                        result = "Компьютер выиграл"
                        score_computer += 1

                    shared_data.result_texts = [
                        f"Игрок: {player_gesture.value if player_gesture is not None else 'Неизвестно'}",
                        f"Компьютер: {computer_gesture.value}",
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
