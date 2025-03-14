import logging
import numpy as np

Simlogger = logging.getLogger('Sim.' + __name__)
logger = logging.getLogger('main.' + __name__)

# A class to store statistical data
class Stats:
    def __init__(self, base_stations, slice_variation, slice_quantity, clients, area, SIM_TIME, data_dir):
        self.base_stations = base_stations
        self.clients = clients
        self.area = area
        self.slice_variation = slice_variation
        self.slice_quantity = slice_quantity
        self.SIM_TIME = SIM_TIME
        self.data_dir = data_dir
        
        self.bs_link_usage = []
        self.bs_link_ue_count = []
        self.slice_link_usage = []
        self.slice_link_ue_count = []
        
        self.bs_link_usage = [[[]for _ in range(len(self.base_stations))]for _ in range(len(self.base_stations))]
        self.bs_link_ue_count = [[[]for _ in range(len(self.base_stations))]for _ in range(len(self.base_stations))]
        self.slice_link_usage = [[[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]for _ in range(len(self.base_stations))]
        self.slice_link_ue_count = [[[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]for _ in range(len(self.base_stations))]
        
        self.AL_bs_load_ratio = []
        self.BL_bs_load_ratio = []
        self.AL_bs_c_count = []
        self.BL_bs_c_count = []
        
        self.AL_slice_usage = []
        self.BL_slice_usage = []
        self.AL_slice_load_ratio = []
        self.BL_slice_load_ratio = []
        self.AL_slice_c_count = []
        self.BL_slice_c_count = []
        self.AL_slice_bandwidth_allocation = []
        self.BL_slice_bandwidth_allocation = []
        
        for bs in self.base_stations:
            self.AL_bs_load_ratio.append([])
            self.BL_bs_load_ratio.append([])
            self.AL_bs_c_count.append([])
            self.BL_bs_c_count.append([])
        
        self.AL_slice_usage = [[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.AL_slice_load_ratio = [[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.AL_slice_c_count = [[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.AL_slice_bandwidth_allocation = [[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.AL_bs_allocation_change_count = [[]for _ in range(len(self.base_stations))]
        self.AL_slice_allocation_change_count = [[]for _ in range(len(self.base_stations))]
        self.AL_bs_active_slice = [[]for _ in range(len(self.base_stations))]
        self.AL_slice_active = [[]for _ in range(len(self.base_stations))]
        self.AL_sl_bw_surplus = [[0 for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.AL_sl_bw_lack = [[0 for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.AL_sl_bw_surplus_time = [[0 for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.AL_sl_bw_lack_time = [[0 for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.AL_bs_bw_surplus_time = [0 for _ in range(len(self.base_stations))]
        self.AL_bs_bw_lack_time = [0 for _ in range(len(self.base_stations))]
        self.AL_bs_usage = [[] for _ in range(len(self.base_stations))]
        
        self.BL_slice_usage = [[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.BL_slice_load_ratio = [[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.BL_slice_c_count = [[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.BL_slice_bandwidth_allocation = [[[]for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.BL_bs_allocation_change_count = [[]for _ in range(len(self.base_stations))]
        self.BL_slice_allocation_change_count = [[]for _ in range(len(self.base_stations))]
        self.BL_bs_active_slice = [[]for _ in range(len(self.base_stations))]
        self.BL_slice_active = [[]for _ in range(len(self.base_stations))]
        self.BL_sl_bw_surplus = [[0 for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.BL_sl_bw_lack = [[0 for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.BL_sl_bw_surplus_time =[[0 for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.BL_sl_bw_lack_time =[[0 for _ in range(len(self.slice_variation))]for _ in range(len(self.base_stations))]
        self.BL_bs_bw_surplus_time = [0 for _ in range(len(self.base_stations))]
        self.BL_bs_bw_lack_time = [0 for _ in range(len(self.base_stations))]
        self.BL_bs_usage = [[] for _ in range(len(self.base_stations))]
        
        self.route_counter = [[], [], [], [], [], [], [], [], [], []]
        self.route_dict = {}
        
        for bs in self.base_stations:
            self.AL_bs_allocation_change_count[bs.pk].append(0)
            self.BL_bs_allocation_change_count[bs.pk].append(0)
            for sl in range(len(bs.access_slices)):
                self.AL_slice_allocation_change_count[bs.pk].append(0)
                self.BL_slice_allocation_change_count[bs.pk].append(0)
                self.AL_slice_active[bs.pk].append(0)
                self.BL_slice_active[bs.pk].append(0)
    
    def get_stats(self):
        stats_to_return = {"AL_bs_load_ratio":self.AL_bs_load_ratio, "BL_bs_load_ratio":self.BL_bs_load_ratio, 
                            "AL_bs_c_count":self.AL_bs_c_count, "BL_bs_c_count":self.BL_bs_c_count,
                            "AL_slice_usage":self.AL_slice_usage, "BL_slice_usage":self.BL_slice_usage, 
                            "AL_slice_load_ratio":self.AL_slice_load_ratio, "BL_slice_load_ratio":self.BL_slice_load_ratio, 
                            "AL_slice_c_count":self.AL_slice_c_count, "BL_slice_c_count":self.BL_slice_c_count, 
                            "AL_slice_bandwidth_allocation":self.AL_slice_bandwidth_allocation, "BL_slice_bandwidth_allocation":self.BL_slice_bandwidth_allocation, 
                            "slice_link_usage":self.slice_link_usage, "slice_link_ue_count":self.slice_link_ue_count,
                            "bs_link_usage":self.bs_link_usage, "bs_link_ue_count":self.bs_link_ue_count, 
                            "AL_sl_bw_surplus": self.AL_sl_bw_surplus, "BL_sl_bw_surplus": self.BL_sl_bw_surplus,
                            "AL_sl_bw_lack": self.AL_sl_bw_lack, "BL_sl_bw_lack": self.BL_sl_bw_lack,
                            "AL_sl_bw_surplus_time": self.AL_sl_bw_surplus_time, "BL_sl_bw_surplus_time": self.BL_sl_bw_surplus_time,
                            "AL_sl_bw_lack_time": self.AL_sl_bw_lack_time, "BL_sl_bw_lack_time": self.BL_sl_bw_lack_time,
                            "route_counter": self.route_counter, "route_dict": self.route_dict,
                            "AL_bs_usage": self.AL_bs_usage, "BL_bs_usage": self.BL_bs_usage, 
                            }
        return stats_to_return

    def collect(self, s_time):
        
        self.s_time = s_time
        
        for bs1 in self.base_stations:
            for bs2 in self.base_stations:
                self.bs_link_usage[bs1.pk][bs2.pk].append(0)
                self.bs_link_ue_count[bs1.pk][bs2.pk].append(0)
                for sl in bs1.access_slices:
                    self.slice_link_usage[bs1.pk][bs2.pk][sl.pk].append(0)
                    self.slice_link_ue_count[bs1.pk][bs2.pk][sl.pk].append(0)
        
        for i in range(len(self.base_stations)):
            self.AL_bs_usage[i].append(0)
            self.BL_bs_usage[i].append(0)
        self.get_total_used_bw()
        self.get_avg_slice_load_ratio()
        self.get_avg_slice_client_count()
        self.get_active_slice()
        
        for i in range(9):
            self.route_counter[i].append(0)
        # link usage
        for c in self.clients:
            if str(f"{c.route_to_donor}") in self.route_dict.keys():
                self.route_dict[str(f"{c.route_to_donor}")] += 1
            else:
                self.route_dict.setdefault(str(f"{c.route_to_donor}"), 1)
            
            if c.route_to_donor == [1,4,7,8,0]:
                self.route_counter[0][-1] += 1
            elif c.route_to_donor == [2,5,8,0]:
                self.route_counter[1][-1] += 1
            elif c.route_to_donor == [2,5,6,0]:
                self.route_counter[2][-1] += 1
            elif c.route_to_donor == [2,3,6,0]:
                self.route_counter[3][-1] += 1
            elif c.route_to_donor == [3,6,0]:
                self.route_counter[4][-1] += 1
            elif c.route_to_donor == [5,8,0]:
                self.route_counter[5][-1] += 1
            elif c.route_to_donor == [8,0]:
                self.route_counter[6][-1] += 1
            elif c.route_to_donor == [0]:
                self.route_counter[7][-1] += 1
            else:
                self.route_counter[8][-1] += 1
            
            
            g = 0
            for _ in range(len(c.route_to_donor)-1):
                self.bs_link_usage[c.route_to_donor[g]][c.route_to_donor[g+1]][-1] += c.requested_usage
                self.bs_link_ue_count[c.route_to_donor[g]][c.route_to_donor[g+1]][-1] += 1
                self.slice_link_usage[c.route_to_donor[g]][c.route_to_donor[g+1]][c.subscribed_slice_index][-1] += c.requested_usage
                self.slice_link_ue_count[c.route_to_donor[g]][c.route_to_donor[g+1]][c.subscribed_slice_index][-1] += 1
                g += 1

    def get_total_used_bw(self):
        t, c, connected_users = 0, 0, 0
        O_add_1, P_add_1 = False, False
        for bs in self.base_stations:
            for sl in bs.access_slices:
                t += sl.capacity.level
                self.AL_slice_usage[bs.pk][sl.pk].append(sl.capacity.level)
                self.AL_bs_usage[bs.pk][-1] += sl.capacity.level
                self.AL_slice_bandwidth_allocation[bs.pk][sl.pk].append(sl.capacity.capacity)
                
                if self.s_time >= 21:
                    if sl.capacity.level - sl.capacity.capacity*0.9 > 0:
                        self.AL_sl_bw_lack[bs.pk][sl.pk] += sl.capacity.level - sl.capacity.capacity*0.9
                        self.AL_sl_bw_lack_time[bs.pk][sl.pk] += 1
                        #logger.info(f"BS{bs.pk}\tSL{sl.pk}\tAL_lack amount\t{sl.capacity.level - sl.capacity.capacity*0.9}")
                        P_add_1 = True
                    elif sl.capacity.capacity*0.8 - sl.capacity.level > 0:
                        self.AL_sl_bw_surplus[bs.pk][sl.pk] += sl.capacity.capacity*0.8 - sl.capacity.level
                        self.AL_sl_bw_surplus_time[bs.pk][sl.pk] += 1
                        #logger.info(f"BS{bs.pk}\tSL{sl.pk}\tAL_surplus amount\t{sl.capacity.capacity*0.8 - sl.capacity.level}")
                        O_add_1 = True
                
                connected_users += sl.connected_users
                if len(self.AL_slice_bandwidth_allocation[bs.pk][sl.pk]) >= 2:
                    if self.AL_slice_bandwidth_allocation[bs.pk][sl.pk][-1] != self.AL_slice_bandwidth_allocation[bs.pk][sl.pk][-2]:
                        c += 1
                        self.AL_slice_allocation_change_count[bs.pk][sl.pk] += 1
            if P_add_1:
                self.AL_bs_bw_lack_time[bs.pk] += 1
            if O_add_1:
                self.AL_bs_bw_surplus_time[bs.pk] += 1
            O_add_1, P_add_1 = False, False
            
            self.AL_bs_allocation_change_count[bs.pk].append(c)
            t, c, connected_users = 0, 0, 0
        
        t, c, connected_users = 0, 0, 0
        for bs in self.base_stations:
            for sl in bs.backhaul_slices:
                t += sl.capacity.level
                self.BL_slice_usage[bs.pk][sl.pk].append(sl.capacity.level)
                self.BL_bs_usage[bs.pk][-1] += sl.capacity.level
                self.BL_slice_bandwidth_allocation[bs.pk][sl.pk].append(sl.capacity.capacity)
                
                if self.s_time >= 21:
                    if sl.capacity.level - sl.capacity.capacity*0.9 > 0:
                        self.BL_sl_bw_lack[bs.pk][sl.pk] += sl.capacity.level - sl.capacity.capacity*0.9
                        self.BL_sl_bw_lack_time[bs.pk][sl.pk] += 1
                        #logger.info(f"BS{bs.pk}\tSL{sl.pk}\tBL_lack amount\t{sl.capacity.level - sl.capacity.capacity*0.9}")
                        P_add_1 = True
                    elif sl.capacity.capacity*0.8 - sl.capacity.level > 0:
                        self.BL_sl_bw_surplus[bs.pk][sl.pk] += sl.capacity.capacity*0.8 - sl.capacity.level
                        self.BL_sl_bw_surplus_time[bs.pk][sl.pk] += 1
                        #logger.info(f"BS{bs.pk}\tSL{sl.pk}\tBL_surplus amount\t{sl.capacity.capacity*0.8 - sl.capacity.level}")
                        O_add_1 = True
                
                connected_users += sl.connected_users
                if len(self.BL_slice_bandwidth_allocation[bs.pk][sl.pk]) >= 2:
                    if self.BL_slice_bandwidth_allocation[bs.pk][sl.pk][-1] != self.BL_slice_bandwidth_allocation[bs.pk][sl.pk][-2]:
                        c += 1
                        self.BL_slice_allocation_change_count[bs.pk][sl.pk] += 1
            if P_add_1:
                self.BL_bs_bw_lack_time[bs.pk] += 1
            if O_add_1:
                self.BL_bs_bw_surplus_time[bs.pk] += 1
            O_add_1, P_add_1 = False, False
            
            self.BL_bs_allocation_change_count[bs.pk].append(c)
            t, c, connected_users = 0, 0, 0
        return t

    def get_active_slice(self):
        c = 0
        for bs in self.base_stations:
            for sl in bs.access_slices:
                if self.AL_slice_bandwidth_allocation[bs.pk][sl.pk][-1] != 0 or self.AL_slice_usage[bs.pk][sl.pk][-1] != 0:
                    c += 1
                    self.AL_slice_active[bs.pk][sl.pk] += 1
                #logger.info(f"AL active {self.AL_slice_active[bs.pk][sl.pk]}")
            self.AL_bs_active_slice[bs.pk].append(c)
            c = 0
        
        c = 0
        for bs in self.base_stations:
            for sl in bs.backhaul_slices:
                if self.BL_slice_bandwidth_allocation[bs.pk][sl.pk][-1] != 0 or self.BL_slice_usage[bs.pk][sl.pk][-1] != 0:
                    c += 1
                    self.BL_slice_active[bs.pk][sl.pk] += 1
                #logger.info(f"BL active {self.BL_slice_active[bs.pk][sl.pk]}")
            self.BL_bs_active_slice[bs.pk].append(c)
            c = 0
    
    def get_avg_slice_load_ratio(self):
        i, j = 0, 0
        for bs in self.base_stations:
            self.AL_bs_load_ratio[bs.pk].append(bs.AL_capacity.level/bs.Wa if bs.Wa != 0 else 0)
            
            for sl in bs.access_slices:
                self.AL_slice_load_ratio[bs.pk][sl.pk].append(sl.capacity.level/sl.capacity.capacity if sl.capacity.capacity != 0 else 0)
                if self.AL_slice_load_ratio[bs.pk][sl.pk][-1] > 0.9 and sl.capacity.capacity != 0:
                    i += 1
                elif sl.capacity.capacity == 0 and sl.capacity.level != 0:
                    i += 1
                elif self.AL_slice_load_ratio[bs.pk][sl.pk][-1] < 0.8 and sl.capacity.capacity != 0:
                    j += 1
                #logger.info(f'{sl.capacity.level}, {sl.capacity.capacity}')
            
            i = 0
            j = 0
        
        i, j = 0, 0
        for bs in self.base_stations:
            self.BL_bs_load_ratio[bs.pk].append(bs.BL_capacity.level/bs.Wa if bs.Wa != 0 else 0)
            
            for sl in bs.backhaul_slices:
                self.BL_slice_load_ratio[bs.pk][sl.pk].append(sl.capacity.level/sl.capacity.capacity if sl.capacity.capacity != 0 else 0)
                if self.BL_slice_load_ratio[bs.pk][sl.pk][-1] > 0.9 and sl.capacity.capacity != 0:
                    i += 1
                elif sl.capacity.capacity == 0 and sl.capacity.level != 0:
                    i += 1
                elif self.BL_slice_load_ratio[bs.pk][sl.pk][-1] < 0.8 and sl.capacity.capacity != 0:
                    j += 1
                #logger.info(f'{sl.capacity.level}, {sl.capacity.capacity}')
            i = 0
            j = 0

    def get_avg_slice_client_count(self):
        t = 0
        for bs in self.base_stations:
            for sl in bs.access_slices:
                t += sl.connected_users
                self.AL_slice_c_count[bs.pk][sl.pk].append(sl.connected_users)
            self.AL_bs_c_count[bs.pk].append(t)
            t = 0
        
        t = 0
        for bs in self.base_stations:
            for sl in bs.backhaul_slices:
                t += sl.connected_users
                self.BL_slice_c_count[bs.pk][sl.pk].append(sl.connected_users)
            self.BL_bs_c_count[bs.pk].append(t)
            t = 0

    def is_client_in_coverage(self, client):
        xs, ys = self.area
        return True if xs[0] <= client.x <= xs[1] and ys[0] <= client.y <= ys[1] else False
    
    def return_usage(self, ALorBL, bs, sl):
        if ALorBL == "AL":
            return self.AL_slice_usage[bs.pk][sl.pk]
        elif ALorBL == "BL":
            return self.BL_slice_usage[bs.pk][sl.pk]
    
    def return_load_ratio(self, ALorBL, bs):
        if ALorBL == "AL":
            return self.AL_bs_load_ratio[bs.pk]
        elif ALorBL == "BL":
            return self.BL_bs_load_ratio[bs.pk]
    
    def return_sim_result (self):
        Simlogger.info(f"BL_bs_usage = {self.BL_bs_usage}")
        Simlogger.info(f"bs_link_usage = {self.bs_link_usage}")
        Simlogger.info(f"route_counter = {self.route_counter}")
        Simlogger.info(f"route_dict = {self.route_dict}")
        
        
        l = list(self.route_dict)
        for j in range(len(l)):
            self.route_dict[str(f"{l[j]}")] = self.route_dict[str(f"{l[j]}")] / self.SIM_TIME
        
        allocation_change_count = []
        for bs in self.base_stations:
            allocation_change_count.append([sum(self.AL_bs_allocation_change_count[bs.pk][10:])/(self.SIM_TIME/10),
                                                sum(self.BL_bs_allocation_change_count[bs.pk][10:])/(self.SIM_TIME/10)])
        
        Simlogger.info(f"allo_change {allocation_change_count}")
        
        sum_AL_slice_allocation_change_count = []
        sum_BL_slice_allocation_change_count = []
        for bs in self.base_stations:
            sum_AL_slice_allocation_change_count.append(sum(self.AL_slice_allocation_change_count[bs.pk]))
            sum_BL_slice_allocation_change_count.append(sum(self.BL_slice_allocation_change_count[bs.pk]))
        
        for bs in self.base_stations:
            self.AL_bs_active_slice[bs.pk] = np.mean(self.AL_bs_active_slice[bs.pk])
            self.BL_bs_active_slice[bs.pk] = np.mean(self.BL_bs_active_slice[bs.pk])
        
        mean_AL_slice_allocation_change_count = []
        mean_BL_slice_allocation_change_count = []
        
        for bs in self.base_stations:
            mean_AL_slice_allocation_change_count.append((sum_AL_slice_allocation_change_count[bs.pk])/(self.SIM_TIME/10))
            mean_BL_slice_allocation_change_count.append((sum_BL_slice_allocation_change_count[bs.pk])/(self.SIM_TIME/10))
            
            Simlogger.info(f"<{self.slice_quantity}> mean AL active {self.AL_bs_active_slice[bs.pk]}")
            Simlogger.info(f"<{self.slice_quantity}> mean BL active {self.BL_bs_active_slice[bs.pk]}")
        
        mean_AL_slice_allocation_change_count = np.mean(mean_AL_slice_allocation_change_count)
        mean_BL_slice_allocation_change_count = np.mean(mean_BL_slice_allocation_change_count)
        
        
        # equivalent to E_i
        AL_sl_bw_surplus = [[]for _ in range(len(self.base_stations))]
        BL_sl_bw_surplus = [[]for _ in range(len(self.base_stations))]
        for bs in self.base_stations:
            for sl in bs.access_slices:
                if self.AL_sl_bw_surplus_time[bs.pk][sl.pk] != 0:
                    AL_sl_bw_surplus[bs.pk].append(self.AL_sl_bw_surplus[bs.pk][sl.pk]/self.AL_sl_bw_surplus_time[bs.pk][sl.pk])
                    #AL_sl_bw_surplus[bs.pk].append(self.AL_sl_bw_surplus[bs.pk][sl.pk])
                else:
                    AL_sl_bw_surplus[bs.pk].append(0)
                if self.BL_sl_bw_surplus_time[bs.pk][sl.pk] != 0:
                    BL_sl_bw_surplus[bs.pk].append(self.BL_sl_bw_surplus[bs.pk][sl.pk]/self.BL_sl_bw_surplus_time[bs.pk][sl.pk])
                    #BL_sl_bw_surplus[bs.pk].append(self.BL_sl_bw_surplus[bs.pk][sl.pk])
                else:
                    BL_sl_bw_surplus[bs.pk].append(0)
        Simlogger.info(f"AL: E_i {AL_sl_bw_surplus}")
        Simlogger.info(f"BL: E_i {BL_sl_bw_surplus}")
        
        # equivalent to L_i
        AL_sl_bw_lack = [[]for _ in range(len(self.base_stations))]
        BL_sl_bw_lack = [[]for _ in range(len(self.base_stations))]
        for bs in self.base_stations:
            for sl in bs.access_slices:
                if self.AL_sl_bw_lack_time[bs.pk][sl.pk] != 0:
                    AL_sl_bw_lack[bs.pk].append(self.AL_sl_bw_lack[bs.pk][sl.pk]/self.AL_sl_bw_lack_time[bs.pk][sl.pk])
                else:
                    AL_sl_bw_lack[bs.pk].append(0)
                    #AL_sl_bw_lack[bs.pk].append(self.AL_sl_bw_lack[bs.pk][sl.pk])
                if self.BL_sl_bw_lack_time[bs.pk][sl.pk] != 0:
                    BL_sl_bw_lack[bs.pk].append(self.BL_sl_bw_lack[bs.pk][sl.pk]/self.BL_sl_bw_lack_time[bs.pk][sl.pk])
                    #BL_sl_bw_lack[bs.pk].append(self.BL_sl_bw_lack[bs.pk][sl.pk])
                else:
                    BL_sl_bw_lack[bs.pk].append(0)
        Simlogger.info(f"AL: L_i {AL_sl_bw_lack}")
        Simlogger.info(f"BL: L_i {BL_sl_bw_lack}")
        
        # equivalent to bar_W
        AL_sl_bw_surplus_time_mean = []
        BL_sl_bw_surplus_time_mean = []
        for bs in self.base_stations:
            AL_sl_bw_surplus_time_mean.append(sum(self.AL_sl_bw_surplus_time[bs.pk])/len(bs.access_slices))
            BL_sl_bw_surplus_time_mean.append(sum(self.BL_sl_bw_surplus_time[bs.pk])/len(bs.access_slices))
        #for bs in self.base_stations:
        #    AL_sl_bw_surplus_time_mean.append(sum(self.AL_sl_bw_surplus_time[bs.pk]))
        #    BL_sl_bw_surplus_time_mean.append(sum(self.BL_sl_bw_surplus_time[bs.pk]))
        Simlogger.info(f"AL: bar_W {AL_sl_bw_surplus_time_mean}")
        Simlogger.info(f"BL: bar_W {BL_sl_bw_surplus_time_mean}")
        
        # equivalent to bar_V
        AL_sl_bw_lack_time_mean = []
        BL_sl_bw_lack_time_mean = []
        for bs in self.base_stations:
            AL_sl_bw_lack_time_mean.append(sum(self.AL_sl_bw_lack_time[bs.pk])/len(bs.access_slices))
            BL_sl_bw_lack_time_mean.append(sum(self.BL_sl_bw_lack_time[bs.pk])/len(bs.access_slices))
        #for bs in self.base_stations:
        #    AL_sl_bw_lack_time_mean.append(sum(self.AL_sl_bw_lack_time[bs.pk]))
        #    BL_sl_bw_lack_time_mean.append(sum(self.BL_sl_bw_lack_time[bs.pk]))
        Simlogger.info(f"AL: bar_V {AL_sl_bw_lack_time_mean}")
        Simlogger.info(f"BL: bar_V {BL_sl_bw_lack_time_mean}")
        
        # equivalent to bar_E
        AL_sl_bw_surplus_mean = []
        BL_sl_bw_surplus_mean = []
        for bs in self.base_stations:
            AL_sl_bw_surplus_mean.append(sum(AL_sl_bw_surplus[bs.pk])/len(bs.access_slices))
            BL_sl_bw_surplus_mean.append(sum(BL_sl_bw_surplus[bs.pk])/len(bs.access_slices))
        #for bs in self.base_stations:
        #    AL_sl_bw_surplus_mean.append(sum(AL_sl_bw_surplus[bs.pk]))
        #    BL_sl_bw_surplus_mean.append(sum(BL_sl_bw_surplus[bs.pk]))
        Simlogger.info(f"AL: bar_E {AL_sl_bw_surplus_mean}")
        Simlogger.info(f"BL: bar_E {BL_sl_bw_surplus_mean}")
        
        # equivalent to bar_L
        AL_sl_bw_lack_mean = []
        BL_sl_bw_lack_mean = []
        for bs in self.base_stations:
            AL_sl_bw_lack_mean.append(sum(AL_sl_bw_lack[bs.pk])/len(bs.access_slices))
            BL_sl_bw_lack_mean.append(sum(BL_sl_bw_lack[bs.pk])/len(bs.access_slices))
        #for bs in self.base_stations:
        #    AL_sl_bw_lack_mean.append(sum(AL_sl_bw_lack[bs.pk]))
        #    BL_sl_bw_lack_mean.append(sum(BL_sl_bw_lack[bs.pk]))
        Simlogger.info(f"AL: bar_L {AL_sl_bw_lack_mean}")
        Simlogger.info(f"BL: bar_L {BL_sl_bw_lack_mean}")
        
        # equivalent to M_j
        AL_bs_bw_surplus = []
        BL_bs_bw_surplus = []
        for bs in self.base_stations:
            if self.AL_bs_bw_surplus_time[bs.pk] != 0:
                AL_bs_bw_surplus.append(sum(self.AL_sl_bw_surplus[bs.pk])/self.AL_bs_bw_surplus_time[bs.pk])
            else:
                AL_bs_bw_surplus.append(0)
            if self.BL_bs_bw_surplus_time[bs.pk] != 0:
                BL_bs_bw_surplus.append(sum(self.BL_sl_bw_surplus[bs.pk])/self.BL_bs_bw_surplus_time[bs.pk])
            else:
                BL_bs_bw_surplus.append(0)
        Simlogger.info(f"AL: M_j {AL_bs_bw_surplus}")
        Simlogger.info(f"BL: M_j {BL_bs_bw_surplus}")
        
        # equivalent to N_j
        AL_bs_bw_lack = []
        BL_bs_bw_lack = []
        for bs in self.base_stations:
            if self.AL_bs_bw_lack_time[bs.pk] != 0:
                AL_bs_bw_lack.append(sum(self.AL_sl_bw_lack[bs.pk])/self.AL_bs_bw_lack_time[bs.pk])
            else:
                AL_bs_bw_lack.append(0)
            if self.BL_bs_bw_lack_time[bs.pk] != 0:
                BL_bs_bw_lack.append(sum(self.BL_sl_bw_lack[bs.pk])/self.BL_bs_bw_lack_time[bs.pk])
            else:
                BL_bs_bw_lack.append(0)
        Simlogger.info(f"AL: N_j {AL_bs_bw_lack}")
        Simlogger.info(f"BL: N_j {BL_bs_bw_lack}")
        
        # equivalent to bar_M
        AL_bs_bw_surplus_mean = sum(AL_bs_bw_surplus)/len(self.base_stations)
        BL_bs_bw_surplus_mean = sum(BL_bs_bw_surplus)/len(self.base_stations)
        Simlogger.info(f"AL: bar_M {AL_bs_bw_surplus_mean}")
        Simlogger.info(f"BL: bar_M {BL_bs_bw_surplus_mean}")
        
        # equivalent to bar_N
        AL_bs_bw_lack_mean = sum(AL_bs_bw_lack)/len(self.base_stations)
        BL_bs_bw_lack_mean = sum(BL_bs_bw_lack)/len(self.base_stations)
        Simlogger.info(f"AL: bar_N {AL_bs_bw_lack_mean}")
        Simlogger.info(f"BL: bar_N {BL_bs_bw_lack_mean}")
        
        return allocation_change_count, mean_AL_slice_allocation_change_count, mean_BL_slice_allocation_change_count\
                , AL_sl_bw_surplus_mean, BL_sl_bw_surplus_mean, AL_sl_bw_lack_mean, BL_sl_bw_lack_mean\
                , AL_sl_bw_surplus_time_mean, BL_sl_bw_surplus_time_mean, AL_sl_bw_lack_time_mean, BL_sl_bw_lack_time_mean\
                , AL_bs_bw_surplus, BL_bs_bw_surplus, AL_bs_bw_lack, BL_bs_bw_lack\
                , self.AL_bs_bw_surplus_time, self.BL_bs_bw_surplus_time, self.AL_bs_bw_lack_time, self.BL_bs_bw_lack_time
        