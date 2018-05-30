###############################################
#This program will run a script that will
#search for the age, gender, and year of the 
#earliest mention of a cell line. 
#
#@Author: Anthony Sciarini
#@Version: 5/30/2018
###############################################

#IMPORTED LIBS
import requests		#Used send HTTP request
import BeautifulSoup	#Used to process HTML documents

#########################
#	GET HTML PAGE	#
#########################

#Requests a HTTP page
req = requests.request('GET','https://web.expasy.org/cellosaurus/CVCL_1058')

#Grabs the HTML page that came from the HTML page
page = BeautifulSoup.BeautifulSoup(req.content)

#Prints the page
print page

