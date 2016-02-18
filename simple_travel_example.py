# The plan generation strategy using pyhop

import pyhop

# Open a file given a file name and returns the file pointer
def openFile(fileName):
	try:
		fo = open(fileName, "r")
	except IOError:
		print "File", fileName, "cannot be read"
		sys.exit()
	return fo

# Calculate taxi rate, given distance
def taxi_rate(dist):
	return round(1.5 + 0.5 * dist, 2)

# Calculate bus rate, given distance	
def bus_rate(dist):
	if dist < 5:
		return 1.0
	else:
		return 2.0

# Get distance between two locations
def distance(x,y):
	global static_state
	try:
		d = static_state.dist[x][y]
	except KeyError:
		# If no info found for this two locations, returns a big number(infinity)
		d = 99999
	return d
	
# Time in minutes it takes to walk for given distance
def time_cost_walk(dist):
	return dist * 6
	
# Time in minutes it takes for taxi travel for given distance
def time_cost_taxi(dist):
	return dist * 1
	
# Time in minutes it takes for bus travel for given distance
def time_cost_bus(dist):
	return dist * 1.5

# Walk object a from location x to y
def walk(state,a,x,y):
	if state.loc[a] == x:
		state.loc[a] = y
		# Reduce the remaining time
		state.time[a] = state.time[a] - time_cost_walk(distance(x,y))
		return state
	else:
		return False

# Call for a taxi at location x by object a
def call_taxi(state,a,x):
	state.loc['taxi'] = x
	return state
    
# Object a rides a taxi from x to y location
def ride_taxi(state,a,x,y):
	if state.loc['taxi']==x and state.loc[a]==x:
		state.loc['taxi'] = y
		state.loc[a] = y      
		# Reduce the remaining time
		state.time[a] = state.time[a] - time_cost_taxi(distance(x,y))
		return state
	else:
		return False
		
# Object a rides a bus from x to y location
def ride_bus(state,a,x,y):
	if state.loc['bus']==x and state.loc[a]==x:
		state.loc['bus'] = y
		state.loc[a] = y  
		# Reduce the remaining time
		state.time[a] = state.time[a] - time_cost_bus(distance(x,y))
		return state
	else:
		return False

# Object a pays the cab driver the cab fair
def pay_cab_driver(state, a, taxi_fair):
	# Must have that much amount
	if state.cash[a] >= taxi_fair:
		# Reduce remaining amount
		state.cash[a] = state.cash[a] - taxi_fair
		return state
	else:
		return False
	
# Object a pays the bus driver the bus fair
def pay_bus_driver(state,a,bus_fair):
	# Must have that much amount
	if state.cash[a] >= bus_fair:
		# Reduce remaining amount
		state.cash[a] = state.cash[a] - bus_fair		
		return state
	else:
		return False

# Object a withdraw amount from his bank account
def withdraw_money(state,a,amount):
	# Must be at the bank and must have that much of amount in the bank to withdraw
	if state.loc[a]=='bank' and amount <= state.balance_bank[a]:
		state.cash[a] = state.cash[a] + amount
		# Reduce the remaining bank balance
		state.balance_bank[a] = state.balance_bank[a] - amount		
		return state
	else:
		return False

# Calculate the total cost for this specific plan
def costForPlan(plan):
	cost = 0
	if plan != False:
		for item in plan:
			if item[0][0:3] == "pay":
				# Add up all cost that have the action 'pay'
				cost = cost + item[2]
	return cost

# Decalare all the operators for pyhop
pyhop.declare_operators(walk, call_taxi, ride_taxi, pay_cab_driver, pay_bus_driver, ride_bus, withdraw_money)

# Main pyhop method to reach the goal state from initial state
def travel_by_goal_state(state, goal):	
	# Get the problem domain info related file
	fo = openFile('static_value.txt')	
	exec('content=' + fo.read())
	global static_state
	static_state = pyhop.State("static")
	for stateItem in content:				
		# Load the problem domain info into the state
		exec("static_state."+stateItem)
		
	a = state.target
	x = state.loc[a]
	y = goal.loc[a]	
	t = state.time[a]	
	cashX = state.cash[a]
	if hasattr(goal, 'cash'):
		cashY = goal.cash[a]
	else:
		cashY = 0		
		
	# Get the nearest bus stop
	bs = state.nearest_bus_stop[state.target]
	# Get the bus fair
	bus_fair = bus_rate(distance(bs,y))
	
	if distance(x,y) <= 2 and t >= time_cost_walk(distance(x,y)):
		# If walking is possible, then travel by foot
		return travel_by_foot(state,a,x,y)
	elif cashX >= taxi_rate(distance(x,y)) and cashY<=cashX-taxi_rate(distance(x,y)) \
		and t >= time_cost_taxi(distance(x,y)):		
		# If taxi travel is possible, then travel by taxi
		return travel_by_taxi(state,a,x,y)
	elif cashX >= bus_fair and cashY <= cashX - bus_fair \
		and distance(x,bs) <= 2 and (bs+':'+y in static_state.bus_route) \
		and t >= time_cost_bus(distance(x,y)):	
		# If bus travel is possible, then travel by bus
		return travel_by_bus(state,a,x,y)	
	elif y != 'bank':
		# If no travel is possible, now we will try to go to the bank to withdraw some money
		# and continue the journey from there
		
		# Intermediate state will be the bank location
		intermediateState = generate_new_state('intermediateState')
		
		intermediateState.loc = {}
		intermediateState.cash = {}
		intermediateState.cash = {}
		intermediateState.time = {}
		intermediateState.balance_bank = {}
		intermediateState.nearest_bus_stop = {}
		intermediateState.target = 'me'
		
		intermediateState.loc[state.target] = 'bank'		
		intermediateState.loc['bus'] = state.loc['bus']
		intermediateState.cash[state.target] = taxi_rate(distance('bank',y))	
		intermediateState.balance_bank[state.target] = state.balance_bank[state.target]
		intermediateState.nearest_bus_stop[state.target] = state.nearest_bus_stop[state.target]
		
		# Find the plan to the bank from the source state
		plan1 = pyhop.pyhop(state,[('travel_by_goal', intermediateState)],verbose=0)
		# Get the cost of this intermediate plan
		cost1 = costForPlan(plan1)
		# Reduce the amount by cost1
		intermediateState.cash[state.target] = state.cash[state.target] - cost1
		
		if plan1 != False:	
			# Now we have a plan to travel to the bank
			# Need one more plan to travel to the goal from the bank
			
			# Amount needed to reach the goal from the bank
			amount_needed = cost1+taxi_rate(distance('bank',y))+\
				goal.cash[state.target]-state.cash[state.target]+3.0
				
			# Get a plan to withdraw necessary amount from the bank
			plan2 = withdraw_money_from_bank(intermediateState,a,amount_needed)			
			
			# If we have that much money in the bank, the plan will pass
			if plan2 != False:				
				# Append the withdraw money plan at the end of the first plan
				plan1.extend(plan2)			
				
				# Reflect the time remaining
				intermediateState.time[state.target] = state.time[state.target]
				
				# Find the next plan of going to the destination from the bank
				plan3 = pyhop.pyhop(intermediateState,[('travel_by_goal', goal)],verbose=0)
				if plan3 != False:				
					# All plans are passed, extend the last plan at the end
					plan1.extend(plan3)
					return plan1
		return False
	else:
		return False
		
# Travel from x to y by foot
def travel_by_foot(state,a,x,y):
	# Check precondition
	if distance(x,y) <= 3:
		return [('walk',a,x,y)]
	else:
		return False

# Travel from x to y by taxi
def travel_by_taxi(state,a,x,y):
	taxi_fair = taxi_rate(distance(x,y))
	# Check precondition
	if state.cash[a] >= taxi_fair:
		return [('call_taxi',a,x), ('ride_taxi',a,x,y), ('pay_cab_driver',a,taxi_fair)]
	else:
		return False

# Travel from x to y by bus		
def travel_by_bus(state,a,x,y):
	global static_state
	bs = state.nearest_bus_stop[a]
	bus_fair = bus_rate(distance(bs,y))
	# Check precondition
	if distance(x,bs) <= 3 and state.cash[a] >= bus_fair and (bs+':'+y in static_state.bus_route):
		return [('walk',a,x,bs), ('pay_bus_driver',a,bus_fair), ('ride_bus',a,bs,y)]
	else:
		return False
		
# Withdraw money from bank
def withdraw_money_from_bank(state,a,amount):
	# Check precondition
	if amount <= state.balance_bank[a]:
		state = withdraw_money(state,a,amount)
		return [('withdraw_money',a,amount)]
	else:
		return False

# Decalare the pyhop method
pyhop.declare_methods('travel_by_goal', travel_by_goal_state)

def generate_new_state(stateName):
	return pyhop.State(stateName)
	
def find_plan(state, goal):	
	return pyhop.pyhop(state,[('travel_by_goal', goal)],verbose=0)
	
def print_state(state):
	pyhop.print_state(state)
