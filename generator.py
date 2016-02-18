# Run this file to generate random case based memory

import sys
import random
from copy import deepcopy
from simple_travel_example import find_plan
from simple_travel_example import generate_new_state
from simple_travel_example import print_state
	
# Make a list for all possible objects
location = ['home', 'park', 'restaurant', 'market', 'bank']
bus_stop = ['bus_stop_1', 'bus_stop_2', 'bus_stop_3']
location_bus_stop = deepcopy(location)
location_bus_stop.extend(bus_stop)
	
# Get a random location
def getRandomLocation(excludeValue):
	if excludeValue == None:
		loc = location[int(random.random()*len(location))]
	else:
		while True:
			loc = location[int(random.random()*len(location))]
			if loc == "bank":
				continue
			if loc != excludeValue:
				break
	return loc

# Get a random bus
def getRandomBusStop():
	return bus_stop[int(random.random()*len(bus_stop))]

# Get a random cash
def getRandomCash():
	return round(random.random()*20, 2)
	
# Get a random time
def getRandomTime():
	return round(random.random()*100, 2)

# Get a random distance	
def getRandomDistance(maxDist):
	return round(random.random()*maxDist, 2)

# Get a random frozen set
def getRandomFrozenSet():
	routeList = []
	for locX in bus_stop:
		for locY in location_bus_stop:
			if random.random() < 0.2:
				routeList.append(locX+':'+locY)	
	return routeList
				
# Generate readable string for state
def generate_state_string(state, tab):
	stateStr = ''
	firstLoop = True
	for (name,val) in vars(state).items():
		if name != '__name__':
			if isinstance(val, basestring):
				val = '\'' + val + '\''
			strVal = str(val)
			strVal = strVal.replace('\'', '\\\'')					
			delimeter = ',\n'
			if firstLoop == True:
				delimeter = ''
				firstLoop = False
			stateStr = stateStr + delimeter + tab + '\'' + name + '=' + strVal + '\''
	tab = tab[:len(tab)-1]
	stateStr = stateStr + '\n' + tab + '])'
	return stateStr
	
# Main funciton to generate random case based memory
if __name__ == "__main__":

	if len(sys.argv) < 2:		
		print "[Error] Usage: python %s noOfProblem" % (sys.argv[0])
		exit()
	
	# Get noOfProblem with from command line argument
	noOfProblem = int(sys.argv[1])	
	
	#noOfProblem = 1
	tab = ''
	fileStr = '[\n'
	tab = tab + '\t'
	
	count = 0
	
	while count < noOfProblem:
		# Generate noOfProblem problems
		
		# Initiate state
		state = generate_new_state('state')
		
		state.loc = {}
		state.cash = {}
		state.cash = {}
		state.balance_bank = {}
		state.nearest_bus_stop = {}
		state.time = {}
		state.target = 'me'
		
		# Randomize state
		state.loc[state.target] = getRandomLocation('bank')
		state.loc['bus'] = getRandomBusStop()		
		state.cash[state.target] = getRandomCash()
		state.balance_bank[state.target] = round(getRandomCash()*getRandomCash(), 2)
		state.nearest_bus_stop[state.target] = getRandomBusStop()
		state.time[state.target] = getRandomTime()
		
		#############################################################
		
		# state.dist = {}
		# for locX in location_bus_stop:
			# state.dist[locX] = {}
			# for locY in location_bus_stop:				
				# if locX != locY:
					# state.dist[locX][locY] = getRandomDistance(15)
					# if locY in state.dist:
						# state.dist[locY][locX] = state.dist[locX][locY]
		
		# state.dist[state.loc[state.target]][state.nearest_bus_stop[state.target]] = getRandomDistance(2)
		
		# state.bus_route = getRandomFrozenSet()	
		
		#############################################################
		
		# Initiate goal state
		goal = generate_new_state('goal')
		goal.loc = {}
		goal.cash = {}
		# Randomize goal state
		goal.loc[state.target] = getRandomLocation(state.loc[state.target])				
		goal.cash[state.target] = getRandomCash()				
		goal.target = 'me'
		
		# Find plan using pyhop
		plan = find_plan(state, goal)
		
		# If plan found make a readable string, that we will write on our case based memory file
		if plan != False:			
			#print plan
			fileStr = fileStr + tab + '([\n'				
			tab = tab + '\t'
			
			fileStr = fileStr + tab + '([\n'				
			tab = tab + '\t'
			fileStr = fileStr + generate_state_string(state, tab) + ',\n'
			tab = tab[:len(tab)-1]
			
			fileStr = fileStr + tab + '([\n'
			tab = tab + '\t'
			fileStr = fileStr + generate_state_string(goal, tab) + '\n'
			tab = tab[:len(tab)-1]
			
			tab = tab[:len(tab)-1]
			fileStr = fileStr + tab + '],\n'
			strPlan = str(plan)
			tab = tab + '\t'
			strPlan = strPlan.replace('[(','[\n'+tab+'(')			
			strPlan = strPlan.replace('),','),\n'+tab)
			strPlan = strPlan.replace(' (\'','(\'')
			tab = tab[:len(tab)-1]
			strPlan = strPlan.replace(')]',')\n'+tab+']')			
			
			fileStr = fileStr + tab + strPlan + '),\n'
			
			count = count + 1
			
	# Write all the plans to our case based memory file 'generated_plan.txt'
	fileStr = fileStr[:len(fileStr)-2] + '\n'
	fileStr = fileStr + ']'
	f = open('generated_plan.txt', 'w')
	f.write(fileStr)	
	f.close()
	print "Successfully generated", noOfProblem, "random plans on the file", "\'generated_plan.txt\'"
