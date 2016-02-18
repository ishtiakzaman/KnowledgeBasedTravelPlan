import sys
from copy import deepcopy
import pyhop
from state import State
from simple_travel_example import find_plan
from state_similarity import StateSimilarity

class Modifier:

	# Initiate the Modifier module with the problem domain related info file name
	def __init__(self, stateSimilarityFileName):
		self.__stateSimilarityFileObject = self.__openFile(stateSimilarityFileName)		
		self.__processFile(self.__stateSimilarityFileObject, 'state_similarity')
		
		self.__stateSimilarity = StateSimilarity("statesimilarity")
		
	# Open a file given a file name and returns the file pointer
	def __openFile(self, fileName):
		try:
			fo = open(fileName, "r")
		except IOError:
			print "File", fileName, "cannot be read"
			sys.exit()
		return fo
	
	# Read the file content onto the object <strListName>	
	def __processFile(self, fo, strListName):
		content = fo.read()		
		exec('self.' + strListName + '=' + content)
		
	# Total cost of this whole plan
	def __costForPlan(self, plan):
		cost = 0
		if plan != False:
			for item in plan:
				if item[0][0:3] == "pay":
					# Add up all cost that have the action 'pay'
					cost = cost + item[2]
		return cost
		
	# We will try to replace the retrieved init / goal state with our init / goal state
	# and will test whether the adapted plan really works or not. If works return this plan.
	def __adaptToCurrentPlan(self, initState, goalState, retrievedInitState,\
													retrievedGoalState, retrievedPlan):
		modifiedPlan = deepcopy(retrievedPlan)
		locX1 = initState.loc[initState.target]
		locX2 = retrievedInitState.loc[retrievedInitState.target]
		locY1 = goalState.loc[goalState.target]
		locY2 = retrievedGoalState.loc[retrievedGoalState.target]
		
		planWithStarting = deepcopy(modifiedPlan)
		
		# Check for adaptation at the starting part		
		if locX1 != locX2:			
			if modifiedPlan[0][0] == 'walk':
				planPart = (modifiedPlan[0][0], modifiedPlan[0][1], locX1, modifiedPlan[0][3])
				modifiedPlan[0] = planPart
								
			elif modifiedPlan[0][0] == 'call_taxi':
				planPart = (modifiedPlan[0][0], modifiedPlan[0][1], locX1)
				modifiedPlan[0] = planPart
				
				planPart = (modifiedPlan[1][0], modifiedPlan[1][1], locX1, modifiedPlan[1][3])
				modifiedPlan[1] = planPart
				
				distance = initState.dist[locX1][modifiedPlan[1][3]]
				taxi_fair = round(1.5 + 0.5 * distance, 2)
				planPart = (modifiedPlan[2][0], modifiedPlan[2][1], taxi_fair)
				modifiedPlan[2] = planPart
				
			print 'Adapted start part', modifiedPlan
			print
			planWithStarting = deepcopy(modifiedPlan)
			
		# Check for adaptation at the end part		
		if locY1 != locY2:			
			k = len(modifiedPlan)-1
			while k >= 0:
				if modifiedPlan[k][0] == 'walk':
					# replace the location for walking
					planPart = (modifiedPlan[k][0], modifiedPlan[k][1], modifiedPlan[k][1], locY1)
					modifiedPlan[k] = planPart
					
					break
				elif modifiedPlan[k][0] == 'call_taxi':
					# replace the location for taxi
					planPart = (modifiedPlan[k+1][0], modifiedPlan[k+1][1], modifiedPlan[k+1][2], locY1)
					modifiedPlan[k+1] = planPart
					
					distance = initState.dist[modifiedPlan[k+1][2]][locY1]
					taxi_fair = round(1.5 + 0.5 * distance, 2)
					planPart = (modifiedPlan[k+2][0], modifiedPlan[k+2][1], taxi_fair)
					modifiedPlan[k+2] = planPart
										
					break
				elif modifiedPlan[k][0] == 'fly':
					# replace the location for fly
					planPart = (modifiedPlan[k][0], modifiedPlan[k][1], modifiedPlan[k][2], locY1)
					modifiedPlan[k] = planPart
					
					distance = initState.dist[modifiedPlan[k][2]][locY1]
					fair = round(1.5 + 0.5 * distance, 2)
					planPart = (modifiedPlan[k+1][0], modifiedPlan[k+1][1], fair)
					modifiedPlan[k+1] = planPart					
					
					break
					
				k = k-1
				
			print 'Adapted last part', modifiedPlan
			print
		
		# Plan created, now test whether this plan really works on not
				
		print 'Testing this plan'		
		planCost = self.__costForPlan(modifiedPlan)
		# Checking whether this plan is possible
		if initState.cash[initState.target] - planCost >= goalState.cash[goalState.target]:
			print 'Plan passed'
			print
			return modifiedPlan, True
			
		print 'Plan failed'
		print
		
		planCost = self.__costForPlan(planWithStarting)
		# Checking whether planWithStarting plan is possible
		if initState.cash[initState.target] - planCost >= goalState.cash[goalState.target]:
			# Partially adapted, thus returning false
			return planWithStarting, False
			
		# No adaptation worked, returning old retrieved plan as it is
		return retrievedPlan, False
	
	# Modifies the retrieved currentCase
	def modifyPlan(self, initState, goalState, currentCase):
		# initState - our init state
		# goalState - our goal state
		# currentCase - retrieved case from the retriever
		
		
		
		# We have two different strategy for modification
		# 1. We will try to replace the retrieved init / goal state with our init / goal state
		# and will test whether the adapted plan really works or not. If works return this plan.
		# 2. If strategy #1 fails, we will try to fill up the missing part at the beginning of the plan
		# and at the end of the plan
		
		
		# Mark the flag as True
		successFlag = True
		if len(currentCase) == 0:
			# No previous plan found
			# Call pyhop to get plan from scratch
			print "Calling pyhop to get plan from scratch"			
			modifiedPlan = find_plan(initState, goalState)
		else:
			# We will try to modify the plan
			
			# Initiate current init state and goal state
			currentInitState = State("currentInitState")
			currentGoalState = State("currentGoalState")			
			for stateItem in currentCase[0][0]:						
				exec("currentInitState."+stateItem)							
			for stateItem in currentCase[0][1]:						
				exec("currentGoalState."+stateItem)
				
			# Copying random bus stop to loc[bus] to avoid KeyError
			currentGoalState.loc['bus'] = 'bus_stop_1'
			
			fo = self.__openFile('static_value.txt')	
			exec('content=' + fo.read())
			for stateItem in content:				
				exec("currentInitState."+stateItem)
				exec("currentGoalState."+stateItem)
			
			currentGoalState.time = {}
			currentGoalState.nearest_bus_stop = {}
			currentGoalState.balance_bank = {}
			currentGoalState.time[currentGoalState.target] = \
				currentInitState.time[currentGoalState.target]
			currentGoalState.nearest_bus_stop[currentGoalState.target] = 'bus_stop_1'
			currentGoalState.balance_bank[currentGoalState.target] = \
				initState.balance_bank[initState.target]
			
			currentPlan = currentCase[1]
			
			# Try to adapt the retrieve plan to the current plan
			modifiedPlan, isComplete = self.__adaptToCurrentPlan(initState, goalState, \
								currentInitState, currentGoalState, currentPlan)
			if isComplete == True:
				# Modification completed
				return modifiedPlan, successFlag
			else:
				# Continue with the returned plan, it could be partially adapted
				currentPlan = deepcopy(modifiedPlan)
			
			# At this point, the adaptation strategy didn't work out correctly
			# we will try to apply our second strategy
			
			
			# cost for current plan
			costOfCurrentPlan = self.__costForPlan(currentPlan)
			
			currentGoalState.cash[currentGoalState.target] = \
				initState.cash[initState.target]-costOfCurrentPlan
			
			modifiedPlan = deepcopy(currentPlan)
			
			if self.__isSimilar(initState, currentInitState) == False:
				# Need to fillup the missing travel at the beginning
				#print "Calling pyhop to get plan for the beginning part"	
				
				newPlan = find_plan(initState, currentInitState)				
				
				if newPlan != False:
					# Got a plan, append it at the beginning
					print newPlan
					print
					newPlan.extend(modifiedPlan)
					modifiedPlan = []
					modifiedPlan = deepcopy(newPlan)
				else:
					print 'Could not find a suitable plan for the beginning part'
					print
					successFlag = False
				
			if self.__isSimilar(goalState, currentGoalState) == False:
				# Need to fillup the missing travel at the end part
				
				#print "Calling pyhop to get plan for the ending part"					
				
				newPlan = find_plan(currentGoalState, goalState)
				
				if newPlan != False:
					# Got a plan, append it at the end
					print newPlan
					print
					modifiedPlan.extend(newPlan)
				else:
					print 'Could not find a suitable plan for the ending part'
					print
					successFlag = False
	
		return modifiedPlan, successFlag
		
	# Check for exact similar location
	def __isSimilar(self, state1, state2):	

		if state1.loc[state1.target] != state2.loc[state1.target]:
			return False
				
		return True
			