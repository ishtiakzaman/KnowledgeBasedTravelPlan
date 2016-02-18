import sys
from state import State
from state_similarity import StateSimilarity

class Retriever:

	# Initiate the module with case based file name and problem domain related info file
	def __init__(self, memoryPlanFileName, stateSimilarityFileName):		
		self.__memoryFileObject = self.__openFile(memoryPlanFileName)
		self.__stateSimilarityFileObject = self.__openFile(stateSimilarityFileName)
		self.__processFile(self.__memoryFileObject, 'plan_memory')
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
				
	# Returns the case that is closest the current and goal state
	def findClosestMatch(self, currentState, goalState):	
		
		# Initiate max similarity value with min threshold
		maxSimilarityValue = self.state_similarity[0]['threshold']
		retrievedCase = []		
		
		# Loop through all case based
		for plan in self.plan_memory:
			
			# Get the init and goal state from the case base memory
			currentStateList = plan[0][0]
			goalStateList = plan[0][1]
			
			goalStateMemory = State("goalStateMemory")
			currentStateMemory = State("currentStateMemory")
			#print 'goalStateList', goalStateList
			#print 'currentStateList', currentStateList
			
			for stateItem in currentStateList:						
				exec("currentStateMemory."+stateItem)
					
			for stateItem in goalStateList:	
				try:
					exec("goalStateMemory."+stateItem)
				except NameError:
					print stateItem
					sys.exit()
			
			# Calculate the similarity by adding the similarity between
			# 1. our goal state vs case based memory goal state
			# 2. our init state vs case based memory init state
			similarityValue = \
					self.__getSimilarityValue(currentState, currentStateMemory) \
					+ self.__getSimilarityValue(goalState, goalStateMemory)			
			
			#print "SIMILARITY VALUE", similarityValue			
			if similarityValue > maxSimilarityValue:
				# Store the case with biggest similarity value
				maxSimilarityValue = similarityValue
				retrievedCase = plan
			#print similarityValue
		
		return retrievedCase
				
	# Returns similarity value between two states
	def __getSimilarityValue(self, state1, state2):	
		value = 0
		# Loop through all properties of the states
		for properties in self.state_similarity[1]:			
			prop = properties.split(':')
			
			if hasattr(state1, prop[0]) and hasattr(state2, prop[0]):	
				# If both states have the property, get their similarity value
				value = value + self.__stateSimilarity.getSimilarityValue(prop[0], state1, state2, \
															self.state_similarity[2]) * int(prop[1])
				
		return value
				
				
				
			