from item import Item
from conveyorbelt import Conveyorbelt

# Baustein Verzweigungselement

class Splitter:

    def __init__(self, name: str, to_conveyorbelts: list, transfer_time: float ):

        self.name = name
        self.to_conveyorbelts = to_conveyorbelts
        self.transfer_time = transfer_time
        self.current_lane = to_conveyorbelts[0].lane
        self.item = None 
        self.target = None
        self.release_at = 0.0 
        self.rr_counter = 0

    # belegt wenn item drin, frei wenn kein item drin
    def is_open(self,model):

        return self.item is None 

    def get_target_conveyorbelt(self,model):

        if model.operating_parameter.routing_mode == "TARGET":
            for conveyorbelt in self.to_conveyorbelts:
                if conveyorbelt.lane == model.operating_parameter.target_lane: # suche nach lane die ausgewählt wurde
                    return conveyorbelt
            
        else: # rr
            index = self.rr_counter % len(self.to_conveyorbelts)
            conveyorbelt = self.to_conveyorbelts[index]
            self.rr_counter +=1
            return conveyorbelt

    def take_item(self, item: Item, from_conveyorbelt: Conveyorbelt, model):

        # wenn belegt, förderband erkennt das mit reached_end
        if not self.is_open(model=model):
            model.last_event = "ITEM_WAITING_AT_SPLITTER"
            return
        
        target = self.get_target_conveyorbelt(model=model) 
        from_conveyorbelt.item_list.remove(item) 
        item.lane = target.lane  
        item.position = 0.0 
        self.item = item 
        self.target = target 
        self.current_lane = target.lane 
        self.release_at = model.simulation_time + self.transfer_time 
        model.last_event = "ITEM_ROUTED_TO_NEXT_LANE"

    def update(self,model):
            # wenn item in splitter ist und transferzeit vorbei
        if self.item is not None and model.simulation_time >= self.release_at:
            self.target.item_list.append(self.item) # dann im splitter gespeichertes item and das neue förderbandobjekt 
            self.item = None


