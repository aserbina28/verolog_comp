# this is a unfinished! working on a strategy to create list of tours

import Instance
import numpy as np
import itertools

instance = Instance.Instance()
instance.read_case_file('instances_2024/CO_Case2408.txt' )

# dictionary of jobs a technician can install based on their ability
technician_jobs = {}
for p in  range(1, instance.numTechnicians+1):
    technician_jobs[p] = []
    for m in range(1, instance.numRequests+1):
        machine_type = instance.requests[m][4]
        if instance.technicians[p][machine_type+3]:
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

#shortest tour ignoring technician
def tour_distance(tour, instance):
    dist = 0
    # find the locations of the technician's start and each request m on the tour
    tourLocationIDs = []
    for m in tour:
        tourLocationIDs.append(instance.requests[m][1])
    # add distance traveled for subsequent requests 
    for i in range(1, len(tourLocationIDs)):
        dist += distance(tourLocationIDs[i-1], tourLocationIDs[i])
    return dist

# function to compute distance between two locations
def distance(location1, location2):
    x1 = instance.locations[location1][1]
    y1 = instance.locations[location1][2]
    x2 = instance.locations[location2][1]
    y2 = instance.locations[location2][2]
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

# TODO use distance and max installation restrictions to create possible tours 
#      for each technician on each day

import itertools

def feasible_tours(instance):
    shortest_tours = {}
    max_installations = 0
    max_distance = 0
    for p in range(1, instance.numTechnicians+1):
        if instance.technicians[p][3] > max_installations:
            max_installations = instance.technicians[p][3]
        if instance.technicians[p][2] > max_distance:
            max_distance = instance.technicians[p][2]
    
    tours = [[]]

    machines_on_tour = []  # Initialize dictionary to store machine types for each tour

    max_installations = 5 # DELETE THIS 
    
    # Iterate over possible tour lengths
    for length in range(1, max_installations + 1):
        print("CURRENT LENGTH:", length)
        # Generate all combinations of locations for the current length
        for combination in itertools.combinations(range(1, instance.numRequests + 1), length):
            # Generate all permutations of the current combination
            for permutation in itertools.permutations(combination):
                # Calculate the distance of the current tour
                current_tour_distance = tour_distance(permutation, instance)
                # Check if this combination of locations has been encountered before
                key = tuple(sorted(permutation))
                if key not in shortest_tours:
                    # If not encountered before, add it to the shortest_tours dictionary
                    shortest_tours[key] = current_tour_distance
                else:
                    # If encountered before, update the shortest distance if necessary
                    shortest_tours[key] = min(shortest_tours[key], current_tour_distance)
    
    tours = tours + [[*tour] for tour in shortest_tours.keys() if tour_distance(tour, instance) < max_distance]
    for tour in tours:
        machines_on_tour.append([instance.requests[int(m)][4] for m in tour])

    return tours, machines_on_tour  # Return both tours list and machines_on_tour dictionary