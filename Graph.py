from matplotlib import gridspec
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import randomcolor

# A class of graph
class Graph:
    def __init__(self, base_stations, clients, slice_variation, xlim, map_limits, data_dir, bs_in_range):
        self.base_stations = base_stations
        self.clients = clients
        self.xlim = xlim
        self.map_limits = map_limits
        self.fig = plt.figure(figsize=(16,9))
        self.slice_variation = slice_variation
        self.data_dir = data_dir
        self.bs_in_range = bs_in_range
        
        self.gridspec_x_value = 0
        for bs in self.base_stations:
            self.gridspec_x_value += 1
        self.gridspec_x_value = self.gridspec_x_value//4 + 1
        
        rand_color = randomcolor.RandomColor()
        colors = rand_color.generate(luminosity='bright', count=len(self.base_stations))
        # distinct color-set up to 9 base stations
        colors = ["red", "yellow", "deepskyblue", "green", "magenta", "cyan", "lime", "blueviolet", "pink"]
        #colors = [np.random.randint(256*0.2, 256*0.7+1, size=(3,))/256 for __ in range(len(self.base_stations))]
        for c, bs in zip(colors, self.base_stations):
            bs.color = c
    
    def draw_all(self, **stats):
        self.draw_map()
        self.draw_stats(**stats)
        plt.clf()
        plt.close()

    # draw the map that shows the location of UEs and coverage area of base stations
    def draw_map(self):
        # map: UE and base station
        plt.figure()
        plt.rcParams["font.size"] = 4
        markers = ['o', 's', 'p', 'P', '*', 'H', 'X', 'D', 'v', '^', '<', '>', '1', '2', '3', '4']
        self.ax = plt.subplot(gridspec.GridSpec(1, 1)[0, 0])
        xlims, ylims = self.map_limits
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)
        self.ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f m'))
        self.ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f m'))
        self.ax.set_aspect('equal')
        
        # base stations
        for bs in self.base_stations:
            circle = plt.Circle(bs.coverage.center, bs.coverage.radius,
                                fill=False, linewidth=1, alpha=0.9, color=bs.color)
            
            #self.ax.scatter(bs.x, bs.y, color=bs.color, s=20)
            self.ax.add_artist(circle)
        
        # UE
        legend_indexed = []
        for c in self.clients:
            label = None
            try:
                if c.get_slice().name.split('_')[0] not in legend_indexed and c.base_station is not None:
                    label = c.get_slice().name.split('_')[0]
                    #legend_indexed.append(c.subscribed_slice_index)
                    legend_indexed.append(label)
                self.ax.scatter(c.x, c.y,
                                color=c.base_station.color if c.base_station is not None else '0.8',
                                label=label, 
                                s=5,
                                #marker=markers[c.subscribed_slice_index % len(markers)]
                                #marker="o" if 'S1' in c.get_slice().name else "s"
                                )
            except:
                self.ax.scatter(c.x, c.y,
                                color='gray',
                                label=label, 
                                s=5,
                                #marker=markers[c.subscribed_slice_index % len(markers)]
                                #marker="o"
                                )
        
        box = self.ax.get_position()
        self.ax.set_position([box.x0 - box.width * 0.05, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        plt.savefig(f"{self.data_dir}/overall_1.png", dpi=1000)
        
        # map: base station
        plt.figure()
        markers = ['o', 's', 'p', 'P', '*', 'H', 'X', 'D', 'v', '^', '<', '>', '1', '2', '3', '4']
        self.ax = plt.subplot(gridspec.GridSpec(1, 1)[0, 0])
        xlims, ylims = self.map_limits
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)
        self.ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f m'))
        self.ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f m'))
        self.ax.set_aspect('equal')
        
        # base stations
        for bs in self.base_stations:
            circle = plt.Circle(bs.coverage.center, bs.coverage.radius,
                                fill=False, linewidth=1, alpha=0.9, color=bs.color)
            
            #self.ax.scatter(bs.x, bs.y, color=bs.color, s=20)
            self.ax.add_artist(circle)
        
        plt.savefig(f"{self.data_dir}/overall_2.png", dpi=1000)

    # draw statistical data on graphs
    def draw_stats(self, **stats):
        # load ratio(access)
        """
        def load_ratio_graph_access(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(gridspec.GridSpec(4, self.gridspec_x_value)[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("ratio")
            for j in range(len(self.slice_variation)):
                self.ax.plot(stats['AL_slice_load_ratio'][bs_num][j])
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('Bandwidth usage ratio at donor(access)')
            else:
                self.ax.set_title(f'Bandwidth usage ratio at node{bs_num}(access)')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            load_ratio_graph_access(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/load_ratio(access).png", dpi=1000)
        
        
        # load ratio(backhaul)
        
        def load_ratio_graph_backhaul(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(gridspec.GridSpec(4, self.gridspec_x_value)[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("ratio"))
            for j in range(len(self.slice_variation)):
                self.ax.plot(stats['BL_slice_load_ratio'][bs_num][j])
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('Bandwidth usage ratio at donor(backhaul)')
            else:
                self.ax.set_title(f'Bandwidth usage ratio at node{bs_num}(backhaul)')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            load_ratio_graph_backhaul(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/load_ratio(backhaul).png", dpi=1000)
        
        # UE count(access)
        
        def UE_count_access(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(gridspec.GridSpec(4, self.gridspec_x_value)[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("UE count")
            for j in range(len(self.slice_variation)):
                self.ax.plot(stats['AL_slice_c_count'][bs_num][j])
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('The number of UEs using donor(access)')
            else:
                self.ax.set_title(f'The number of UEs using node{bs_num}(access)')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            UE_count_access(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/user_amount(access).png", dpi=1000)
        
        # UE count(backhaul)
        
        def UE_count_backhaul(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(gridspec.GridSpec(4, self.gridspec_x_value)[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("UE count")
            for j in range(len(self.slice_variation)):
                self.ax.plot(stats['BL_slice_c_count'][bs_num][j])
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('The number of UEs using donor(backhaul)')
            else:
                self.ax.set_title(f'The number of UEs using node{bs_num}(backhaul)')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            UE_count_backhaul(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/user_amount(backhaul).png", dpi=1000)
        """
        
        # bandwidth allocation
        """
        def bandwidth_allocation(bs_num, x_cap, y_cap):
            self.ax = plt.subplot(gridspec.GridSpec(4, self.gridspec_x_value)[y_cap, x_cap])
            plt.xlabel("time")
            plt.ylabel("bps")
            for j in range(len(self.slice_variation)):
                self.ax.plot(stats['AL_slice_bandwidth_allocation'][bs_num][j])
                self.ax.plot(stats['BL_slice_bandwidth_allocation'][bs_num][j])
            self.ax.set_xlim(self.xlim)
            locs = self.ax.get_xticks()
            locs[0] = self.xlim[0]
            locs[-1] = self.xlim[1]
            self.ax.set_xticks(locs)
            self.ax.use_sticky_edges = False
            if bs_num == 0:
                self.ax.set_title('Allocated bandwidth to slices at donor')
            else:
                self.ax.set_title(f'Allocated bandwidth to slices at node{bs_num}')
        
        plt.figure(figsize=((len(self.base_stations)//4+1)*4,9))
        
        for a in range(len(self.base_stations)):
            x_cap, y_cap = divmod(a, 4)
            bandwidth_allocation(a, x_cap, y_cap)
        
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/bandwidth_allocation.png", dpi=1000)
        """
        
        # link usage
        plt.figure(figsize=(26, 18))
        plt.rcParams["font.size"] = 19
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[0, 0])
        self.ax.plot([x/1000 for x in stats['BL_bs_usage'][1]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABnode1 Usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[0, 1])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][1][2],stats['bs_link_usage'][2][1])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode1-2 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[0, 2])
        self.ax.plot([x/1000 for x in stats["BL_bs_usage"][2]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABnode2 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[0, 3])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][2][3],stats['bs_link_usage'][3][2])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode2-3 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[0, 4])
        self.ax.plot([x/1000 for x in stats["BL_bs_usage"][3]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABnode3 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[1, 0])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][1][4],stats['bs_link_usage'][4][1])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode1-4 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[1, 2])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][2][5],stats['bs_link_usage'][5][2])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode2-5 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[1, 4])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][3][6],stats['bs_link_usage'][6][3])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode3-6 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[2, 0])
        self.ax.plot([x/1000 for x in stats["BL_bs_usage"][4]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABnode4 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[2, 1])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][4][5],stats['bs_link_usage'][5][4])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode4-5 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[2, 2])
        self.ax.plot([x/1000 for x in stats["BL_bs_usage"][5]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABnode5 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[2, 3])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][5][6],stats['bs_link_usage'][6][5])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode5-6 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[2, 4])
        self.ax.plot([x/1000 for x in stats["BL_bs_usage"][6]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABnode6 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[3, 0])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][4][7],stats['bs_link_usage'][7][4])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode4-7 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[3, 2])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][5][8],stats['bs_link_usage'][8][5])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode5-8 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[3, 4])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][6][0],stats['bs_link_usage'][0][6])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode6-IABdonor usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[4, 0])
        self.ax.plot([x/1000 for x in stats["BL_bs_usage"][7]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABnode7 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[4, 1])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][7][8],stats['bs_link_usage'][8][7])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode7-8 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[4, 2])
        self.ax.plot([x/1000 for x in stats["BL_bs_usage"][8]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABnode8 usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[4, 3])
        self.ax.plot([sum(v)/1000 for v in zip(stats['bs_link_usage'][8][0],stats['bs_link_usage'][0][8])])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'Link IABnode8-IABdonor usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax = plt.subplot(gridspec.GridSpec(5, 5)[4, 4])
        self.ax.plot([x/1000 for x in stats["BL_bs_usage"][0]])
        plt.xlabel("Timestep")
        plt.ylabel("Gbps")
        self.ax.set_title(f'IABdonor usage')
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/link_usage.png", dpi=200)
        
        
        # Route counter
        y_lim = 0
        for i in range(9):
            if y_lim < max(stats["route_counter"][i]):
                y_lim = max(stats["route_counter"][i])
        y_lim = y_lim * 1.1
        plt.figure(figsize=(9, 14))
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[0, 0])
        plt.rcParams["font.size"] = 17
        self.ax.plot(stats["route_counter"][0])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'Route 1→4→7→8→donor', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[0, 1])
        self.ax.plot(stats["route_counter"][1])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'Route 2→5→8→donor', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[1, 0])
        self.ax.plot(stats["route_counter"][2])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'Route 2→5→6→donor', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[1, 1])
        self.ax.plot(stats["route_counter"][3])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'Route 2→3→6→donor', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[2, 0])
        self.ax.plot(stats["route_counter"][4])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'Route 3→6→donor', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[2, 1])
        self.ax.plot(stats["route_counter"][5])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'Route 5→8→donor', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[3, 0])
        self.ax.plot(stats["route_counter"][6])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'Route 8→donor', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[3, 1])
        self.ax.plot(stats["route_counter"][7])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'Route(directlt access to donor)', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        self.ax = plt.subplot(gridspec.GridSpec(5,2)[4, 0])
        self.ax.plot(stats["route_counter"][8])
        plt.xlabel("Timestep")
        plt.ylabel("the number of UE")
        self.ax.set_title(f'other Routes', fontsize=17)
        self.ax.set_xlim(self.xlim)
        locs = self.ax.get_xticks()
        locs[0] = self.xlim[0]
        locs[-1] = self.xlim[1]
        self.ax.set_xticks(locs)
        self.ax.use_sticky_edges = False
        plt.ylim(0, y_lim)
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/Route.png", dpi=200)
        
        
        plt.rcParams["font.size"] = 28
        plt.figure(figsize=(16, 9))
        l = list(stats["route_dict"])
        for j in range(len(l)):
            stats["route_dict"][str(f"{l[j]}").replace("[", "").replace("]", "").replace(", ", "→").replace("0", "donor")] = stats["route_dict"].pop(str(f"{l[j]}")) / 2000
        x, y = zip(*sorted(stats["route_dict"].items(), key=lambda x:x[1], reverse=True))
        ax = plt.gca()
        #print(max(y))
        plt.barh(x[::-1], y[::-1])
        labels = ax.get_xticklabels()
        plt.setp(labels, rotation=0)
        plt.xlabel("the number of averaged UE")
        plt.ylabel("Route")
        plt.xlim(0, max(y)*1.1)
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/Route_dict.png", dpi=200)
        