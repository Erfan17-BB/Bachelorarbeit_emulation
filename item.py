from dataclasses import dataclass

# Itemklasse

@dataclass
class Item: 

    item_id : int = 0
    lane : int = 0
    position : float = 0.0