##########################################################
#
# This program will run a script that will 
# search for the age, gender, and year of the 
# earliest mention of a cell line on the Expasy Database. 
#
# @Author: Anthony Sciarini
# @Version: 5/31/2018
#
##########################################################

###############
#IMPORTED LIBS#
###############
import sys				#System commands lib
import unicodedata			#Unicode lib
import requests				#HTTP request lib
import re				#Regular Expression lib
import csv				#Comma seperated values lib
from bs4 import BeautifulSoup	        #Process HTML documents lib

#############################################################################################
#
# This class contains the functions needed to use a script to search through HTML documents 
# retrived via the Expasy database for cancer cell line, and to grab various data about the 
# cell ine such as: Primary name, Aliases, Year of origin, Age of the individual the cells 
# were taken from, and the Ethnicity. If any of the previously mentioned data was not 
# available then the script will return 'NA'. When the script is run it opens a csv document
# containing all of the cell ine names and then uses that with a url qury template for the
# expasy database to search for each cell line on the database and grab whatever data is
# available for the cell line. 
#
# @Author Anthony Sciarin
# @Version 6/15/2018
#
############################################################################################
class Cell_scraper:

	#####################################################################################
	# 
	# The constructor of this class takes a string containing the url to search for the
	# the cell line on the expasy database. The first link in the result of that search
	# is then chosen to have data retrieved from. If no results are returned then 'NA'
	# is returned for all data and the year is set to zero.
	# 
	####################################################################################
	def __init__(self, url):

		#Make HTTP request
		req = requests.request('GET', url)

		#Grab the HTML that contains the search results for the cell
		self.results_page = BeautifulSoup(req.content, 'html.parser')

		#Find the first hyper link if it exists
		first_link = self.results_page.find('tr')
		
                #If the search was successful then a web page for the cell line on the expasy database was found.
		#The variable self.page_found is set to be True, meaning that we will be able to use all of the 
		#functions for grabbing information that this class has to offer. 
		if str(first_link) != 'None':				
			next_url = 'https://web.expasy.org/' + first_link.a['href']		
			# ~ Get HTML page that the first hyper link leads to.
			req = requests.request('GET', next_url)		
			self.page = BeautifulSoup(req.content, 'html.parser')
			self.page_found = True
	
		#If no results came back then no page was found. self.page_found gets set to False, meaning none
		#of the functions for grabbing data can be used.
		else:
			self.page_found = False

	#########################################################################################				
	# 
	# If a page for the cell line was found, this function looks up data stored in the table 
	# the table that expasy organizes all the data for the cell line in.
	#
	# @Return A string containing the data if it is available, otherwise it returns 'NA'.
        #
	########################################################################################
	def table_look_up(self, table_row):	
		if self.page_found == True:	
			#Loop through each row in the page's table
			for row in self.page.find_all('tr'):
				if str(row.th) != 'None':
					if str(row.th.string) == table_row:
						return row.td.contents[0].string
			else:
				return 'NA'
		else:
			return 'NA'
		
	######################################################################################################
        #
	# If a page for the cell line was found, this function grabs all of the years (If available) from 
        # the publication section of the expasy database and returns the earliest year from the 
        # publications section.
        # 
        # @Return A string containing the lowest year from the publication section, otherwise it returns 'NA'
        #        
	######################################################################################################
	def min_pub_yr(self):	
		if self.page_found == True:
			#Search for all years in the publication page
			yrs = []		
			yrs += re.findall('[ \( , ' ' ]19\d{2}[\) , ' ' , \.]' , str(self.page))
			yrs += re.findall('[ \( , ' ' ]20\d{2}[\) , ' ' , \.]' , str(self.page))
	
			#Convert list to string
			yrs = map(self.sub_str, yrs)
			yrs = map(int, yrs)
	
			#Return the samllest year
			if len(yrs) is 0:	#If no years were found print NA
				return 'NA'
			else:			#Else return all of the years
				return str(min(yrs))
		else:
			return 'NA'
	
	############################################################################################################
	#
	# This is a helper function used to remove the characers surrounding years found by the regular expression
	# used to find all of the years. It returns said modified string. This funcion is used as a lambda function		TODO: CHANGE NAME TO string_trimmer.
	# along with map() function to gracefully removes the non digit characters years returned from the regular 
	# expressions to find years so they can be converted into integers with the int() and map() functions 
	# and compared so the minimum year cab be found with the min() function.
        #
	# @Return A string with the first and last character removed
	# 
	############################################################################################################
	def sub_str(self,str):
		return str[1:len(str)-1]
	
	##########
	#Function# ~ This function grabs the list of urls of the cell line collections that have this cell line in there collection 
	##########   
	def search_cell_line_collections(self):
		if self.page_found == True:		
			#Return message
			rtn = ''		
	
			#Grab cell line collections row from expasy page
			clc = ''
			for row in self.page.find_all('tr'):
				if str(row.th) != 'None':
					if str(row.th.string) == 'Cell line collections':
						clc = row
						break

			#If no cell pages return NA for min cell year and ethnicity	
			if clc == '':
				return 'NA,NA'
	
			#Append all the hyper links in cell line collections section
			links = []
			for link in clc.find_all('a'):
				#print link.string
				links.append(link['href'])
			
			#Grab min year from publication	
			rtn += self.grab_min_year_and_ethnicity(links) 
		
			return rtn
		else:
			return 'NA,NA'

	##########
	#Function# ~ Searches through specific HTML tags known to contain the year of origin for a cell line.
	##########
	def grab_years(self , tag_type , url_page):
		yrs = []
		for tag in url_page.find_all(tag_type):
			#Filter out any unreadable characters that would prevent valid years to be searched and convert the HTML tag to a String.				
			tag_str = unicodedata.normalize('NFKD', unicode(tag)).encode('ascii' , 'ignore')  	
			
			####################################################################################################			
			#Uses a regular expresssion to search through each HTML tag for years in the following formats...
			#	Any year that is...
			#	-In the 1900s
			#	-In the 2000s
			#       -At the start of a line
			#	-At the end of a line
			#	-At the end of a sentence, for instance 1968.
			#	-Surrounded in parentheses (1968)
			#	-At the start or end of a HTML tag, for instance <p>1968</p>
			#	-Has a semi colon following it 1968;
			#	-And any combination of the above!
			####################################################################################################

       			yrs += re.findall('[ ^ , \( , \s , \> ]19\d{2}[ \) , \s , \. , ; , $ , \< ]' , str(tag_str))
			yrs += re.findall('[ ^ , \( , \s , \> ]20\d{2}[ \) , \s , \. , ; , $ , \< ]' , str(tag_str))
			
		return yrs

	###########
	#Functions# ~ Opens up each cell line collection website for the cell line and uses the grab_years and grab_ethnicity function to grab the year of origin and  
	###########   Ethnicity if it is available.
	def grab_min_year_and_ethnicity(self,links):

		if self.page_found == True:
			
			#List to contian the min years from each web page
			master_yr_list = []

			#Variable that will contain the ethncity of the cell
			ethnicity = 'NA'
			
			#For each valid cell line collection url, grab the ethnicity and the minimum year of origin if they are available. 
			for url in links:
				
				#Create list to store years and a String to store the ethnicity#
				yrs = []
	
				#List of cell line collection webiste urls that do not have any useful information relating to ethnicity or years. These are the bad urls.
				bad_url = ['en.pasteur.ac' , 'clsgmbh' , 'ibvr.org' , 'kcb.kiz' , 'cellbank.snu.ac.kr' , 'coriell.org', 
					  'www.fli.de/en/services', 'dtp.cancer.gov']
				
				#Boolean value that gets flipped if it turns out that the website has no useful data.
	                        no_data = False  

				#Check if the cell line collection web page is one of the bad urls.
				for url_str in bad_url:
					if url_str in url:	
						no_data = True
						break

				#If if the cell line collection has no useful data then skip it.
				if no_data is True:
					continue
			
				#If there is some issue in connecting to tha page then skip this cell line collection.
				try:
			        	url_req = requests.request('GET', url)
				except requests.exceptions.SSLError:
					#'failed to connect to web page'
					continue			

				#Grab HTML from the page, prepare lists for years
       				url_page = BeautifulSoup(url_req.content,'html.parser')

				#Depending on the cell line collection website, search ONLY in the tags where years amd ethnicity related to cell
				#line can be found.

				#TODO add case for - https://www.aidsreagent.org/reagentdetail.cfm?t=cell_lines&id=322


				#Search for the cells ethnicity
				if 'brc.riken' in url:
					ethnicity = self.grab_ethnicity(url_page, ethnicity)

			        #Search years from <span> tags
				if 'www.phe-culturecollections.org' in url:
					#Search for years
					yrs += self.grab_years('span' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page , ethnicity)
					
				#Search years from <dd> tags
				if 'dsmz.de/catalogues' in url:
					#Search for years
					yrs += self.grab_years('dd' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page , ethnicity)
					
				#Search years from <p> tags	
				if 'www.atcc.org' in url or 'www.addexbio.com' in url:
					#Search for years
					yrs += self.grab_years('p' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page , ethnicity)
					
				#Search years from <td> tags
				if 'www.atcc.org' in url or 'catalog.bcrc.firdi.org' in url or 'iclc.it/details' in url or 'http://cellbank.nibiohn.go.jp' in url or 'idac.tohoku.ac' in url:	
					#Search for years
					yrs += self.grab_years('td' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page , ethnicity)
					
				#Search years from <div> tags
				if 'http://bcrj.org.br' in url:
					#Search for years
					yrs += self.grab_years('div' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page, ethnicity)			
				
			        #Remove any characters surrounding that years.
				yrs = map(self.sub_str, yrs)  
				
				#Convert each year to an in the minimum year can be found			
				yrs = map(int, yrs)

				#Print years fro testing
				print 'Years pulled from ' + str(url)
				print yrs

				#Append the minimum year if one exists
			        if len(yrs) is not 0 :
			                master_yr_list.append(min(yrs))
				
			#TODO REMOVE YEARS LESS THAN 1950

			#Return the overll minimum year.
			if len(master_yr_list) is not 0:
			        return str(min(master_yr_list)) + ',' + str(ethnicity)
			else:
				return 'NA' + ',' + str(ethnicity)	
		else:
			return 'NA,NA'	

	##########
	#Function# 
	##########
	def grab_ethnicity(self,url_page,cell_eth):
		#Types of possible ethinicites for cell lines.
		categories = ['Caucasian' , 'caucasian' , 'Chinese' ,'chinese' , 'Japanese' , 'japanese' , 
			      'Filipino' , 'filipino' , 'Korean' , 'korean' , 'Vietnamese', 'vietnamese',
			      'African American' , 'african american' , 'Black' , 'black']
		
		#Search the entire HTML page for the ethnicity
		#Convert HTML to unicode then back to ascii form to filter out any unreadable characters
                page_str = unicodedata.normalize('NFKD', unicode(url_page)).encode('ascii' , 'ignore')			
		

		if cell_eth == 'NA':
			for ethnicity in categories:
				if ethnicity in str(page_str):
					return ethnicity
			else:
				return cell_eth
		else:
			return cell_eth
	
######	
#Main# ~ Main function.
######
def main():

	####################
	# Acquire URL List #
	####################
	
	# Url template used to search for specific cell line on the Expasy database 
	# https://web.expasy.org/cgi-bin/cellosaurus/search?input=your_query	

	#Open a csv file containing the names of all the spread sheets
	with open('cell_lines.csv') as csvfile:
		
		#Make a csv reader
		reader = csv.DictReader(csvfile)
		
		#String that contains the url template to search for a specific cell ine on the Expasy database.
		query_url = 'https://web.expasy.org/cgi-bin/cellosaurus/search?input='
	
		#A list to contain all of the URLs for searching each cell line.
		query_list = []
		
		#For each cell line primary name that was scanned by the reader, a url to search for that cell line is created and then  
		for row in reader:
                	query_list.append(query_url + row['Cell line primary name'])

		#The row number of the cell line in the spread sheet.
		index = 1
		
		for query in query_list:
			obj = Cell_scraper(query)
	
			#Prints out data in a csv format.

			#print obj.table_look_up('Cell line name') + ',' + obj.table_look_up('Synonyms') + ',' + obj.table_look_up('Sex of cell') + ',' + obj.table_look_up('Age at sampling') + ',' + obj.min_pub_yr() + ',' + obj.scrape_clc()
			

			#Prints out data in a more readable format 

			print '__________' + str(index) + '__________'
			print obj.table_look_up('Cell line name')
			print obj.table_look_up('Synonyms')
			print obj.table_look_up('Sex of cell')
			print obj.table_look_up('Age at sampling')
			print obj.min_pub_yr()
			print obj.search_cell_line_collections()
			index += 1	

#############
#Run Program#
#############				
if __name__ == '__main__':
	main()

#TODO - Find a way to determine what cell line it came from.
	#Use a dictionary some how...
#UTLIMATE TODO! - Make sure we can retreive data from all cell line websites
	#Make a list of all cell lines and note what HTML tags the years are contained in.
	#Make sure to only search through those tags for that cell line. This will improve speed and reduce chances of
	#picking up a date unrealted to the cell line. 

##############
#TESTING ZONE#
##############                  
#req = requests.request('GET' , 'https://web.expasy.org/cgi-bin/cellosaurus/search?input=ABC-1')
#page = BeautifulSoup(req.content, 'html.parser')
#print page
#lst = []

