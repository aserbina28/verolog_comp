# Trucks2.py is the WORKING IP for solving the truck problem given technician solutions

import numpy as np
from gurobipy import *


def distance(instance, location1, location2):
    x1 = instance.locations[location1][1]
    y1 = instance.locations[location1][2]
    x2 = instance.locations[location2][1]
    y2 = instance.locations[location2][2]
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)


def IP_Trucks(instance, machines):

    # create routes
    routes = [["machine", "distance", "cost"]]
    for m in range(1, instance.numRequests+1):
        location_m = instance.requests[m][1]
        depot = 1
        dist = distance(instance, location_m, depot) * 2 # going there and back
        cost = dist * instance.truckDistanceCost
        routes.append([m, dist, cost])
    
    model = Model()

    # decision var is route r performed on day d
    x = {}
    for r in range(1,len(routes)):
        for d in range(1, instance.days+1):
            x[r,d] = model.addVar(0,1, routes[r][2],  GRB.BINARY, "x_%d_%d" % (r,d)) 
    
    # decision var max number trucks used any day
    n_trucks = model.addVar(0, GRB.INFINITY, instance.truckCost, GRB.INTEGER, "n_trucks")

    # decision var trucks used on day d
    f = {}
    for d in range(1, instance.days+1):
        f[d] = model.addVar(0, GRB.INFINITY, instance.truckDayCost, GRB.CONTINUOUS, "f_%d"%d)

    # decision var number idle days for machine request m
    w = {}
    for m in range(1, instance.numRequests+1):
        w[m] = model.addVar(0, 30, 0, GRB.INTEGER, "w_%d"%m)
    
    # decision var whether route r contains request m
    a = {}
    for r in range(1, len(routes)):
        for m in range(1, instance.numRequests+1):
            if routes[r][0] == m:
                a[r,m] = model.addVar(1, 1, 0,  GRB.BINARY, "a_%d_%d" % (r,m)) 
            else:
                a[r,m] = model.addVar(0, 0, 0,  GRB.BINARY, "a_%d_%d" % (r,m)) 
    
    # constraint every request m is in one route r
    for m in range(1, instance.numRequests+1):
        model.addConstr(quicksum(a[r,m]*x[r,d] for r in range(1,len(routes)) for d in range(1, instance.days+1)) == 1)

    # constraint for fleet size 
    for d in range(1, instance.days+1):
        model.addConstr(quicksum(x[r,d] for r in range(1,len(routes))) <= n_trucks)

    # constraint for number of trucks on day d
    for d in range(1, instance.days +1):
        model.addConstr(quicksum(x[r,d] for r in range(1,len(routes))) == f[d])
    
    # constarint for idle days 
    for m in range(1, instance.numRequests+1):
        model.addConstr(machines[m-1][1] - quicksum(d*a[r,m]*x[r,d] for d in range(1, instance.days+1) for r in range(1,len(routes))) == w[m])
    
    # constraint for earliest delivery and latest delivery (depending on technician schedule)
    for m in range(1, instance.numRequests+1):
        model.addConstr(quicksum(a[r,m]*x[r,d] for d in range(1, instance.requests[m][2]) for r in range(1,len(routes)))==0)
        model.addConstr(quicksum(a[r,m]*x[r,d] for d in range(machines[m-1][1], instance.days+1) for r in range(1,len(routes)))==0)
        model.addConstr(quicksum(a[r,m]*x[r,d] for d in range(instance.requests[m][3], instance.days+1) for r in range(1,len(routes)))==0)
    

    # assume capacity constarint met because routes only contain one request thus never exceed capacity
    
    model.setParam('OutputFlag', False)
    model.optimize()

    # create lists to store solutions
    route_days = [["day", "request"]]
    num_truck_days = [["num trucks", "day"]]
    if model.SolCount == 0:
        print("***NO SOLUTION FOUND***")
    else:
        #parse decision vars and add to list
        for v in model.getVars():
            if v.X > 0 and 'x' in v.varName:
                x,r,d = v.varName.split('_')
                request = routes[int(r)][0]
                dist = routes[int(r)][1]
                cost = routes[int(r)][2]
                route_days.append([int(d), request])
            if 'f' in v.varName:
                f,d = v.varName.split('_')
                num_truck_days.append([int(d), int(v.X)])
    

    return route_days, num_truck_days


