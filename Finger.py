from enums.finger import FingerState


class Finger:
    def __init__(self, tip_x: int, tip_y: int, state: FingerState):
        self.tip_x: int = tip_x
        self.tip_y: int = tip_y
        self.state: FingerState = state
