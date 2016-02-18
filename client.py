from retriever import Retriever
from modifier import Modifier
from state import State 
import pyhop

# Open a file given a file name and returns the file pointer
def openFile(fileName):
	try:
		fo = open(fileName, "r")
	except IOError:
		print "File", fileName, "cannot be read"
		sys.exit()
	return fo
	
# Main function from where program starts
if __name__ == '__main__':
	
	# Open the predefined problem domain related info file here
	fo = openFile('static_value.txt')	
	exec('content=' + fo.read())
	
	# Create the Retriever module, given case based memory file and 
	# problem domain related info file 
	rt = Retriever('generated_plan.txt', 'state_similarity.txt')
	
	# Create a current state and goal state to test our program
	
	# Create the current state here
	currentState = State('current')
	currentState.target = 'me'
	currentState.loc = {'me':'IU Campus', 'bus':'bus_stop_2'}
	currentState.cash = {'me':3050}	
	currentState.balance_bank = {'me':120}
	currentState.time = {'me':1820}
	currentState.nearest_bus_stop={'me': 'bus_stop_2'}
	# Put the domain related info into the state
	for stateItem in content:				
		exec("currentState."+stateItem)
	
	# Create the goal state here
	goalState = State('goal')
	goalState.loc = {'me':'Paris'}
	goalState.cash = {'me':170}
	goalState.target = 'me'
	# Put the domain related info into the state
	for stateItem in content:		
		exec("goalState."+stateItem)
		
	# Print out basic information about the current and goal state
	print "Start location:", currentState.loc['me']
	print "Start cash:", currentState.cash['me']	
	print "Final location:", goalState.loc['me']
	print "Final cash:", goalState.cash['me']	
	print
		
	# Use the Retreiver module to get a closed match case
	# The returning case has source state, dest state and executed plan 
	retrievedCase = rt.findClosestMatch(currentState, goalState)
	
	
	if len(retrievedCase) > 0:		
		# Get the plan part of the case
		retrievedPlan = retrievedCase[1]
		print 'Retrieved plan:', retrievedPlan
	else:
		print 'No match found'
	print
		
	# Create the Modifier module, given the problem domain related info file 
	modifier = Modifier('state_similarity.txt')
	
	# Use the Modifier module to get a modified plan
	# Current state, goal state and the retrieved case(with source state, dest state, plan) is passed
	modifiedPlan, successFlag = modifier.modifyPlan(currentState, goalState, retrievedCase)
	
	# We see whether the modifier could modify to a better plan
	if successFlag == True:
		print "Modified Plan:", modifiedPlan
	else:
		# Modifier could not fully modify the plan to match our goal state, partially modified plan
		# is shown here
		print "Closest Plan found:", modifiedPlan