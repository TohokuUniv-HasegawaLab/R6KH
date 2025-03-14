import main, yaml, os, csv, sys, utils, logging
from rich.logging import RichHandler

def setLogging(): # set logging file
    Simlogger = logging.getLogger("Sim") # debug, info, warning, error, critical
    Simlogger.setLevel(logging.INFO)

    stream_handler = RichHandler(markup=True,rich_tracebacks=True)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(fmt="%(name)s || %(message)s", datefmt="[%X]"))
    Simlogger.addHandler(stream_handler)

    file_handler = logging.FileHandler('Simlogger.log', mode="wt")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s || %(levelname)s || %(name)s || %(message)s", datefmt="[%X]"))
    Simlogger.addHandler(file_handler)
    
    return Simlogger

SIM_TIME = 2000 # define how many timesteps the simulator proceed
c_count = 7 
NUM_CLIENTS = 2**c_count # should be set to 2^n(n = 0~) # define how many UEs are deployed
S1_quantity_list = [2**i for i in range(0, c_count+1)] # how many slices named 'S1' will be deployed

# following lists will accumulate results of simulation
allocation_change_count = []
AL_bandwidthalt_per_reallocation = []
BL_bandwidthalt_per_reallocation = []
AL_sl_bw_surplus = []
BL_sl_bw_surplus = []
AL_sl_bw_lack = []
BL_sl_bw_lack = []
AL_sl_bw_surplus_time = []
BL_sl_bw_surplus_time = []
AL_sl_bw_lack_time = []
BL_sl_bw_lack_time = []
AL_bs_bw_surplus = []
BL_bs_bw_surplus = []
AL_bs_bw_lack = []
BL_bs_bw_lack = []
AL_bs_bw_surplus_time = []
BL_bs_bw_surplus_time = []
AL_bs_bw_lack_time = []
BL_bs_bw_lack_time = []

slice_quantity_list = []
for i in range(len(S1_quantity_list)):
    slice_quantity_list.append([S1_quantity_list[i]])

# remove one of file to choose a scenario

#import_file = "grid" # 3*3 and a donor is placed at bottom right
import_file = "line" # 2 nodes 1 donor in line

if import_file == "grid":
    setting_file = "setting_grid.yml"
    in_range_file = "basestation_in_range_grid.csv"
elif import_file == "line":
    setting_file = "setting_line.yml"
    in_range_file = "basestation_in_range_line.csv"

# load setting file and in_range_file
with open(os.path.join(os.path.dirname(__file__), setting_file), 'r') as stream:
    data = yaml.load(stream, Loader=yaml.FullLoader)

with open(os.path.join(os.path.dirname(__file__), in_range_file), mode='r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    bs_in_range = [row for row in reader]

futures = []
Simlogger = setLogging()

# simulate the scenario

for slice_quantity in slice_quantity_list:
    
    Simlogger.info(f"{slice_quantity}")
    
    try:
        data_dir = f"{slice_quantity}"
        futures.append(main.main(SIM_TIME, NUM_CLIENTS, data, bs_in_range, data_dir, slice_quantity))
    
    except KeyboardInterrupt:
        print("\nSimulation manually aborted")
        #os.system('afplay /System/Library/Sounds/Purr.aiff')
        sys.exit(0)
    
    Simlogger.info(f"futures = {futures}")

a = futures

#Simlogger.info(f"futures = {futures}")

# following lists will accumulate results of simulation
for s in range(len(slice_quantity_list)):
    allocation_change_count.append(a[s][0])
    AL_bandwidthalt_per_reallocation.append(a[s][1])
    BL_bandwidthalt_per_reallocation.append(a[s][2])
    
    AL_sl_bw_surplus.append(a[s][3])
    BL_sl_bw_surplus.append(a[s][4])
    AL_sl_bw_lack.append(a[s][5])
    BL_sl_bw_lack.append(a[s][6])
    AL_sl_bw_surplus_time.append(a[s][7])
    BL_sl_bw_surplus_time.append(a[s][8])
    AL_sl_bw_lack_time.append(a[s][9])
    BL_sl_bw_lack_time.append(a[s][10])
    
    AL_bs_bw_surplus.append(a[s][11])
    BL_bs_bw_surplus.append(a[s][12])
    AL_bs_bw_lack.append(a[s][13])
    BL_bs_bw_lack.append(a[s][14])
    AL_bs_bw_surplus_time.append(a[s][15])
    BL_bs_bw_surplus_time.append(a[s][16])
    AL_bs_bw_lack_time.append(a[s][17])
    BL_bs_bw_lack_time.append(a[s][18])

# draw graph
utils.output_graph(S1_quantity_list\
    , allocation_change_count, AL_bandwidthalt_per_reallocation, BL_bandwidthalt_per_reallocation\
    , AL_sl_bw_surplus, BL_sl_bw_surplus, AL_sl_bw_lack, BL_sl_bw_lack\
    , AL_sl_bw_surplus_time, BL_sl_bw_surplus_time, AL_sl_bw_lack_time, BL_sl_bw_lack_time\
    , AL_bs_bw_surplus, BL_bs_bw_surplus, AL_bs_bw_lack, BL_bs_bw_lack\
    , AL_bs_bw_surplus_time, BL_bs_bw_surplus_time, AL_bs_bw_lack_time, BL_bs_bw_lack_time\
    , len(bs_in_range)-1)

print('Simulation successfully completed!')
#os.system('afplay /System/Library/Sounds/Glass.aiff')
sys.exit(0)