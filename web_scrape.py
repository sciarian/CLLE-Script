###############################################
#This program will run a script that will
#search for the age, gender, and year of the 
#earliest mention of a cell line. 
#
#@Author: Anthony Sciarini
#@Version: 5/30/2018
###############################################

#IMPORTED LIBS
import requests				#Used send HTTP request
from bs4 import BeautifulSoup	        #Used to process HTML documents

#########################
#	GET HTML PAGE	#
#########################

#Requests a HTTP page
req = requests.request('GET','https://web.expasy.org/cellosaurus/CVCL_1058')

#Grabs the HTML page that came from the HTML page
page = BeautifulSoup(req.content, 'html.parser')

#Prints HTML page
#print page

###TODO LIST###
#-GRAB AGE
#-GRAB GENDER
#-GRAB RACE
#-GRAB YEAR ***
###############

#########################
#	SCRAPE DOC	#
#########################

#------------------------------------
#Print out Synonyms, age, and sex
#------------------------------------

for row in page.find_all('th'):
	if row.string == 'Cell line name':
		print row.string
	if row.string == 'Synonyms':
		print row.string
	if row.string == 'Sex of cell':
		print row.string
	if row.string == 'Age at sampling':
		print row.string
	  
