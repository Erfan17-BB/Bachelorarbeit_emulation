from dataclasses import dataclass

# Betriebsparameter, die vom Dt eingestellt

@dataclass
class OperatingParameter: 
    # Ausgangswerte
    speed : float = 1.0 # m/s
    item_creation_period : float = 5.0 # s
    routing_mode : str = "ROUND_ROBIN" # default rr, ansonsten targetlane
    target_lane : int = 1

    # grenzwertbereich 
    min_speed : float = 0.1
    max_speed : float = 3.0 
    min_item_creation_period : float = 1.0
    max_item_creation_period : float = 60.0

