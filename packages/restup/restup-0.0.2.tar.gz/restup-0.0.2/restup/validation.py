from enum import Enum, unique, auto

class Validation(Enum):
    ANY = auto()
    NONE = auto()
    EQUALS = auto()