import sys
from state import State 

# This class check the similarity between two states for our problem domain
class StateSimilarity:

	def __init__(self, name):
		self.__name = name
		
	# Similarity check function
	# We give which property we are looking for with the states and the similarity matrix
	def getSimilarityValue(self, propName, state1, state2, similarityMatrix):
		# Returns a value between 0(no similarity) and 1(exact similar)
		pair1 = getattr(state1, propName)
		pair2 = getattr(state2, propName)		
		
		key1 = pair1.keys()[0]
		value1 = pair1[key1]
		
		key2 = pair2.keys()[0]
		value2 = pair2[key2]
		
		# If both state has same value, proper match return 1
		if key1 == key2 and value1 == value2:
			value = 1
			
		elif propName == 'loc':	
			# We are looking for similarity with location, look at the similarity matrix
			matrix = State("matrix")
			exec("matrix." + similarityMatrix[0])
			
			try:
				# Look at the similarityMatrix[A][B]
				value = matrix.similarity[value1][value2]
			except KeyError:
				value = 0
				try:
					# Look at the similarityMatrix[B][A], as similarityMatrix[A][B] does not exist
					value = matrix.similarity[value2][value1]
				except KeyError:
					value = 0
						
		elif propName == 'cash':			
			if value1 < value2:
				# Goal state have more money, good job
				value= 1			
			else:
				# Returns the fraction how close the two states are
				value = 1.0 - ((value1 - value2) * 1.0 / value1)
		
		elif propName == 'time':			
			if value1 < value2:
				# Goal state have more time to spend
				value= 1			
			else:
				# Returns the fraction how close the two states are
				value = 1.0 - ((value1 - value2) * 1.0 / value1)
				
		return value
	
	
