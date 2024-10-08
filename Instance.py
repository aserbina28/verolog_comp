
class Instance(object):
    def __init__(self):
        self.dataset = None
        self.distance = None
        self.name = None
        self.days = None
        self.truckCapacity = None
        self.truckMaxDistance = None
        self.truckDistanceCost = None
        self.truckDayCost = None
        self.truckCost = None
        self.technicianDistanceCost = None
        self.technicianDayCost = None
        self.technicianCost = None
        self.numMachines = None
        self.machines = [['id', 'size', 'penalty']]
        self.numLocations = None
        self.locations = [['id', 'x', 'y']]
        self.numRequests = None
        self.requests = [['id', 'location_id', 'first_day', 'last_day', 'machine_id', 'num_machines']]
        self.numTechnicians = None
        self.technicians = [['id', 'location_id', 'max_distance', 'max_installations', 'installation_ability']]

    def read_case_file(self, filename):
        # open file, read line by line
        file = open(filename)
        for line in file:
            line = line.strip()
            if len(line) != 0: 
                # read constants and assign to variables
                var, value = line.split(' = ')
                if var == 'DATASET':
                    self.dataset = value
                elif var == 'DISTANCE':
                    self.distance = int(value)
                elif var == 'NAME':
                    self.name = value
                elif var == 'DAYS':
                    self.days = int(value)
                elif var == 'TRUCK_CAPACITY':
                    self.truckCapacity = int(value)
                elif var == 'TRUCK_MAX_DISTANCE':
                    self.truckMaxDistance = int(value)
                elif var == 'TRUCK_DISTANCE_COST':
                    self.truckDistanceCost = int(value)
                elif var == 'TRUCK_DAY_COST':
                    self.truckDayCost = int(value)
                elif var == 'TRUCK_COST':
                    self.truckCost = int(value)
                elif var == 'TECHNICIAN_DISTANCE_COST':
                    self.technicianDistanceCost = int(value)
                elif var == 'TECHNICIAN_DAY_COST':
                    self.technicianDayCost = int(value)
                elif var == 'TECHNICIAN_COST':
                    self.technicianCost = int(value)
                # create 2d lists for machines, locations, reqests, technicians 
                elif var == 'MACHINES':
                    self.numMachines = int(value)
                    for i in range(self.numMachines):
                        self.machines.append([])
                        row = file.readline().strip().split()
                        for j in row:
                            self.machines[i+1].append(int(j))
                elif var == 'LOCATIONS':
                    self.numLocations = int(value)
                    for i in range(self.numLocations):
                        self.locations.append([])
                        for j in file.readline().strip().split():
                            self.locations[i+1].append(int(j))
                elif var == 'REQUESTS':
                    self.numRequests = int(value)
                    for i in range(self.numRequests):
                        self.requests.append([])
                        for j in file.readline().strip().split():
                            self.requests[i+1].append(int(j))
                elif var == 'TECHNICIANS':
                    self.numTechnicians = int(value)
                    for i in range(self.numTechnicians):
                        self.technicians.append([])
                        for j in file.readline().strip().split():
                            self.technicians[i+1].append(int(j))
        file.close()


class Technician(object):
    def __init__(self, id, location_id, max_distance, max_installations, installation_ability):
        self.id = id
        self.location_id = location_id
        self.max_distance = max_distance
        self.max_installations = max_installations
        self.installation_ability = installation_ability
    