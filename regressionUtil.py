
#Used for one-dimensional gradient of squared loss
def calculateLossGradient(weight, distance, time):
	return 2 * (weight * distance - time)

def  updateWeight(weight, distance, time)
	return weight - 