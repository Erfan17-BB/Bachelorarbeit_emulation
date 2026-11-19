from kpi import Kpi
from operating_parameter import OperatingParameter
from conveyorbelt import Conveyorbelt
from splitter import Splitter
from sink import Sink
from sensor import Sensor
from source import Source

# Virtuelles Modell

class VirtualModel:

    def __init__(self):

        self.step_size = 0.01 # 0.01s Schrittweite
        self.operating_parameter = OperatingParameter() # mit Standardparametrisierung
        self.kpi = Kpi()

        self.state = "STOPPED"
        self.step_counter = 0
        self.simulation_time = 0.0
        self.last_event = "MODEL_INIT"

        # Referenzförderbandsystem : source, main, splitter, sub1, sub2, sub3, sink1, sink2, sink3

        self.sink1 = Sink(name="sink1")
        self.sink2 = Sink(name="sink2")
        self.sink3 = Sink(name="sink3")

        self.sub1 = Conveyorbelt(name="sub1", lane=1, length=5.0, transfer_to=self.sink1)
        self.sub2 = Conveyorbelt(name="sub2", lane=2, length=5.0, transfer_to=self.sink2)
        self.sub3 = Conveyorbelt(name="sub3", lane=3, length=5.0, transfer_to=self.sink3)

        self.splitter = Splitter(name="splitter", to_conveyorbelts=[self.sub1,self.sub2,self.sub3], transfer_time=1.0)

        self.main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=self.splitter)

        self.source = Source(name="source", conveyorbelt=self.main, gap_zone=0.3)

        self.order = [self.sink3,self.sink2,self.sink1, self.sub3, self.sub2, self.sub1, self.splitter, self.main, self.source]

        self.main_entry_sensor = Sensor(name="main_entry_sensor", position=0.1, conveyorbelt=self.main, detection_range=0.03)
        self.main_exit_sensor = Sensor(name="main_exit_sensor", position=5.0, conveyorbelt=self.main, detection_range=0.03)

        self.sub1_entry_sensor = Sensor(name="sub1_entry_sensor", position=0.1, conveyorbelt=self.sub1, detection_range=0.03)
        self.sub2_entry_sensor = Sensor(name="sub2_entry_sensor", position=0.1, conveyorbelt=self.sub2, detection_range=0.03)
        self.sub3_entry_sensor = Sensor(name="sub3_entry_sensor", position=0.1, conveyorbelt=self.sub3, detection_range=0.03)

        self.sub1_exit_sensor = Sensor(name="sub1_exit_sensor", position=5.0, conveyorbelt=self.sub1, detection_range=0.03)
        self.sub2_exit_sensor = Sensor(name="sub2_exit_sensor", position=5.0, conveyorbelt=self.sub2, detection_range=0.03)
        self.sub3_exit_sensor = Sensor(name="sub3_exit_sensor", position=5.0, conveyorbelt=self.sub3, detection_range=0.03)

        self.sensor_list = [self.main_entry_sensor, self.main_exit_sensor,
                            self.sub1_entry_sensor,self.sub2_entry_sensor,self.sub3_entry_sensor,
                            self.sub1_exit_sensor, self.sub2_exit_sensor,self.sub3_exit_sensor]
        
        self.conveyorbelt_list = [self.main, self.sub1,self.sub2,self.sub3]

        self.source_list = [self.source]
        self.splitter_list = [self.splitter]
        self.sink_list = [self.sink1, self.sink2, self.sink3]

        self.check_composition()

    def check_composition(self): 

         # 1. jede quelle genau vor einem band 
        for source in self.source_list:
              if source.conveyorbelt not in self.conveyorbelt_list:
                   raise ValueError

        # 2. jede senke liegt am ende von genau einem band
        for sink in self.sink_list:
             amount = 0
             for conveyorbelt in self.conveyorbelt_list:
                  if conveyorbelt.transfer_to is sink:
                       amount +=1
             if amount != 1:
                  raise ValueError

        # 3. jedes band hat genau einen Nachfolger, und das ist kein band 
        for conveyorbelt in self.conveyorbelt_list:
             if conveyorbelt.transfer_to is None:
                  raise ValueError
             if isinstance(conveyorbelt.transfer_to, Conveyorbelt):
                  raise ValueError

        # 4. jeder splitter hat genau ein eingehendes band und mindestens 2 ausgehende 
        for splitter in self.splitter_list: 
             amount = 0
             for conveyorbelt in self.conveyorbelt_list:
                  if conveyorbelt.transfer_to is splitter:
                    amount +=1
             if amount != 1:
                  raise ValueError
             if len(splitter.to_conveyorbelts) < 2:
                  raise ValueError
             for conveyorbelt in splitter.to_conveyorbelts:
                  if conveyorbelt not in self.conveyorbelt_list:
                       raise ValueError

        # 4 checks auf grenzen
    def check_operating_parameter(self, speed:float, item_creation_period: float, routing_mode: str, target_lane : int) -> bool:

        if speed < self.operating_parameter.min_speed or speed > self.operating_parameter.max_speed:
                 return False
        
        if item_creation_period < self.operating_parameter.min_item_creation_period or item_creation_period > self.operating_parameter.max_item_creation_period:
                 return False
        
        if routing_mode != "ROUND_ROBIN" and routing_mode != "TARGET":
                 return False

        valid_target_lane = False
        for conveyorbelt in self.splitter.to_conveyorbelts:
            if conveyorbelt.lane == target_lane:
                valid_target_lane = True


        if not valid_target_lane:
            return False
                 
        return True
    # erst zustand betriebszustand prüfen, dann check der grenzen, wenn valid -> alle 4 übernehmen
    def update_operating_parameter_when_stopped(self, new_speed:float, new_item_creation_period: float, new_routing_mode: str, new_target_lane : int):
                 
            if self.state != "STOPPED":
                      self.last_event = "NEW_PARAMETERS_ONLY_WHEN_STOPPED"
                      return
            if not self.check_operating_parameter(speed=new_speed, item_creation_period=new_item_creation_period, routing_mode=new_routing_mode, target_lane=new_target_lane):
                    self.last_event = "INVALID_PARAMETER"
                    return

            # alle werden überschrieben
            self.operating_parameter.speed = new_speed
            self.operating_parameter.item_creation_period = new_item_creation_period
            self.operating_parameter.routing_mode = new_routing_mode
            self.operating_parameter.target_lane = new_target_lane
            self.last_event = "PARAMETER_UPDATED"

     # betriebsfunktion
    # reset
    def reset_model(self):
         self.state = "STOPPED"
         self.step_counter = 0
         self.simulation_time = 0.0
         self.last_event = "MODEL_GOT_RESET"

         for conveyorbelt in self.conveyorbelt_list:
              conveyorbelt.item_list = []

         self.splitter.item = None
         self.splitter.target = None
         self.splitter.release_at = 0.0
         self.splitter.rr_counter = 0 

         self.source.items_created = 0
         self.sink1.items_received = 0
         self.sink2.items_received = 0
         self.sink3.items_received = 0

         self.operating_parameter = OperatingParameter()
         self.kpi = Kpi()
         
         self.update_sensors()


            
    def command_run(self):
        self.state = "RUNNING"
        self.last_event = "COMMAND_RUN_PRESSED"

    def command_stop(self):
            self.state = "STOPPED"
            self.last_event = "COMMAND_STOP_PRESSED"




    def update_sensors(self):
         for sensor in self.sensor_list:
              sensor.detect()


    def all_current_items(self) -> list:

        item_list = []

        for conveyorbelt in self.conveyorbelt_list:
            for item in conveyorbelt.item_list:
                item_list.append(item)
        if self.splitter.item is not None : # wenn item drin
            item_list.append(self.splitter.item)
        return item_list

    # sucht in quellen, senken, listen
    def update_kpis(self):
         self.kpi.created_items = self.source.items_created
         self.kpi.wip = len(self.all_current_items())
         self.kpi.tp_1 = self.sink1.items_received
         self.kpi.tp_2 = self.sink2.items_received
         self.kpi.tp_3 = self.sink3.items_received
         self.kpi.tp_all = self.kpi.tp_1 + self.kpi.tp_2 + self.kpi.tp_3


    def simulation_step(self):

         if self.state == "RUNNING":
              self.step_counter+=1
              self.simulation_time = round((self.simulation_time + self.step_size),3)
              # sonst springt er direkt raus, zählt nix

              for component in self.order:
                   component.update(model=self) 


         self.update_sensors()
         self.update_kpis()

    


