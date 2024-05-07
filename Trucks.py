# Trucks.py is unfinished & does not work
from gurobipy import *
from pyexpat import model

import Instance
import numpy as np

# pass in file name of instance (hard code or command line)
filename = 'instances_2024/CO_Case2420.txt'
# filename = sys.argv[1]

# create "instance" and read file
instance = Instance.Instance()
instance.read_case_file(filename)


def instance_distance(instance):
    locations = {loc[0]: (loc[1], loc[2]) for loc in instance.locations[1:]}
    distances = {}
    for l1 in locations:
        for l2 in locations:
            if l1 != l2:
                distance = np.sqrt(
                    (locations[l1][0] - locations[l2][0]) ** 2 + (locations[l1][1] - locations[l2][1]) ** 2)
                distances[(l1, l2)] = distance
            elif l1 == l2:
                distances[(l1, l2)] = 0
    return distances


def request_size(instance):
    request_sizes = {}
    for request in instance.requests[1:]:
        size = request[5] * instance.machines[request[4]][1]
        request_sizes[request[0]] = size
    return request_sizes

distances = instance_distance(instance)

def Truck_MIP(instance):

    model = Model('Truck_MIP')

    # Decision Variables
    # decision var truck k goes from i to request j on day d
    x = model.addVars(instance.numRequests, instance.numRequests, instance.numRequests, instance.days, vtype=GRB.BINARY, name="x")
    # decision var if truck k used on day d
    y = model.addVars(instance.numRequests, instance.days, vtype=GRB.BINARY, name="y")
    # decision var continuous 
    # u = model.addVars(instance.numRequests, instance.numRequests, instance.days, vtype=GRB.CONTINUOUS,name="u")

    # decision var
    

    # Objective
    model.setObjective(quicksum(instance.truckDayCost * y[k, d] + instance.truckDistanceCost * x[i, j, k, d] * distances[(instance.requests[i][2],instance.requests[j][2])]
            for i in range(1,instance.numRequests)
            for j in range(1,instance.numRequests)
            for k in range(1,instance.numRequests)
            for d in range(1,instance.days)), GRB.MINIMIZE
    )

    # capacity constraint (after truck visits i, capcaity cannot increase past max)
    model.addConstrs((u[i, k, d] <= instance.truckCapacity
                      for i in range(1,instance.numRequests)
                      for k in range(1,instance.numRequests)
                      for d in range(instance.days)), name="capacity")
    
    # capcaity constraint part 2
    model.addConstrs((u[i, k, d] >= instance.machines[instance.requests[k][4]][1] * instance.requests[k][5]
                      for i in range(1,instance.numRequests)
                      for k in range(1,instance.numRequests)
                      for d in range(1,instance.days)), name="load")

    # constraint trucks can only go from i to one location j on a given day
    model.addConstrs((quicksum(x[i, j, k, d] for j in range(1,instance.numRequests) if i != j) == 1 # maybe <= ?
                      for i in range(1,instance.numRequests)
                      for k in range(1,instance.numRequests)
                      for d in range(1,instance.days)), name="routing")

    # constraint that every request is served (not working)
    model.addConstrs((quicksum(x[i, j, k, d]
                        for k in range(1, instance.numRequests)
                        for d in range(1, instance.days)
                        for j in range(1, instance.numRequests)) == 1
                        for i in range(1, instance.numRequests)), name="serve_once")

    # matrix constraint technitian output

    # constraint for request release and end dates

    model.optimize()

    if model.status == GRB.OPTIMAL:
        print_routes_and_costs(model, instance, x, y)
    else:
        print("No optimal solution found.")


def print_routes_and_costs(model, instance, x, y):
    print("Optimal solution found. Displaying daily routes and costs:")

    # Extracting and displaying the solution
    for d in range(instance.days):
        print(f"\nDay {d + 1}:")
        daily_cost = 0

        for k in range(instance.numRequests):
            route = []
            route_cost = 0
            print(f"  Truck {k + 1}:")
            for i in range(instance.numLocations):
                for j in range(instance.numLocations):
                    if i != j and x[i, j, k, d].x > 0.5:
                        route.append((i, j))
                        route_cost += instance.truckDistanceCost * distances[(i,j)]

            if route:
                print(f"    Route: {route}")
                print(f"    Route Cost: {route_cost}")
                daily_cost += route_cost + instance.truckDayCost if y[k, d].x > 0.5 else 0

        print(f"  Total Cost for Day {d + 1}: {daily_cost}")


Truck_MIP(instance)
