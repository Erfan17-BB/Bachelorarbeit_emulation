from conveyorbelt import Conveyorbelt
from item import Item

# Baustein Senke

class Sink:

    def __init__(self, name:str ):

        self.name = name
        self.items_received = 0

    def take_item(self, from_conveyorbelt : Conveyorbelt, item: Item, model):

        from_conveyorbelt.item_list.remove(item)
        self.items_received +=1
        model.last_event = "ITEM_LEFT_SYSTEM"

    def update(self,model):
        pass