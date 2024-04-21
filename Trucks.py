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
    x = model.addVars(instance.numLocations, instance.numLocations, instance.numRequests, instance.days,vtype=GRB.BINARY, name="x")
    y = model.addVars(instance.numRequests, instance.days, vtype=GRB.BINARY, name="y")
    u = model.addVars(instance.numLocations, instance.numRequests, instance.days, vtype=GRB.CONTINUOUS,name="u")

    # Objective
    model.setObjective(quicksum(instance.truckDayCost * y[k, d] + instance.truckDistanceCost * x[i, j, k, d] * distances[(i,j)]
            for i in range(1,instance.numLocations)
            for j in range(1,instance.numLocations)
            for k in range(1,instance.numRequests)
            for d in range(1,instance.days)), GRB.MINIMIZE
    )


    model.addConstrs((u[i, k, d] <= instance.truckCapacity
                      for i in range(1,instance.numLocations)
                      for k in range(1,instance.numRequests)
                      for d in range(instance.days)), name="capacity")

    model.addConstrs((quicksum(x[i, j, k, d] for j in range(1,instance.numLocations) if i != j) == 1
                      for i in range(1,instance.numLocations)
                      for k in range(1,instance.numRequests)
                      for d in range(1,instance.days)), name="routing")

    model.addConstrs((u[i, k, d] >= instance.machines[instance.requests[k][4]][1] * instance.requests[k][5]
                      for i in range(1,instance.numLocations)
                      for k in range(1,instance.numRequests)
                      for d in range(1,instance.days)), name="load")

    model.addConstrs((quicksum(x[i, j, k, d]
                        for k in range(1, instance.numRequests)
                        for d in range(1, instance.days)
                        for j in range(1, instance.numLocations)) == 1
                        for i in range(1, instance.numRequests)), name="serve_once")

    # matrix constraint technitian output

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
