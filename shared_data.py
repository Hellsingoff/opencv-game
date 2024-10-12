import threading
from typing import Optional, Dict, List

from Finger import Finger
from enums.finger import FingerName
from enums.gesture import GestureType


class SharedData:
    def __init__(self):
        self.gesture: Dict[int, Optional[GestureType]] = {1: None, 2: None}
        self.last_valid_gesture: Dict[int, Optional[GestureType]] = {1: None, 2: None}
        self.frame: Optional[any] = None
        self.fingers: Dict[int, Dict[FingerName, Finger]] = {1: {}, 2: {}}
        self.lock: threading.Lock = threading.Lock()
        self.round_in_progress: bool = False
        self.countdown_start: Optional[float] = None
        self.result_texts: List[str] = []
        self.showing_result: bool = False
        self.player_count: int = 1


shared_data = SharedData()
