#!/usr/bin/python
<<<<<<< HEAD
=======

>>>>>>> master
from bs4 import BeautifulSoup
import re
import fnmatch
import os
import unicodedata
import locale
import sys
import random
<<<<<<< HEAD
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

#Uses Riegel formula to find most recent race and calculate your new time from that.
def riegelClassify(athleteDataDict, inputDistance):
	sys.stdout = oldout
	distances = athleteDataDict.keys()
	i = 1
	old1980 = '12-28-1980'
	mostRecentRaceDate = datetime.strptime(old1980, "%m-%d-%Y")
	mostRecentRace = (0,0,mostRecentRaceDate)
	#get most recent race
	mostRecentDistance = 0
	mostRecentTime = 0
	for distance in distances:
		#find most recent race
		races = athleteDataDict[distance]
		for race in races:
			raceDate = datetime.strptime(race[2], "%m-%d-%Y") #struct_time
			if raceDate > mostRecentRaceDate:
				mostRecentDistance = distance
				mostRecentRaceDate = raceDate
				mostRecentTime =  convertTimeToSeconds(race[0])



	predTime = (mostRecentTime) * ((inputDistance / float(mostRecentDistance))**1.06)

	global classificationMap #see below where constructd. (fast, med, slow) times.
	#find the closest race value to this.
	keys = sorted(classificationMap.keys())
	closestKey = keys[0]
	curDist = sys.maxint
	for key in keys:
		if (key - inputDistance) < curDist:
			curDist = (inputDistance - key)
			closestKey = key
	
	print "closest distance we have preprogrammed data for:",closestKey
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

	print "Predicted time for",inputDistance,convertSecondsToTime(predTime)
	print "plan: ",fitness
	return (predTime, fitness)
=======
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

#Changes to directory of the dataCruncher file
rootDir = os.path.dirname(os.path.realpath(__file__))
>>>>>>> master


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
<<<<<<< HEAD
					if 'Meter' not in numberArr[1]:
						number *= 1609
=======
>>>>>>> master
				else:
					#print numberArr[0],"discarded"
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

<<<<<<< HEAD
=======

def convertTimeToSeconds(time):
	seconds = 0.0
	for i, part in enumerate(reversed(time.split(":"))):
		seconds += float(part) * (60**i)
	return seconds

>>>>>>> master
class DataCruncher():

	def __init__(self):
		dataFolder = os.path.join(rootDir, "Data")
		menFolder = os.path.join(dataFolder, "Men")
<<<<<<< HEAD
		print menFolder
		#womenFolder = os.path.join(dataFolder, "Women")
		self.athleteNameDict = dict()
		self.getAthleteDataInFolder(menFolder)
		# global classificationMap
		# raceDistances = self.athleteNameDict.keys()



		#print self.athleteNameDict.keys()
		#getAthleteDataInFolder(womenFolder, athleteNameDict)	

	def getAthleteDistances(athleteName):
		distances = []
		for raceDistance in self.athleteNameDict[athleteName].keys():
			distances.append(raceDistance)
		return distances
=======
		#womenFolder = os.path.join(dataFolder, "Women")

		self.athleteNameDict = dict()
		self.getAthleteDataInFolder(menFolder)
		#getAthleteDataInFolder(womenFolder, athleteNameDict)

>>>>>>> master

	def getFastestTimesOverDistance(self, name, distance):
		if name not in self.athleteNameDict:
			raise Exception("Athlete with that name not found")
		if distance not in self.athleteNameDict[name]:
			raise Exception("Athlete has not run that race")
<<<<<<< HEAD
		return max(convertTimeToSeconds(race[0]) for race in self.athleteNameDict[name][distance])

	def printForPurpose(self, isOracle = True):
		#f = open('output_blanked.txt','w'); sys.stdout = f
		random.seed(2)
		for name in self.athleteNameDict:
			if isOracle:
				fileName = str(name) +'_blanked.txt'
			else:
				fileName = str(name) + '_predicted.txt'
			f = open(fileName, 'w'); sys.stdout = f
			print name

			predictDistance = ""
			predictIndex = random.randint(0, len(self.athleteNameDict[name])-1)
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
				(predTime, difficultyLevel) = riegelClassify(self.athleteNameDict[name], predictDistance)
				sys.stdout = f
				print "Predicted time for the",predictDistance,":*",predTime
				print "Training plan level: *",difficultyLevel


		f.close()


	def getAthleteDataInFolder(self, folder):
		dataDict = self.athleteNameDict
=======
		return min(convertTimeToSeconds(race[0]) for race in self.athleteNameDict[name][distance])

	def getNames(self):
		return self.athleteNameDict.keys()

	def getDistancesForName(self, name):
		return self.athleteNameDict[name].keys()

	def printHistoryWithBlanks(self):
		f = open('output_blanked.txt','w'); sys.stdout = f
		random.seed()
		for name in self.athleteNameDict:
			print "Name*", name

			blank_index = random.randint(0, len(self.athleteNameDict[name])-1)
			for i, distance in enumerate(self.athleteNameDict[name]):
				if blank_index == i:
					print "Predict the time for the", distance, " here: *  "
					continue
				print "Distance*", distance
				for i, race in enumerate(self.athleteNameDict[name][distance]):
					print "Race *",race[1], "* Time*", race[0], "*Date* ", race[2]
		f.close()

	def getAthleteDataInFolder(self, folder):
		dataDict = self.athleteNameDict

>>>>>>> master
		files = listdir_nohidden(folder)
		for i in range(len(files)):
			thisFile = os.path.join(folder, files[i])
			filePtr = open(thisFile)
			soup = BeautifulSoup(filePtr, 'html.parser')
			(athleteName, athleteData) = mapDataForRaceList(soup)
			dataDict[athleteName] = athleteData

<<<<<<< HEAD
d = DataCruncher()
#classificationMap is map of distances -> (fast, intermediate, slow) times. (tuples)
global classificationMap
classificationMap[400] = (convertTimeToSeconds('48.5'),convertTimeToSeconds('54.0'),convertTimeToSeconds('60.0'))
classificationMap[800] = (convertTimeToSeconds('1:50.0'),convertTimeToSeconds('1:55'),convertTimeToSeconds('2:00.0'))
classificationMap[1600] = (convertTimeToSeconds('3:59.9'),convertTimeToSeconds('4:20.0'),convertTimeToSeconds('4:40.0'))
classificationMap[3200] = (convertTimeToSeconds('8:40.0'),convertTimeToSeconds('9:00.0'),convertTimeToSeconds('9:20.0'))
classificationMap[5000] = (convertTimeToSeconds('14:59.0'),convertTimeToSeconds('15:30.0'),convertTimeToSeconds('16:00.0'))
classificationMap[10000] = (convertTimeToSeconds('30:00.0'),convertTimeToSeconds('32:30.0'),convertTimeToSeconds('34:00.0'))
d.printForPurpose(False)
# athleteData = d.athleteNameDict
#d.printHistory()
=======


#d = DataCruncher()
#d.printHistoryBlanked()
>>>>>>> master
