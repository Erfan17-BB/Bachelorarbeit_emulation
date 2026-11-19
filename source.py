from conveyorbelt import Conveyorbelt
from item import Item

# Baustein Quelle

class Source: 

    def __init__(self, name:str, conveyorbelt : Conveyorbelt, gap_zone: float):

        self.name = name
        self.conveyorbelt = conveyorbelt
        self.gap_zone = gap_zone # Sperrbereich
        self.items_created = 0

    def gap_zone_is_free(self):
        # letztes item in sperrbereich
        for item in self.conveyorbelt.item_list:
            if item.position < self.gap_zone:
                return False
            
        return True 

    def update(self,model):

        # volle periode
        steps_per_item = round(model.operating_parameter.item_creation_period
                               / model.step_size) #500 steps

        if model.step_counter % steps_per_item == 0: 
            if self.gap_zone_is_free():
                self.items_created +=1
                item = Item(item_id=self.items_created, lane=self.conveyorbelt.lane, position=0.0)
                self.conveyorbelt.item_list.append(item)
                model.last_event = "ITEM_CREATED"
        
        
        

