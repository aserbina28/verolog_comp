# this is a unfinished! working on a strategy to create list of tours

import Instance
import numpy as np

# function to make list of tours for technicians with given instance
def make_tours(instance):
    tours = [["tours"]]
    for t in range(1, instance.numRequests+1):
        tours.append([t])
        for t2 in range(t, instance.numRequests+1):
            tours.append([t, t2])
    
    return tours

# function to compute distance of tour for person
def tour_distance(technician, tour, instance):
    dist = 0
    # find the locations of the technician's start and each request m on the tour
    technicianLocationID = instance.technicians[technician][1]
    tourLocationIDs = []
    for m in tour:
        tourLocationIDs.append(instance.requests[m][1])
    # add distance from technician start to first request 
    dist += distance(technicianLocationID, tourLocationIDs[0])
    # add distance traveled for subsequent requests 
    for i in range(1, len(tourLocationIDs)):
        dist += distance(tourLocationIDs[i-1], tourLocationIDs[i])
    # add disatnce of techncian going back to their starting place
    dist += distance(tourLocationIDs[len(tourLocationIDs)-1], technicianLocationID)
    return dist

def distance(location1, location2):
    x1 = instance.locations[location1][1]
    y1 = instance.locations[location1][2]
    x2 = instance.locations[location2][1]
    y2 = instance.locations[location2][2]
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

# function to make list of schedules for technicians with given instance
def make_schedule(instance):
    schedule = [["schedule"]]
    
    for i in range(2, instance.days+1):
        schedule.append([1])
        for j in range(2, instance.days+1):
            schedule[i].append(i)
    return schedule


# test
instance = Instance.Instance()
instance.read_case_file('instances_2024/CO_Case2404.txt' )