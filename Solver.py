import numpy as np
from gurobipy import *
import Instance


# pass in file name of instance (hard code or command line)
filename = 'instances_2024/CO_Case2404.txt' 
# filename = sys.argv[1]

# create "instance" and read file
instance = Instance.Instance()
instance.read_case_file(filename)

#TODO make tours and schedules more strategic  

# tours (start with making tours only one or two machine requests)
tours = [["tours"]]
for t in range(1, instance.numRequests+1):
    tours.append([t])
    for t2 in range(t, instance.numRequests+1):
        tours.append([t, t2])

# schedule (allow everything for now)
schedule = [["schedule"]]
schedule.append([1])
for i in range(2, instance.days+1):
    schedule[1].append(i)

# function to solve IP for technicians
def IP_Technicians():

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
            h[p,t] += instance.technicianDistanceCost * distance(technicianLocationID, tourLocationIDs[0])
            # add cost of distance traveled for subsequent requests 
            for i in range(1, len(tourLocationIDs)-1):
                h[p,t] += instance.technicianDistanceCost * distance(tourLocationIDs[i-1], tourLocationIDs[i])
            # add cost of techncian going back to their starting place
            h[p,t] += instance.technicianDistanceCost * distance(tourLocationIDs[len(tourLocationIDs)-1], technicianLocationID)
            h[p,t] += instance.technicianDayCost
    
    # variable indicates if schedule s contains day d
    e = {}
    for s in range(1, len(schedule)):
        for d in range(1, instance.days+1):
            if d in schedule[s]:
                e[s,d] = 1
            else:
                e[s,d] = 0
    
    # variable indicates whether machine request m can be delivered on day d
    l = {}
    for m in range(1, instance.numRequests+1):
        for d in range(1, instance.days+1):
            # is the day greater than (after) the first day the request is released?
            if d > instance.requests[m][2]: 
                l[m,d] = 1
            else:
                l[m,d] = 0
    
    # gurobi model
    model = Model()

    # decision var person p performs tour t on day d
    y = {}
    for p in range(1, instance.numTechnicians+1):
        for t in range(1, len(tours)):
            for d in range(1, instance.days+1):
                y[p,t,d] = model.addVar(0, 1, 0, GRB.BINARY, "y_%d_%d_%d" %(p,t,d))
    
    # decision var person p has schedule s
    z = {}
    for p in range(1, instance.numTechnicians+1):
        for s in range(1, len(schedule)):
            z[p,s] = model.addVar(0, 1, 0, GRB.BINARY, "z_%d_%d" %(p,s))

     # decision variable for total cost of person p
    c = {}
    for p in range(1, instance.numTechnicians+1):
       c[p] = model.addVar(0, GRB.INFINITY, 1, GRB.CONTINUOUS, "c_%d"%p)
    
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
                    for d in range(1, instance.days+1)) >= 1)

    # constraint machines can't be installed until after the request is released
    for m in range(1, instance.numRequests+1):
        for d in range(1, instance.days+1):
            model.addConstr(quicksum(b[t,m]*y[p,t,d] for t in range(1, len(tours)) for p in range(1, instance.numTechnicians+1)) <=l[m,d])

    #TODO add constraints about techncians abilities/ max requests/ max distance

    model.setParam('OutputFlag', False)
    model.optimize()

     # create list to store y variable values 
    solutions = [["technician", "tour", "day"]] 

    if model.SolCount == 0:
        print("***NO SOLUTION FOUND***")
    else:
        #parse decision vars and add to list
        for v in model.getVars():
            if v.X > 0 and 'y' in v.varName:
                y,p,t,d = v.varName.split('_')
                solutions.append([p, tours[int(t)], d])
    
    return solutions

def distance(location1, location2):
    x1 = instance.locations[location1][1]
    y1 = instance.locations[location1][2]
    x2 = instance.locations[location2][1]
    y2 = instance.locations[location2][2]
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)


# call techncian function
technician_solutions = IP_Technicians()
# print solution
for i in range(1, len(technician_solutions)):
    print(f"Technician {technician_solutions[i][0]} performs tour {(technician_solutions[i][1])} on day {technician_solutions[i][2]}")