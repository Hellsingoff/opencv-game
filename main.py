import threading
from hand_tracking import process_hand
from game_logic import game_loop

if __name__ == "__main__":
    hand_thread = threading.Thread(target=process_hand)
    hand_thread.daemon = True
    hand_thread.start()
    game_loop()
