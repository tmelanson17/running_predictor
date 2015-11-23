import dataCruncher
import collections
import math 

'''
 Steps:
 1. Feature vector that takes distance and raises to an exponent
 2. Linear regression (gradientLoss = 2(f(x)-y)fa(x) = 2(a*phi(x)-y)phi(x)
'''


class LinearDistanceRegression():

    def __init__(self, eta):
        self.eta = eta
        self.a = {"Distance":0}
        self.b = {"Distance":1.00}


    def dotProduct(self, d1, d2):
        """
        @param dict d1: a feature vector represented by a mapping from a feature (string) to a weight (float).
        @param dict d2: same as d1
        @return float: the dot product between d1 and d2
        """
        if len(d1) < len(d2):
            return self.dotProduct(d2, d1)
        else:
            return sum(d1.get(f, 0) * v for f, v in d2.items())

    def exponentFeatureExtractor(self, inputs, exponent):
        '''
        @param dict inputs: the set of inputs to turn into features
        @param float exponent: the power with which to raise all the inputs for the features
        @return dict: the features of every value in input raised to exponent
        '''

        returnMap = dict()
        for i in inputs:
            returnMap[i] = inputs[i] ** exponent[i]
        return returnMap

    def logFeatureExtractor(self, inputs, multiplier):
        '''
        @return dict: the log (base e) of each feature multiplied by A value
        '''
        returnMap = dict()
        for i in inputs:
            returnMap[i] = math.log(inputs[i]*multiplier[i])
        return returnMap

    #Does linear regression with squared loss
    def absoluteLossRegression(self, weight, phi, y, yhat, eta):
        '''
        @param dict weight: the sparse vector of weights to adjust
        @param dict x: the input
        @param float y: the time
        @param eta: the step size
        @return void
        ''' 

        for i in weight:
            delta = phi[i] if yhat - y > 0 else -1*phi[i]
            weight[i] = weight[i] - eta * delta


    def calculateA(self, distance, time, eta):
        '''
        @return dict: the weight value of a for ax^b
        '''
        phi = self.exponentFeatureExtractor(distance, self.b)
        yhat = self.dotProduct(self.a, phi)
        self.absoluteLossRegression(self.a, phi, time, yhat, eta)

  
    def calculateB(self, distance, time, eta):

 
        phi = self.logFeatureExtractor(distance, self.a)
        yhat = self.dotProduct(self.b, phi)
        self.absoluteLossRegression(self.b, phi, time, yhat, eta)


    def train(self, distances, times, eta):

        yAVals = [time for time in times]
                #distances = dc.getDistancesForName(n)
        yBVals = [math.log(time) for time in times] #[dc.getFastestTimesOverDistance(n, d) for d in distances]
   
        for i in range(len(distances)):
            self.calculateA(distances[i], yAVals[i], 0.0000027)
            self.calculateB(distances[i], yBVals[i], 0.001)

    '''
        @param dataset -- a list of names with distances
        Adjusts the eta hyperparameter to minimize data loss
    '''
    def validate(self, dataCruncher):

        deltas = list()
        eta = 0.00000027

        
        for n in dataCruncher.getNames():
            self.a = {"Distance": 0}
            self.b = {"Distance": 1.0}
            xSet = [{"Distance": d} for d in dataCruncher.getDistancesForName(n)]
            ySet = [dataCruncher.getFastestTimesOverDistance(n, d) for d in dataCruncher.getDistancesForName(n)]

            self.train(xSet, ySet, eta)
    
            eightKTime = int(self.dotProduct(self.a, self.exponentFeatureExtractor({'Distance': 8000}, {"Distance":1.00})))
            actualTime = int(dataCruncher.getFastestTimesOverDistance(n, 8000))

            currentDelta = float(abs(eightKTime - actualTime)) / actualTime

            print n
            print "s value:", self.a
            print "E value:", self.b
            print "Eta:", eta
            print "Error", currentDelta

            deltas.append((currentDelta, eta, self.a))


        minDelta, self.eta, _ = min(deltas)

        print "Minimum total error:", minDelta
        print "Computed eta:", self.eta

ldr = LinearDistanceRegression(0.01)
ldr.validate(dataCruncher.DataCruncher())
