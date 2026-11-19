import asyncio
from asyncua import Client
from virtual_model import VirtualModel
from opcua_server import main
import pytest

# Hochlastablaufstest über OPC-UA-Server mit OPC-UA-Testclient
# Gleichen Parameter wie im Modelltest

url = "opc.tcp://localhost:4840/freeopcua/server"
uri = "http://emulation.de"


@pytest.mark.asyncio
async def test_hochlastablaufstest():

    model = VirtualModel()
    testserver = asyncio.create_task(main(model=model))
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

        # reset bei beginn eines testablaufs für messung
        await reset_variablenode.write_value(True)
        await asyncio.sleep(0.05)
        # item creation period auf 1.0 setzen für highload
        await item_creation_variablenode.write_value(1.0)
        await run_variablenode.write_value(True)


        # 60 sekunden betriebszeit
        # dt liest alle 10ms zeit ab, bis 60s vorbei sind
        betriebszeit = 0.0
        while betriebszeit < 60.0:

            await asyncio.sleep(0.01)
            betriebszeit = await simulation_time_variablenode.read_value() # aktuelle zeit wird hochgesetzt bis 60
        await stop_variablenode.write_value(True) # anlage stoppen 

        # 50ms nach stop warten 
        await asyncio.sleep(0.05)

        # kennzahlen lesen nach stop 

        ist_items = await created_items_variablenode.read_value()
        ist_wip = await wip_variablenode.read_value()
        ist_tp1 = await tp_lane1_variablenode.read_value()
        ist_tp2 = await tp_lane2_variablenode.read_value()
        ist_tp3 = await tp_lane3_variablenode.read_value()
        ist_tpall = await tp_all_variablenode.read_value()

        soll_items = 60
        soll_wip = 11
        soll_tp1 = 17
        soll_tp2 = 16
        soll_tp3 = 16
        soll_tpall = 49
 
        print(f"{'Kennzahl':<22}|{'Sollwert':<8}|{'Istwert':<8}|Bewertung")
        print("-"*56)

        print(f"{'Erzeugte Stückgüter':<22}|{soll_items:<8}|{ist_items:<8}|{'Bestanden' if soll_items == ist_items else 'Nicht Bestanden'}")
        print(f"{'Umlaufbestand':<22}|{soll_wip:<8}|{ist_wip:<8}|{'Bestanden' if soll_wip == ist_wip else 'Nicht Bestanden'}")
        print(f"{'Durchsatz Senke 1':<22}|{soll_tp1:<8}|{ist_tp1:<8}|{'Bestanden' if soll_tp1 == ist_tp1 else 'Nicht Bestanden'}")
        print(f"{'Durchsatz Senke 2':<22}|{soll_tp2:<8}|{ist_tp2:<8}|{'Bestanden' if soll_tp2 == ist_tp2 else 'Nicht Bestanden'}")
        print(f"{'Durchsatz Senke 3':<22}|{soll_tp3:<8}|{ist_tp3:<8}|{'Bestanden' if soll_tp3 == ist_tp3 else 'Nicht Bestanden'}")
        print(f"{'Gesamtdurchsatz':<22}|{soll_tpall:<8}|{ist_tpall:<8}|{'Bestanden' if soll_tpall == ist_tpall else 'Nicht Bestanden'}")

        assert ist_items == soll_items
        assert ist_wip == soll_wip
        assert ist_tp1 == soll_tp1
        assert ist_tp2 == soll_tp2
        assert ist_tp3 == soll_tp3
        assert ist_tpall == soll_tpall

    testserver.cancel()
        
