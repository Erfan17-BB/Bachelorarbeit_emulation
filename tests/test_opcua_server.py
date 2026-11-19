from asyncua import Client, ua
from virtual_model import VirtualModel
from opcua_server import main 

import asyncio
import pytest

url = "opc.tcp://localhost:4840/freeopcua/server" # adresse server
uri = "http://emulation.de" # namespace


@pytest.mark.asyncio
async def test_server():

    model = VirtualModel()
    testserver = asyncio.create_task(main(model=model)) # server als task
    await asyncio.sleep(5)

    async with Client(url=url) as client:

        nsidx = await client.get_namespace_index(uri=uri)

        # dt holt alle variablenknoten
        
        run_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:COMMANDS/{nsidx}:RUN")
        stop_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:COMMANDS/{nsidx}:STOP")
        reset_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:COMMANDS/{nsidx}:RESET")

        speed_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:COMMANDS/{nsidx}:SPEED")
        item_creation_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:COMMANDS/{nsidx}:ITEM_CREATION_PERIOD")
        routing_mode_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:COMMANDS/{nsidx}:ROUTING_MODE")
        target_lane_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:COMMANDS/{nsidx}:TARGET_LANE")

        state_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:RESPONSES/{nsidx}:STATE")
        last_event_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:RESPONSES/{nsidx}:LAST_EVENT")
        current_lane_splitter_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:RESPONSES/{nsidx}:CURRENT_LANE_SPLITTER")
        simulation_time_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:RESPONSES/{nsidx}:SIMULATION_TIME")
        
        main_entry_sensor_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:SENSORS/{nsidx}:MAIN_ENTRY_SENSOR")
        main_exit_sensor_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:SENSORS/{nsidx}:MAIN_EXIT_SENSOR")
        sub1_exit_sensor_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:SENSORS/{nsidx}:SUB1_EXIT_SENSOR")
        sub2_exit_sensor_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:SENSORS/{nsidx}:SUB2_EXIT_SENSOR")
        sub3_exit_sensor_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:SENSORS/{nsidx}:SUB3_EXIT_SENSOR")
        sub1_entry_sensor_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:SENSORS/{nsidx}:SUB1_ENTRY_SENSOR")
        sub2_entry_sensor_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:SENSORS/{nsidx}:SUB2_ENTRY_SENSOR")
        sub3_entry_sensor_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:SENSORS/{nsidx}:SUB3_ENTRY_SENSOR")

        created_items_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:KPI/{nsidx}:CREATED_ITEMS")
        wip_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:KPI/{nsidx}:WIP")
        tp_all_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:KPI/{nsidx}:TP_ALL")
        tp_lane1_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:KPI/{nsidx}:TP_LANE1")
        tp_lane2_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:KPI/{nsidx}:TP_LANE2")
        tp_lane3_variablenode = await client.nodes.root.get_child(f"0:Objects/{nsidx}:Conveyorbeltsystem/{nsidx}:KPI/{nsidx}:TP_LANE3")

        # Test Übergabe vom Modell an Server

        assert await run_variablenode.read_value() is False
        assert await stop_variablenode.read_value() is False
        assert await reset_variablenode.read_value() is False

        # Standardparametrisierung
        assert await speed_variablenode.read_value() == 1.0
        assert await item_creation_variablenode.read_value() == 5.0
        assert await routing_mode_variablenode.read_value() == "ROUND_ROBIN"
        assert await target_lane_variablenode.read_value() == 1

        assert await state_variablenode.read_value() == "STOPPED"
        assert await last_event_variablenode.read_value() == "MODEL_INIT"
        assert await current_lane_splitter_variablenode.read_value() == 1
        assert await simulation_time_variablenode.read_value() == 0.0

        assert await main_entry_sensor_variablenode.read_value() is False
        assert await main_exit_sensor_variablenode.read_value() is False
        assert await sub1_exit_sensor_variablenode.read_value() is False
        assert await sub2_exit_sensor_variablenode.read_value() is False
        assert await sub3_exit_sensor_variablenode.read_value() is False
        assert await sub1_entry_sensor_variablenode.read_value() is False
        assert await sub2_entry_sensor_variablenode.read_value() is False
        assert await sub3_entry_sensor_variablenode.read_value() is False

        assert await created_items_variablenode.read_value() == 0
        assert await wip_variablenode.read_value() == 0
        assert await tp_all_variablenode.read_value() == 0
        assert await tp_lane1_variablenode.read_value() == 0
        assert await tp_lane2_variablenode.read_value() == 0
        assert await tp_lane3_variablenode.read_value() == 0


        
        # test betriebsfunktion run + while stopped

        await run_variablenode.write_value(True)

        await asyncio.sleep(0.025) # nach Windows verspätung
        

        assert model.state == "RUNNING"
        assert model.step_counter >= 1
        assert model.simulation_time == model.step_counter*model.step_size
        assert await run_variablenode.read_value() is False
        assert await state_variablenode.read_value() == "RUNNING"
        assert await last_event_variablenode.read_value() == "COMMAND_RUN_PRESSED"
        assert await simulation_time_variablenode.read_value() > 0.0

        # test betriebsfunktion stop + while running

        # model wird gestoppt : nach 25 ms -> model stopped 
        await stop_variablenode.write_value(True)
        await asyncio.sleep(0.025) 
        assert model.state == "STOPPED"
        assert await stop_variablenode.read_value() is False
        assert await state_variablenode.read_value() == "STOPPED"


        # server macht weitere zyklen, model aber keine steps

        steps_bei_stopped_moment = model.step_counter
        await asyncio.sleep(0.025)
        
        assert model.step_counter == steps_bei_stopped_moment 
        assert await simulation_time_variablenode.read_value() == steps_bei_stopped_moment * model.step_size

        # test betriebsfunktion reset
        # reset auf standardparametrisierung und ausgangswerten
        await speed_variablenode.write_value(1.5)
        await routing_mode_variablenode.write_value("TARGET")
        
        await reset_variablenode.write_value(True)
        await asyncio.sleep(0.025)
        
        assert await state_variablenode.read_value() == "STOPPED"
        assert model.step_counter == 0
        assert await speed_variablenode.read_value() == 1.0
        assert await item_creation_variablenode.read_value() == 5.0
        assert await routing_mode_variablenode.read_value() == "ROUND_ROBIN"
        assert await target_lane_variablenode.read_value() == 1
        assert await last_event_variablenode.read_value() == "MODEL_GOT_RESET"
        assert await current_lane_splitter_variablenode.read_value() == 1
        assert await simulation_time_variablenode.read_value() == 0.0


        # test betriebsparameter 

        # betriebsparameter im stopped übernommen durch setter direkt
        await speed_variablenode.write_value(2.0)
        assert model.operating_parameter.speed == 2.0
        assert await speed_variablenode.read_value() == 2.0
        await item_creation_variablenode.write_value(3.0)
        assert model.operating_parameter.item_creation_period == 3.0
        await target_lane_variablenode.write_value(2) 
        assert model.operating_parameter.target_lane == 2
        await routing_mode_variablenode.write_value("TARGET")
        assert model.operating_parameter.routing_mode == "TARGET"


        # test betriebsparameter ausserhalb grenzen

        # max 3.0
        with pytest.raises(ua.UaStatusCodeError):
            await speed_variablenode.write_value(5.0)
        assert await speed_variablenode.read_value() == 2.0 # abgelehnt
        assert model.operating_parameter.speed == 2.0 # auch hier noch vorheriger wert 


        # item creation 0.1 ungültig
        with pytest.raises(ua.UaStatusCodeError):
            await item_creation_variablenode.write_value(0.1)
        assert await item_creation_variablenode.read_value() == 3.0
        assert model.operating_parameter.item_creation_period == 3.0

        # routing false notrr 
        with pytest.raises(ua.UaStatusCodeError):
            await routing_mode_variablenode.write_value("notrr")
        assert await routing_mode_variablenode.read_value() == "TARGET" # abgelehnt 
        assert model.operating_parameter.routing_mode == "TARGET"


        # target lane nicht aus 3
        with pytest.raises(ua.UaStatusCodeError):
                await target_lane_variablenode.write_value(4)
        assert await target_lane_variablenode.read_value() == 2 # abgelehnt nur 1,2,3
        assert model.operating_parameter.target_lane == 2 


        # test betriebsparameter gültig aber running 

        await run_variablenode.write_value(True)
        await asyncio.sleep(0.025)
        assert model.state == "RUNNING"
        with pytest.raises(ua.UaStatusCodeError):
            await speed_variablenode.write_value(2.5)
        assert await speed_variablenode.read_value() == 2.0 # noch gleich

    
        with pytest.raises(ua.UaStatusCodeError):
             await item_creation_variablenode.write_value(5.0)
        assert await item_creation_variablenode.read_value() == 3.0 # abgelehnt


        with pytest.raises(ua.UaStatusCodeError):
             await routing_mode_variablenode.write_value("ROUND_ROBIN")
        assert await routing_mode_variablenode.read_value() == "TARGET" # auch abgelehnt


        with pytest.raises(ua.UaStatusCodeError):
             await target_lane_variablenode.write_value(3)
        assert await target_lane_variablenode.read_value() == 2 # abgelehnt

    testserver.cancel()








