# Technicians.py is the IP for solving technician problem

import numpy as np
from gurobipy import *
from Tours import feasible_tours
import math

# function to calculate distance
def distance(instance, location1, location2):
    x1 = instance.locations[location1][1]
    y1 = instance.locations[location1][2]
    x2 = instance.locations[location2][1]
    y2 = instance.locations[location2][2]
    return math.ceil(math.sqrt(pow(x1-x2, 2) + pow(y1-y2, 2)))

# function to solve IP for technicians
def IP_Technicians(instance):

    # create tours
    tours, machines_on_tour = feasible_tours(instance)

    # schedule 
    schedule = [["schedule"]]
    # give 1 day off for 4 days worked
    for i in range(0,5):
        schedule.append([])
        for j in range(1, instance.days+1):
            if j % 5 - i != 0:
                schedule[i+1].append(j)
    start = len(schedule)
    # give 2 days off for 5 days worked
    for i in range(0,7):
        schedule.append([])
        for j in range(1, instance.days+1):
            if j % 7 != i and j % 7 != i+1:
                schedule[start+i].append(j)

    #length of tour t performed by technician p
    def tech_tour_distance(t, p):
        dist = 0
        technicianLocationID = instance.technicians[p][1]
        tourLocationIDs = []
        for m in tours[t]:
            tourLocationIDs.append(instance.requests[m][1])
        # add the distance from technician start to first request 1
        dist += distance(instance, technicianLocationID, tourLocationIDs[0]) 
        for i in range(1, len(tourLocationIDs)):
            dist += distance(instance, tourLocationIDs[i-1], tourLocationIDs[i])
                # add distance of techncian going back to their starting place
        dist += distance(instance, tourLocationIDs[-1], technicianLocationID)    
        return dist

    # variable indicates if tour t includes machine m
    b = {}
    for t in range(1, len(tours)):
        for m in range(1, instance.numRequests+1):
            if m in tours[t]:
                b[t,m] = 1
            else:
                b[t,m] = 0
    
    # variable indicates cost of person p completeing tour t
    h = {}            
    for p in range(1, instance.numTechnicians+1):
        for t in range(1, len(tours)): 
            h[p,t] = 0
            # find the locations of the technician's start and each request m on the tour
            technicianLocationID = instance.technicians[p][1]
            tourLocationIDs = []
            for m in tours[t]:
                tourLocationIDs.append(instance.requests[m][1])
            # add the $/unit of distance from technician start to first request 1
            h[p,t] += instance.technicianDistanceCost * distance(instance, technicianLocationID, tourLocationIDs[0])
            # add cost of distance traveled for subsequent requests 
            for i in range(1, len(tourLocationIDs)):
                h[p,t] += instance.technicianDistanceCost * distance(instance, tourLocationIDs[i-1], tourLocationIDs[i])
            # add cost of techncian going back to their starting place
            h[p,t] += instance.technicianDistanceCost * distance(instance, tourLocationIDs[len(tourLocationIDs)-1], technicianLocationID)
            h[p,t] += instance.technicianDayCost
    
    # variable indicates if schedule s contains day d
    e = {}
    for s in range(1, len(schedule)):
        for d in range(1, instance.days+1):
            if d in schedule[s]:
                e[s,d] = 1
            else:
                e[s,d] = 0

    # variable indicates whether machine request m can be installed on day d
    l = {}
    for m in range(1, instance.numRequests+1):
        for d in range(1, instance.days+1):
            # is the day greater than (after) the release date - changing this parameter leads to different results
            if d > instance.requests[m][2]:
                l[m,d] = 1
            else:
                l[m,d] = 0

    # gurobi model
    model = Model()
    
    # decision var person p performs tour t on day d
    y = {}
    for p in range(1, instance.numTechnicians + 1):
        for t in range(1, len(tours)):
            for d in range(1, instance.days + 1):
                # Check if the tour distance is within the technician's limit
                if tech_tour_distance(t, p) <= instance.technicians[p][2]:
                    # Check if the technician can install all machines in the tour
                    if all(instance.technicians[p][m+3] for m in machines_on_tour[t]):
                        y[p, t, d] = model.addVar(0, 1, 0, GRB.BINARY, "y_%d_%d_%d" % (p, t, d))
                    else:
                        y[p, t, d] = model.addVar(0, 0, 0, GRB.BINARY, "y_%d_%d_%d" % (p, t, d))  # Set the decision variable to 0 if technician cannot install all machines
                else:
                    y[p, t, d] = model.addVar(0, 0, 0, GRB.BINARY, "y_%d_%d_%d" % (p, t, d))  # Set the decision variable to 0 if the distance exceeds the limit

    # decision var person p has schedule s
    z = {}
    for p in range(1, instance.numTechnicians+1):
        for s in range(1, len(schedule)):
            z[p,s] = model.addVar(0, 1, 0, GRB.BINARY, "z_%d_%d" %(p,s))

     # decision variable for total cost of person p
    c = {}
    for p in range(1, instance.numTechnicians+1):
       c[p] = model.addVar(0, GRB.INFINITY, 1, GRB.CONTINUOUS, "c_%d"%p)

    # decision variable certain idle days
    w = {}
    for m in range(1, instance.numRequests+1):
        w[m] = model.addVar(0, GRB.INFINITY, 1, GRB.INTEGER, name = "w_%d"%m)

    # constraint that person costs the amount calculated
    for p in range(1, instance.numTechnicians+1):
         model.addConstr(quicksum(h[p,t] * y[p,t,d] for t in range(1, len(tours)) \
                    for d in range(1, instance.days+1)) == c[p])
    
    # constraint each person can only work one schedule
    for p in range(1, instance.numTechnicians+1):
        model.addConstr(quicksum(z[p,s] for s in range(1, len(schedule))) == 1) 
    
    # constraint each person can only work days in their schedule
    for d in range(1, instance.days+1):
        for p in range(1, instance.numTechnicians+1):
            model.addConstr(quicksum(y[p,t,d] for t in range(1, len(tours))) <= \
                    quicksum(e[s,d]*z[p,s] for s in range(1, len(schedule))))
    
    # constraint every machine gets installed
    for m in range(1, instance.numRequests+1):
        model.addConstr(quicksum(b[t,m]*y[p,t,d] for t in range(1, len(tours)) for p in range(1, instance.numTechnicians+1) \
                    for d in range(1, instance.days+1)) == 1) # exactly equal means can't go to request twice

    # constraint machines can't be installed until after the request is released
    for m in range(1, instance.numRequests+1):
        for d in range(1, instance.days+1):
            model.addConstr(quicksum(b[t,m]*y[p,t,d] for t in range(1, len(tours)) for p in range(1, instance.numTechnicians+1)) <=l[m,d])

    # constraint for max requests for a technician
    for p in range(1, instance.numTechnicians + 1):
        for t in range(1, len(tours)):
            for d in range(1, instance.days + 1):
                model.addConstr(quicksum(b[t, m] * y[p, t, d] for m in tours[t]) <= instance.technicians[p][3])

    # constarint for certain idle days
    for m in range(1, instance.numRequests+1):
        model.addConstr(quicksum(d*b[t,m]*y[p,t,d] for d in range(1, instance.days+1) for t in range(1,len(tours)) for p in range(1, instance.numTechnicians + 1))-1 - instance.requests[m][3] <= w[m])
    
    # variable indicating number of techncians hired each day
    hired = {}
    for p in range(1, instance.numTechnicians + 1):
        for d in range(1, instance.days + 1):
            hired[p, d] = quicksum(y[p, t, d] for t in range(1, len(tours)))

    # variable representing whether technician p is hired at all during the planning horizon
    hired_overall = {}
    for p in range(1, instance.numTechnicians + 1):
        hired_overall[p] = quicksum(hired[p, d] for d in range(1, instance.days + 1))/d

    # variable representing the total number of unique technicians hired
    num_unique_hired = quicksum(hired_overall[p] for p in range(1, instance.numTechnicians + 1))
    
    # variable representing the total cost for all technicians
    total_cost = quicksum(c[p] for p in range(1, instance.numTechnicians + 1))



    # Objective: Minimize the total cost multiplied by the number of unique technicians hired, factor in idle costs
    model.setObjective(total_cost + num_unique_hired*instance.technicianCost+quicksum(w[m]*instance.machines[instance.requests[m][4]][2]*instance.requests[m][5] for m in range(1, instance.numRequests+1)), GRB.MINIMIZE)
    model.setParam('OutputFlag', False)
    model.optimize()

     # create list to store y variable values 
    solutions = [["technician", "tour", "day"]] 
    machine_days = [] # stores pair with [machine request, day]
    
    # create var for technician dist
    technician_dist = 0

    if model.SolCount == 0:
        print("***NO SOLUTION FOUND***")
    else:
        #parse decision vars and add to list
        for v in model.getVars():
            if v.X > 0 and 'y' in v.varName:
                y,p,t,d = v.varName.split('_')
                solutions.append([p, tours[int(t)], d])
                for r in tours[int(t)]:
                    machine_days.append([int(r), int(d)])
                technician_dist += tech_tour_distance(int(t), int(p))

    all_vars = model.getVars()
    values = model.getAttr("X", all_vars)
    names = model.getAttr("VarName", all_vars)

    adjusted_obj_val = model.objval - sum(w[m].X*instance.machines[instance.requests[m][4]][2]*instance.requests[m][5] for m in range(1, instance.numRequests + 1))
    # for name, val in zip(names, values):
    #     print(f"{name} = {val}")

    return solutions, machine_days, technician_dist, adjusted_obj_val