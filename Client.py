import random, logging
import numpy as np

from utils import format_bps

logger = logging.getLogger('main.' + __name__)

class Client:
    def __init__(self, pk, x, y, mobility_pattern, subscribed_slice_index, stat_collector,
                slice_weights, base_stations, area_x, area_y, df_user_info, access_slices, backhaul_slices, requested_usage, data_dir):
        # please refer to making instance of each UEs in main.py
        self.pk = pk
        self.x = x
        self.y = y
        self.mobility_pattern = mobility_pattern
        self.base_station = None
        self.stat_collector = stat_collector
        self.subscribed_slice_index = subscribed_slice_index
        self.requested_usage = requested_usage
        self.connected = False
        self.base_stations = base_stations
        self.area_x = area_x
        self.area_y = area_y
        self.df_user_info = df_user_info
        self.green_to_donor = False
        self.access_slices = access_slices
        self.backhaul_slices = backhaul_slices
        self.route_to_donor = []
        self.pre_bs = None
        self.pre_route = []
        self.data_dir = data_dir
        self.slice_weights = slice_weights
    
    # generate UE's requesting bandwidth
    def generate_usage(self, i):
        self.requested_usage = self.access_slices[self.subscribed_slice_index].usage_pattern.generate()
        logger.info(f'[{i}] Client_{self.pk} [{self.x}, {self.y}] ^ requests {format_bps(self.requested_usage)} usage.')
    
    # update how many UEs is using the access or backhaul link of the base station
    def connect(self, i):
        self.connected = True
        
        if self.pre_bs != None:
            self.disconnect(i)
            logger.info(f'[{i}] Client_{self.pk} [{self.x}, {self.y}] <--> handed over to {self.base_station}')
        
        # AL
        self.base_stations[self.route_to_donor[0]].access_slices[self.subscribed_slice_index].connected_users += 1
        # BL
        if len(self.route_to_donor) >= 2:
            for a in self.route_to_donor:
                self.base_stations[a].backhaul_slices[self.subscribed_slice_index].connected_users += 1
        
        logger.info(f'[{i}] Client_{self.pk} [{self.x}, {self.y}] -> connected to {self.base_station}, slice:{self.subscribed_slice_index}, route to donor is: {self.route_to_donor}, got {format_bps(self.requested_usage)}')
    
    # consume bandwidth of the base stations on the route
    def start_consume(self, i):
        # AL
        self.base_stations[self.route_to_donor[0]].access_slices[self.subscribed_slice_index].capacity.get(self.requested_usage)
        self.base_stations[self.route_to_donor[0]].AL_capacity.get(self.requested_usage)
        # BL
        if len(self.route_to_donor) >= 2:
            # nodes
            self.base_stations[self.route_to_donor[0]].backhaul_slices[self.subscribed_slice_index].capacity.get(self.requested_usage)
            self.base_stations[self.route_to_donor[0]].BL_capacity.get(self.requested_usage)
            for a in self.route_to_donor[1:-1]:
                self.base_stations[a].backhaul_slices[self.subscribed_slice_index].capacity.get(2*self.requested_usage)
                self.base_stations[a].BL_capacity.get(2*self.requested_usage)
            # donor
            self.base_stations[self.route_to_donor[-1]].backhaul_slices[self.subscribed_slice_index].capacity.get(self.requested_usage)
            self.base_stations[self.route_to_donor[-1]].BL_capacity.get(self.requested_usage)
    
    # not in use
    def disconnect(self, i):
        # AL
        self.pre_bs.access_slices[self.subscribed_slice_index].connected_users -= 1
        # BL
        if len(self.pre_route) >= 2:
            for a in self.pre_route:
                self.base_stations[a].backhaul_slices[self.subscribed_slice_index].connected_users -= 1
        
        self.connected = False
        logger.info(f'[{i}] Client_{self.pk} [{self.x}, {self.y}] <- disconnected from {self.pre_bs}')
    
    # move UE
    def move_phase(self, i):
        vec = 2*np.pi*np.random.uniform(0, 1)
        amount = np.random.uniform(self.mobility_pattern[0], self.mobility_pattern[1])
        x = amount*np.cos(vec)
        y = amount*np.sin(vec)
        
        while self.x + x > self.area_x[1] or self.x + x < self.area_x[0] or self.y + y > self.area_y[1] or self.y + y < self.area_y[0]:
            vec = 2*np.pi*np.random.uniform(0, 1)
            amount = np.random.uniform(self.mobility_pattern[0], self.mobility_pattern[1])
            x = amount*np.cos(vec)
            y = amount*np.sin(vec)
        self.x += x
        self.y += y
        self.x = round(self.x, 2)
        self.y = round(self.y, 2)
    
    # which slice the UE is accumulated
    def get_slice(self):
        if self.base_station is None:
            return None
        return self.base_station.access_slices[self.subscribed_slice_index]
    
    # not in use
    def usage_randomizer(self, i):
        r = random.random()
        w = [0, 1] # [change, change + maintain usage]
        self.requested_usage
        if w[0] > r: # change or maintain connection
            self.requested_usage = random.randint(100, 100)

    def __str__(self):
        return f'Client_{self.pk} [{self.x:<5}, {self.y:>5}] connected to: slice={self.get_slice()} @ {self.base_station}\t with mobility pattern of {self.mobility_pattern}'
