################################################
#
# This program will run a script that will 
# search for the age, gender, and year of the 
# earliest mention of a cell line. 
#
# @Author: Anthony Sciarini
# @Version: 5/31/2018
#
################################################

###############
#IMPORTED LIBS#
###############
import sys				#System commands lib
import requests				#HTTP request lib
import re				#Regular Expression lib
import csv				#Comma seperated values lib
from bs4 import BeautifulSoup	        #Process HTML documents lib

##########################################################################################
#This class contains all the functions needed to scrap cell line info rom html documents.
##########################################################################################
class Cell_scraper:

	#############
	#Constructor# ~ This guy will take the http URL and grab the HTML page it leads to.
	#############
	def __init__(self, url):

		#Make HTTP request
		req = requests.request('GET', url)

		#Grab the HTML that contains the search results for the cell
		self.results_page = BeautifulSoup(req.content, 'html.parser')

		# ~ Find the first hyper link
		first_link = self.results_page.find('tr')
		next_url = 'https://web.expasy.org/' + first_link.a['href']		
		
		# ~ Get HTML page that the first hyper link leads to.
		req = requests.request('GET', next_url)		
		self.page = BeautifulSoup(req.content, 'html.parser')

	#########				
	#Funtion# ~ Look up the content stored at a table row.
	#########
	def table_look_up(self, table_row):	
			
		#Loop through each row in the page's table
		for row in self.page.find_all('tr'):
			if str(row.th) != 'None':
				if str(row.th.string) == table_row:
					return row.th.string + ' : ' + row.td.contents[0].string
	##########
	#Function# ~ Find min year in publication section
	##########
	def find_min_pub(self):
		return 'nothing!'
	
	##########
	#Function# ~ Find the min year in cell line collections TODO
	##########

	##########
	#Function# ~ Find the ethinicity in cell line collections TODO
	##########

######
#Main# ~ Main function.
######
def main():

	####################
	#Acquire URL List#
	####################
	
	###How to look up cell line data for cellosaurus by URL!!!
	# https://web.expasy.org/cgi-bin/cellosaurus/search?input=your_query	

	#Opening a the cell_lines xcell spread sheet
	with open('cell_lines.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		
		#Query template
		query_url = 'https://web.expasy.org/cgi-bin/cellosaurus/search?input='
	
		#List to contain the queries
		query_list = []

		#Make a query for each cell line and add it to the query list
		for row in reader:
         		query_list.append(query_url + row['Cell line primary name'])

		#Print basic info for each cell
		for query in query_list:
			obj = Cell_scraper(query)
			print obj.table_look_up('Cell line name')
			print obj.table_look_up('Synonyms')
			print obj.table_look_up('Sex of cell')
			print obj.table_look_up('Age at sampling')
			print '************************************************'			
#############
#Run Program#
#############				
if __name__ == '__main__':
	main()
