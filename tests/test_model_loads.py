from virtual_model import VirtualModel

# 60 second high load test

# Sollwerte für Hochlasttest

    # Gesamtdurchsatz = 49
    # Durchsatz sink1 = 17
    # Durchsatz sink2 = 16
    # Durchsatz sink3 = 16
    # WIP = 11
    # Erzeugte Items = 60 

def test_60_seconds_high_load(): 

    model = VirtualModel()
    # high load settings
    model.operating_parameter.item_creation_period = 1.0
    model.command_run() 

    for i in range(6000):
        model.simulation_step()

    assert model.simulation_time == 60.0

    assert model.kpi.created_items == 60  
    assert model.kpi.wip == 11  
    assert model.kpi.tp_1 == 17 
    assert model.kpi.tp_2 == 16 
    assert model.kpi.tp_3 == 16 
    assert model.kpi.tp_all == 49 


# dynamischer ablauf mit verschiedenen parametern 
def test_sequence_different_parameter_still_works():

    model = VirtualModel()
    model.update_operating_parameter_when_stopped(new_speed=1.0, new_item_creation_period=2.0,
                                                  new_routing_mode="ROUND_ROBIN", new_target_lane=1)

    model.command_run()
    for i in range(2000):
        model.simulation_step()

        # 2000*0.01 = 20 sek
        # creation period = 2.0 -> alle 200 steps neues item, durchlaufzeit 1100 pro item
    assert model.simulation_time == 20 
    assert model.kpi.created_items == 10 # alle 200 steps = 2s
    assert model.kpi.tp_all == 4 # erstes nach 200, Durchlaufzeit 1100 -> 1300 bei sink + 200 bis 2000 = 4
    assert model.kpi.tp_1 == 2 # rr
    assert model.kpi.tp_2 == 1
    assert model.kpi.tp_3 == 1
    assert model.kpi.wip == 10-4

    # stop + reset
    model.command_stop()
    assert model.state == "STOPPED"
    model.reset_model()
    assert model.last_event == "MODEL_GOT_RESET"
    assert model.simulation_time == 0.0
    assert model.kpi.created_items == 0
    assert model.kpi.tp_all == 0
    assert model.kpi.tp_1 == 0
    assert model.kpi.tp_2 == 0
    assert model.kpi.tp_3 == 0

        # parameter ändern
    model.update_operating_parameter_when_stopped(new_speed=2.5, new_item_creation_period=2.0,
                                                          new_routing_mode="TARGET", new_target_lane=2)


    assert model.operating_parameter.speed == 2.5
    assert model.operating_parameter.routing_mode == "TARGET"
    assert model.operating_parameter.target_lane == 2

    model.command_run()
    for i in range(1000):
        model.simulation_step()

    # 0.025 pro step,  5/ 0.025 = 200 steps pro band
    # 200 +100+200 = durchlaufzeit
    assert model.simulation_time == 10.0 # neu 1000*0.01
    assert model.kpi.created_items == 5 # ab 200,400,600,800,1000
    assert model.kpi.tp_1 == 0
    assert model.kpi.tp_2 == 2 # erstes nach 200 creation + 500 durchlaufzeit 700,900,1100
    assert model.kpi.tp_3 == 0
    assert model.kpi.tp_all == 2

    model.command_stop()
    assert model.state == "STOPPED"




        