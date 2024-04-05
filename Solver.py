import numpy as np
from gurobipy import *
import Instance 

# pass in file name of instance (hard code or command line)
filename = 'CO_Case2401.txt' 
# filename = sys.argv[1]

# create instance for this case and read file
case = Instance.Instance()
case.read_case_file(filename)

# find possible daily routes given trucks, locations, requests
routes = []
