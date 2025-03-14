import time, pandas, os, logging, shutil, datetime, random, pickle
import numpy as np
from rich.logging import RichHandler
import BaseStation, Client, Coverage, Distributor, Graph, Slice, Stats, Container, route_generate, utils

Simlogger = logging.getLogger('Sim.' + __name__)

# set logging file
def setLogging(data_dir):
    logger = logging.getLogger("main") # debug, info, warning, error, critical
    logger.setLevel(logging.INFO)

    stream_handler = RichHandler(markup=True,rich_tracebacks=True)
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(logging.Formatter(fmt="%(name)s || %(message)s", datefmt="[%X]"))
    logger.addHandler(stream_handler)

    global file_handler
    file_handler = logging.FileHandler(f'{data_dir}/logger.log', mode="wt")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s || %(levelname)s || %(name)s || %(message)s", datefmt="[%X]"))
    logger.addHandler(file_handler)
    
    return logger

# main part of simulator
def main(SIM_TIME, NUM_CLIENTS, data, bs_in_range, data_dir, slice_quantity):
    start_time = time.time()
    
    # make directory to store the slimulation result
    try:
        os.mkdir(f"{data_dir}")
    except:
        shutil.rmtree(f"{data_dir}")
        print(f"output files are overwritten in {data_dir}")
        os.mkdir(f"{data_dir}")
    
    # logging initiation
    logger = setLogging(data_dir)
    
    logger.info("======logging proccess initiated======")
    logger.info(f"num client is {NUM_CLIENTS}, sim time is {SIM_TIME}, slice_quantity is {slice_quantity}")
    
    # import scinario from setting file
    SETTINGS = data['settings']
    SLICES_INFO = data['slices']
    MOBILITY_PATTERNS = data['mobility_patterns']
    BASE_STATIONS = data['base_stations']
    CLIENTS = data['clients']
    collected, c1, slice_weights, slice_ps_num = 0, 0, [], []
    for __, s in SLICES_INFO.items():
        collected += s['client_weight']
        slice_weights.append(collected)
        c1 += s['client_weight'] * NUM_CLIENTS
        slice_ps_num.append(c1)

    slice_variation = []
    for name, s in SLICES_INFO.items():
        for i in range(slice_quantity[0]):
            slice_variation.append(f'{name}_{i}')

    collected, mb_weights = 0, []
    for __, mb in MOBILITY_PATTERNS.items():
        collected += mb['client_weight']
        mb_weights.append(collected)

    mobility_patterns = []
    for name, mb in MOBILITY_PATTERNS.items():
        mobility_pattern = [mb['params']['min'], mb['params']['max'], name, random.uniform]
        mobility_patterns.append(mobility_pattern)

    usage_patterns = {}
    for name, s in SLICES_INFO.items():
        usage_patterns[name] = Distributor.Distributor(name, utils.get_dist(s['usage_pattern']['distribution']), *s['usage_pattern']['params'])

    collected = 0
    location_patterns = []
    for __, location in CLIENTS['location'].items():
        collected += location['client_weight']
        location_patterns.append(collected)
    
    # make instance of each base stations
    base_stations = []
    i = 0
    for b in BASE_STATIONS:
        b_id = b['id']
        b_type = b['type']
        if SETTINGS["bs_batch_change"]["change"]:
            coverage = SETTINGS["bs_batch_change"][b_type]["coverage"]
            Wa = SETTINGS["bs_batch_change"][b_type]["Wa"]
            Wb = SETTINGS["bs_batch_change"][b_type]["Wb"]
        
        else:
            coverage = b['coverage']
            Wa = b['Wa']
            Wb = b['Wb']
        access_slices = []
        backhaul_slices = []
        
        # access link
        j = 0
        for name, s in SLICES_INFO.items():
            for n in range(slice_quantity[0]):
                sl = Slice.Slice(j, f'{name}_{n}', 0, s['client_weight'], 0, usage_patterns[name])
                sl.capacity = Container.Container(capacity=0)
                access_slices.append(sl)
                j += 1
        
        # backhaul link
        j = 0
        for name, s in SLICES_INFO.items():
            for n in range(slice_quantity[0]):
                sl = Slice.Slice(j, f'{name}_{n}', 0, s['client_weight'], 0, usage_patterns[name])
                sl.capacity = Container.Container(capacity=0)
                backhaul_slices.append(sl)
                j += 1
        
        base_station = BaseStation.BaseStation(i, b['x'], b['y'], Coverage.Coverage((b['x'], b['y']), coverage), b_id, b_type, Wa, Wb, access_slices, backhaul_slices, data_dir)
        base_station.AL_capacity = Container.Container(capacity=Wa)
        base_station.BL_capacity = Container.Container(capacity=Wb)
        base_stations.append(base_station)
        i += 1

    x_vals = SETTINGS['statistics_params']['x']
    y_vals = SETTINGS['statistics_params']['y']
    
    # initiate collecting statistical data
    stats = Stats.Stats(base_stations, slice_variation, slice_quantity, None, ((x_vals['min'], x_vals['max']), (y_vals['min'], y_vals['max'])), SIM_TIME, data_dir)

    # make dataframe where UEs data are stored
    df_user_info = pandas.DataFrame(columns=["id", "slice", "bandwidth", "x", "y", "green_to_donor", "route_to_donor", "pre_bs", "pre_route", "in_range"])

    # make instance of each UEs 
    clients = []
    slice_type = 0
    sub_slice = -1
    location_number = 0
    for i in range(NUM_CLIENTS):
        if slice_ps_num[slice_type] < i + 1:
            slice_type += 1
            sub_slice = -1
        if slice_quantity[slice_type] < sub_slice + 2:
            sub_slice = -1
        sub_slice += 1
        
        # coodination
        if location_patterns[location_number] * NUM_CLIENTS <= i:
            location_number += 1
        
        location_x = round(random.uniform(CLIENTS['location'][location_number]['x']['params']['min'], CLIENTS['location'][location_number]['x']['params']['max']), 2)
        location_y = round(random.uniform(CLIENTS['location'][location_number]['y']['params']['min'], CLIENTS['location'][location_number]['y']['params']['max']), 2)
        
        # movable area
        area_x = [CLIENTS['location'][location_number]['x']['params']['min'], CLIENTS['location'][location_number]['x']['params']['max']]
        area_y = [CLIENTS['location'][location_number]['y']['params']['min'], CLIENTS['location'][location_number]['y']['params']['max']]
        
        # slice
        connected_slice_index = utils.get_slice_index(slice_type, sub_slice, slice_quantity)
        mobility_pattern = utils.get_random_mobility_pattern(mb_weights, mobility_patterns)
        
        c = Client.Client(i, location_x, location_y, mobility_pattern, connected_slice_index, 
                        stats, slice_weights, base_stations, area_x, area_y, df_user_info, 
                        access_slices, backhaul_slices, 0, data_dir)
        clients.append(c)
    
    stats.clients = clients
    
    # ===== simulation begin =====
    for i in range(1,SIM_TIME+1):
        
        # =Reallocate bandwidth of slices=
        
        # when the iteration counter shows 10
        if i == 10:
            for bs in base_stations:
                t, a = 0, 0
                for sl in bs.access_slices:
                    sl.capacity.capacity = sl.capacity.level*1.176
                    t += sl.capacity.capacity
                    a += sl.capacity.level
                # if the base station can't afford to secure the 1.176 times of requested bandwidth
                if 0.93*bs.Wa < t:
                    for sl in bs.access_slices:
                        sl.capacity.capacity = sl.capacity.level
                
                t, a = 0, 0
                for sl in bs.backhaul_slices:
                    sl.capacity.capacity = sl.capacity.level*1.176
                    t += sl.capacity.capacity
                    a += sl.capacity.level
                # if the base station can't afford to secure the 1.176 times of requested bandwidth
                if 0.93*bs.Wb < t:
                    for sl in bs.backhaul_slices:
                        sl.capacity.capacity = sl.capacity.level
        
        # when the iteration counter shows a multiple of 10 except the counter shows 0 or 10
        if i % 10 == 0 and i != 0 and i != 10:
            for bs in base_stations:
                t = 0
                for sl in bs.access_slices:
                    old_capacity = sl.capacity.capacity
                    #if (max(stats.return_usage("AL", bs, sl)[-10:]) - old_capacity*0.9 > 0) or (old_capacity*0.8 - max(stats.return_usage("AL", bs, sl)[-10:]) > 0): # refer last 10 timesteps
                    if (stats.return_usage("AL", bs, sl)[-1] - old_capacity*0.9 > 0) or (old_capacity*0.8 - stats.return_usage("AL", bs, sl)[-1] > 0): # refer the last timestep
                        sl.capacity.capacity = stats.return_usage("AL", bs, sl)[-1] * 1.176
                    t += sl.capacity.capacity
                if 0.9*bs.Wa < t:
                    for sl in bs.access_slices:
                        sl.capacity.capacity = stats.return_usage("AL", bs, sl)[-1]
                    logger.info(f"Error: could't reserve extra access link bandwidth at bs{bs.pk}")
                
                t = 0
                for sl in bs.backhaul_slices:
                    old_capacity = sl.capacity.capacity
                    #if (max(stats.return_usage("BL", bs, sl)[-10:]) - old_capacity*0.9 > 0) or (old_capacity*0.8 - max(stats.return_usage("BL", bs, sl)[-10:]) > 0): # refer last 10 timesteps
                    if (stats.return_usage("BL", bs, sl)[-1] - old_capacity*0.9 > 0) or (old_capacity*0.8 - stats.return_usage("BL", bs, sl)[-1] > 0): # refer the last timestep
                        sl.capacity.capacity = stats.return_usage("BL", bs, sl)[-1] * 1.176
                    t += sl.capacity.capacity
                if 0.9*bs.Wb < t:
                    for sl in bs.backhaul_slices:
                        sl.capacity.capacity = stats.return_usage("BL", bs, sl)[-1]
                    logger.info(f"Error: could't reserve extra backhaul link bandwidth at bs{bs.pk}")
        
        
        # =Reset base station and slice usage=
        for bs in base_stations:
            bs.AL_capacity.level = 0
            bs.BL_capacity.level = 0
            for sl in bs.access_slices:
                sl.capacity.level = 0
            for sl in bs.backhaul_slices:
                sl.capacity.level = 0
        
        # =Move UEs=
        for c in clients:
            c.move_phase(i)
        
        # =Preparate generating route from UE to IAB donor=
        for c in clients:
            if  c.requested_usage <= 0:
                c.generate_usage(i)
            
            c.usage_randomizer(i)
            
            # check whether UE is within range of any base stations
            c.in_range = False
            for bs in base_stations:
                if utils.distance(c.x, c.y, bs.x, bs.y) <= bs.coverage.radius:
                    c.in_range = True
            
            # put data into df_user_info
            try:
                df_user_info.loc[c.pk, ["id", "slice", "bandwidth", "x", "y", "green_to_donor", "route_to_donor", "pre_bs", "pre_route", "in_range"]]\
                            = [c.pk, c.subscribed_slice_index, c.requested_usage, c.x, c.y, False, [], c.pre_bs, c.pre_route, c.in_range]
            except:
                logger.error("Error: couldn't find routes from UEs to the donor")
                logger.info('======logging proccess terminated======')
                logger.removeHandler(file_handler)
                return False
        
        # =Activate route generator=
        df_user_info = route_generate.route_generate(df_user_info, data, bs_in_range, base_stations, data_dir, slice_quantity)
        for c in clients:
            c.green_to_donor = c.df_user_info.iat[c.pk, 5]
            c.route_to_donor = c.df_user_info.iat[c.pk, 6]
            if c.green_to_donor == True:
                c.base_station = c.base_stations[c.df_user_info.iat[c.pk, 6][0]]
            else:
                c.base_station = None
        
        # =Connect UE to or disconnect UE from access link=
        for c in clients:
            if c.green_to_donor:
                c.start_consume(i)
                if c.base_station != c.pre_bs or c.route_to_donor != c.pre_route:
                    c.connect(i)
            else:
                if c.pre_bs != None and c.base_station == None: # access no base station but accessed in one previous timestep
                    c.disconnect(i)
        
        # =Update simulator iteration counter=
        if i % 60 == 0 and i != 0:
            print(f'==={int(i/60)} times===')
        
        for c in clients:
            c.pre_bs = c.base_station
            c.pre_route = c.route_to_donor
        
        if i >= 11:
            stats.collect(i)
        
    # ===== simluation end =====
    
    # calculate run time
    end_time = time.time()
    running_time = end_time - start_time
    logger.info(f'run time: {round(running_time)}s')
    
    # output stats to text file
    with open(f"{data_dir}/stats_text.txt","wt") as f:
        f.write(f"{stats.get_stats()}")
    
    # output graph
    graph = Graph.Graph(base_stations, clients, slice_variation, (0, SIM_TIME),
                        ((x_vals['min'], x_vals['max']), (y_vals['min'], y_vals['max'])), data_dir, bs_in_range)
    graph.draw_all(**stats.get_stats())
    
    # terminate logging
    logger.info(f'{datetime.datetime.now()}')
    logger.info('======logging proccess terminated======')
    logger.removeHandler(file_handler)
    
    # return results of simulation
    return stats.return_sim_result()