
'''
	Defines a Hidden Markov chain of probabilities

'''
class HMM():
	def __init__():
		self.probs = dict()

	'''
		@param node: the position in the HMM we are training
		@param dataset: a dictionary of training values {g,r},
			where we traing p(g) and p(r|g)
		sets self.probs(g) based on this single link
	'''
	def trainLink(node, dataset):
		if node not in dataset:
			self.probs[node] = dict()
		for g in dataset:
			r = dataset[g]
