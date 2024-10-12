import threading

from Finger import Finger
from enums.finger import FingerName
from enums.gesture import GestureType
from typing import Optional, Dict, List


class SharedData:
    def __init__(self) -> None:
        self.gesture: Optional[GestureType] = None
        self.last_valid_gesture: Optional[GestureType] = None
        self.frame: Optional[any] = None
        self.fingers: Dict[FingerName, Finger] = {}
        self.lock: threading.Lock = threading.Lock()
        self.round_in_progress: bool = False
        self.countdown_start: Optional[float] = None
        self.result_texts: List[str] = []
        self.showing_result: bool = False


shared_data = SharedData()
