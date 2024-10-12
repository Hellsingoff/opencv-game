from enum import Enum


class FingerName(Enum):
    INDEX = 1
    MIDDLE = 2
    RING = 3
    PINKY = 4


class FingerState(Enum):
    BENT = 1
    STRAIGHT = 2
    INTERMEDIATE = 3
