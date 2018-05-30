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

#Grabs the HTML page that came from the request
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

#--------------------------------------------------------
#Look up each attribute in the expasy table by table row
#--------------------------------------------------------

#Loop through each row on the expasy table
for row in page.find_all('tr'):

	#Makes sure the row is not blank
	if str(row.th) != 'None':

		#Print the cell line
		if row.th.string == 'Cell line name':
			print row.th.string + ' : ' + row.td.contents[0].string

		#Print the Synonyms for he cell
		if row.th.string == 'Synonyms':
			print row.th.string + ' : ' + row.td.contents[0].string
	
		#Print the Sex of the cell
		if row.th.string == 'Sex of cell':
			print row.th.string + ' : ' + row.td.contents[0].string
		
		if row.th.string == 'Age at sampling':
			print row.th.string + ' : ' + row.td.contents[0].string
