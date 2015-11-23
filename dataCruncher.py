#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import fnmatch
import os
import unicodedata
import locale
import sys
import random
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

#Changes to directory of the dataCruncher file
rootDir = os.path.dirname(os.path.realpath(__file__))


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


def convertTimeToSeconds(time):
	seconds = 0.0
	for i, part in enumerate(reversed(time.split(":"))):
		seconds += float(part) * (60**i)
	return seconds

class DataCruncher():

	def __init__(self):
		dataFolder = os.path.join(rootDir, "Data")
		menFolder = os.path.join(dataFolder, "Men")
		#womenFolder = os.path.join(dataFolder, "Women")

		self.athleteNameDict = dict()
		self.getAthleteDataInFolder(menFolder)
		#getAthleteDataInFolder(womenFolder, athleteNameDict)


	def getFastestTimesOverDistance(self, name, distance):
		if name not in self.athleteNameDict:
			raise Exception("Athlete with that name not found")
		if distance not in self.athleteNameDict[name]:
			raise Exception("Athlete has not run that race")
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

		files = listdir_nohidden(folder)
		for i in range(len(files)):
			thisFile = os.path.join(folder, files[i])
			filePtr = open(thisFile)
			soup = BeautifulSoup(filePtr, 'html.parser')
			(athleteName, athleteData) = mapDataForRaceList(soup)
			dataDict[athleteName] = athleteData



#d = DataCruncher()
#d.printHistoryBlanked()