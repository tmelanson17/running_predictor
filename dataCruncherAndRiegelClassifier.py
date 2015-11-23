#!/usr/bin/python
from bs4 import BeautifulSoup
import re
import fnmatch
import os
import unicodedata
import locale
import sys
import random
import riegelClassifier
#import datetime
from datetime import datetime
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 
oldout = sys.stdout

#Changes to directory of the dataCruncher file
rootDir = os.path.dirname(os.path.realpath(__file__))
global classificationMap
classificationMap = dict()

def convertTimeToSeconds(time):
		seconds = 0.0
		timeArr = time.split(":")
		(hours, minutes, seconds) = (0,0,0)
		if len(timeArr) == 3: #hh:mm:ss.ms
			(hours, minutes, seconds) = tuple(timeArr)
		elif len(timeArr) == 2:
			(minutes, seconds) = tuple(timeArr)
		elif len(timeArr) == 1:
			seconds = timeArr[0]
		return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
		# for i, part in enumerate(reversed(time.split(":"))):
		# 	seconds += float(part) * (60**i)
		return seconds

def convertSecondsToTime(inputTimeInSeconds):
	minutes = int(inputTimeInSeconds // 60)
	hours = int(inputTimeInSeconds // (3600))
	seconds = inputTimeInSeconds % 60.0
	(hours, minutes) = (str(hours), str(minutes))
	secondsTime = seconds
	seconds = "{:.2f}".format(seconds)
	if secondsTime < 10:
		seconds = '0' + seconds
	if int(hours) > 0:
		timeString = hours + ":" + minutes + ":" + seconds
	elif int(minutes) > 0:
		timeString = minutes + ":" + seconds
	else:
		timeString = str(seconds)
	return timeString

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def listdir_nohidden(path):
    arr = os.listdir(path)
    newArr = []
    for f in arr:
        if not f.startswith('.'):
            newArr.append(f)
    return newArr

def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]


#Uses Riegel formula to find most recent race and calculate your new time from that.
#Also uses a rule-of-thumb classification map for training plan intensity.
def riegelClassify(athleteName, inputDistance, dataCrunchObject):
	sys.stdout = oldout
	(mostRecentRace, mostRecentDistance) = dataCrunchObject.getMostRecentRaceForAthlete(athleteName)
	mostRecentTime = mostRecentRace[0]
	#print mostRecentTime, inputDistance, mostRecentDistance
	predTime = (mostRecentTime) * ((inputDistance / float(mostRecentDistance))**1.06)
	global classificationMap #see below where constructed. (fast, med, slow) times.
	#find the closest race value to this.
	keys = sorted(classificationMap.keys())
	closestKey = keys[0]
	curDist = sys.maxint
	for key in keys:
		if (key - inputDistance) < curDist:
			curDist = (inputDistance - key)
			closestKey = key
	
	thisRaceSpeed = inputDistance / float(predTime) #meters/second
	raceSpeeds = [(closestKey / float(time)) for time in classificationMap[closestKey]]
	(fastRaceSpeed, medRaceSpeed, slowRaceSpeed) = tuple(raceSpeeds)

#find the closest race speed, look at predicted time.
	
	if thisRaceSpeed >= fastRaceSpeed:
		fitness = 'fast; hard training plan'
	elif thisRaceSpeed <= slowRaceSpeed:
		fitness = 'beginner; easy training plan'
	else:
		fitness = 'medium; intermediate training plan'
	#print "\nPredicted time for",inputDistance,convertSecondsToTime(predTime)
	#print 'Based on this predicted time, we think you can train at this level:',
	#print fitness,"\n"

	return (predTime, fitness)


def mapDataForRaceList(soup, stripText = True): #returns tuple of (athlete name, dictionary of race results)
	athleteName = soup.h1.string
	raceList = soup.find_all('h3')
	raceDict = dict()
	for race in raceList:
		raceName = race.get_text()
		raceName = raceName.encode('ascii','ignore')
		if raceName == "Events":
			continue
		if raceName == "Athlete Info":
			break

		if(stripText):
			if('One Mile' in raceName):
				number = 1609
			elif('Two Mile' in raceName):
				number = 1609 * 2
			elif('Three Mile' in raceName):
				number = 1609 * 3
			elif('Four Mile' in raceName):
				number = 1609 * 4
			elif('Five Mile' in raceName):
				number = 1609 * 5
			else:
				numberArr = (raceName.split()) #race name
				if 'x' not in numberArr[0]:
					number = locale.atoi(numberArr[0])
					if 'Meter' not in numberArr[1]:
						number *= 1609
				else:
					#discard the weird 2.x, 3.x races
					continue
			raceName = number

		allTimesTuples = []
		for sib in race.next_siblings: #There is only one 'sibling' so this loop runs once only. Don't think too hard about it. 
			if str(type(sib)) == '<class \'bs4.element.Tag\'>':
				raceData = sib.get_text()
				raceData = raceData.encode('ascii','ignore')
				allTimes = raceData.split('\n') 
				allTimes = [(x.strip(' ')).rstrip() for x in allTimes]
				allTimes = filter(None, allTimes) #take out empty strings from the list
				chunky = chunks(allTimes, 3)
				for elem in chunky:
					allTimesTuples.append(tuple(elem))
				#for every ranking, read in a tuple of (time, location, date). Time in format mm:ss.ms and date in format mm-dd-yy.
				#allTimesTuples is a list of each result

		
		raceDict[raceName] = allTimesTuples
	return (athleteName, raceDict)

class DataCruncher():
	def __init__(self):
		dataFolder = os.path.join(rootDir, "Data")
		menFolder = os.path.join(dataFolder, "Men")
		print menFolder
		self.OLDRACE = (0, 0, '01-01-1980', "%m-%d-%Y") #time in s, location, date
		#womenFolder = os.path.join(dataFolder, "Women")
		self.athleteNameDict = dict()
		self.getAthleteDataInFolder(menFolder)
		#getAthleteDataInFolder(womenFolder, athleteNameDict)	

	#INPUTS: athlete name and distance.
	#OUTPUTS: the athlete's most recent race. Returns a duple of a tuple of the race (time, place, date) and the distance.
	#format ((time, place, date), distance)
	def getMostRecentRaceForAthleteAndDistance(self,athleteName, specifiedDistance):
		def getMostRecentRaceForDistance(athleteDataDict, distance):
			mostRecentRace = self.OLDRACE
			races = athleteDataDict[distance]
			for race in races:
				raceDate = datetime.strptime(race[2], "%m-%d-%Y") #struct_time
				mostRecentRaceDate = datetime.strptime(mostRecentRace[2], "%m-%d-%Y")
				if raceDate > mostRecentRaceDate:
					mostRecentRace = race
			return (convertTimeToSeconds(mostRecentRace[0]), mostRecentRace[1], mostRecentRace[2])

		athleteDataDict = self.athleteNameDict[athleteName]
		if not specifiedDistance:
			mostRecentRace = self.OLDRACE
			for distance in athleteDataDict.keys():
				mostRecentRaceForDistance = getMostRecentRaceForDistance(athleteDataDict = athleteDataDict, distance = distance)
				if mostRecentRaceForDistance[2] > mostRecentRace[2]:
					mostRecentRace = mostRecentRaceForDistance
					mostRecentDistance = int(distance)	
		else:
			mostRecentDistance = specifiedDistance
			mostRecentRace = getMostRecentRaceForDistance(athleteDataDict, specifiedDistance)
		return mostRecentRace, mostRecentDistance

	#INPUT: athlete's name
	#OUTPUT: athlete's most recent race, regardless of distance. 
	def getMostRecentRaceForAthlete(self, athleteName):
		return self.getMostRecentRaceForAthleteAndDistance(athleteName, specifiedDistance = None)

	#INPUT: athlete's name
	#OUTPUT: array of all distances an athlete has run.
	def getAthleteDistances(athleteName):
		distances = []
		for raceDistance in self.athleteNameDict[athleteName].keys():
			distances.append(raceDistance)
		return distances

	#INPUT: athlete's name, athlete's distance.
	#OUTPUT: Athlete's PR for this distance.
	def getFastestTimesOverDistance(self, name, distance):
		if name not in self.athleteNameDict:
			raise Exception("Athlete with that name not found")
		if distance not in self.athleteNameDict[name]:
			raise Exception("Athlete has not run that race")
		return max(convertTimeToSeconds(race[0]) for race in self.athleteNameDict[name][distance])

	def printForPurpose(self, isOracle = True):
		sprintError = 0
		distanceError = 0
		distancePreds = 0
		sprintPreds = 0
		perfectPreds = 0	
		random.seed(2)
		for name in self.athleteNameDict:
			if isOracle:
				fileName = str(name) +'_blanked.txt'
			else:
				fileName = str(name) + '_predicted.txt'
			f = open(fileName, 'w'); sys.stdout = f

			predictDistance = ""
			predictIndex = random.randint(0, len(self.athleteNameDict[name])-1)
			predictDistance = 0
			for i, distance in enumerate(sorted(self.athleteNameDict[name])):
				if predictIndex == i:
					predictDistance = distance
					continue
				if i is not 0:
					print "\n"
				print distance,"meters *Date*Race*"
				for i, race in enumerate(self.athleteNameDict[name][distance]):
					print race[0], "*", race[2], "*", race[1] 
			print "\n\n"

			if isOracle:
				print "Predict the time for the", predictDistance, " here: *  "
				print "Give a 6-week training plan for the",predictDistance,"below:\n*\n*"
			else:
				sys.stdout = oldout
				print name,
				(predTime, difficultyLevel) = riegelClassify(name, predictDistance, self)
				sys.stdout = f
				print "\nPredicted time for the",predictDistance,":*", convertSecondsToTime(predTime)
				print "Training plan level: *",difficultyLevel

				sys.stdout = oldout

				#print out erro rates
				realRaceData = self.getMostRecentRaceForAthleteAndDistance(name, predictDistance)
				print realRaceData
				realRaceTime = realRaceData[0][0]
				realRaceDate = realRaceData[0][2]
			#	print realRaceTime
			#	print predTime
				print "Race distance:",predictDistance
				print "Predicted time:",convertSecondsToTime(predTime)
				print "Actual time", convertSecondsToTime(realRaceTime), "run on", realRaceDate
				error = (realRaceTime - predTime) / float(realRaceTime)
				print "Error: ", error

				if predictDistance <=1000:
					sprintError += abs(error)
					sprintPreds += 1
				else:
					distanceError += abs(error)
					distancePreds += 1
				if error == 0:
					perfectPreds += 1
			f.close()
		sys.stdout = oldout
		totalError = sprintError + distanceError
		totalPreds = sprintPreds + distancePreds
		print "Average error %", (totalError) / float(totalPreds) * 100
		print "Sprint error %", (sprintError) / float(sprintPreds) * 100
		print "Distance error %", (distanceError) / float(distancePreds) * 100
		print "Perfect predictions ",perfectPreds

	def getAthleteDataInFolder(self, folder):
		dataDict = self.athleteNameDict
		files = listdir_nohidden(folder)
		for i in range(len(files)):
			thisFile = os.path.join(folder, files[i])
			filePtr = open(thisFile)
			soup = BeautifulSoup(filePtr, 'html.parser')
			(athleteName, athleteData) = mapDataForRaceList(soup)
			dataDict[athleteName] = athleteData


d = DataCruncher()
#classificationMap is map of distances -> (fast, intermediate, slow) times. (tuples)
global classificationMap
classificationMap[400] = (convertTimeToSeconds('48.5'),convertTimeToSeconds('54.0'),convertTimeToSeconds('60.0'))
classificationMap[800] = (convertTimeToSeconds('1:50.0'),convertTimeToSeconds('1:55'),convertTimeToSeconds('2:00.0'))
classificationMap[1600] = (convertTimeToSeconds('3:59.9'),convertTimeToSeconds('4:20.0'),convertTimeToSeconds('4:40.0'))
classificationMap[3200] = (convertTimeToSeconds('8:40.0'),convertTimeToSeconds('9:00.0'),convertTimeToSeconds('9:20.0'))
classificationMap[5000] = (convertTimeToSeconds('14:59.0'),convertTimeToSeconds('15:30.0'),convertTimeToSeconds('16:00.0'))
classificationMap[10000] = (convertTimeToSeconds('30:00.0'),convertTimeToSeconds('32:30.0'),convertTimeToSeconds('34:00.0'))
d.printForPurpose(isOracle = False)
i = 0
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Edward Cheserek', 10000)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Jonathan Green', 1500)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Joe Rosa', 4000)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Thomas Curtin', 3218)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Sean McGorty', 6000)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Pierce Murphy', 3200)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Patrick Tiernan', 1500)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Martin Hehir', 2000)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Marc Scott', 6436)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Malachy Schrobilgen', 6000)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Justyn Knight', 10000)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Grant Fisher', 1609)[0][0];i += 1
# print i,")",d.getMostRecentRaceForAthleteAndDistance('Shaun Thompson', 400)[0][0];i += 1
# athleteData = d.athleteNameDict
#d.printHistory()