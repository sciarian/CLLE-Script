###############################################
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
		else:
			return table_row + ' : U' 
	##########
	#Function# ~ Find min year in publication section.
	##########
	def min_pub_yr(self):	
		#Search for all years

		#TODO Modify RE to work for (####) and ####
	
		yr_19 = re.findall('\(19\d{2}\)' , str(self.page))
		yr_20 = re.findall('\(20\d{2}\)' , str(self.page))
		
		#Concatinate lists together
		result = yr_19 + yr_20 
	
		#Convert list to string
		result = map(self.sub_str,result)
		result = map(int, result)
	
		#Return result
		if len(result) is 0:
			return 'Earliest year from pub med : U'
		else:
			return 'Earliest year from pub med : ' + str(min(result))
	
	##########
	#Function# ~ Sub string function used to remove the parentheses around the years in publication
	##########   refereneces.
	def sub_str(self,str):
		return str[1:len(str)-1]
	
	##########
	#Function# ~ Find the min year in cell line collections TODO
	##########
	def min_clc_yr(self):
		
		#Grab cell line collections row from expasy page
		clc = ''
		for row in self.page.find_all('tr'):
			if str(row.th) != 'None':
				if str(row.th.string) == 'Cell line collections':
					clc = row
					break
		
		if clc == '':
			return 'Earliest year from cell line collections : U'

		#Append all the hyper links in cell line collections section
		links = []
		for link in clc.find_all('a'):
			print link.string
			links.append(link['href'])

		#Open each hyper link
		master_yr_list = []
		for url in links:
			try:
		        	url_req = requests.request('GET', url)
			except requests.exceptions.SSLError:
				print 'failed to connect to web page'
				continue			

       			url_page = BeautifulSoup(url_req.content,'html.parser')
		        yr_20 = []
		        yr_19 = []

		        #Scrape for years with regex
		        for tag in url_page.find_all('span'):
		     	        yr_19 += re.findall('19\d{2}', str(tag))
		      	        yr_20 += re.findall('20\d{2}', str(tag))

			#Sum all of the years together
	       		all_yr = []
		        all_yr = yr_19 + yr_20

		        #Convert elements of list from string -> int
	    		map(int, all_yr)

			#Append the minimum year if one exists
		        if len(all_yr) is not 0 :
		                master_yr_list.append(min(all_yr))

		#Print over all minimum year
		if len(master_yr_list) != 0:
		        return 'Earliest year from cell line collections : ' + min(master_yr_list)
		else:
			return 'Earliest year from cell line collections : U'	
		
	##########
	#Function# ~ Find the ethinicity in cell line collections TODO
	##########
	
######	
#Main# ~ Main function.
######
def main():

	####################
	# Acquire URL List #
	####################
	
	# How to look up cell line data for cellosaurus by URL!!!
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
			print obj.min_pub_yr()
			print obj.min_clc_yr()
			print '************************************************'			
#############
#Run Program#
#############				
if __name__ == '__main__':
	main()

#TODO - Search for ethnicity of each web page
#TODO - Find a way to determine what cell line it came from.
#TODO - Find out why we are getting super low years for when cells were extracted.
#TODO - Find out how to tab over to history section of ATCC websites.
	#GET HTML FOR ATTC PAGE AND SEE WHAT HAPPENS!
	#req = requests.request('GET' , 'https://www.atcc.org/Products/All/CRL-8303.aspx#generalinformation')
#TODO - Find out how to get year from ACC pages
	#Cell line with ACC

##############
#TESTING ZONE#
##############
#req = requests.request('GET' , 'https://web.expasy.org/cellosaurus/CVCL_2270')	
#page = BeautifulSoup(req.content, 'html.parser')
#print page  

