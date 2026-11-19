import asyncio 
from asyncua import Server, ua 
from virtual_model import VirtualModel
import time
import logging

logging.getLogger("asyncua.server.uaprocessor").setLevel(logging.CRITICAL)

async def main(model: VirtualModel):

    server = Server()
    await server.init()

    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/") 

    uri = "http://emulation.de"
    nsidx = await server.register_namespace(uri)

    # adressraum erstellen

    conveyorbeltsystem = await server.nodes.objects.add_object(nsidx, "Conveyorbeltsystem")

    # kommandogruppe
    commands_group = await conveyorbeltsystem.add_object(nsidx, "COMMANDS")

    # betriebsfunktionen
    run_variablenode = await commands_group.add_variable(nsidx, "RUN", False) # opc ua automatic datatype
    stop_variablenode = await commands_group.add_variable(nsidx, "STOP", False)
    reset_variablenode = await commands_group.add_variable(nsidx, "RESET", False)

    # betriebsparameter
    speed_variablenode = await commands_group.add_variable(nsidx, "SPEED", model.operating_parameter.speed)
    item_creation_period_variablenode = await commands_group.add_variable(nsidx, "ITEM_CREATION_PERIOD", model.operating_parameter.item_creation_period)
    routing_mode_variablenode = await commands_group.add_variable(nsidx, "ROUTING_MODE", model.operating_parameter.routing_mode)
    target_lane_variablenode = await commands_group.add_variable(nsidx, "TARGET_LANE", model.operating_parameter.target_lane)

    await run_variablenode.set_writable()
    await stop_variablenode.set_writable()
    await reset_variablenode.set_writable()
    await speed_variablenode.set_writable()
    await item_creation_period_variablenode.set_writable()
    await routing_mode_variablenode.set_writable()
    await target_lane_variablenode.set_writable()

    # rückmeldegruppe
    response_group = await conveyorbeltsystem.add_object(nsidx, "RESPONSES")
    # rückmeldungen
    state_variablenode = await response_group.add_variable(nsidx, "STATE", model.state)
    last_event_variablenode = await response_group.add_variable(nsidx, "LAST_EVENT", model.last_event)
    current_splitter_lane_variablenode = await response_group.add_variable(nsidx, "CURRENT_LANE_SPLITTER", model.splitter.current_lane)
    simulation_time_variablenode = await response_group.add_variable(nsidx, "SIMULATION_TIME", model.simulation_time)

    # sensorgruppe
    sensor_group = await conveyorbeltsystem.add_object(nsidx, "SENSORS")
    # sensoren
    main_entry_sensor_variablenode = await sensor_group.add_variable(nsidx, "MAIN_ENTRY_SENSOR", model.main_entry_sensor.state)
    main_exit_sensor_variablenode = await sensor_group.add_variable(nsidx, "MAIN_EXIT_SENSOR", model.main_exit_sensor.state)
    sub1_entry_sensor_variablenode = await sensor_group.add_variable(nsidx, "SUB1_ENTRY_SENSOR", model.sub1_entry_sensor.state)
    sub2_entry_sensor_variablenode = await sensor_group.add_variable(nsidx, "SUB2_ENTRY_SENSOR", model.sub2_entry_sensor.state)
    sub3_entry_sensor_variablenode = await sensor_group.add_variable(nsidx, "SUB3_ENTRY_SENSOR", model.sub3_entry_sensor.state)
    sub1_exit_sensor_variablenode = await sensor_group.add_variable(nsidx, "SUB1_EXIT_SENSOR", model.sub1_exit_sensor.state)
    sub2_exit_sensor_variablenode = await sensor_group.add_variable(nsidx, "SUB2_EXIT_SENSOR", model.sub2_exit_sensor.state)
    sub3_exit_sensor_variablenode = await sensor_group.add_variable(nsidx, "SUB3_EXIT_SENSOR", model.sub3_exit_sensor.state)

    # kpigruppe
    kpi_group = await conveyorbeltsystem.add_object(nsidx, "KPI")
    # kpis
    created_items_variablenode = await kpi_group.add_variable(nsidx, "CREATED_ITEMS", model.kpi.created_items)
    wip_variablenode = await kpi_group.add_variable(nsidx, "WIP", model.kpi.wip)
    tp_all_variablenode = await kpi_group.add_variable(nsidx, "TP_ALL", model.kpi.tp_all)
    tp_lane1_variablenode = await kpi_group.add_variable(nsidx, "TP_LANE1", model.kpi.tp_1)
    tp_lane2_variablenode = await kpi_group.add_variable(nsidx, "TP_LANE2", model.kpi.tp_2)
    tp_lane3_variablenode = await kpi_group.add_variable(nsidx, "TP_LANE3", model.kpi.tp_3)


    # einheiten
    await speed_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("m/s"))))
    await item_creation_period_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("s"))))
    await simulation_time_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("s"))))
    await created_items_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("Stück"))))
    await wip_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("Stück"))))
    await tp_all_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("Stück"))))
    await tp_lane1_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("Stück"))))
    await tp_lane2_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("Stück"))))
    await tp_lane3_variablenode.write_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant(ua.LocalizedText("Stück"))))


    # setter bevor wert in knoten geschrieben wird
    def speed_setter(node, attr, datavalue):

        value = datavalue.Value.Value # value aus anfrage 
        if value != model.operating_parameter.speed: 
            
            model.update_operating_parameter_when_stopped(new_speed=value, 
                                                          new_item_creation_period=model.operating_parameter.item_creation_period,
                                                          new_routing_mode=model.operating_parameter.routing_mode,
                                                          new_target_lane=model.operating_parameter.target_lane)
            if model.operating_parameter.speed != value: 
                
                if model.state != "STOPPED":
                    raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidState) 
                raise ua.UaStatusCodeError(ua.StatusCodes.BadOutOfRange)
            
        node.attributes[attr].value = datavalue

    server.set_attribute_value_setter(speed_variablenode.nodeid, speed_setter)


    def item_creation_period_setter(node, attr, datavalue):
    
            value = datavalue.Value.Value
            if value != model.operating_parameter.item_creation_period:
                
                model.update_operating_parameter_when_stopped(new_speed=model.operating_parameter.speed, 
                                                              new_item_creation_period=value,
                                                              new_routing_mode=model.operating_parameter.routing_mode,
                                                              new_target_lane=model.operating_parameter.target_lane)
                if model.operating_parameter.item_creation_period != value: 
                    
                    if model.state != "STOPPED":
                        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidState) 
                    raise ua.UaStatusCodeError(ua.StatusCodes.BadOutOfRange)
                
            node.attributes[attr].value = datavalue  
    
    server.set_attribute_value_setter(item_creation_period_variablenode.nodeid, item_creation_period_setter)

    def routing_mode_setter(node, attr, datavalue):
    
            value = datavalue.Value.Value
            if value != model.operating_parameter.routing_mode: 
                
                model.update_operating_parameter_when_stopped(new_speed=model.operating_parameter.speed, 
                                                              new_item_creation_period=model.operating_parameter.item_creation_period,
                                                              new_routing_mode=value,
                                                              new_target_lane=model.operating_parameter.target_lane)
                if model.operating_parameter.routing_mode != value: 
                    
                    if model.state != "STOPPED":
                        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidState) 
                    raise ua.UaStatusCodeError(ua.StatusCodes.BadOutOfRange)
                
            node.attributes[attr].value = datavalue  
    
    server.set_attribute_value_setter(routing_mode_variablenode.nodeid, routing_mode_setter)

    def target_lane_setter(node, attr, datavalue):
    
            value = datavalue.Value.Value
            if value != model.operating_parameter.target_lane: 
                
                model.update_operating_parameter_when_stopped(new_speed=model.operating_parameter.speed, 
                                                              new_item_creation_period=model.operating_parameter.item_creation_period,
                                                              new_routing_mode=model.operating_parameter.routing_mode,
                                                              new_target_lane=value)
                if model.operating_parameter.target_lane != value: 
                    
                    if model.state != "STOPPED":
                        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidState) 
                    raise ua.UaStatusCodeError(ua.StatusCodes.BadOutOfRange)
                
            node.attributes[attr].value = datavalue  
    
    server.set_attribute_value_setter(target_lane_variablenode.nodeid, target_lane_setter)

    async with server:
         next_cycle = time.perf_counter() # zielzeitpunkt des nächsten zyklus auf wanduhr, start bei nullpunkt 0
         messung_start = time.perf_counter()
         zyklen = 0
         max_phasen_duration = 0.0 # längste phasendauer

         while True:
              
              cycle_start = time.perf_counter() # aktuelle startzeit
              zyklen +=1

              # Phase 1 : Betriebsfunktionscheck
              if await stop_variablenode.read_value():
                                 model.command_stop()
                                 
                                 print("Zykluszeit Durchschnitt :", round((time.perf_counter() - messung_start) / zyklen * 1000,2))
                                 print(f"Längste Phasendauer : {round(max_phasen_duration*1000,2)}")
                                 


              elif await reset_variablenode.read_value():
                   model.reset_model()
                   # neue messung
                   messung_start = time.perf_counter() 
                   zyklen = 0
                   max_phasen_duration = 0.0

              elif await run_variablenode.read_value():
                   model.command_run()    

            # wieder auf false setzen
              await stop_variablenode.write_value(False)
              await reset_variablenode.write_value(False)
              await run_variablenode.write_value(False)

              # Phase 2 : Simulationsstep
              model.simulation_step()

              # Phase 3 : Synchronisieren modell und knoten mit werten von modell
              await speed_variablenode.write_value(model.operating_parameter.speed)
              await item_creation_period_variablenode.write_value(model.operating_parameter.item_creation_period)
              await routing_mode_variablenode.write_value(model.operating_parameter.routing_mode)
              await target_lane_variablenode.write_value(model.operating_parameter.target_lane)

              await state_variablenode.write_value(model.state)
              await last_event_variablenode.write_value(model.last_event)
              await current_splitter_lane_variablenode.write_value(model.splitter.current_lane)
              await simulation_time_variablenode.write_value(model.simulation_time)

              await main_entry_sensor_variablenode.write_value(model.main_entry_sensor.state)
              await main_exit_sensor_variablenode.write_value(model.main_exit_sensor.state)   
              await sub1_exit_sensor_variablenode.write_value(model.sub1_exit_sensor.state)   
              await sub2_exit_sensor_variablenode.write_value(model.sub2_exit_sensor.state)   
              await sub3_exit_sensor_variablenode.write_value(model.sub3_exit_sensor.state)
              await sub1_entry_sensor_variablenode.write_value(model.sub1_entry_sensor.state)   
              await sub2_entry_sensor_variablenode.write_value(model.sub2_entry_sensor.state)   
              await sub3_entry_sensor_variablenode.write_value(model.sub3_entry_sensor.state)   

              await created_items_variablenode.write_value(model.kpi.created_items)
              await wip_variablenode.write_value(model.kpi.wip) 
              await tp_all_variablenode.write_value(model.kpi.tp_all) 
              await tp_lane1_variablenode.write_value(model.kpi.tp_1) 
              await tp_lane2_variablenode.write_value(model.kpi.tp_2) 
              await tp_lane3_variablenode.write_value(model.kpi.tp_3) 

             # dauer von phase berechnen
              phasen_duration = time.perf_counter() - cycle_start

              # max überschreiben
              if model.state == "RUNNING" and phasen_duration > max_phasen_duration:
                max_phasen_duration = phasen_duration

              # zielzeitpunkt berechnen
              next_cycle = next_cycle + model.step_size # optimal : 10,20,30

              await asyncio.sleep(max(0, next_cycle - time.perf_counter()))
              # restzeit bis nächstem zyklus
              


if __name__ == "__main__":
     asyncio.run(main(model=VirtualModel()))








                   


            

