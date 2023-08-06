from enum import Enum

class Alert(Enum):
	SHOULD_RESET = 0
	SHOULD_WATER = 1
	LOW_TEMPERATURE = 2
	HIGH_TEMPERATURE = 3
