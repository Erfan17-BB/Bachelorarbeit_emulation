import pytest
from item import Item
from conveyorbelt import Conveyorbelt
from virtual_model import VirtualModel
from sink import Sink
from source import Source
from sensor import Sensor
from splitter import Splitter

# move_item test
def test_move_item():

    model = VirtualModel()
    conveyorbelt = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to = None)
    item1 = Item(item_id=1, lane=0, position=0.0)
    item2 = Item(item_id=2, lane=0, position=0.0)
    item3 = Item(item_id=3, lane=0, position=4.98)

    # 1 step 
    # speed*step_size = 1.0 * 0.01 = 0.01
    conveyorbelt.move_item(item=item1, model=model)
    assert item1.position == 0.01

    # 100 steps = 1.0
    
    for i in range(100):
        conveyorbelt.move_item(item=item2, model=model)

    assert item2.position == 1.0

    # letzter step übertritt
    # bandende mit 3.0 speed -> 0.03 step -> 5.01
    model.operating_parameter.speed = 3.0
    conveyorbelt.move_item(item=item3, model=model)

    assert item3.position == 5.0

# reached_end test 
def test_reached_end():

    conveyorbelt = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to= None)
    item = Item(item_id=1, lane=0, position=5.0)
    conveyorbelt.item_list = [item]


    assert conveyorbelt.reached_end() is True

    item.position = 4.8
    assert conveyorbelt.reached_end() is False

    conveyorbelt2 = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to= None)
    assert conveyorbelt2.reached_end() is False

    conveyorbelt3 = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to= None)
    item3 = Item(item_id=1, lane=0, position=5.01)
    conveyorbelt.item_list = [item3]

    assert conveyorbelt.reached_end() is True

# take item sink test
def test_take_item():

    model = VirtualModel()
    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=None)
    item = Item(item_id=1,lane="main", position= 5.0)
    main.item_list = [item]
    sink = Sink(name="sink")

    assert len(main.item_list) == 1
    sink.take_item(from_conveyorbelt=main, item=item, model=model)

    assert sink.items_received == 1
    assert model.last_event == "ITEM_LEFT_SYSTEM"
    assert len(main.item_list) == 0

# gapzone blockiert
def test_gap_zone_is_free_blocked():

    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=None)
    item = Item(item_id=1,lane="main", position= 0.29)
    item2 = Item(item_id=1,lane="main", position= 0.3)
    main.item_list = [item,item2]
    source = Source(name="source", conveyorbelt=main, gap_zone=0.3)
    

    assert source.gap_zone_is_free() is False

# gapzone frei
def test_gap_zone_is_free_open():

    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=None)
    item = Item(item_id=1,lane="main", position= 0.31)
    main.item_list = [item]
    source = Source(name="source", conveyorbelt=main, gap_zone=0.3)
    

    assert source.gap_zone_is_free() is True

# source update 499 und 500 steps
def test_update_source():

    model = VirtualModel()
    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=None)
    source = Source(name="source", conveyorbelt=main,gap_zone=0.3)

    # periode 5.0 : 0.01 = 500 steps pro item
    # 500,1000,1500 stepcounter % 500 -> create item
    model.step_counter = 499
    source.update(model=model)

    assert source.items_created == 0

    model.step_counter = 500

    source.update(model=model)
    assert source.items_created == 1

    assert len(main.item_list) == 1
    assert main.item_list[0].item_id == 1
    assert main.item_list[0].lane == 0 
    assert main.item_list[0].position == 0.0 
    assert model.last_event == "ITEM_CREATED" 

# source update item in gapzone
def test_update_source_gapzone_blocked():

    model = VirtualModel()
    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=None)
    source = Source(name="source", conveyorbelt=main,gap_zone=0.3) 
    item = Item(item_id=1, lane=0,position=0.29)
    main.item_list = [item]
    model.step_counter = 500

    source.update(model=model)

    assert source.items_created == 0

# source update item ausserhalb gapzone
def test_update_source_gapzone_free():

    model = VirtualModel()
    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=None)
    source = Source(name="source", conveyorbelt=main,gap_zone=0.3) 
    item = Item(item_id=1, lane=0,position=0.31)
    main.item_list = [item]
    model.step_counter = 500

    source.update(model=model)

    assert source.items_created == 1

# sensor detects position 0.1 range 0.03 -> 0.07 - 0.13
def test_sensor_detect_in_range():

    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=None)
    item = Item(item_id=1, lane=0,position=0.07)
    main.item_list = [item]
    sensor = Sensor(name="sensor1", position=0.1, conveyorbelt=main, detection_range=0.03)

    sensor.detect()
    assert sensor.state is True

    item.position = 0.13
    sensor.detect()
    assert sensor.state is True

    item.position = 0.14
    sensor.detect()
    assert sensor.state is False

# sensor detects position 5.0 range 0.03 -> 4,97 - 5
def test_sensor_detect_in_range_exit():

    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=None)
    item = Item(item_id=1, lane=0,position=4.96)
    main.item_list = [item]
    sensor = Sensor(name="sensor1", position=5.0, conveyorbelt=main, detection_range=0.03)

    sensor.detect()
    assert sensor.state is False

    item.position = 4.97
    sensor.detect()
    assert sensor.state is True

    item.position = 5.0
    sensor.detect()
    assert sensor.state is True

# splitter tests 

# get target conveyorbelt rr
def test_splitter_get_target_conveyorbelt_rr():

    sub1 = Conveyorbelt(name="sub1", lane=1, length=5.0, transfer_to=None)
    sub2 = Conveyorbelt(name="sub2", lane=2, length=5.0, transfer_to=None)
    sub3 = Conveyorbelt(name="sub3", lane=3, length=5.0, transfer_to=None)
    splitter = Splitter(name="splitter", to_conveyorbelts=[sub1,sub2,sub3], transfer_time=1.0)
    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=splitter)
    model = VirtualModel() 

    assert splitter.get_target_conveyorbelt(model=model) is sub1 # index = 0%3 = R0 -> [0] -> lane1 -> rr+=1
    assert splitter.get_target_conveyorbelt(model=model) is sub2 # index = 1%3 = R1 -> [1] -> lane2 -> rr+1...
    assert splitter.get_target_conveyorbelt(model=model) is sub3
    assert splitter.get_target_conveyorbelt(model=model) is sub1 # index = 3%3 = R0 -> [0] -> Lane 1 
    assert splitter.rr_counter == 4

# get target conveyorbelt target 1
def test_splitter_get_target_conveyorbelt_target_lane_1():

    sub1 = Conveyorbelt(name="sub1", lane=1, length=5.0, transfer_to=None)
    sub2 = Conveyorbelt(name="sub2", lane=2, length=5.0, transfer_to=None)
    sub3 = Conveyorbelt(name="sub3", lane=3, length=5.0, transfer_to=None)
    splitter = Splitter(name="splitter", to_conveyorbelts=[sub1,sub2,sub3], transfer_time=1.0)
    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=splitter)
    model = VirtualModel()
    model.operating_parameter.routing_mode = "TARGET"
    model.operating_parameter.target_lane = 1

    assert splitter.get_target_conveyorbelt(model=model) is sub1 

# splitter takes item + routes nach release
def test_splitter_takes_item():

    sub1 = Conveyorbelt(name="sub1", lane=1, length=5.0, transfer_to=None)
    sub2 = Conveyorbelt(name="sub2", lane=2, length=5.0, transfer_to=None)
    sub3 = Conveyorbelt(name="sub3", lane=3, length=5.0, transfer_to=None)
    splitter = Splitter(name="splitter", to_conveyorbelts=[sub1,sub2,sub3], transfer_time=1.0)
    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=splitter)
    model = VirtualModel()  

    # 500 steps
    model.simulation_time = 5.0
    item = Item(item_id=1, lane=0, position=5.0)
    main.item_list = [item]

    assert splitter.is_open(model=model) is True
    splitter.take_item(item=item, from_conveyorbelt=main, model=model)

    assert main.item_list == []
    assert splitter.item is item # item in splitter gespeichert
    assert splitter.target is sub1
    assert sub1.item_list == [] # noch leer, erst mit update wird item in neue liste hinzugefügt
    assert item.lane == 1
    assert item.position == 0.0
    assert splitter.current_lane == 1
    assert splitter.release_at == 5.0 + 1.0
    assert model.last_event == "ITEM_ROUTED_TO_NEXT_LANE"
    assert splitter.is_open(model=model) is False

    # release
    model.simulation_time = 6.0
    splitter.update(model=model)

    assert splitter.item is None # splitter hat kein item mehr
    assert sub1.item_list == [item] # jetzt ist es hinzugefügt auf neuem förderband
    assert item.position == 0.0 
    assert splitter.is_open(model=model) is True

# splitter blocked test
def test_splitter_takes_item_while_blocked():

    sub1 = Conveyorbelt(name="sub1", lane=1, length=5.0, transfer_to=None)
    sub2 = Conveyorbelt(name="sub2", lane=2, length=5.0, transfer_to=None)
    sub3 = Conveyorbelt(name="sub3", lane=3, length=5.0, transfer_to=None)
    splitter = Splitter(name="splitter", to_conveyorbelts=[sub1,sub2,sub3], transfer_time=1.0)
    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=splitter)
    model = VirtualModel()  

    # 500 steps
    model.simulation_time = 5.0
    item = Item(item_id=1, lane=0, position=5.0)
    main.item_list = [item]

    item_in_splitter = Item(item_id=1, lane=0, position=0.0)
    splitter.item = item_in_splitter
    splitter.target = sub1
    splitter.release_at = 6.0

    # splitter blockiert weil item noch drin
    splitter.take_item(item=item, from_conveyorbelt=main, model=model)
    assert model.last_event == "ITEM_WAITING_AT_SPLITTER"
    assert splitter.item is item_in_splitter
    assert splitter.item is not item
    assert item in main.item_list
    assert item not in sub1.item_list
    assert item not in sub2.item_list
    assert item not in sub3.item_list
    assert splitter.rr_counter == 0
    

# conveyorbelt update test 
# move item mit korrekter speed: 
def test_conveyorbelt_update():

    model = VirtualModel()
    sink = Sink(name="sink")
    conveyorbelt = Conveyorbelt(name="sub2", lane=2, length=5.0, transfer_to=sink)
    item = Item(item_id=1, lane=2, position=0.0)
    item2 = Item(item_id=2, lane=2, position=0.5)
    conveyorbelt.item_list = [item,item2]

    conveyorbelt.update(model=model)
    assert conveyorbelt.item_list[0].position == 0.01
    assert conveyorbelt.item_list[1].position == 0.51

# band stoppt wenn splitter blockiert ist
def test_conveyorbelt_update_while_splitter_blocked():

    model = VirtualModel()

    sub1 = Conveyorbelt(name="sub1", lane=1, length=5.0, transfer_to=None)
    sub2 = Conveyorbelt(name="sub2", lane=2, length=5.0, transfer_to=None)
    sub3 = Conveyorbelt(name="sub3", lane=3, length=5.0, transfer_to=None)

    splitter = Splitter(name="splitter", to_conveyorbelts=[sub1,sub2,sub3], transfer_time=1.0)

    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=splitter)

    blocking_item = Item(item_id=0, lane=0, position=0.0)
    splitter.item = blocking_item
    splitter.target = sub1
    splitter.release_at = 5.0

    # item reached end
    waiting_item = Item(item_id=1, lane=0, position=5.0)
    item_behind_waiting_item = Item(item_id=2, lane=0, position=0.0)
    main.item_list = [waiting_item,item_behind_waiting_item]

    main.update(model=model)
    main.update(model=model)
    main.update(model=model)
    # item hat noch die gleiche pos
    assert waiting_item.position == 5.0
    assert item_behind_waiting_item.position == 0.0

# splitter nimmt item und band bewegt items
def test_conveyor_update_when_splitter_free():

    model = VirtualModel()

    sub1 = Conveyorbelt(name="sub1", lane=1, length=5.0, transfer_to=None)
    sub2 = Conveyorbelt(name="sub2", lane=2, length=5.0, transfer_to=None)
    sub3 = Conveyorbelt(name="sub3", lane=3, length=5.0, transfer_to=None)

    splitter = Splitter(name="splitter", to_conveyorbelts=[sub1,sub2,sub3], transfer_time=1.0)

    main = Conveyorbelt(name="main", lane=0, length=5.0, transfer_to=splitter)

    blocking_item = Item(item_id=0, lane=0, position=0.0)
    splitter.item = blocking_item
    splitter.target = sub1
    splitter.release_at = 5.0 

    # item reached end
    waiting_item = Item(item_id=1, lane=0, position=5.0)
    item_behind_waiting_item = Item(item_id=2, lane=0, position=0.0)
    main.item_list = [waiting_item,item_behind_waiting_item]

    # splitter noch blockiert
    main.update(model=model)

    # splitter hat item gerouted und ist wieder frei
    model.simulation_time = 5.0
    splitter.update(model=model) 
    assert blocking_item in sub1.item_list # got routed correctly
    assert splitter.is_open(model=model) is True

    # next step : item von splitter genommen
    main.update(model=model)

    assert waiting_item.lane == 1
    assert waiting_item not in main.item_list
    assert splitter.item is waiting_item # waiting item now in splitter

    # items auf band bewegen sich nicht
    assert item_behind_waiting_item.position == 0.0 

    # next step items bewegen sich wieder
    main.update(model=model)
    assert item_behind_waiting_item.position == 0.01


# test check composition : jede quelle genau vor einem band
def test_check_comp_source_no_conveyorbelt():

    model = VirtualModel()
    model.source.conveyorbelt = None

    with pytest.raises(ValueError):
        model.check_composition()
# test check composition : jede senke am ende von einem band
def test_check_comp_sink_two_conveyorbelts():

    # 2 subs transferto auf sink1
    model = VirtualModel()
    model.sub2.transfer_to = model.sink1

    with pytest.raises(ValueError):
        model.check_composition()

# test check composition : band ohne nachfolger
def test_check_comp_conveyorbelt_without_successor():

    model = VirtualModel()
    model.conveyorbelt_list.append(Conveyorbelt(name="weiteres", lane=4, length=5.0, transfer_to=None))

    with pytest.raises(ValueError):
        model.check_composition()


# test check composition : 2 bänder hintereinander 
def test_check_comp_conveyorbelt_with_conveyorbelts():

    model = VirtualModel()
    # main -> sub1
    model.main.transfer_to = model.sub1

    with pytest.raises(ValueError):
        model.check_composition()

# test splitter 2 eingehende bänder
def test_check_comp_splitter_two_incoming_conveyorbelts():

    model = VirtualModel()
    # zweites band auch an splitter
    model.conveyorbelt_list.append(Conveyorbelt(name="weiteres", lane=4, length=5.0, transfer_to=model.splitter))

    with pytest.raises(ValueError):
        model.check_composition()

# test splitter nur ein ausgehendes band 
def test_check_comp_splitter_one_out_going_conveyorbelt():

    model = VirtualModel()
    model.splitter.to_conveyorbelts = [model.sub1]

    with pytest.raises(ValueError):
            model.check_composition()


# test ausgehendes band gehört nicht zum virtuellen modell
def test_check_comp_splitter_unknown_outgoing_conveyorbelt():

    model = VirtualModel()
    model.splitter.to_conveyorbelts = [model.sub1, model.sub2,model.sub3, Conveyorbelt(name="anderes", lane=9, length=5.0, transfer_to=model.sink1)]

    with pytest.raises(ValueError):
            model.check_composition()

# neues zweistufiges virtuelles modell
# quelle, band, splitter -> sub1 -> splitter2, -> sub4,sub5 -> sink1,sink4
#                           sub2, sub3 -> sink2, sink3

def test_second_virtual_model():
    model = VirtualModel()

    model.sink4 = Sink(name="sink4")
    model.sub4 = Conveyorbelt(name="sub4", lane=4, length=5.0, transfer_to=model.sink1)
    model.sub5 = Conveyorbelt(name="sub5", lane=5, length=5.0, transfer_to=model.sink4)
    model.splitter2 = Splitter(name="splitter2", to_conveyorbelts=[model.sub4,model.sub5], transfer_time=1.0)

    # neue anordnung
    model.sub1.transfer_to = model.splitter2

    model.sink_list = [model.sink1, model.sink2, model.sink3, model.sink4]
    model.conveyorbelt_list = [model.main, model.sub1,model.sub2,model.sub3, model.sub4, model.sub5]
    model.splitter_list = [model.splitter, model.splitter2]
    model.order = [model.sink4, model.sink1, model.sink2, model.sink3, model.sub4, model.sub5, model.splitter2,
                   model.sub1, model.sub2, model.sub3, model.splitter, model.main, model.source]

    model.check_composition()

    # hochlastablauf standardparametrisierung + creationperiod 1.0
    model.operating_parameter.item_creation_period = 1.0
    model.command_run()
    for i in range(3000): # 30 items
        model.simulation_step()

        # zu sink1 : 500+100+500+100+500 = Durchlaufzeit 1700 zu sink1
        # zu sink4 : 500+100+500+100+500 = Durchlaufzeit 1700 zu sink4
        # zu sink2 : 500+100+500 = Durchlaufzeit 1100 zu sink2
        # zu sink3 : 500+100+500 = Durchlaufzeit 1100 zu sink3
        # zu sink1,4 : jedes dritte item wegen splitter1
        # step 1800 senke 1, step 2100 senke 4
        # step 2400 senke 1, step 2700 senke 4
        # step 3000 senke 1 -> eins mehr

    assert model.kpi.created_items == 30
    assert model.sink1.items_received == 3
    assert model.sink4.items_received == 2
    assert model.sink2.items_received == 6
    assert model.sink3.items_received == 6

# test command run 
def test_command_run():

    model = VirtualModel()
    model.command_run()

    assert model.last_event == "COMMAND_RUN_PRESSED"
    assert model.state == "RUNNING"

# test command stop 
def test_command_stop(): 

    model = VirtualModel()
    model.command_run()
    
    assert model.last_event == "COMMAND_RUN_PRESSED"
    assert model.state == "RUNNING"

    model.command_stop()
    assert model.last_event == "COMMAND_STOP_PRESSED"
    assert model.state == "STOPPED"

# sensor update 
def test_sensor_update_with_correct_items():

    model = VirtualModel()
    item = Item(item_id=1, lane=0, position=model.main_entry_sensor.position) 
    item2 = Item(item_id=2, lane=0, position=model.main_exit_sensor.position) 
    item3 = Item(item_id=3, lane=2, position=model.sub2_entry_sensor.position) 
    item4 = Item(item_id=4, lane=2, position=model.sub2_exit_sensor.position)
    model.main.item_list = [item,item2] 
    model.sub2.item_list = [item3,item4] 

    model.update_sensors()
    assert model.main_entry_sensor.state is True
    assert model.main_exit_sensor.state is True
    assert model.sub2_exit_sensor.state is True
    assert model.sub2_entry_sensor.state is True

def test_sensor_update_still_false():
    
    model = VirtualModel()
    model.update_sensors()

    assert model.main_exit_sensor.state is False

# kpi update liest korrekt ab 
def test_update_kpis():

    model = VirtualModel()
    model.source.items_created = 2

    item = Item(item_id=1, lane=0, position=1.0)
    item2 = Item(item_id=2, lane=0, position=2.0)
    item3 = Item(item_id=3, lane=0, position=0.0)
    item4 = Item(item_id=4, lane=1, position=1.0)

    model.main.item_list = [item,item2]
    model.splitter.item = item3
    model.sub1.item_list = [item4]

    model.sink1.items_received = 2
    model.sink3.items_received = 1

    model.update_kpis()

    assert model.kpi.created_items == 2
    assert model.kpi.wip == 4
    assert model.kpi.tp_1 == 2
    assert model.kpi.tp_2 == 0
    assert model.kpi.tp_3 == 1
    assert model.kpi.tp_all == 3

# simulation step tests
def test_simulation_time_correct_while_running():

    model = VirtualModel()

    for i in range(100):
        model.simulation_step()

    assert model.step_counter == 0
    assert model.simulation_time == 0.0

    model.command_run()

    for i in range(100):
        model.simulation_step()

    # 100 steps
    assert model.step_counter == 100
    assert model.simulation_time == 1.0

    model.command_stop()
    model.simulation_step()

    assert model.step_counter == 100
    assert model.simulation_time == 1.0

# simulation step bewegt keine items in stopped
def test_simulation_step_no_movement_while_stopped():

    model = VirtualModel()
    item = Item(item_id=1, lane=0, position=0.0)
    model.main.item_list = [item]

    model.simulation_step()

    assert item.position == 0.0

# item nach 500 steps erzeugt
def test_simulation_step_first_item():

    model = VirtualModel()
    model.command_run()

    # first item after 500, no item at 499
    for i in range(499):
        model.simulation_step()

    # kein item erzeugt
    assert model.source.items_created == 0

    # 500th step -> creation, counter 500 % 500 = r0 steps per item -> creation period 5.0
    model.simulation_step()

    assert model.source.items_created == 1
    assert len(model.main.item_list) == 1
    assert model.main.item_list[0].position == 0.0
    assert model.last_event == "ITEM_CREATED"

# nach 1000 simulationsteps item routed by splitter
def test_simulation_step_1000_first_routing():

    model = VirtualModel()
    model.command_run()

    # nach 999 item bei 4.99 vor splitter, 500 creation + 499
    for i in range(999):
        model.simulation_step()

    assert model.step_counter == 999
    assert model.simulation_time == 9.99
    assert model.source.items_created == 1
    assert len(model.main.item_list) == 1
    assert model.main.item_list[0].lane == 0
    assert model.main.item_list[0].position == 4.99
    assert model.main_exit_sensor.state is True
    assert model.kpi.wip == 1

    # vor routing 
    assert model.sub1.item_list == []
    assert model.splitter.rr_counter == 0


    first_item = model.main.item_list[0]

    #step 1000
    model.simulation_step()

    assert model.step_counter == 1000
    assert model.simulation_time == 10.0
    assert model.source.items_created == 2 # new item at 0.0

    # item position war 4.99, dann simstep -> routed by splitter im selben step

    assert first_item not in model.main.item_list
    assert model.splitter.item is first_item # item in splitter
    # main exit sensor false
    assert model.main_exit_sensor.state is False
    # item nicht auf sub1
    assert model.sub1.item_list == []
    # item lane auf 1
    assert first_item.lane == 1
    assert first_item.position == 0.0

    # rr sollte bei 1 sein
    assert model.splitter.rr_counter == 1
    assert model.splitter.current_lane == 1

    # release time = 10 + 1.0 
    assert model.splitter.release_at == 11.0
    assert model.splitter.is_open(model=model) is False

    # simtime 11.0 : splitter release time
    for i in range(100):
        model.simulation_step()

    # items auf main wurden bewegt
    assert model.step_counter == 1100
    assert model.main.item_list[0].position == 1.0
    assert model.splitter.is_open(model=model) is True
    assert first_item.position == 0.0 
    assert first_item in model.sub1.item_list

    # step 1101 -> item sollte 0.01 bewegt sein
    model.simulation_step()

    assert first_item.position == 0.01

# reset model test 
def test_reset_model():

    model = VirtualModel()
    model.command_run()

    for i in range(1000):
        model.simulation_step()

    assert model.source.items_created == 2

    model.reset_model()

    assert model.state == "STOPPED"
    assert model.step_counter == 0
    assert model.simulation_time == 0.0
    assert model.last_event == "MODEL_GOT_RESET"

    assert model.main.item_list == []
    assert model.sub1.item_list == []
    assert model.sub2.item_list == []
    assert model.sub3.item_list == []

    assert model.source.items_created == 0
    assert model.sink1.items_received == 0
    assert model.sink2.items_received == 0
    assert model.sink3.items_received == 0

    # Standardparams
    assert model.operating_parameter.speed == 1.0
    assert model.operating_parameter.item_creation_period == 5.0
    assert model.operating_parameter.routing_mode == "ROUND_ROBIN"
    assert model.operating_parameter.target_lane == 1

    assert model.kpi.created_items == 0
    assert model.kpi.wip == 0
    assert model.kpi.tp_1 == 0
    assert model.kpi.tp_2 == 0
    assert model.kpi.tp_3 == 0
    assert model.kpi.tp_all == 0

    

# check operating parameters in boundaries
def test_check_operating_parameters_in_boundaries():

    model = VirtualModel()

    # Standard 1 m/s, 5.0, rr, lane1

    assert model.check_operating_parameter(speed=1.0, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=1)

    # speed grenzen 
    assert model.check_operating_parameter(speed=0.1, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=1)
    assert model.check_operating_parameter(speed=0.01, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=1) is False
    assert model.check_operating_parameter(speed=3.0, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=1)
    assert model.check_operating_parameter(speed=4.0, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=1) is False

    # creation period
    assert model.check_operating_parameter(speed=0.1, item_creation_period=0.9, routing_mode="ROUND_ROBIN", target_lane=1) is False
    assert model.check_operating_parameter(speed=0.1, item_creation_period=61.0, routing_mode="ROUND_ROBIN", target_lane=1) is False
    assert model.check_operating_parameter(speed=0.1, item_creation_period=1.0, routing_mode="ROUND_ROBIN", target_lane=1)
    assert model.check_operating_parameter(speed=0.1, item_creation_period=60.0, routing_mode="ROUND_ROBIN", target_lane=1)

    # routing mode 
    assert model.check_operating_parameter(speed=0.1, item_creation_period=1.0, routing_mode="alles_andere", target_lane=1) is False
    assert model.check_operating_parameter(speed=0.1, item_creation_period=1.0, routing_mode="target", target_lane=1) is False
    assert model.check_operating_parameter(speed=0.1, item_creation_period=1.0, routing_mode="ROUND_ROBIN", target_lane=1)
    assert model.check_operating_parameter(speed=0.1, item_creation_period=1.0, routing_mode="TARGET", target_lane=1)

    # target lane = 1,2,3
    assert model.check_operating_parameter(speed=1.0, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=1)
    assert model.check_operating_parameter(speed=1.0, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=2)
    assert model.check_operating_parameter(speed=1.0, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=3)
    assert model.check_operating_parameter(speed=1.0, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=4) is False
    assert model.check_operating_parameter(speed=1.0, item_creation_period=5.0, routing_mode="ROUND_ROBIN", target_lane=0) is False

# neue betriebsparameter nur bei stopped + valid

# stopped + valid 
def test_parameter_update_when_stopped_valid():

    model = VirtualModel()

    model.update_operating_parameter_when_stopped(new_speed=0.5, new_item_creation_period=2.0, new_routing_mode="TARGET", new_target_lane=2)

    assert model.operating_parameter.speed == 0.5
    assert model.operating_parameter.item_creation_period == 2.0
    assert model.operating_parameter.routing_mode == "TARGET"
    assert model.operating_parameter.target_lane == 2
    assert model.last_event == "PARAMETER_UPDATED"

# stopped + invalid 
def test_parameter_update_when_stopped_invalid():

    model = VirtualModel()

    model.update_operating_parameter_when_stopped(new_speed=4.0, new_item_creation_period=2.0, new_routing_mode="TARGET", new_target_lane=4)

    assert model.operating_parameter.speed == 1.0
    assert model.operating_parameter.item_creation_period == 5.0
    assert model.operating_parameter.routing_mode == "ROUND_ROBIN"
    assert model.operating_parameter.target_lane == 1
    assert model.last_event == "INVALID_PARAMETER"
# running + valid 
def test_parameter_update_when_running_valid():

    model = VirtualModel()
    model.command_run()

    model.update_operating_parameter_when_stopped(new_speed=0.5, new_item_creation_period=2.0, new_routing_mode="TARGET", new_target_lane=2)

    assert model.operating_parameter.speed == 1.0
    assert model.operating_parameter.item_creation_period == 5.0
    assert model.operating_parameter.routing_mode == "ROUND_ROBIN"
    assert model.operating_parameter.target_lane == 1
    assert model.last_event == "NEW_PARAMETERS_ONLY_WHEN_STOPPED"

# running + invalid 
def test_parameter_update_when_running_invalid():

    model = VirtualModel()
    model.command_run()

    model.update_operating_parameter_when_stopped(new_speed=5.5, new_item_creation_period=2.0, new_routing_mode="TARGET", new_target_lane=2)

    assert model.operating_parameter.speed == 1.0
    assert model.operating_parameter.item_creation_period == 5.0
    assert model.operating_parameter.routing_mode == "ROUND_ROBIN"
    assert model.operating_parameter.target_lane == 1
    assert model.last_event == "NEW_PARAMETERS_ONLY_WHEN_STOPPED"



