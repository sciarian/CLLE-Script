################################################
#This program will run a script that will 
#search for the age, gender, and year of the 
#earliest mention of a cell line. 
#
#@Author: Anthony Sciarini
#@Version: 5/30/2018
################################################

###############
#IMPORTED LIBS#
###############
import requests				#Used send HTTP request
from bs4 import BeautifulSoup	        #Used to process HTML documents

##########################################################################################
#This class contains all the functions needed to scrap cell line info rom html documents.
##########################################################################################
class Cell_line_scraper:

	#############
	#Constructor# ~ This guy will take the http URL and convert it to HTML TODO
	#############
	def __init__(self, url):

		#Make HTTP request
		req = requests.request('GET', url)

		#Grab the HTML doc that came with request
		self.page = BeautifulSoup(req.content, 'html.parser')

	#########				
	#Funtion# ~ Look up the content stored at a table row
	#########
	def table_look_up(self, table_row):	
			
		#Loop through each row in the page's table
		for row in self.page.find_all('tr'):
			if str(row.th) != 'None':
				if str(row.th.string) == table_row:
					print row.th.string + ' : ' + row.td.contents[0].string	

##################################
####################  RUN PROGRAM 	
####################	  	    
####################		   
##################################

###Create Cell line scraper for document
obj = Cell_line_scraper("https://web.expasy.org/cellosaurus/CVCL_1058")

###Print cell info
obj.table_look_up('Cell line name')
obj.table_look_up('Synonyms')
obj.table_look_up('Sex of cell')
obj.table_look_up('Age at sampling')
