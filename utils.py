import math, random, cv2, os
import numpy as np
from matplotlib import gridspec
import matplotlib.pyplot as plt

rng = np.random.default_rng()

# calculate the distance between(a, b) and (c, d)
def distance(a, b, c, d):
    #return 0.959961 * max((abs(c - a), abs(d - b))) + 0.397461 * min((abs(c - a), abs(d - b))) # memo; sapproximate square root
    a = c-a
    b = d-b
    return math.sqrt(a**2 + b**2)

# reformat bandwidth
def format_bps(size, pos=None, return_float=False):
    # https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb
    power, n = 1000, 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T', 5: 'P', 6:'E', 7: 'Z', 8:'Y'}
    while size >= power:
        size /= power
        n += 1
    if return_float:
        return f'{size:.3f} {power_labels[n]}bps'
    return f'{size:.0f} {power_labels[n]}bps'

# get distribution
def get_dist(d):
    return {
        'randrange': random.randrange, # start, stop, step
        'randint': random.randint, # a, b
        'random': random.random,
        'uniform': random.uniform, # a, b
        'triangular': random.triangular, # low, high, mode
        'beta': random.betavariate, # alpha, beta
        'expo': random.expovariate, # lambda
        'gamma': random.gammavariate, # alpha, beta
        'gauss': random.gauss, # mu, sigma
        'lognorm': random.lognormvariate, # mu, sigma
        'normal': random.normalvariate, # mu, sigma
        'vonmises': random.vonmisesvariate, # mu, kappa
        'pareto': random.paretovariate, # alpha
        'weibull': random.weibullvariate, # alpha, beta
        "np_uniform": rng.uniform
    }.get(d)

# randomizer
def get_random_mobility_pattern(vals, mobility_patterns):
    i = 0
    #r = random.random()
    r = rng.random()

    while vals[i] < r:
        i += 1

    return mobility_patterns[i]

# randomizer
def get_random_slice_index(slice_weights, slice_quantity):
    i = 0
    #r = random.random()
    r = rng.random()

    while slice_weights[i] < r:
        i += 1
    #j = random.randrange(slice_quantity[i])
    j = rng.integers(slice_quantity[i])
    for k in range(i):
        j += slice_quantity[k]
    return j

# get slice index that UE is acculuated
def get_slice_index(slice_type, sub_slice, slice_quantity):
    for i in range(slice_type):
        sub_slice += slice_quantity[i]
    return sub_slice

# generate graph
def output_graph(S1_quantity_list, allocation_change_count\
    , AL_bandwidthalt_per_reallocation, BL_bandwidthalt_per_reallocation\
    , AL_sl_bw_surplus, BL_sl_bw_surplus, AL_sl_bw_lack, BL_sl_bw_lack\
    , AL_sl_bw_surplus_time, BL_sl_bw_surplus_time, AL_sl_bw_lack_time, BL_sl_bw_lack_time\
    , AL_bs_bw_surplus, BL_bs_bw_surplus, AL_bs_bw_lack, BL_bs_bw_lack\
    , AL_bs_bw_surplus_time, BL_bs_bw_surplus_time, AL_bs_bw_lack_time, BL_bs_bw_lack_time\
    , bs_quantity):
    
    new_allo_count = []
    y_lim = 0
    for bs_num in range(bs_quantity):
        data_type_list = []
        for i in range(2):
            slice_list = []
            for sl in range(len(S1_quantity_list)):
                slice_list.append(allocation_change_count[sl][bs_num][i])
                if allocation_change_count[sl][bs_num][i] > y_lim:
                    y_lim = allocation_change_count[sl][bs_num][i]
            data_type_list.append(slice_list)
        new_allo_count.append(data_type_list)
    y_lim = y_lim * 1.1
    
    plt.rcParams["font.size"] = 12
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        plt.ylabel("the number of bandwidth changed slices")
        plt.ylim(0, y_lim)
        plt.plot(S1_quantity_list, new_allo_count[bs_num][0])
        if bs_num == 0:
            plt.title("IAB donor")
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"allo_count(access).png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        plt.ylabel("the number of bandwidth changed slices")
        plt.ylim(0, y_lim)
        plt.plot(S1_quantity_list, new_allo_count[bs_num][1])
        if bs_num == 0:
            plt.title("IAB donor")
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"allo_count(backhaul).png", dpi=200, bbox_inches='tight')
    
    cv2.imwrite('allocation_count.png', cv2.hconcat([cv2.imread('./allo_count(access).png'), cv2.imread('./allo_count(backhaul).png')]))
    os.remove("./allo_count(access).png")
    os.remove("./allo_count(backhaul).png")
    
    # sort bw surplus by bs, slice
    new_AL_sl_bw_surplus = []
    new_BL_sl_bw_surplus = []
    new_AL_sl_bw_lack = []
    new_BL_sl_bw_lack = []
    tempAL_sl_surplus = []
    tempBL_sl_surplus = []
    tempAL_sl_lack = []
    tempBL_sl_lack = []
    new_AL_bs_bw_surplus = []
    new_BL_bs_bw_surplus = []
    new_AL_bs_bw_lack = []
    new_BL_bs_bw_lack = []
    tempAL_bs_surplus = []
    tempBL_bs_surplus = []
    tempAL_bs_lack = []
    tempBL_bs_lack = []
    amount_y_lim = 0
    for a in range(bs_quantity):
        for s in range(len(S1_quantity_list)):
            tempAL_sl_surplus.append(AL_sl_bw_surplus[s][a])
            tempAL_bs_surplus.append(AL_bs_bw_surplus[s][a])
            if AL_sl_bw_surplus[s][a] > amount_y_lim:
                amount_y_lim = AL_sl_bw_surplus[s][a]
            tempBL_sl_surplus.append(BL_sl_bw_surplus[s][a])
            tempBL_bs_surplus.append(BL_bs_bw_surplus[s][a])
            if BL_sl_bw_surplus[s][a] > amount_y_lim:
                amount_y_lim = BL_sl_bw_surplus[s][a]
            tempAL_sl_lack.append(AL_sl_bw_lack[s][a])
            tempAL_bs_lack.append(AL_bs_bw_lack[s][a])
            if AL_sl_bw_lack[s][a] > amount_y_lim:
                amount_y_lim = AL_sl_bw_lack[s][a]
            tempBL_sl_lack.append(BL_sl_bw_lack[s][a])
            tempBL_bs_lack.append(BL_bs_bw_lack[s][a])
            if BL_sl_bw_lack[s][a] > amount_y_lim:
                amount_y_lim = BL_sl_bw_lack[s][a]
        new_AL_sl_bw_surplus.append(tempAL_sl_surplus)
        new_BL_sl_bw_surplus.append(tempBL_sl_surplus)
        new_AL_sl_bw_lack.append(tempAL_sl_lack)
        new_BL_sl_bw_lack.append(tempBL_sl_lack)
        tempAL_sl_surplus = []
        tempBL_sl_surplus = []
        tempAL_sl_lack = []
        tempBL_sl_lack = []
        new_AL_bs_bw_surplus.append(tempAL_bs_surplus)
        new_BL_bs_bw_surplus.append(tempBL_bs_surplus)
        new_AL_bs_bw_lack.append(tempAL_bs_lack)
        new_BL_bs_bw_lack.append(tempBL_bs_lack)
        tempAL_bs_surplus = []
        tempBL_bs_surplus = []
        tempAL_bs_lack = []
        tempBL_bs_lack = []
    
    amount_y_lim = amount_y_lim * 1.1
    
    # whole
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # surplus allocated bandwidth of slices
        plt.ylabel("Mbps")
        #plt.ylim(0, amount_y_lim)
        plt.plot(S1_quantity_list, new_AL_bs_bw_surplus[bs_num])
        # surplus allocated of slices for each number of slices(access)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"bw_surplus(access)_whole.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # surplus allocated bandwidth of slices
        plt.ylabel("Mbps")
        #plt.ylim(0, amount_y_lim)
        plt.plot(S1_quantity_list, new_BL_bs_bw_surplus[bs_num])
        # surplus allocated of slices for each number of slices(backhaul)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"bw_surplus(backhaul)_whole.png", dpi=200, bbox_inches='tight')


    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # lack allocated bandwidth of slices
        plt.ylabel("Mbps")
        #plt.ylim(0, amount_y_lim)
        plt.plot(S1_quantity_list, new_AL_bs_bw_lack[bs_num])
        # lack allocated bandwidth of slices for each number of slices(access)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"bw_lack(access)_whole.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # lack allocated bandwidth of slices
        plt.ylabel("Mbps")
        #plt.ylim(0, amount_y_lim)
        plt.plot(S1_quantity_list, new_BL_bs_bw_lack[bs_num])
        # lack allocated bandwidth of slices for each number of slices(backhaul)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"bw_lack(backhaul)_whole.png", dpi=200, bbox_inches='tight')
    
    cv2.imwrite('bw_surplus_lack_bs.png', cv2.hconcat([cv2.imread('./bw_surplus(access)_whole.png'), cv2.imread('./bw_surplus(backhaul)_whole.png'), cv2.imread('./bw_lack(access)_whole.png'), cv2.imread('./bw_lack(backhaul)_whole.png')]))
    os.remove("./bw_surplus(access)_whole.png")
    os.remove("./bw_surplus(backhaul)_whole.png")
    os.remove("./bw_lack(access)_whole.png")
    os.remove("./bw_lack(backhaul)_whole.png")
    # each
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # surplus allocated bandwidth of slices
        plt.ylabel("Mbps")
        #plt.ylim(0, amount_y_lim)
        plt.plot(S1_quantity_list, new_AL_sl_bw_surplus[bs_num])
        # surplus allocated of slices for each number of slices(access)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"bw_surplus(access)_each.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # surplus allocated bandwidth of slices
        plt.ylabel("Mbps")
        #plt.ylim(0, amount_y_lim)
        plt.plot(S1_quantity_list, new_BL_sl_bw_surplus[bs_num])
        # surplus allocated of slices for each number of slices(backhaul)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"bw_surplus(backhaul)_each.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # lack allocated bandwidth of slices
        plt.ylabel("Mbps")
        #plt.ylim(0, amount_y_lim)
        plt.plot(S1_quantity_list, new_AL_sl_bw_lack[bs_num])
        # lack allocated bandwidth of slices for each number of slices(access)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"bw_lack(access)_each.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # lack allocated bandwidth of slices
        plt.ylabel("Mbps")
        #plt.ylim(0, amount_y_lim)
        plt.plot(S1_quantity_list, new_BL_sl_bw_lack[bs_num])
        # lack allocated bandwidth of slices for each number of slices(backhaul)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"bw_lack(backhaul)_each.png", dpi=200, bbox_inches='tight')
    
    cv2.imwrite('bw_surplus_lack_sl.png', cv2.hconcat([cv2.imread('./bw_surplus(access)_each.png'), cv2.imread('./bw_surplus(backhaul)_each.png'), cv2.imread('./bw_lack(access)_each.png'), cv2.imread('./bw_lack(backhaul)_each.png')]))
    os.remove("./bw_surplus(access)_each.png")
    os.remove("./bw_surplus(backhaul)_each.png")
    os.remove("./bw_lack(access)_each.png")
    os.remove("./bw_lack(backhaul)_each.png")
    
    # sort bw surplus by bs, slice
    new_AL_sl_bw_surplus_time = []
    new_BL_sl_bw_surplus_time = []
    new_AL_sl_bw_lack_time = []
    new_BL_sl_bw_lack_time = []
    tempAL_sl_surplus = []
    tempBL_sl_surplus = []
    tempAL_sl_lack = []
    tempBL_sl_lack = []
    new_AL_bs_bw_surplus_time = []
    new_BL_bs_bw_surplus_time = []
    new_AL_bs_bw_lack_time = []
    new_BL_bs_bw_lack_time = []
    tempAL_bs_surplus = []
    tempBL_bs_surplus = []
    tempAL_bs_lack = []
    tempBL_bs_lack = []
    time_y_lim = 0
    for a in range(bs_quantity):
        for s in range(len(S1_quantity_list)):
            tempAL_sl_surplus.append(AL_sl_bw_surplus_time[s][a])
            tempAL_bs_surplus.append(AL_bs_bw_surplus_time[s][a])
            if AL_sl_bw_surplus_time[s][a] > time_y_lim:
                time_y_lim = AL_sl_bw_surplus_time[s][a]
            tempBL_sl_surplus.append(BL_sl_bw_surplus_time[s][a])
            tempBL_bs_surplus.append(BL_bs_bw_surplus_time[s][a])
            if BL_sl_bw_surplus_time[s][a] > time_y_lim:
                time_y_lim = BL_sl_bw_surplus_time[s][a]
            tempAL_sl_lack.append(AL_sl_bw_lack_time[s][a])
            tempAL_bs_lack.append(AL_bs_bw_lack_time[s][a])
            if AL_sl_bw_lack_time[s][a] > time_y_lim:
                time_y_lim = AL_sl_bw_lack_time[s][a]
            tempBL_sl_lack.append(BL_sl_bw_lack_time[s][a])
            tempBL_bs_lack.append(BL_bs_bw_lack_time[s][a])
            if BL_sl_bw_lack_time[s][a] > time_y_lim:
                time_y_lim = BL_sl_bw_lack_time[s][a]
        new_AL_sl_bw_surplus_time.append(tempAL_sl_surplus)
        new_BL_sl_bw_surplus_time.append(tempBL_sl_surplus)
        new_AL_sl_bw_lack_time.append(tempAL_sl_lack)
        new_BL_sl_bw_lack_time.append(tempBL_sl_lack)
        tempAL_sl_surplus = []
        tempBL_sl_surplus = []
        tempAL_sl_lack = []
        tempBL_sl_lack = []
        new_AL_bs_bw_surplus_time.append(tempAL_bs_surplus)
        new_BL_bs_bw_surplus_time.append(tempBL_bs_surplus)
        new_AL_bs_bw_lack_time.append(tempAL_bs_lack)
        new_BL_bs_bw_lack_time.append(tempBL_bs_lack)
        tempAL_bs_surplus = []
        tempBL_bs_surplus = []
        tempAL_bs_lack = []
        tempBL_bs_lack = []
    
    # whole slices
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # surplus allocated bandwidth of slices
        plt.ylabel("Timestep")
        #plt.ylim(0, time_y_lim)
        plt.plot(S1_quantity_list, new_AL_bs_bw_surplus_time[bs_num])
        # surplus allocated of slices for each number of slices(access)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"bw_surplus_time(access)_whole.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # surplus allocated bandwidth of slices
        plt.ylabel("Timestep")
        #plt.ylim(0, time_y_lim)
        plt.plot(S1_quantity_list, new_BL_bs_bw_surplus_time[bs_num])
        # surplus allocated of slices for each number of slices(backhaul)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"bw_surplus_time(backhaul)_whole.png", dpi=200, bbox_inches='tight')


    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # lack allocated bandwidth of slices
        plt.ylabel("Timestep")
        #plt.ylim(0, time_y_lim)
        plt.plot(S1_quantity_list, new_AL_bs_bw_lack_time[bs_num])
        # lack allocated bandwidth of slices for each number of slices(access)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"bw_lack_time(access)_whole.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # lack allocated bandwidth of slices
        plt.ylabel("Timestep")
        #plt.ylim(0, time_y_lim)
        plt.plot(S1_quantity_list, new_BL_bs_bw_lack_time[bs_num])
        # lack allocated bandwidth of slices for each number of slices(backhaul)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"bw_lack_time(backhaul)_whole.png", dpi=200, bbox_inches='tight')
    
    cv2.imwrite('bw_surplus_lack_bs_time.png', cv2.hconcat([cv2.imread('./bw_surplus_time(access)_whole.png'), cv2.imread('./bw_surplus_time(backhaul)_whole.png'), cv2.imread('./bw_lack_time(access)_whole.png'), cv2.imread('./bw_lack_time(backhaul)_whole.png')]))
    os.remove("./bw_surplus_time(access)_whole.png")
    os.remove("./bw_surplus_time(backhaul)_whole.png")
    os.remove("./bw_lack_time(access)_whole.png")
    os.remove("./bw_lack_time(backhaul)_whole.png")
    
    # each slices
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # surplus allocated bandwidth of slices
        plt.ylabel("Timestep")
        #plt.ylim(0, time_y_lim)
        plt.plot(S1_quantity_list, new_AL_sl_bw_surplus_time[bs_num])
        # surplus allocated of slices for each number of slices(access)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"bw_surplus_time(access)_each.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # surplus allocated bandwidth of slices
        plt.ylabel("Timestep")
        #plt.ylim(0, time_y_lim)
        plt.plot(S1_quantity_list, new_BL_sl_bw_surplus_time[bs_num])
        # surplus allocated of slices for each number of slices(backhaul)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"bw_surplus_time(backhaul)_each.png", dpi=200, bbox_inches='tight')


    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # lack allocated bandwidth of slices
        plt.ylabel("Timestep")
        #plt.ylim(0, time_y_lim)
        plt.plot(S1_quantity_list, new_AL_sl_bw_lack_time[bs_num])
        # lack allocated bandwidth of slices for each number of slices(access)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Access link")
        plt.tight_layout()
        plt.savefig(f"bw_lack_time(access)_each.png", dpi=200, bbox_inches='tight')
    
    plt.figure(figsize=((bs_quantity//4+1)*4,9))
    for bs_num in range(bs_quantity):
        x_cap, y_cap = divmod(bs_num, 4)
        plt.subplot(gridspec.GridSpec(4, bs_quantity//4+1)[y_cap, x_cap])
        plt.xlabel("the number of provided slices")
        # lack allocated bandwidth of slices
        plt.ylabel("Timestep")
        #plt.ylim(0, time_y_lim)
        plt.plot(S1_quantity_list, new_BL_sl_bw_lack_time[bs_num])
        # lack allocated bandwidth of slices for each number of slices(backhaul)
        if bs_num == 0:
            plt.title('IAB donor')
        else:
            plt.title(f'IAB node{bs_num}')
        plt.suptitle("Backhaul link")
        plt.tight_layout()
        plt.savefig(f"bw_lack_time(backhaul)_each.png", dpi=200, bbox_inches='tight')
    
    cv2.imwrite('bw_surplus_lack_sl_time.png', cv2.hconcat([cv2.imread('./bw_surplus_time(access)_each.png'), cv2.imread('./bw_surplus_time(backhaul)_each.png'), cv2.imread('./bw_lack_time(access)_each.png'), cv2.imread('./bw_lack_time(backhaul)_each.png')]))
    os.remove("./bw_surplus_time(access)_each.png")
    os.remove("./bw_surplus_time(backhaul)_each.png")
    os.remove("./bw_lack_time(access)_each.png")
    os.remove("./bw_lack_time(backhaul)_each.png")