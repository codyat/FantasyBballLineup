#!/usr/bin/env python3

###########################################################
### Script was written to automatically set your lineup
###      Author: Cody Troyer
###      Date: January 23, 2018
###
###      Version: 1.1
###########################################################

#################################################
###   Changelog
#################################################
# v1.0    Initial Release
# v1.1    Removed hardcoded values for public access
#
#################################################

import sys
import time
import smtplib
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

class AutoLineup(unittest.TestCase):
	# Sets up the chrome driver
	def setUp(self):
		options = Options()
		options.add_argument("--start-maximized")
		self.driver = webdriver.Chrome(chrome_options=options)
		self.driver.get("http://www.espn.com/fantasy/basketball/")

	# Gets the owners name from the page
	def getOwnerName(self):
		return WebDriverWait(self.driver,10).until(lambda driver: self.driver.find_element_by_xpath('//*[@id="content"]/div/div[4]/div/div/div[3]/div[1]/div[2]/div[1]/ul[2]/li[1]')).get_attribute('innerHTML')

	# Gets the team name from the page
	def getTeamName(self):
		 return WebDriverWait(self.driver,10).until(lambda driver: self.driver.find_element_by_class_name('team-name')).get_attribute('innerHTML').split('<e', 1)[0]

	# Gets the league name from the page
	def getLeagueName(self):
		return WebDriverWait(self.driver, 10).until(lambda driver: self.driver.find_element_by_xpath('//*[@id="content"]/div/div[4]/div/div/div[3]/div[1]/div[2]/div[1]/ul[1]/li/a')).get_attribute('innerHTML').split('<strong>', 1)[1].split('</strong>', 1)[0]

	# Gets today's Date
	def getDate(self):
		return WebDriverWait(self.driver, 10).until(lambda driver: self.driver.find_element_by_class_name("date-on").find_element_by_xpath(".//div").text)

	# Prints a header with Owner's name, Team's name and League's name 
	def printHeader(self):
		print("Looking at", self.getOwnerName() + "'s Team")
		print("{:=^60}".format(""))
		print("Team:", self.getTeamName())
		print("League:", self.getLeagueName())
		print("{:=^60}".format(""))
		print()

	# Sends email notifiying user that the script was able to fit all players in the lineup OR if not, notify the user of which players could NOT be added due to scheduling confict or injuries
	def sendEmail(self):
		print("Sending email...")
		emailServer = smtplib.SMTP('smtp.gmail.com', 587)
		emailServer.ehlo()
		emailServer.starttls()

		email = self.NOTIF_EMAIL 
		password = self.NOTIF_EMAIL_PW

		recipientEmail = str(self.EMAIL)

		emailServer.login(email, password)

		emailBody = '\nHey ' + self.getOwnerName().split(' ')[0] + ',\nYour lineup has been set for ' + self.getDate() + ' for ' + self.getTeamName()[:-1] + '.\n\nYour Lineup currently looks like ' 
		
		lineup = "\nPG     -  " + optimalLineup["PG"] + "\nSG     -  " + optimalLineup["SG"] + "\nSF     -  " + optimalLineup["SF"] + "\nPF     -  " + optimalLineup["PF"] + "\nC       -  " + optimalLineup["C"] + "\nG       -  " + optimalLineup["G"] + "\nF       -  " + optimalLineup["F"] + "\nUTIL  -  " + optimalLineup["UTIL1"] + "\nUTIL  -  " + optimalLineup["UTIL2"] + "\nUTIL  -  " + optimalLineup["UTIL3"]

		bench = ""
		for i in benched:
			bench = bench + "\nBench -  " + i[0] 
			if i[1]: bench += "	         (injured)"
			if i[2]: bench += "	         (playing today)"
			
		emailBody = emailBody + lineup + '\n\n And your bench currently looks like ' + bench

		emailServer.sendmail(email, recipientEmail, 'Subject: Lineup Set! ' + self.getLeagueName() + '\n' + emailBody)
		emailServer.quit()
		print("Sent.")

	# Removes players that are not scheduled to play in todays matches from the total players list
	def removePlayersNotPlaying(self):
		global playerList
		playerList = players[:]
		playerList2Remove=[]
		for i in players:
			if not i[3]: playerList2Remove.append(i)
			elif i[2]:   playerList2Remove.append(i)
		
		for i in playerList2Remove:
			playerList.remove(i)

	# Checks all rows of the standard clubhouse roster view and generates a list of all players in your roster
	def generatePlayerList(self):
		driver = self.driver

		global players	
		players = []
		PlayerRows = driver.find_elements_by_class_name("pncPlayerRow")
		for i in PlayerRows:
			player = []

			# add player name
			s=i.find_element_by_xpath(".//td[2]").text
			if s.replace(" ", "") != "":
				player.append(i.find_element_by_xpath(".//td[2]/a[1]").text)

				# add player position
				positions=[]
				for j in ' '.join(i.find_element_by_xpath('.//td[2]').text.split(',')[1:]).split(' ')[2:]:
					for k in ["PG","SG","PF","SF","C"]:
						if k in j:
							positions.append(k)
				player.append(positions)
						
				# add player injured
				inj = i.find_element_by_xpath(".//td[2]").text.split(' ')[-1]
				player.append(inj == "D" or inj == "DTD" or inj == "O" or inj == "P" or inj == "IR")
	
				# add player playing today
				player.append(i.find_element_by_xpath(".//td[6]").text != "")
				
				# add player roster number
				player.append(i.find_element_by_xpath(".//td[3]/div[2]").get_attribute("id"))
				players.append(player)
		
		self.removePlayersNotPlaying()

	# Creates a list of all the players left on the bench
	def generateBenchedList(self):
		global benched
		benched = []
		for i in self.driver.find_elements_by_class_name("pncPlayerRow"):
			if i.get_attribute("id") != "pncEmptyRow" and i.find_element_by_xpath(".//td[1]").text == "Bench":
				player = []
				name = i.find_element_by_xpath(".//td[2]").text
				if name.replace(" ", "") != "":
					player.append(i.find_element_by_xpath(".//td[2]/a[1]").text)
	
					# add player injured
					inj = i.find_element_by_xpath(".//td[2]").text.split(' ')[-1]
					player.append(inj == "D" or inj == "DTD" or inj == "O" or inj == "P" or inj == "IR")

					# add player playing today
					player.append(i.find_element_by_xpath(".//td[6]").text != "")
					
					benched.append(player)		

	# Narrows down the playerlist by the number of positions the players play
	def narrowPlayersByPos(self, num):
		tempPlayers=[]
		for i in playerList:
			if len(i[1]) == num:
				tempPlayers.append(i)
		return tempPlayers
	
	# narrows down playerlist by removing the players that have already been placed in the optimal lineup
	def narrowPlayersByPlayersLeft(self, optimalLineup):
		tempPlayers = playerList[:]
		for i in optimalLineup:
			for j in playerList:
				if optimalLineup[i] == j[0]:
					tempPlayers.remove(j)
		return tempPlayers

	# Creates an optimal lineup that will maximaze the number of players in your lineup
	def optimizeLineup(self):
		driver = self.driver
		global optimalLineup
		slots = driver.find_elements_by_class_name("playerSlot")
		optimalLineup = {}

		for i in slots:
			if i.text != "Bench" and i.text != "UTIL": 
				optimalLineup[i.text] = ""
		optimalLineup["UTIL1"] = ""
		optimalLineup["UTIL2"] = ""
		optimalLineup["UTIL3"] = ""

		# Fill positions PG, PF, SF, SG, C 
		for it in range(1,3,1):
			slots2Remove = []
			playerList2Remove = []
			narrowPlayers = self.narrowPlayersByPos(it)
			for i in slots:
				if i.text != "Bench":
					for j in narrowPlayers:
						if i.text in j[1]:	
							if j not in playerList2Remove:
								optimalLineup[i.text] = j[0]
								slots2Remove.append(i)
								playerList2Remove.append(j)
								break
			for i in slots2Remove:
				slots.remove(i)

			for i in playerList2Remove:
				narrowPlayers.remove(i)
			
		# Now fill the G and F positions
		narrowPlayers = self.narrowPlayersByPlayersLeft(optimalLineup)
		
		for i in narrowPlayers:
			if "SG" in i[1] or "PG" in i[1]:
				optimalLineup["G"] = i[0]
				narrowPlayers.remove(i)
				break

		for i in narrowPlayers:
			if "SF" in i[1] or "PF" in i[1]:
				optimalLineup["F"] = i[0]
				narrowPlayers.remove(i)
				break

		# Now fill the Util Spots
		utilCount = 1
		playerList2Remove = []
		for i in narrowPlayers:
			if utilCount < 4:
				optimalLineup["UTIL"+str(utilCount)] = i[0]
				playerList2Remove.append(i)
				utilCount += 1
			else:
				break

		for i in playerList2Remove:
			narrowPlayers.remove(i)

	# Moves all players to the bench so there's not conflict with button mappings
	def moveAllPlayersToBench(self):
		driver = self.driver
		wait = WebDriverWait(driver, 10)
		print("Benching all players...")

		count = 0
		for i in driver.find_elements_by_class_name("pncPlayerRow"):
			pos = i.find_element_by_xpath(".//td[1]").text
			if pos != "Bench" and pos.replace(" ", "") != "":
				if i.find_element_by_xpath(".//td[2]").text.replace(" ", "") != "":
					count += 1
					
					moveButton = wait.until(lambda driver: i.find_element_by_class_name("pncButtonMove"))
					driver.execute_script("arguments[0].scrollIntoView();", moveButton)
					moveButton.click()
				
					# get last bench spot
					lastBench = driver.find_elements_by_class_name("pncButtonHere")[-1].get_attribute("id")

					hereButton = wait.until(lambda driver: driver.find_element_by_id(lastBench))
					driver.execute_script("arguments[0].scrollIntoView();", hereButton)
					hereButton.click()

		if count > 0: self.submitLineup()

		self.driver.refresh()
		time.sleep(3)

	# moves optimalLineup players from the bench to their positions in the lineup
	def setLineup(self):
		driver = self.driver
		print("Setting Lineup...")

		utilCount = 1
		for i in driver.find_elements_by_class_name("pncPlayerRow"):
			name = i.find_element_by_xpath(".//td[2]").text
			if name.replace(" ", "") != "":
				name = i.find_element_by_xpath(".//td[2]/a[1]").text

			pos = i.find_element_by_xpath(".//td[1]").text
			if pos != "Bench":
				if pos == "UTIL" and utilCount < 4:
					pos += str(utilCount)
					utilCount += 1

				if pos != "UTIL" and optimalLineup[pos] != "":
					if name != optimalLineup[pos]:
						print("Moving", optimalLineup[pos], "to", pos + "...")
						self.movePlayer(self.name2ButtonID(optimalLineup[pos]), i)
		self.submitLineup()
		print()

	# Takes in a name (ie "Kobe Bryant") and returns his buttonID (ie moveButton_12832)
	def name2ButtonID(self, name):
		for j in playerList:
			if j[0] == name:
				return j[4]
		return ""

	# Clicks the button with the Move ID (mid) to the playerRow passed in
	def movePlayer(self, mid, playerRow):
		if mid == "": return
		driver = self.driver
		wait = WebDriverWait(driver, 10)
	
		moveButton = wait.until(lambda driver: driver.find_element_by_id(mid))
		driver.execute_script("arguments[0].scrollIntoView();", moveButton)
		moveButton.click()

		hid = playerRow.find_element_by_xpath(".//td[3]").find_element_by_class_name("pncButtonHere").get_attribute("id")
		
		hereButton = wait.until(lambda driver: driver.find_element_by_id(hid))
		driver.execute_script("arguments[0].scrollIntoView();", hereButton)
		hereButton.click()
	
	# clicks the submit button
	def submitLineup(self):
		driver = self.driver
		wait = WebDriverWait(driver, 10)
	
		submitButton = wait.until(lambda driver: driver.find_element_by_id("pncSaveRoster1"))
		driver.execute_script("arguments[0].scrollIntoView();", submitButton)
		submitButton.click()
		time.sleep(2)

	# Clicks login button on ESPN Fantasy homepage and inserts your account info.
	def login(self):
		# initialize variables
		driver = self.driver
		wait = WebDriverWait(driver, 10)

		# click Log In button
		loginButtonXpath = "//*[@id='global-header']/div[2]/ul/li[2]/a"
		loginButtonElement1 = wait.until(lambda driver: driver.find_element_by_xpath(loginButtonXpath))
		loginButtonElement1.click()

		# find email and pass ID
		emailFieldID = "//*[@id='did-ui']/div/div/section/section/form/section/div[1]/div/label/span[2]/input"
		passFieldID = "//*[@id='did-ui']/div/div/section/section/form/section/div[2]/div/label/span[2]/input"
		
		# switch to frame so script can type
		time.sleep(1)
		driver.switch_to.frame("disneyid-iframe")
		
		# find email input box and type in email
		emailFieldElement = wait.until(lambda driver: driver.find_element_by_xpath(emailFieldID))
		emailFieldElement.click()
		emailFieldElement.clear()
		emailFieldElement.send_keys(str(self.USERNAME))

		# find pass input box and type in password
		passFieldElement = wait.until(lambda driver: driver.find_element_by_xpath(passFieldID))
		passFieldElement.click()
		passFieldElement.clear()
		passFieldElement.send_keys(str(self.PASSWORD))
		
		# click log in button
		loginButtonXpath2 = "//*[@id='did-ui']/div/div/section/section/form/section/div[3]/button[2]"
		loginButtonElement2 = wait.until(lambda driver: driver.find_element_by_xpath(loginButtonXpath2))
		loginButtonElement2.click()
		time.sleep(4)

		leagueURL = "http://games.espn.com/fba/clubhouse?leagueId=" + str(self.LEAGUEID) + "&teamId=" + str(self.TEAMID) + "&seasonId=" + str(self.SEASONID) #+ "&scoringPeriodId=106&view=stats&context=clubhouse"
		driver.get(leagueURL)
		time.sleep(4)

	def tearDown(self):
		self.driver.quit()

	def test_main(self):
		self.login()
		
		self.printHeader()
		self.generatePlayerList()
		self.optimizeLineup()
		self.moveAllPlayersToBench()
		self.setLineup()
		self.generateBenchedList()
		self.sendEmail()		

		self.tearDown()

if __name__ == '__main__':
	if len(sys.argv) > 1:
		AutoLineup.NOTIF_EMAIL_PW = sys.argv.pop()
		AutoLineup.NOTIF_EMAIL    = sys.argv.pop()
		AutoLineup.EMAIL          = sys.argv.pop()
		AutoLineup.PASSWORD       = sys.argv.pop()
		AutoLineup.USERNAME       = sys.argv.pop()
		AutoLineup.SEASONID       = sys.argv.pop()
		AutoLineup.TEAMID         = sys.argv.pop()
		AutoLineup.LEAGUEID       = sys.argv.pop()
	unittest.main()
