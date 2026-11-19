from conveyorbelt import Conveyorbelt

# Baustein Sensor

class Sensor:

    def __init__(self, name: str, position: float, conveyorbelt: Conveyorbelt, detection_range: float):


        self.name = name
        self.position = position
        self.conveyorbelt = conveyorbelt
        self.detection_range = detection_range
        self.state = False

    def detect(self) -> bool:
        
        self.state = False

        for item in self.conveyorbelt.item_list:
            if round(abs(item.position - self.position),3) <= self.detection_range:
                self.state = True
                return
            

