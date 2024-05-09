# Tours.py creates feasible tours for technicians

import numpy as np
import itertools
import Instance

#shortest tour ignoring technician
def tour_distance(tour, instance):
    dist = 0
    # find the locations of the technician's start and each request m on the tour
    tourLocationIDs = []
    for m in tour:
        tourLocationIDs.append(instance.requests[m][1])
    # add distance traveled for subsequent requests 
    for i in range(1, len(tourLocationIDs)):
        dist += distance(tourLocationIDs[i-1], tourLocationIDs[i], instance)
    return dist

# function to compute distance between two locations
def distance(location1, location2, instance):
    x1 = instance.locations[location1][1]
    y1 = instance.locations[location1][2]
    x2 = instance.locations[location2][1]
    y2 = instance.locations[location2][2]
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

def tech_distance(tour, instance):
    tech_tour_dist = 0
    for i in range(1, instance.numTechnicians+1):
        tech_tour_dist = distance(instance.locations[instance.requests[tour[0]][1]][0], instance.locations[instance.technicians[i][1]][0], instance) + tour_distance(tour,instance) + distance(instance.locations[instance.requests[tour[-1]][1]][0], instance.locations[instance.technicians[i][1]][0], instance)
        if tech_tour_dist <= instance.technicians[i][2]:
            return True
    return False

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

    max_installations = 5# DELETE THIS
    
    # Iterate over possible tour lengths
    for length in range(1, max_installations + 1):
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
    
    tours = tours + [[*tour] for tour in shortest_tours.keys() if tech_distance(tour, instance)] # modified this

    for tour in tours:
        machines_on_tour.append([instance.requests[int(m)][4] for m in tour])

    return tours, machines_on_tour  # Return both tours list and machines_on_tour dictionary

