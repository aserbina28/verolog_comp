# this is a unfinished! working on a strategy to create list of tours

import Instance
import numpy as np
import itertools

instance = Instance.Instance()
instance.read_case_file('instances_2024/CO_Case2401.txt' )

# dictionary of jobs a technician can install based on their ability
technician_jobs = {}
for p in  range(1, instance.numTechnicians+1):
    technician_jobs[p] = []
    for m in range(1, instance.numRequests+1):
        machine_type = instance.requests[m][4]
        if instance.technicians[p][machine_type+3]:
            for n in range(1, instance.requests[m][5]+1):
                technician_jobs[p].append(m)
    print(f"technician {p} can install {technician_jobs[p]}")

# dictionary(?) jobs a technician can install on each day
day_technician_jobs = {}
for p in  range(1, instance.numTechnicians+1):
    for d in range(1, instance.days+1):
        day_technician_jobs[p,d] = []
        for m in technician_jobs[p]:
            if d > int(instance.requests[m][2]): #DECIDE: should we also restrict by last day?
                day_technician_jobs[p,d].append(m)
        print(f"technician {p} can install {day_technician_jobs[p,d]} on day {d}")

# TODO use distance and max installation restrictions to create possible tours 
#      for each technician on each day


available_requests = []
for m in range(1, instance.numRequests+1):
    machine_type = instance.requests[m][4]
    for n in range(1, instance.requests[m][5]+1):
        available_requests.append(m)
print("Available requests: ", available_requests )

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

# function to compute distance between two locations
def distance(location1, location2):
    x1 = instance.locations[location1][1]
    y1 = instance.locations[location1][2]
    x2 = instance.locations[location2][1]
    y2 = instance.locations[location2][2]
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

#function to find a possible list of tours for a given person on a given day choosing from available requests 
def daily_tour(technician, day, instance, available_requests):
    daily_tours = []
    max_dist = instance.technicians[technician][2]
    max_install = instance.technicians[technician][3]
    jobs_can_do_today = []
    for a in available_requests:
        machine_type = instance.requests[a][4]
        if instance.technicians[technician][machine_type+3]:
            if d > int(instance.requests[m][2]):
                for n in range(1, instance.requests[a][5]+1):
                    jobs_can_do_today.append(a) #finds the list of jobs a given technician can do today
    #all possible tours from available jobs
    tour_combinations = list(itertools.combinations(jobs_can_do_today, max_install))
    for tour in tour_combinations:
        if tour_distance(technician, tour, instance) <=max_dist:
            daily_tours.append(tour)
            print(max_dist, " ", tour_distance(technician, tour, instance))
    

daily_tour(1, 2, instance, available_requests)