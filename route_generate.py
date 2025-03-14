from pulp import *
import logging
from utils import distance
from math import *

Simlogger = logging.getLogger('Sim.' + __name__)
logger = logging.getLogger('main.' + __name__)

# utilized in Activate route generator in main.py
def route_generate(df_user_info, data, bs_in_range, BASE_STATIONS, data_dir, slice_quantity):
    SLICES_INFO = data['slices']
    
    # e
    # base stations setting
    e = []
    i = 1
    for b in BASE_STATIONS:
        e.append(bs_in_range[i][1:])
        i += 1
    
    # S
    # slices setting
    slice_info = []
    for name, s in SLICES_INFO.items():
        for i in range(slice_quantity[0]):
            slice_info.append(f'{name}_{i}')
    
    # Wa, Wb, wa, wb
    # Wa, Wb; access, backhaul link bandwidth for each base stations
    # wa, wb; access, backhaul link bandwidth for each slices
    Wa = []
    Wb = []
    wa = []
    wb = []
    bw = []
    
    for bs in BASE_STATIONS:
        Wa.append(bs.Wa)
        Wb.append(bs.Wb)
        
        for sl in bs.access_slices:
            bw.append(sl.capacity.capacity)
        wa.append(bw)
        bw = []
        
        for sl in bs.backhaul_slices:
            bw.append(sl.capacity.capacity)
        wb.append(bw)
        bw = []
    
    # V
    # base station location and coverage
    bs_info = []
    for b in BASE_STATIONS:
        bs_info.append([b.x, b.y, b.coverage.radius])
    
    # U
    # import UE dataframe
    ps = df_user_info.values.tolist()
    
    # set problem and objective
    prob = LpProblem('routing_generation', sense = LpMinimize)
    
    # decision variables
    l = [[[LpVariable("l%s,%s_%s"%(u,i,j), cat="Binary") if i != j and int(e[i][j]) == 1 else 0 for j in range(len(e))] for i in range(len(e))] for u in range(len(ps))]
    c = [[LpVariable("c%s,%s"%(u,i), cat="Binary") if distance(ps[u][3], ps[u][4], bs_info[i][0], bs_info[i][1]) <= bs_info[i][2] else 0 for i in range(len(e))] for u in range(len(ps))]
    ya = [[LpVariable("ya%s,%s"%(i,s), lowBound=0) for s in range(len(slice_info))] for i in range(len(e))]
    yb = [[LpVariable("yb%s,%s"%(i,s), lowBound=0) for s in range(len(slice_info))] for i in range(len(e))]
    z = LpVariable('z', lowBound=0)
    
    # constraints
    
    # minimize z
    prob += z
    
    # subject to
    # Total backhaul links used by all UEs is below z
    prob += lpSum(l[u][i][j] for u in range(len(ps)) for i in range(len(e)) for j in range(len(e))) <= z
    
    # Each user accesses one base station
    for u in range(len(ps)):
        if ps[u][9]:
            prob += lpSum(c[u][i] for i in range(len(e))) == 1
    
    # Each user's route ends at the donor
    for u in range(len(ps)):
        if ps[u][9]:
            prob += lpSum(l[u][i][0] for i in range(len(e))) + c[u][0] == 1
    
    # If the u uses the link between vi and vj, a subsequent backhaul link must exist (applied big-M, M=1)
    # If the u doesn't use the link between vi and vj, no restrictions on a subsequent backhaul link(i.e. the number of subsequent link can take 0 to 2)
    for u in range(len(ps)):
            for j in range(1,len(e)):
                for i in range(1,len(e)):
                    if i != j and int(e[i][j]) == 1:
                        prob += l[u][i][j] <= lpSum(l[u][j][k] if k != i and k != j else 0 for k in range(len(e)))
                        prob += lpSum(l[u][j][k] if k != i and k != j else 0 for k in range(len(e))) <= 2 - l[u][i][j]
    
    # If the u access to vi, a subsequent backhaul link must exist (applied big-M, M=1)
    # If the u doesn't access to vi, no restrictions on a subsequent backhaul link(i.e. the number of subsequent link can take 0 to 2)
    for u in range(len(ps)):
            for i in range(1,len(e)):
                if c[u][i] == 1:
                    prob += c[u][i] <= lpSum(l[u][i][j] for j in range(len(e)))
                    prob += lpSum(l[u][i][j] for j in range(len(e))) <= 2 - c[u][i]
    
    # prohibit exceeding maximum bandwidth allocated to access link of slices at each base stations
    for i in range(len(e)):
        for sl in range(len(slice_info)):
            prob += lpSum(ps[u][2] * c[u][i] if ps[u][1] == sl else 0\
                            for u in range(len(ps))) \
                            <= wa[i][sl] + ya[i][sl]
    
    # prohibit exceeding maximum bandwidth allocated to backhaul link of slices at each base station
    # donor
    for sl in range(len(slice_info)):
        prob += lpSum(ps[u][2] * l[u][i][0] if i != 0 and ps[u][1] == sl else 0\
                        for i in range(len(e)) for u in range(len(ps))) \
                + lpSum(ps[u][2] * c[u][0] if ps[u][1] == sl else 0\
                        for u in range(len(ps))) \
                        <= wb[0][sl] + yb[0][sl]
    # nodes
    for j in range(1,len(e)):
        for sl in range(len(slice_info)):
            prob += lpSum(2 * ps[u][2] * l[u][i][j] if i != j and ps[u][1] == sl else 0\
                            for i in range(len(e)) for u in range(len(ps))) \
                    + lpSum(ps[u][2] * c[u][j] if ps[u][1] == sl else 0\
                            for u in range(len(ps))) \
                            <= wb[j][sl] + yb[j][sl]
    
    # prohibit exceeding unused and no allocation bandwidth for access link at each base station
    for i in range(len(e)):
        prob += lpSum(ya[i][sl] for sl in range(len(slice_info))) <= Wa[i] - lpSum(wa[i][sl] for sl in range(len(slice_info)))
    
    # prohibit exceeding unused and no allocation bandwidth for backhaul link at each base station
    for i in range(len(e)):
        prob += lpSum(yb[i][sl] for sl in range(len(slice_info))) <= Wb[i] - lpSum(wb[i][sl] for sl in range(len(slice_info)))
    
    #logger.info(f'{prob}')
    status = prob.solve(CPLEX(msg=0))
    #status = prob.solve(SCIP(msg=0)) # if you use SCIP as solver, remove # and place # in CPLEX
    #logger.info(f"Status, {LpStatus[status]}")
    
    
    if LpStatus[status] == "Optimal":
        route, ps_route = [], []
        link_pre = None
        for u in range(len(ps)):
            if ps[u][9]:
                # check if there is a link to IABdonor(update "green_to_donor")
                df_user_info.iat[u, 5] = False
                
                for i in range(len(e)):
                    if round(value(l[u][i][0])) == 1:
                        df_user_info.iat[u, 5] = True
                    if round(value(c[u][0])) == 1:
                        df_user_info.iat[u, 5] = True
                
                # make list of routes
                if df_user_info.iat[u, 5] == True:
                    
                    for i in range(len(e)):
                        if round(value(c[u][i])) == 1:
                            route.append(i)
                            link_pre = i
                    if link_pre is not None:
                        counter = 0
                        while link_pre != 0:
                            for i in range(len(e)):
                                for j in range(len(e)):
                                    if round(value(l[u][i][j])) == 1 and i == link_pre:
                                        route.append(j)
                                        link_pre = j
                                        counter += 1
                                        # Sometimes the optimization problem couldn't be solved or get proper answer for unknown reasons.
                                        # In this case, the answer obtained in one previous timestep will be applied to the current answer.
                                        if counter >= 10:
                                            route = df_user_info.iat[u, 8]
                                            link_pre = 0
                                            Simlogger.info(f"pre_route applied: {route}")
                                            for i in range(len(e)):
                                                if round(value(c[u][i])) == 1:
                                                    Simlogger.info(f'{c[u][i]}: {value(c[u][i])}')
                                                for j in range(len(e)):
                                                    if round(value(l[u][i][j])) == 1:
                                                        Simlogger.info(f'{l[u][i][j]}: {value(l[u][i][j])}')
                    else:
                        pass
            
            ps_route.append(route)
            route = []
        
        for (p, r) in zip(range(len(ps)), ps_route):
            if r != []:
                df_user_info.iat[p, 6] = r
            else:
                df_user_info.iat[p, 6] = []
                df_user_info.iat[p, 5] = False
        
        #print(f"objective value {value(prob.objective)}")
        
        return df_user_info