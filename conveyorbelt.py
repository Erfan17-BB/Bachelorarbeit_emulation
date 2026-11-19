from item import Item

# Förderbandklasse

class Conveyorbelt:

    def __init__(self, name: str, lane : int, length: float, transfer_to):

        self.name = name
        self.lane = lane
        self.length = length 
        self.transfer_to = transfer_to
        self.item_list =  []
        
    # items bewegen um 0.01
    def move_item(self, item : Item, model) -> None: 
                                                     
        new_position = round((item.position + model.operating_parameter.speed * model.step_size),6)
        # bei übertritt
        if new_position > self.length:
            new_position = self.length
    
        item.position = new_position

    # wenn bandende erreicht
    def reached_end(self) -> bool:

        if len(self.item_list) == 0:
            return False
        else:
            return self.item_list[0].position >= self.length

    def update(self,model):

        if self.reached_end(): # vorderstes item ist am ende
            self.transfer_to.take_item(item=self.item_list[0], from_conveyorbelt = self, model=model)
            return

        # items werden bewegt
        for item in self.item_list.copy():
            self.move_item(item=item, model=model)

            if item.position >= self.length: # falls ein item nachdem es bewegt wurde jetzt vor dem nachfolger steht
                self.transfer_to.take_item(item=self.item_list[0], from_conveyorbelt = self, model=model)



        