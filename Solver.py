# Solver.py runs the IP and creates an output file
from gurobipy import *
import Instance
import Trucks2
import Technicians


# pass in file name of instance (hardcode or command line)
filename = 'instances_2024/CO_Case2405.txt' 
# filename = sys.argv[1]

# create "instance" and read file
instance = Instance.Instance()
instance.read_case_file(filename)
      
# solve technician problem
technician_solutions, machines, technician_dist, tech_cost_total = Technicians.IP_Technicians(instance)

# solve truck problem
route_days, truck_days, total_truck_dist, idle_costs, truck_cost_total = Trucks2.IP_Trucks(instance, sorted(machines))
route_days[1:] = sorted(route_days[1:], key=lambda x: x[0])

# print solution
for i in range(1, len(technician_solutions)):
    print(f"Technician {technician_solutions[i][0]} performs tour {(technician_solutions[i][1])} on day {technician_solutions[i][2]}")
for i in range(1, len(route_days)):
    print(f"on day {route_days[i][0]} request {route_days[i][1]} is dropped off")
for i in range(1, len(truck_days)): 
    print(f"day {truck_days[i][0]} there are {truck_days[i][1]} trucks")

# create a dictionary to store number of techncians that work on certain days
technician_days = {}
for i in range(1, len(technician_solutions)):
    if technician_solutions[i][2] not in technician_days:
        technician_days[technician_solutions[i][2] ] = 1
    else:
        technician_days[technician_solutions[i][2] ] += 1


# print line to be copy/pasted to validate current solution
print("\nCOPY/PASTE below to validate: ")
print(f"python Validate.py --instance instances_2024/CO_Case{filename[22:26]}.txt --solution solutions/solution_{filename[22:26]}.txt \n")

# create output file 
with open(f"solutions/solution_{filename[22:26]}.txt", "w") as file:

    # write dataset / name
    file.write(f"DATASET = {instance.dataset}\n")
    file.write(f"NAME = {instance.name} \n")

    # write solution stats
    file.write("\n")
    file.write(f"TRUCK_DISTANCE = {total_truck_dist} \n")
    file.write(f"NUMBER_OF_TRUCK_DAYS = {sum([truck_days[i][1]  for i in range(1, len(truck_days))])} \n")
    file.write(f"NUMBER_OF_TRUCKS_USED = {max([truck_days[i][1] for i in range(1, len(truck_days))])} \n")
    file.write(f"TECHNICIAN_DISTANCE = {technician_dist} \n")
    file.write(f"NUMBER_OF_TECHNICIAN_DAYS = {len(technician_solutions)-1} \n")
    file.write(f"NUMBER_OF_TECHNICIANS_USED = {len(set([technician_solutions[i][0] for i in range(1, len(technician_solutions))]))} \n")
    file.write(f"IDLE_MACHINE_COSTS = {idle_costs}\n")
    file.write(f"TOTAL_COST = {int(truck_cost_total + tech_cost_total)} \n")

    # write schedule
    for d in range(1,instance.days+1):
        file.write("\n")
        file.write(f"DAY = {d} \n")
        file.write(f"NUMBER_OF_TRUCKS = {truck_days[d][1]} \n")
        count = 1
        for i in range(1, len(route_days)):
            if int(route_days[i][0]) == d:
                file.write(f"{count} ")
                for j in range(0,len(route_days[i][1])):
                    file.write(f"{route_days[i][1][j]} ")
                file.write(f"\n")
                count+=1
        if f"{d}" not in technician_days:
            file.write(f"NUMBER_OF_TECHNICIANS = {0} \n")
        else:
            file.write(f"NUMBER_OF_TECHNICIANS = {technician_days[f'{d}']} \n")
            for i in range(1, len(technician_solutions)):
                if d == int(technician_solutions[i][2]):
                    file.write(f"{technician_solutions[i][0]} {' '.join(map(str, technician_solutions[i][1]))} \n")
        